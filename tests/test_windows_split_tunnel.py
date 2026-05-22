import configparser
import json
from types import SimpleNamespace

from helpers.windows_split_tunnel import (
    WindowsAppCatalog,
    WindowsDefaultRoute,
    WindowsRouteManager,
    get_split_tunnel_apps,
    is_split_tunnel_enabled,
    set_split_tunnel_apps,
)
from conf.meile_config import MeileGuiConfig


def test_split_tunnel_config_round_trip():
    config = configparser.ConfigParser()
    config.add_section("network")

    set_split_tunnel_apps(config, ["C:\\Apps\\Browser\\browser.exe", "C:\\Tools\\chat.exe"])
    config.set("network", "splittunnel", "1")

    assert is_split_tunnel_enabled(config)
    assert get_split_tunnel_apps(config) == [
        "C:\\Apps\\Browser\\browser.exe",
        "C:\\Tools\\chat.exe",
    ]


def test_windows_app_catalog_lists_unique_executables(tmp_path):
    root = tmp_path / "Program Files"
    app_dir = root / "Acme"
    app_dir.mkdir(parents=True)
    app = app_dir / "Acme.exe"
    app.write_text("", encoding="utf-8")
    duplicate = app_dir / "acme.EXE"
    duplicate.write_text("", encoding="utf-8")
    ignored = app_dir / "readme.txt"
    ignored.write_text("", encoding="utf-8")

    apps = WindowsAppCatalog(search_roots=[root]).list_apps()

    assert [(item.name, item.path) for item in apps] == [("Acme", str(app))]


def test_windows_app_catalog_parses_registry_apps():
    def runner(command, **kwargs):
        payload = [
            {
                "DisplayName": "Browser",
                "DisplayIcon": "C:\\Apps\\Browser\\browser.exe,0",
                "InstallLocation": "C:\\Apps\\Browser",
            },
            {
                "DisplayName": "Broken",
                "DisplayIcon": "",
                "InstallLocation": "",
            },
        ]
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    apps = WindowsAppCatalog(search_roots=[], runner=runner).list_apps()

    assert [(item.name, item.path) for item in apps] == [
        ("Browser", "C:\\Apps\\Browser\\browser.exe")
    ]


def test_route_manager_adds_host_routes_for_selected_process_destinations():
    commands = []

    def runner(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    processes = [
        {"pid": 100, "name": "browser.exe", "exe": "C:\\Apps\\Browser\\browser.exe"},
        {"pid": 200, "name": "other.exe", "exe": "C:\\Apps\\Other\\other.exe"},
    ]
    connections = [
        SimpleNamespace(pid=100, raddr=SimpleNamespace(ip="203.0.113.10")),
        SimpleNamespace(pid=100, raddr=("198.51.100.25", 443)),
        SimpleNamespace(pid=100, raddr=SimpleNamespace(ip="127.0.0.1")),
        SimpleNamespace(pid=200, raddr=SimpleNamespace(ip="192.0.2.50")),
    ]
    manager = WindowsRouteManager(
        runner=runner,
        process_provider=lambda: processes,
        connection_provider=lambda: connections,
    )

    added = manager.apply_routes(
        ["C:\\Apps\\Browser\\browser.exe"],
        WindowsDefaultRoute(interface_index=12, gateway="192.168.1.1"),
    )

    assert added == ["198.51.100.25", "203.0.113.10"]
    assert commands == [
        [
            "route",
            "add",
            "198.51.100.25",
            "mask",
            "255.255.255.255",
            "192.168.1.1",
            "IF",
            "12",
            "METRIC",
            "1",
        ],
        [
            "route",
            "add",
            "203.0.113.10",
            "mask",
            "255.255.255.255",
            "192.168.1.1",
            "IF",
            "12",
            "METRIC",
            "1",
        ],
    ]


def test_default_route_is_parsed_from_powershell_json():
    def runner(command, **kwargs):
        payload = {"InterfaceIndex": 7, "NextHop": "10.0.0.1"}
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    manager = WindowsRouteManager(runner=runner)

    assert manager.capture_default_route() == WindowsDefaultRoute(
        interface_index=7,
        gateway="10.0.0.1",
    )


def test_meile_config_adds_split_tunnel_defaults(tmp_path):
    meile_config = MeileGuiConfig()
    meile_config.BASEDIR = str(tmp_path)
    meile_config.CONFFILE = str(tmp_path / "config.ini")
    meile_config.IMGDIR = str(tmp_path / "img")

    config = meile_config.read_configuration(meile_config.CONFFILE)

    assert config.has_section("split_tunnel")
    assert config["network"]["splittunnel"] == "0"
    assert get_split_tunnel_apps(config) == []
