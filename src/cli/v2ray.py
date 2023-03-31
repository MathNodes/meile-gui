from subprocess import Popen
import multiprocessing
from multiprocessing import Process
from time import sleep
import psutil
import netifaces
import json
from os import path

from typedef.konstants import ConfParams 
from conf.meile_config import MeileGuiConfig

class V2RayHandler():
    v2ray_script = None
    v2ray_pid    = None
    tunproc      = "tun2socks.exe"
    v2rayproc    = "v2ray.exe"
    
    def __init__(self, script, **kwargs):
        self.v2ray_script = script
        print(self.v2ray_script)
    
    def fork_v2ray(self):
        v2ray_daemon_cmd = 'gsudo %s' %(self.v2ray_script)
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True,close_fds=True)
        
        print("PID: %s" % v2ray_srvc_proc.pid)
    
        self.v2ray_pid = v2ray_srvc_proc.pid

        
    def start_daemon(self):
        
        print("Starting v2ray service...")
        MeileConfig = MeileGuiConfig()
        routes_bat = path.join(MeileConfig.BASEBINDIR, 'routes.bat')
        
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        
        SERVER = self.read_v2ray_config(MeileConfig)
        wifidx = self.get_wifi_idx()
        
        batfile = open(routes_bat, 'w')
        
        #batfile.write('START /B %s/%s run -c %s/v2ray_config.json' % (MeileConfig.BASEBINDIR, self.v2rayproc, MeileConfig.SENTINELDIR))
        batfile.write('START /B %s/%s -device wintun -proxy socks5://127.0.0.1:1080\n' % (MeileConfig.BASEBINDIR,self.tunproc))
        batfile.write('netsh interface ip set address name="wintun" source=static addr=192.168.123.1 mask=255.255.255.0 gateway=none\n')
        batfile.write('route add 0.0.0.0 mask 0.0.0.0 192.168.123.1 if %s metric 5\n' % wifidx)
        batfile.write('route add %s mask 255.255.255.255 %s' % (SERVER, default_gateway))
        batfile.flush()
        batfile.close()
        
        self.v2ray_script = routes_bat
        
        multiprocessing.get_context('spawn')
        fork = Process(target=self.fork_v2ray)
        fork.run()
        sleep(1.5)
        return True
    
    def kill_daemon(self):
        MeileConfig = MeileGuiConfig()
        for proc in psutil.process_iter():
            print(proc.name())
            if proc.name() == tunproc or proc.name() == v2rayproc:
                proc.kill()
        
        SERVER = self.read_v2ray_config(MeileConfig)
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        
        routes_bat = path.join(MeileConfig.BASEBINDIR, 'delroutes.bat')
        
        batfile = open(routes_bat, 'w')
        
        batfile.write('TASKKILL /F /IM tun2socks.exe\n')
        batfile.write('TASKKILL /F /IM v2ray.exe\n')
        batfile.write('netsh interface set interface name="wintun" disable\n')
        batfile.write('route del 0.0.0.0 mask 0.0.0.0 192.168.123.1 if 0 metric 5\n')
        batfile.write('route del %s mask 255.255.255.255 %s\n' % (SERVER, default_gateway))
        batfile.flush()
        batfile.close()
        
        self.v2ray_script = routes_bat
        
        v2ray_daemon_cmd = 'gsudo %s' %(self.v2ray_script)
        proc2 = Popen(v2ray_daemon_cmd, shell=True)
        proc2.wait(timeout=30)
        proc_out,proc_err = proc2.communicate()
        return proc2.returncode
        
    def read_v2ray_config(self, MeileConfig):
        
        with open(path.join(MeileConfig.SENTINELDIR, 'v2ray_config.json'), 'r') as V2RAYFILE:
            v2ray = V2RAYFILE.read()
        
        JSON = json.loads(v2ray)
        
        return JSON['outbounds'][0]['settings']['vnext'][0]['address']
    
    def get_wifi_idx(self):
        from scapy.arch.windows import *
        for iface in get_windows_if_list():
            if "Wi-Fi" in iface['name']:
                return iface['index']