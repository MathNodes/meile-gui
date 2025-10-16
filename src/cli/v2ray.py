import subprocess
import time
import os
import tempfile
from dataclasses import dataclass
from conf.meile_config import MeileGuiConfig

'''
class V2RayHandler():
    v2ray_script = None
    v2ray_pid    = None
    
    def __init__(self, script, **kwargs):
        self.v2ray_script = script
        print(self.v2ray_script)
    
    def fork_v2ray(self):
        v2ray_daemon_cmd = "%s" % self.v2ray_script
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True,close_fds=True)
        
        print("PID: %s" % v2ray_srvc_proc.pid)
    
        self.v2ray_pid = v2ray_srvc_proc.pid

        
    def start_daemon(self):
        
        print("Starting v2ray service...")
        
        multiprocessing.get_context('fork')
        warp_fork = Process(target=self.fork_v2ray)
        warp_fork.run()
        sleep(1)
        return True
    
    def kill_daemon(self):
        proc2 = Popen(self.v2ray_script, shell=True)
        proc2.wait(timeout=30)
        proc_out,proc_err = proc2.communicate()
        return proc2.returncode


class V2RayHandler:
    def __init__(self, script, **kwargs):
        self.v2ray_script = script
        self.v2ray_pid = None
        print(self.v2ray_script)

    def fork_v2ray(self):
        v2ray_daemon_cmd = f"{self.v2ray_script}"
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True, close_fds=True)
        self.v2ray_pid = v2ray_srvc_proc.pid
        print(f"PID: {self.v2ray_pid}")
        # Wait for the process to complete
        v2ray_srvc_proc.wait()

    def start_daemon(self):
        print("Starting v2ray service...")
        # Use 'spawn' or 'fork' context appropriately for your OS
        ctx = multiprocessing.get_context('fork')
        warp_fork = ctx.Process(target=self.fork_v2ray)
        warp_fork.start()
        warp_fork.join()  # Wait here for the process to finish
        return True

    def kill_daemon(self):
        proc2 = Popen(self.v2ray_script, shell=True)
        proc2.wait(timeout=30)
        return proc2.returncode
'''


class V2RayHandler:
    v2ray_pid = 0
    def __init__(self, script_path, **kwargs):
        self.script_path = script_path
        self.processes = []
        self.MeileConfig = MeileGuiConfig()
        
    def run_privileged_script(self, commands):
        script_content = "#!/bin/bash\n"
        script_content += "\n".join(commands)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
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
                text=True
            )
            
            stdout, stderr = proc.communicate(timeout=120)
            
            os.unlink(temp_script_path)
            
            if proc.returncode == 0:
                return True
            else:
                print(f"Privileged script failed with return code {proc.returncode}")
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
            process = subprocess.Popen(cmd, shell=True, 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL)
            return process
        else:
            return subprocess.run(cmd, shell=True, timeout=30)

    def start_daemon(self):
        print("Starting v2ray service...")
        
        '''
        xray_cmd = f"{os.environ['HOME']}/.meile-gui/bin/xray run -c {os.environ['HOME']}/.meile-gui/v2ray_config.json > /dev/null 2>&1 &"
        self.run_cmd(xray_cmd, background=True)
        time.sleep(1)
        
        check_xray_cmd = "ps aux | grep xray | grep -v grep"
        result = self.run_cmd(check_xray_cmd)
        print(f"Xray process check: {result}")
        
        try:
            curl_cmd = "curl --preproxy socks5://localhost:1080 -s https://icanhazip.com"
            result = self.run_cmd(curl_cmd)
            print(f"Curl result: {result}")
        except:
            print("Curl failed or timed out - xray might not be ready yet")
        
        nic_cmd = "route get default | grep 'interface' | cut -d ':' -f 2 | tr -d ' '"
        nic = subprocess.check_output(nic_cmd, shell=True, text=True).strip()
        
        privileged_commands = [
            "mkdir -p /tmp/meile-gui",
            f"{os.environ['HOME']}/.meile-gui/bin/tun2socks -device utun123 -proxy socks5://127.0.0.1:1080 -interface {nic} > /tmp/meile-gui/tun2socks.log 2>&1 &",
            "sleep 2",
            "if ps aux | grep tun2socks | grep -v grep > /dev/null; then",
            "   echo 'tun2socks is running' > /tmp/meile-gui/tun2socks-status.log",
            "else",
            "   echo 'tun2socks failed to start' > /tmp/meile-gui/tun2socks-status.log",
            "   cat /tmp/meile-gui/tun2socks.log",
            "   exit 1",
            "fi",
            "ifconfig utun123 198.18.0.1 198.18.0.1 up",
            "sleep 1"
        ]
        '''
        privileged_commands = ["launchctl bootstrap system /Library/LaunchDaemons/app.meile.xray.plist"]
        privileged_commands.append("sleep 3")
        privileged_commands.append("curl --preproxy socks5://localhost:1080 -s https://icanhazip.com")
        privileged_commands.append("sleep 1")
        privileged_commands.append("launchctl bootstrap system /Library/LaunchDaemons/app.meile.tun2socks.plist")
        privileged_commands.append("sleep 2")
        privileged_commands.append("ifconfig utun123 198.18.0.1 198.18.0.1 up")
        
        networks = ["1.0.0.0/8", "2.0.0.0/7", "4.0.0.0/6", "8.0.0.0/5", 
                   "16.0.0.0/4", "32.0.0.0/3", "64.0.0.0/2", "128.0.0.0/1", "198.18.0.0/15"]
        
        for network in networks:
            privileged_commands.append(f"route add -net {network} 198.18.0.1")
        
        if not self.run_privileged_script(privileged_commands):
            print("Failed to execute privileged commands")
            return False
        
        #sentinel_xray_connect_bash = os.path.join(self.MeileConfig.BASEBINDIR, "sentinel-xray-connect.sh")
        #connectBASH = [sentinel_xray_connect_bash]
        #proc2 = subprocess.Popen(connectBASH)
        #proc2.wait(timeout=30)
        #pid2 = proc2.pid
        #proc_out, proc_err = proc2.communicate()
        
        return True
    
    def kill_daemon(self):
        privileged_commands = []
        
        networks = ["1.0.0.0/8", "2.0.0.0/7", "4.0.0.0/6", "8.0.0.0/5", 
                   "16.0.0.0/4", "32.0.0.0/3", "64.0.0.0/2", "128.0.0.0/1", "198.18.0.0/15"]
        
        for network in networks:
            privileged_commands.append(f"route delete -net {network} 198.18.0.1")
        
        privileged_commands.append("ifconfig utun123 198.18.0.1 198.18.0.1 down")
        privileged_commands.append("launchctl bootout system /Library/LaunchDaemons/app.meile.xray.plist")
        privileged_commands.append("launchctl bootout system /Library/LaunchDaemons/app.meile.tun2socks.plist")

        self.run_privileged_script(privileged_commands)
        
        for proc in self.processes:
            proc.terminate()
        
        return True

@dataclass
class V2RayFragmentConfiguration:
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
              "mux": {
                "concurrency": -1,
                "enabled": False
              },
              "protocol": "vmess",
              "settings": {
                "vnext": [
                  {
                    "address": self.vmess_address,
                    "port": self.vmess_port,
                    "users": [
                      {
                        "alterId": 0,
                        "id": self.vmess_uid,
                        "level" : 8,
                       "security": "chacha20-poly1305"
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
