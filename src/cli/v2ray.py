from subprocess import Popen, PIPE
import multiprocessing
from multiprocessing import Process
from time import sleep
from dataclasses import dataclass
import psutil
import netifaces
import json
from os import path
import win32gui, win32con

from typedef.konstants import ConfParams 
from conf.meile_config import MeileGuiConfig

class V2RayHandler():
    MeileConfig = MeileGuiConfig()
    v2ray_script = None
    v2ray_pid    = None
    tunproc      = "tun2socks.exe"
    v2rayproc    = "v2ray.exe"
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_CONSOLE = 0x00000010
    
    def __init__(self, script, **kwargs):
        self.v2ray_script = script

        print(self.v2ray_script)
    
    def fork_v2ray(self):
        v2ray_daemon_cmd = 'cmd.exe /c start cmd.exe /k gsudo.exe %s' %(self.v2ray_script)
        #v2ray_daemon_cmd = 'gsudo.exe %s' %(self.v2ray_script)
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True,stdout=PIPE,stderr=PIPE)
        sleep(10)
        print("PID: %s" % v2ray_srvc_proc.pid)
        hwnd = win32gui.FindWindow(None, f'C:\\Windows\\system32\\cmd.exe')
        print(hwnd)
        win32gui.ShowWindow(hwnd,win32con.SW_HIDE)
        self.v2ray_pid = v2ray_srvc_proc.pid

        
    def enum_windows_callback(self, hwnd, wildcard):
        if wildcard in win32gui.GetClassName(hwnd).lower():
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            
    def start_daemon(self):
        
        print("Starting v2ray service...")
        
        routes_bat = 'routes.bat'
        gateways = netifaces.gateways()
        
        # This is a little tricky on windows, we may be able to use instead:
        # One person complained not working on Ethernet, this may solve it:
        default_gateway = gateways[netifaces.AF_INET][0][0]
        
        #default_gateway = gateways['default'][netifaces.AF_INET][0]
        
        SERVER = self.read_v2ray_config()
        #wifidx = self.get_primary_if_idx(netifaces.gateways()['default'][netifaces.AF_INET][1])
        
        batfile = open(routes_bat, 'w')
        
        batfile.write('CD "%s"\n' % path.join(self.MeileConfig.BASEBINDIR, "V2Ray"))
        batfile.write('START "" /B %s run -c %s\n' % (self.v2rayproc, path.join(self.MeileConfig.BASEDIR, "v2ray_config.json")))
        batfile.write('timeout /t 1\n')
        batfile.write('CD "%s"\n' % self.MeileConfig.BASEBINDIR)
        batfile.write('START "" /B %s -device tun://tun00 -proxy socks5://127.0.0.1:1080"\n' % self.tunproc)
        #v2ray = [path.join(self.MeileConfig.BASEBINDIR, "V2Ray", self.v2rayproc), "run", "-c",path.join(self.MeileConfig.BASEDIR, "v2ray_config.json")]
        #Popen(v2ray, shell=False)
        #sleep(3)
        #tun2socks = [path.join(self.MeileConfig.BASEBINDIR, self.tunproc), "-device", "tun://tun00", "-proxy", "socks5://127.0.0.1:1080"]
        #Popen(tun2socks, shell=False)
        #sleep(5)
        batfile.write('timeout /t 3\n')
        batfile.write('netsh interface ip set address "tun00" static address=10.10.10.2 mask=255.255.255.0 gateway=10.10.10.1\n')
        batfile.write('netsh interface ip set dns name="tun00" static 1.1.1.1\n')
        batfile.write('route add %s %s metric 5\n' % (SERVER, default_gateway))
        batfile.write('route add 0.0.0.0 mask 0.0.0.0 10.10.10.1')
        batfile.flush()
        batfile.close()
        
        self.v2ray_script = routes_bat
        
        #multiprocessing.get_context('spawn')
        #fork = Process(target=self.fork_v2ray)
        #fork.run()
        self.fork_v2ray()
        
        return True
    
    def kill_daemon(self):
        
        SERVER = self.read_v2ray_config()
        gateways = netifaces.gateways()
        #print(gateways['default'][netifaces.AF_INET])
        # This is a little tricky on windows, we may be able to use instead:
        # One person complained not working on Ethernet, this may solve it:
        default_gateway = gateways[netifaces.AF_INET][0][0]
        
        #default_gateway = gateways['default'][netifaces.AF_INET][0]
        #wifidx = self.get_primary_if_idx(netifaces.gateways()['default'][netifaces.AF_INET][1])
        
        routes_bat = 'delroutes.bat'
        
        batfile = open(routes_bat, 'w')
        
        batfile.write('route delete %s %s metric 5\n' % (SERVER, default_gateway))
        batfile.write('route delete 0.0.0.0 mask 0.0.0.0 10.10.10.1\n')
        batfile.write('netsh interface set interface name="tun00" disable\n')
        batfile.write('timeout /t 3\n')
        batfile.write('TASKKILL /F /IM tun2socks.exe\n')
        batfile.write('TASKKILL /F /IM v2ray.exe\n')
        batfile.write('TASKKILL /F /IM cmd.exe\n')
        batfile.flush()
        batfile.close()
        
        self.v2ray_script = routes_bat
        
        v2ray_daemon_cmd = 'gsudo.exe %s' %(self.v2ray_script)
        proc2 = Popen(v2ray_daemon_cmd, shell=True)
        proc2.wait(timeout=30)
        proc_out,proc_err = proc2.communicate()
        return proc2.returncode
        
    def read_v2ray_config(self):
        
        with open(path.join(self.MeileConfig.BASEDIR, 'v2ray_config.json'), 'r') as V2RAYFILE:
            v2ray = V2RAYFILE.read()
        
        JSON = json.loads(v2ray)
        
        return JSON['outbounds'][0]['settings']['vnext'][0]['address']
    
@dataclass
class V2RayConfiguration:
    api_port: int

    vmess_port: int
    vmess_address: str
    vmess_uid: str
    vmess_transport: str

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
                    "protocol": "vmess",
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