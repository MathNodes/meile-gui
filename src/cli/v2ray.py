import subprocess
from subprocess import Popen, PIPE
import multiprocessing
from multiprocessing import Process
from time import sleep
from dataclasses import dataclass
import sys
import os
import tempfile
import socket, time


from conf.meile_config import MeileGuiConfig
from helpers.helpers import wait_for_port


# Platform-conditional imports
if sys.platform == 'win32':
    import threading
    import psutil
    import netifaces
    import json
    from os import path
    import win32gui, win32con
    from typedef.konstants import ConfParams
elif sys.platform == 'darwin':
    import tempfile
    from os import path
    from typedef.konstants import ConfParams,NodeKeys
elif sys.platform.startswith('linux'):
    import psutil
    from typedef.konstants import ConfParams
    import threading
    

# ---------------------------------------------------------------------------
# V2RayHandler – one class per platform, selected at the bottom of this
# section via V2RayHandler = _LinuxV2RayHandler | _WindowsV2RayHandler | …
# ---------------------------------------------------------------------------

class _LinuxV2RayHandler():
    v2ray_script = None
    v2ray_pid    = None

    def __init__(self, script, **kwargs):
        self.v2ray_script = script
        print(f"v2ray_script: {self.v2ray_script}")
        print(self.v2ray_script)

    def fork_v2ray(self):
        v2ray_daemon_cmd = (
            'pkexec env PATH=%s %s'
            % (ConfParams.PATH, self.v2ray_script)
        )
        v2ray_srvc_proc = Popen(
            v2ray_daemon_cmd, shell=True, close_fds=True
        )

        print("PID: %s" % v2ray_srvc_proc.pid)

        self.v2ray_pid = v2ray_srvc_proc.pid

    

    def start_daemon(self):
        print("Starting v2ray service...")

        try:
            self.fork_v2ray()
        except Exception as e:
            print(f"[start_daemon] fork_v2ray failed: {e!r}")
            return False

        result = {"ok": False}

        def worker():
            try:
                result["ok"] = wait_for_port("127.0.0.1", 1080, timeout=120)
            except Exception as e:
                print(f"[start_daemon] worker error: {e!r}")
                result["ok"] = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        while t.is_alive():
            print(".", end="", flush=True)
            time.sleep(0.3) 

        return result["ok"]

    def kill_daemon(self):
        v2ray_daemon_cmd = (
            'pkexec env PATH=%s %s'
            % (ConfParams.PATH, self.v2ray_script)
        )
        proc2 = Popen(v2ray_daemon_cmd, shell=True)
        proc2.wait(timeout=30)
        proc_out, proc_err = proc2.communicate()
        return proc2.returncode

class _WindowsV2RayHandler():
    MeileConfig = MeileGuiConfig()
    v2ray_script = None
    v2ray_pid    = None
    tunproc      = "tun2socks.exe"
    v2rayproc    = "xray.exe"
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_CONSOLE = 0x00000010
    WINDOW_TITLE = "meile_v2ray_daemon"

    def __init__(self, script, **kwargs):
        self.v2ray_script = script
        print(self.v2ray_script)

    def fork_v2ray(self):
        # Use "title" command so we can find the window
        # reliably by its exact title
        v2ray_daemon_cmd = (
            'cmd.exe /c start "%s" cmd.exe /k gsudo.exe %s'
            % (self.WINDOW_TITLE, self.v2ray_script)
        )
        v2ray_srvc_proc = Popen(
            v2ray_daemon_cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE
        )
        sleep(5)
        print("PID: %s" % v2ray_srvc_proc.pid)

        # Find and hide the window by our known title
        hwnd = self._find_window_by_title(self.WINDOW_TITLE)
        if hwnd:
            print("Found window hwnd=%s, hiding..." % hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        else:
            print("WARNING: Could not find cmd window to hide")

        self.v2ray_pid = v2ray_srvc_proc.pid

    def _find_window_by_title(self, title):
        """
        Enumerate all windows and find the one whose
        title contains our unique identifier.
        """
        result = []

        def callback(hwnd, _):
            window_title = win32gui.GetWindowText(hwnd)
            if title in window_title:
                result.append(hwnd)
            return True

        win32gui.EnumWindows(callback, None)

        if result:
            return result[0]
        return None

    def start_daemon(self):

        print("Starting v2ray service...")

        routes_bat = 'routes.bat'
        gateways = netifaces.gateways()

        default_gateway = gateways[netifaces.AF_INET][0][0]

        SERVER = self.read_v2ray_config()

        batfile = open(routes_bat, 'w')

        batfile.write('CD "%s"\n' % self.MeileConfig.BASEBINDIR)
        batfile.write('START "" /B %s run -c %s\n' % (self.v2rayproc, path.join(self.MeileConfig.BASEDIR, "v2ray_config.json")))
        batfile.write('timeout /t 1\n')
        batfile.write('START "" /B %s -device tun://tun00 -proxy socks5://127.0.0.1:1080"\n' % self.tunproc)
        batfile.write('timeout /t 2\n')
        batfile.write('netsh interface ip set address "tun00" static address=10.10.10.2 mask=255.255.255.0 gateway=10.10.10.1\n')
        batfile.write('netsh interface ip set dns name="tun00" static 1.1.1.1\n')
        batfile.write('route add %s %s metric 5\n' % (SERVER, default_gateway))
        batfile.write('route add 0.0.0.0 mask 0.0.0.0 10.10.10.1')
        batfile.flush()
        batfile.close()

        self.v2ray_script = routes_bat

        try:
            self.fork_v2ray()
        except Exception as e:
            print(f"[start_daemon] fork_v2ray failed: {e!r}")
            return False

        result = {"ok": False}

        def worker():
            try:
                result["ok"] = wait_for_port("127.0.0.1", 1080, timeout=120)
            except Exception as e:
                print(f"[start_daemon] worker error: {e!r}")
                result["ok"] = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        while t.is_alive():
            print(".", end="", flush=True)
            time.sleep(0.3) 

        return result["ok"]

    def kill_daemon(self):

        SERVER = self.read_v2ray_config()
        gateways = netifaces.gateways()
        default_gateway = gateways[netifaces.AF_INET][0][0]

        routes_bat = 'delroutes.bat'

        batfile = open(routes_bat, 'w')

        batfile.write('route delete %s %s metric 5\n' % (SERVER, default_gateway))
        batfile.write('route delete 0.0.0.0 mask 0.0.0.0 10.10.10.1\n')
        batfile.write('netsh interface set interface name="tun00" disable\n')
        batfile.write('timeout /t 3\n')
        batfile.write('TASKKILL /F /IM tun2socks.exe\n')
        batfile.write('TASKKILL /F /IM xray.exe\n')
        batfile.flush()
        batfile.close()

        self.v2ray_script = routes_bat

        # Use our known title so we can find/kill it
        v2ray_daemon_cmd = 'gsudo.exe %s' % (self.v2ray_script)
        proc2 = Popen(v2ray_daemon_cmd, shell=True)
        proc2.wait(timeout=30)
        proc_out, proc_err = proc2.communicate()

        # Kill the hidden cmd.exe window we spawned
        hwnd = self._find_window_by_title(self.WINDOW_TITLE)
        if hwnd:
            win32gui.PostMessage(
                hwnd, win32con.WM_CLOSE, 0, 0
            )

        return proc2.returncode

    def read_v2ray_config(self):

        with open(path.join(self.MeileConfig.BASEDIR, 'v2ray_config.json'), 'r') as V2RAYFILE:
            v2ray = V2RAYFILE.read()

        JSON = json.loads(v2ray)

        return JSON['outbounds'][0]['settings']['vnext'][0]['address']
        

class _DarwinV2RayHandler:
    v2ray_pid = 0

    def __init__(self, script_path, **kwargs):
        self.script_path = script_path
        self.processes = []
        self.MeileConfig = MeileGuiConfig()

    def run_privileged_script(self, commands):
        script_content = "#!/bin/bash\n"
        script_content += "\n".join(commands)

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.sh', delete=False
        ) as f:
            f.write(script_content)
            temp_script_path = f.name

        os.chmod(temp_script_path, 0o755)

        applescript = f'''
        tell application "System Events"
            do shell script "{temp_script_path}" with administrator privileges
        end tell
        '''

        try:
            proc = subprocess.Popen(
                ['osascript', '-e', applescript],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = proc.communicate(timeout=120)

            os.unlink(temp_script_path)

            if proc.returncode == 0:
                return True
            else:
                print(
                    "Privileged script failed with"
                    " return code %s" % proc.returncode
                )
                print(f"STDERR: {stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Privileged execution timed out")
            try:
                proc.kill()
            except:
                pass
            os.unlink(temp_script_path)
            return False
        except Exception as e:
            print(f"Error running privileged script: {e}")
            os.unlink(temp_script_path)
            return False

    def run_cmd(self, cmd, background=False):
        if background:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return process
        else:
            return subprocess.run(cmd, shell=True, timeout=30)

    def start_daemon(self, proto: str = "V2Ray"):
        if proto == NodeKeys.ProtocolTypes[1]: 
            print("Starting v2ray service...")
            PLIST_DIR = os.path.expanduser("~/.meile-gui/launchd")
            xray_plist = f"{PLIST_DIR}/app.meile.xray.plist"
            tun2_plist = f"{PLIST_DIR}/app.meile.tun2socks.plist"
    
            privileged_commands = [
                'mkdir -p "/Library/Application Support/Meile/launchd"',
                f'cp "{xray_plist}" "/Library/Application Support/Meile/launchd/"',
                f'cp "{tun2_plist}" "/Library/Application Support/Meile/launchd/"',
                'chown -R root:wheel "/Library/Application Support/Meile"',
                'chmod 755 "/Library/Application Support/Meile" "/Library/Application Support/Meile/launchd"',
                'chmod 644 "/Library/Application Support/Meile/launchd/"*.plist',
                "rm -rf /Library/LaunchDaemons/app.meile.tun2socks.plist",
                "rm -rf /Library/LaunchDaemons/app.meile.wireguard.plist",
                "rm -rf /Library/LaunchDaemons/app.meile.xray.plist",
                "launchctl enable system/app.meile.xray",
                'launchctl bootstrap system "/Library/Application Support/Meile/launchd/app.meile.xray.plist"',
            ]
            privileged_commands.append("sleep 3")
            privileged_commands.append(
                "curl --preproxy socks5://localhost:1080"
                " -s https://icanhazip.com"
            )
            privileged_commands.append("sleep 1")
            privileged_commands.append(f"launchctl enable system/app.meile.tun2socks")
            privileged_commands.append(f'launchctl bootstrap system "/Library/Application Support/Meile/launchd/app.meile.tun2socks.plist"')
            privileged_commands.append("sleep 2")
            privileged_commands.append("ifconfig utun123 198.18.0.1 198.18.0.1 up")
    
            networks = [
                "1.0.0.0/8",
                "2.0.0.0/7",
                "4.0.0.0/6",
                "8.0.0.0/5",
                "16.0.0.0/4",
                "32.0.0.0/3",
                "64.0.0.0/2",
                "128.0.0.0/1",
                "198.18.0.0/15",
            ]
    
            for network in networks:
                privileged_commands.append(
                    f"route add -net {network} 198.18.0.1"
                )
    
            if not self.run_privileged_script(privileged_commands):
                print("Failed to execute privileged commands")
                return False
    
            return True
        elif proto == NodeKeys.ProtocolTypes[3]:
            print("Starting xray service...")
            PLIST_DIR = os.path.expanduser("~/.meile-gui/launchd")
            xray_plist = f"{PLIST_DIR}/app.meile.xray.plist"
            tun2_basename = "app.meile.tun2socks-xray.plist"
            tun2_plist = f"{PLIST_DIR}/{tun2_basename}"
            dest = "/Library/Application Support/Meile/launchd"
        
            # --- computed unprivileged, before routes are hijacked ---
            gw_cmd = (
                "route -n get default 2>/dev/null "
                "| awk '/gateway:/ {print $2}'"
            )
            GW = subprocess.check_output(gw_cmd, shell=True, text=True).strip()
            if not GW:
                print("Could not determine default gateway; aborting.")
                return False
        
            proxy_ip_file = path.join(ConfParams.KEYRINGDIR, "xray.proxy")
            with open(proxy_ip_file, "r") as f:
                XRAY_SERVER = f.read().strip()
            if not XRAY_SERVER:
                print("No server IP in xray.proxy; aborting.")
                return False
        
            privileged_commands = [
                f'mkdir -p "{dest}"',
                f'cp "{xray_plist}" "{dest}/"',
                f'cp "{tun2_plist}" "{dest}/"',
                'chown -R root:wheel "/Library/Application Support/Meile"',
                f'chmod 755 "/Library/Application Support/Meile" "{dest}"',
                f'chmod 644 "{dest}/"*.plist',
                "rm -rf /Library/LaunchDaemons/app.meile.tun2socks.plist",
                "rm -rf /Library/LaunchDaemons/app.meile.wireguard.plist",
                "rm -rf /Library/LaunchDaemons/app.meile.xray.plist",
                "launchctl enable system/app.meile.xray",
                f'launchctl bootstrap system "{dest}/app.meile.xray.plist"',
                "sleep 3",
                "curl --preproxy socks5://localhost:1080 -s https://icanhazip.com",
                "sleep 1",
                "launchctl enable system/app.meile.tun2socks-xray",
                f'launchctl bootstrap system "{dest}/{tun2_basename}"',
                "sleep 2",
                "ifconfig utun123 198.18.0.1 198.18.0.1 up",
                f"route add -host {XRAY_SERVER} {GW}",
            ]
        
            networks = [
                "1.0.0.0/8", "2.0.0.0/7", "4.0.0.0/6", "8.0.0.0/5",
                "16.0.0.0/4", "32.0.0.0/3", "64.0.0.0/2", "128.0.0.0/1",
                "198.18.0.0/15",
            ]
            for network in networks:
                privileged_commands.append(f"route add -net {network} 198.18.0.1")
        
            if not self.run_privileged_script(privileged_commands):
                print("Failed to execute privileged commands")
                return False
        
            return True
        elif proto == NodeKeys.ProtocolTypes[5]:
            print("Starting Hysteria2 service...")
            PLIST_DIR = os.path.expanduser("~/.meile-gui/launchd")
            hysteria_plist = f"{PLIST_DIR}/app.meile.hysteria.plist"
            tun2_basename = "app.meile.tun2socks-xray.plist"
            tun2_plist = f"{PLIST_DIR}/{tun2_basename}"
            dest = "/Library/Application Support/Meile/launchd"
        
            # --- computed unprivileged, before routes are hijacked ---
            gw_cmd = (
                "route -n get default 2>/dev/null "
                "| awk '/gateway:/ {print $2}'"
            )
            GW = subprocess.check_output(gw_cmd, shell=True, text=True).strip()
            if not GW:
                print("Could not determine default gateway; aborting.")
                return False
        
            proxy_ip_file = path.join(ConfParams.KEYRINGDIR, "hysteria.proxy")
            with open(proxy_ip_file, "r") as f:
                XRAY_SERVER = f.read().strip()
            if not XRAY_SERVER:
                print("No server IP in xray.proxy; aborting.")
                return False
        
            privileged_commands = [
                f'mkdir -p "{dest}"',
                f'cp "{hysteria_plist}" "{dest}/"',
                f'cp "{tun2_plist}" "{dest}/"',
                'chown -R root:wheel "/Library/Application Support/Meile"',
                f'chmod 755 "/Library/Application Support/Meile" "{dest}"',
                f'chmod 644 "{dest}/"*.plist',
                "rm -rf /Library/LaunchDaemons/app.meile.tun2socks.plist",
                "rm -rf /Library/LaunchDaemons/app.meile.wireguard.plist",
                "rm -rf /Library/LaunchDaemons/app.meile.xray.plist",
                "launchctl enable system/app.meile.hysteria",
                f'launchctl bootstrap system "{dest}/app.meile.hysteria.plist"',
                "sleep 3",
                "curl --preproxy socks5://localhost:1080 -s https://icanhazip.com",
                "sleep 1",
                "launchctl enable system/app.meile.tun2socks-xray",
                f'launchctl bootstrap system "{dest}/{tun2_basename}"',
                "sleep 2",
                "ifconfig utun123 198.18.0.1 198.18.0.1 up",
                f"route add -host {XRAY_SERVER} {GW}",
            ]
        
            networks = [
                "1.0.0.0/8", "2.0.0.0/7", "4.0.0.0/6", "8.0.0.0/5",
                "16.0.0.0/4", "32.0.0.0/3", "64.0.0.0/2", "128.0.0.0/1",
                "198.18.0.0/15",
            ]
            for network in networks:
                privileged_commands.append(f"route add -net {network} 198.18.0.1")
        
            if not self.run_privileged_script(privileged_commands):
                print("Failed to execute privileged commands")
                return False
        
            return True
        else:
            return False
            

    def kill_daemon(self, proto: str = "V2Ray"):
        if proto == NodeKeys.ProtocolTypes[1]: 
            privileged_commands = []
    
            networks = [
                "1.0.0.0/8",
                "2.0.0.0/7",
                "4.0.0.0/6",
                "8.0.0.0/5",
                "16.0.0.0/4",
                "32.0.0.0/3",
                "64.0.0.0/2",
                "128.0.0.0/1",
                "198.18.0.0/15",
            ]
    
            for network in networks:
                privileged_commands.append(
                    f"route delete -net {network} 198.18.0.1"
                )
    
            privileged_commands.append(
                "ifconfig utun123 198.18.0.1 198.18.0.1 down"
            )
            privileged_commands.append(f'launchctl bootout system "/Library/Application Support/Meile/launchd/app.meile.xray.plist" ; launchctl bootout system "/Library/Application Support/Meile/launchd/app.meile.tun2socks.plist" ; launchctl disable system/app.meile.xray ; launchctl disable system/app.meile.tun2socks')
    
            self.run_privileged_script(privileged_commands)
    
            for proc in self.processes:
                proc.terminate()
    
            return True
        elif proto == NodeKeys.ProtocolTypes[3]:
            tun2_basename = "app.meile.tun2socks-xray.plist"
            dest = "/Library/Application Support/Meile/launchd"
        
            # --- computed unprivileged, before routes are hijacked ---
            gw_cmd = (
                "route -n get default 2>/dev/null "
                "| awk '/gateway:/ {print $2}'"
            )
            GW = subprocess.check_output(gw_cmd, shell=True, text=True).strip()
            if not GW:
                print("Could not determine default gateway; aborting.")
                return False
        
            proxy_ip_file = path.join(ConfParams.KEYRINGDIR, "xray.proxy")
            with open(proxy_ip_file, "r") as f:
                XRAY_SERVER = f.read().strip()
            if not XRAY_SERVER:
                print("No server IP in xray.proxy; aborting.")
                return False
            privileged_commands = []
            
            privileged_commands.append(f"route delete -host {XRAY_SERVER} {GW}")
    
            networks = [
                "1.0.0.0/8",
                "2.0.0.0/7",
                "4.0.0.0/6",
                "8.0.0.0/5",
                "16.0.0.0/4",
                "32.0.0.0/3",
                "64.0.0.0/2",
                "128.0.0.0/1",
                "198.18.0.0/15",
            ]
    
            for network in networks:
                privileged_commands.append(
                    f"route delete -net {network} 198.18.0.1"
                )
    
            privileged_commands.append(
                "ifconfig utun123 198.18.0.1 198.18.0.1 down"
            )
            privileged_commands.append(f'launchctl bootout system "{dest}/app.meile.xray.plist" ; launchctl bootout system "{dest}/{tun2_basename}" ; launchctl disable system/app.meile.xray ; launchctl disable system/app.meile.tun2socks-xray')
    
            self.run_privileged_script(privileged_commands)
    
            for proc in self.processes:
                proc.terminate()
    
            return True
        elif proto == NodeKeys.ProtocolTypes[5]:
            tun2_basename = "app.meile.tun2socks-xray.plist"
            dest = "/Library/Application Support/Meile/launchd"
        
            # --- computed unprivileged, before routes are hijacked ---
            gw_cmd = (
                "route -n get default 2>/dev/null "
                "| awk '/gateway:/ {print $2}'"
            )
            GW = subprocess.check_output(gw_cmd, shell=True, text=True).strip()
            if not GW:
                print("Could not determine default gateway; aborting.")
                return False
        
            proxy_ip_file = path.join(ConfParams.KEYRINGDIR, "hysteria.proxy")
            with open(proxy_ip_file, "r") as f:
                XRAY_SERVER = f.read().strip()
            if not XRAY_SERVER:
                print("No server IP in xray.proxy; aborting.")
                return False
            privileged_commands = []
            
            privileged_commands.append(f"route delete -host {XRAY_SERVER} {GW}")
    
            networks = [
                "1.0.0.0/8",
                "2.0.0.0/7",
                "4.0.0.0/6",
                "8.0.0.0/5",
                "16.0.0.0/4",
                "32.0.0.0/3",
                "64.0.0.0/2",
                "128.0.0.0/1",
                "198.18.0.0/15",
            ]
    
            for network in networks:
                privileged_commands.append(
                    f"route delete -net {network} 198.18.0.1"
                )
    
            privileged_commands.append(
                "ifconfig utun123 198.18.0.1 198.18.0.1 down"
            )
            privileged_commands.append(f'launchctl bootout system "{dest}/app.meile.hysteria.plist" ; launchctl bootout system "{dest}/{tun2_basename}" ; launchctl disable system/app.meile.hysteria ; launchctl disable system/app.meile.tun2socks-xray')
    
            self.run_privileged_script(privileged_commands)
    
            for proc in self.processes:
                proc.terminate()
    
            return True
            
        else:
            return False
            

# ---------------------------------------------------------------------------
# Select the correct handler for the current platform
# ---------------------------------------------------------------------------
if sys.platform.startswith('linux'):
    V2RayHandler = _LinuxV2RayHandler
elif sys.platform == 'win32':
    V2RayHandler = _WindowsV2RayHandler
elif sys.platform == 'darwin':
    V2RayHandler = _DarwinV2RayHandler
else:
    raise RuntimeError(
        f"Unsupported platform: {sys.platform}"
    )

# ---------------------------------------------------------------------------
# Configuration dataclasses – identical across all three platforms
# ---------------------------------------------------------------------------

@dataclass
class V2RayFragmentConfiguration:
    api_port: int

    vmess_port: int
    vmess_address: str
    vmess_uid: str
    vmess_transport: str
    proxy_protocol: str

    proxy_port: int = 1080

    def get(self) -> dict:
        return {
            "api": {
                "services": [
                    "StatsService"
                ],
                "tag": "api"
            },
            "inbounds": [
                {
                    "listen": "127.0.0.1",
                    "port": self.api_port,
                    "protocol": "dokodemo-door",
                    "settings": {
                        "address": "127.0.0.1"
                    },
                    "tag": "api"
                },
                {
                    "listen": "127.0.0.1",
                    "port": self.proxy_port,
                    "protocol": "socks",
                    "settings": {
                        "ip": "127.0.0.1",
                        "udp": True
                    },
                    "sniffing": {
                        "destOverride": [
                            "http",
                            "tls"
                        ],
                        "enabled": True
                    },
                    "tag": "proxy"
                }
            ],
            "log": {
                "loglevel": "none"
            },
            "outbounds": [
                {
                    "mux": {
                        "concurrency": -1,
                        "enabled": False
                    },
                    "protocol": self.proxy_protocol,
                    "settings": {
                        "vnext": [
                            {
                                "address": self.vmess_address,
                                "port": self.vmess_port,
                                "users": [
                                    {
                                        "alterId": 0,
                                        "id": self.vmess_uid,
                                        "level": 8,
                                        "security":
                                            "chacha20-poly1305"
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "grpcSettings": {
                            "authority": "",
                            "health_check_timeout": 20,
                            "idle_timeout": 60,
                            "multiMode": False,
                            "serviceName": ""
                        },
                        "network": self.vmess_transport,
                        "sockopt": {
                            "dialerProxy": "fragment",
                            "tcpKeepAliveIdle": 100,
                            "tcpNoDelay": True
                        }
                    },
                    "tag": "vmess"
                },
                {
                    "tag": "fragment",
                    "protocol": "freedom",
                    "settings": {
                        "domainStrategy": "AsIs",
                        "fragment": {
                            "packets": "1-3",
                            "length": "1-3",
                            "interval": "2-8"
                        }
                    },
                    "streamSettings": {
                        "sockopt": {
                            "tcpKeepAliveIdle": 100,
                            "tcpNoDelay": True
                        }
                    }
                },
                {
                    "protocol": "freedom",
                    "settings": {
                        "domainStrategy": "UseIP"
                    },
                    "tag": "direct"
                },
                {
                    "protocol": "blackhole",
                    "settings": {
                        "response": {
                            "type": "http"
                        }
                    },
                    "tag": "block"
                }
            ],
            "policy": {
                "levels": {
                    "0": {
                        "downlinkOnly": 0,
                        "uplinkOnly": 0
                    }
                },
                "system": {
                    "statsOutboundDownlink": True,
                    "statsOutboundUplink": True
                }
            },
            "routing": {
                "rules": [
                    {
                        "inboundTag": ["api"],
                        "outboundTag": "api",
                        "type": "field"
                    }
                ]
            },
            "stats": {}
        }

@dataclass
class V2RayConfiguration:
    api_port: int

    vmess_port: int
    vmess_address: str
    vmess_uid: str
    vmess_transport: str
    proxy_protocol: str

    proxy_port: int = 1080

    def get(self) -> dict:
        return {
            "api": {
                "services": [
                    "StatsService"
                ],
                "tag": "api"
            },
            "inbounds": [
                {
                    "listen": "127.0.0.1",
                    "port": self.api_port,
                    "protocol": "dokodemo-door",
                    "settings": {
                        "address": "127.0.0.1"
                    },
                    "tag": "api"
                },
                {
                    "listen": "127.0.0.1",
                    "port": self.proxy_port,
                    "protocol": "socks",
                    "settings": {
                        "ip": "127.0.0.1",
                        "udp": True
                    },
                    "sniffing": {
                        "destOverride": [
                            "http",
                            "tls"
                        ],
                        "enabled": True
                    },
                    "tag": "proxy"
                }
            ],
            "log": {
                "loglevel": "none"
            },
            "outbounds": [
                {
                    "protocol": self.proxy_protocol,
                    "settings": {
                        "vnext": [
                            {
                                "address": self.vmess_address,
                                "port": self.vmess_port,
                                "users": [
                                    {
                                        "alterId": 0,
                                        "id": self.vmess_uid
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": self.vmess_transport
                    },
                    "tag": "vmess"
                }
            ],
            "policy": {
                "levels": {
                    "0": {
                        "downlinkOnly": 0,
                        "uplinkOnly": 0
                    }
                },
                "system": {
                    "statsOutboundDownlink": True,
                    "statsOutboundUplink": True
                }
            },
            "routing": {
                "rules": [
                    {
                        "inboundTag": [
                            "api"
                        ],
                        "outboundTag": "api",
                        "type": "field"
                    }
                ]
            },
            "stats": {},
            "transport": {
                "dsSettings": {},
                "grpcSettings": {},
                "gunSettings": {},
                "httpSettings": {},
                "kcpSettings": {},
                "quicSettings": {
                    "security": "chacha20-poly1305"
                },
                "tcpSettings": {},
                "wsSettings": {}
            }
        }