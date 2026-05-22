import configparser
import ipaddress
import json
import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from time import sleep


CONFIG_SECTION = "split_tunnel"
CONFIG_APPS_KEY = "apps"
CONFIG_ENABLED_KEY = "splittunnel"


@dataclass(frozen=True)
class WindowsApp:
    name: str
    path: str


@dataclass(frozen=True)
class WindowsDefaultRoute:
    interface_index: int
    gateway: str


def _ensure_config(config):
    if not config.has_section("network"):
        config.add_section("network")
    if not config.has_section(CONFIG_SECTION):
        config.add_section(CONFIG_SECTION)


def _path_key(value):
    return os.path.normpath(os.path.expandvars(str(value))).casefold()


def get_split_tunnel_apps(config):
    if not config.has_section(CONFIG_SECTION):
        return []

    raw_apps = config.get(CONFIG_SECTION, CONFIG_APPS_KEY, fallback="[]")
    try:
        apps = json.loads(raw_apps)
    except json.JSONDecodeError:
        apps = [line for line in raw_apps.splitlines() if line.strip()]

    selected = []
    seen = set()
    for app in apps:
        app_path = str(app).strip()
        if not app_path:
            continue
        key = _path_key(app_path)
        if key in seen:
            continue
        selected.append(app_path)
        seen.add(key)
    return selected


def set_split_tunnel_apps(config, apps):
    _ensure_config(config)
    selected = []
    seen = set()
    for app in apps:
        app_path = str(app).strip()
        if not app_path:
            continue
        key = _path_key(app_path)
        if key in seen:
            continue
        selected.append(app_path)
        seen.add(key)
    config.set(CONFIG_SECTION, CONFIG_APPS_KEY, json.dumps(selected))


def is_split_tunnel_enabled(config):
    if not config.has_section("network"):
        return False
    return config.getboolean("network", CONFIG_ENABLED_KEY, fallback=False)


def set_split_tunnel_enabled(config, enabled):
    _ensure_config(config)
    config.set("network", CONFIG_ENABLED_KEY, "1" if enabled else "0")


def split_tunnel_summary(apps):
    if not apps:
        return "No apps selected"
    names = [Path(app).stem for app in apps[:3]]
    suffix = "" if len(apps) <= 3 else f" +{len(apps) - 3}"
    return ", ".join(names) + suffix


class WindowsAppCatalog:
    def __init__(self, search_roots=None, walker=os.walk, runner=None):
        self.search_roots = search_roots
        self.walker = walker
        self.runner = runner or WindowsRouteManager._run

    def _default_search_roots(self):
        roots = []
        for env_name in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
            env_path = os.environ.get(env_name)
            if env_path:
                roots.append(Path(env_path))

        start_menu = os.environ.get("ProgramData")
        if start_menu:
            roots.append(Path(start_menu) / "Microsoft" / "Windows" / "Start Menu")

        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            roots.append(
                Path(user_profile)
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Windows"
                / "Start Menu"
            )
        return roots

    def list_apps(self, limit=250):
        apps = []
        seen = set()
        for app in self._registry_apps():
            self._append_app(apps, seen, app)
            if len(apps) >= limit:
                return sorted(apps, key=lambda app: app.name.casefold())

        roots = self.search_roots
        if roots is None:
            if os.name != "nt":
                return sorted(apps, key=lambda app: app.name.casefold())
            roots = self._default_search_roots()

        for root in roots:
            root = Path(root)
            if not root.exists():
                continue
            for dirpath, _, filenames in self.walker(root):
                for filename in sorted(filenames):
                    if not filename.lower().endswith(".exe"):
                        continue
                    app_path = str(Path(dirpath) / filename)
                    self._append_app(
                        apps,
                        seen,
                        WindowsApp(name=Path(filename).stem, path=app_path),
                    )
                    if len(apps) >= limit:
                        return sorted(apps, key=lambda app: app.name.casefold())
        return sorted(apps, key=lambda app: app.name.casefold())

    def _registry_apps(self):
        if os.name != "nt" and self.search_roots is None:
            return []
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "$paths = @("
                "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
                "'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
                "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'"
                "); "
                "Get-ItemProperty $paths -ErrorAction SilentlyContinue | "
                "Where-Object { $_.DisplayName } | "
                "Select-Object DisplayName,DisplayIcon,InstallLocation | "
                "ConvertTo-Json -Compress"
            ),
        ]
        try:
            result = self.runner(command)
        except OSError:
            return []
        if result.returncode != 0 or not result.stdout.strip():
            return []

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []
        if isinstance(payload, dict):
            payload = [payload]

        apps = []
        for item in payload:
            name = str(item.get("DisplayName") or "").strip()
            app_path = self._path_from_registry_item(item)
            if name and app_path:
                apps.append(WindowsApp(name=name, path=app_path))
        return apps

    @staticmethod
    def _path_from_registry_item(item):
        display_icon = str(item.get("DisplayIcon") or "").strip()
        if not display_icon:
            return None
        app_path = os.path.expandvars(display_icon.strip('"'))
        exe_index = app_path.lower().find(".exe")
        if exe_index >= 0:
            app_path = app_path[:exe_index + 4].strip().strip('"')
        if app_path.lower().endswith(".exe"):
            return app_path
        return None

    @staticmethod
    def _append_app(apps, seen, app):
        key = _path_key(app.path)
        if key in seen:
            return
        apps.append(app)
        seen.add(key)


class WindowsRouteManager:
    def __init__(
        self,
        runner=None,
        process_provider=None,
        connection_provider=None,
        state_path=None,
    ):
        self.runner = runner or self._run
        self.process_provider = process_provider or self._processes
        self.connection_provider = connection_provider or self._connections
        self.state_path = Path(state_path) if state_path else None

    @staticmethod
    def _run(command, **kwargs):
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            **kwargs,
        )

    @staticmethod
    def _processes():
        import psutil

        return psutil.process_iter(["pid", "name", "exe"])

    @staticmethod
    def _connections():
        import psutil

        return psutil.net_connections(kind="inet")

    def capture_default_route(self):
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "$route = Get-NetRoute -AddressFamily IPv4 "
                "-DestinationPrefix '0.0.0.0/0' | "
                "Where-Object { $_.NextHop -and $_.NextHop -ne '0.0.0.0' } | "
                "Sort-Object RouteMetric,InterfaceMetric | "
                "Select-Object -First 1 InterfaceIndex,NextHop; "
                "$route | ConvertTo-Json -Compress"
            ),
        ]
        result = self.runner(command)
        if result.returncode != 0 or not result.stdout.strip():
            return None

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        interface_index = payload.get("InterfaceIndex")
        gateway = payload.get("NextHop")
        if interface_index is None or not gateway:
            return None
        return WindowsDefaultRoute(interface_index=int(interface_index), gateway=gateway)

    def collect_destinations(self, app_paths):
        selected_paths = {_path_key(app) for app in app_paths}
        selected_names = {Path(app).name.casefold() for app in app_paths}
        selected_pids = set()

        for process in self.process_provider():
            info = process if isinstance(process, dict) else getattr(process, "info", {})
            pid = info.get("pid")
            exe = info.get("exe") or ""
            name = info.get("name") or Path(exe).name
            if not pid:
                continue
            if _path_key(exe) in selected_paths or name.casefold() in selected_names:
                selected_pids.add(pid)

        destinations = set()
        for conn in self.connection_provider():
            if getattr(conn, "pid", None) not in selected_pids:
                continue
            remote_ip = self._remote_ip(conn)
            if remote_ip and self._is_routeable_ipv4(remote_ip):
                destinations.add(remote_ip)
        return sorted(destinations)

    def apply_routes(self, app_paths, default_route=None):
        default_route = default_route or self.capture_default_route()
        if not default_route:
            return []

        state = self._load_state()
        known_routes = {
            (
                route.get("destination"),
                route.get("gateway"),
                route.get("interface_index"),
            )
            for route in state.get("routes", [])
        }
        added = []
        routes = state.get("routes", [])
        for destination in self.collect_destinations(app_paths):
            route_key = (
                destination,
                default_route.gateway,
                default_route.interface_index,
            )
            if route_key in known_routes:
                continue
            command = [
                "route",
                "add",
                destination,
                "mask",
                "255.255.255.255",
                default_route.gateway,
                "IF",
                str(default_route.interface_index),
                "METRIC",
                "1",
            ]
            result = self.runner(command)
            if result.returncode == 0:
                added.append(destination)
                routes.append(
                    {
                        "destination": destination,
                        "gateway": default_route.gateway,
                        "interface_index": default_route.interface_index,
                    }
                )
                known_routes.add(route_key)

        if added:
            state["routes"] = routes
            self._save_state(state)
        return added

    def remove_routes(self):
        state = self._load_state()
        for route in state.get("routes", []):
            destination = route.get("destination")
            gateway = route.get("gateway")
            if not destination or not gateway:
                continue
            self.runner(
                [
                    "route",
                    "delete",
                    destination,
                    "mask",
                    "255.255.255.255",
                    gateway,
                ]
            )
        if self.state_path and self.state_path.exists():
            self.state_path.unlink()

    @staticmethod
    def _remote_ip(connection):
        remote = getattr(connection, "raddr", None)
        if not remote:
            return None
        if hasattr(remote, "ip"):
            return remote.ip
        if isinstance(remote, (tuple, list)) and remote:
            return remote[0]
        return None

    @staticmethod
    def _is_routeable_ipv4(value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False
        return (
            address.version == 4
            and not address.is_loopback
            and not address.is_link_local
            and not address.is_multicast
            and not address.is_unspecified
        )

    def _load_state(self):
        if not self.state_path or not self.state_path.exists():
            return {"routes": []}
        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"routes": []}

    def _save_state(self, state):
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with self.state_path.open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=2)


class WindowsSplitTunnelSession:
    def __init__(self, manager, app_paths, default_route, interval=5):
        self.manager = manager
        self.app_paths = app_paths
        self.default_route = default_route
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if not self.app_paths or not self.default_route:
            return []

        added = self.manager.apply_routes(self.app_paths, self.default_route)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return added

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self.manager.remove_routes()

    def _loop(self):
        while not self._stop.is_set():
            sleep(self.interval)
            self.manager.apply_routes(self.app_paths, self.default_route)


_active_session = None


def activate_windows_split_tunnel(session):
    global _active_session
    if _active_session:
        _active_session.stop()
    _active_session = session
    if not _active_session:
        return []
    return _active_session.start()


def default_state_path():
    return Path.home() / ".meile-gui" / "split_tunnel_routes.json"


def prepare_windows_split_tunnel(config_path, route_manager=None):
    config = configparser.ConfigParser()
    config.read(config_path)
    app_paths = get_split_tunnel_apps(config)
    if not is_split_tunnel_enabled(config) or not app_paths:
        return None

    manager = route_manager or WindowsRouteManager(state_path=default_state_path())
    default_route = manager.capture_default_route()
    if not default_route:
        return None
    return WindowsSplitTunnelSession(manager, app_paths, default_route)


def stop_windows_split_tunnel(route_manager=None):
    global _active_session
    if _active_session:
        _active_session.stop()
        _active_session = None
        return

    manager = route_manager or WindowsRouteManager(state_path=default_state_path())
    manager.remove_routes()
