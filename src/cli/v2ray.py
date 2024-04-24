from subprocess import Popen
import multiprocessing
from multiprocessing import Process
from time import sleep
from dataclasses import dataclass
import psutil

from typedef.konstants import ConfParams 
from conf.meile_config import MeileGuiConfig

class V2RayHandler():
    v2ray_script = None
    v2ray_pid    = None
    
    def __init__(self, script, **kwargs):
        self.v2ray_script = script
        print(self.v2ray_script)
    
    def fork_v2ray(self):
        v2ray_daemon_cmd = 'pkexec env PATH=%s %s' %(ConfParams.PATH, self.v2ray_script)
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True,close_fds=True)
        
        print("PID: %s" % v2ray_srvc_proc.pid)
    
        self.v2ray_pid = v2ray_srvc_proc.pid

        
    def start_daemon(self):
        
        print("Starting v2ray service...")
        
        multiprocessing.get_context('fork')
        warp_fork = Process(target=self.fork_v2ray)
        warp_fork.run()
        sleep(1.5)
        return True
    
    def kill_daemon(self):
        v2ray_daemon_cmd = 'pkexec env PATH=%s %s' %(ConfParams.PATH, self.v2ray_script)
        proc2 = Popen(v2ray_daemon_cmd, shell=True)
        proc2.wait(timeout=30)
        proc_out,proc_err = proc2.communicate()
        return proc2.returncode
    
    
    
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