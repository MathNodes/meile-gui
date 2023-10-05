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
        
        # This is a little tricky on windows, we may be able to use instead:
        # One person complained not working on Ethernet, this may solve it:
        default_gateway = gateways[netifaces.AF_INET][0][0]
        
        #default_gateway = gateways['default'][netifaces.AF_INET][0]
        
        SERVER = self.read_v2ray_config(MeileConfig)
        #wifidx = self.get_primary_if_idx(netifaces.gateways()['default'][netifaces.AF_INET][1])
        
        batfile = open(routes_bat, 'w')
        
        #batfile.write('START /B %s/%s run -c %s/v2ray_config.json' % (MeileConfig.BASEBINDIR, self.v2rayproc, MeileConfig.SENTINELDIR))
        batfile.write('START /B %s/%s -device tun://tun00 -proxy socks5://127.0.0.1:1080\n' % (MeileConfig.BASEBINDIR,self.tunproc))
        batfile.write('timeout /t 5\n')
        batfile.write('netsh interface ip set address "tun00" static address=10.10.10.2 mask=255.255.255.0 gateway=10.10.10.1\n')
        batfile.write('netsh interface ip set dns name="tun00" static 1.1.1.1\n')
        batfile.write('route add %s %s metric 5\n' % (SERVER, default_gateway))
        batfile.write('route add 0.0.0.0 mask 0.0.0.0 10.10.10.1')
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
        
        SERVER = self.read_v2ray_config(MeileConfig)
        gateways = netifaces.gateways()
        #print(gateways['default'][netifaces.AF_INET])
        # This is a little tricky on windows, we may be able to use instead:
        # One person complained not working on Ethernet, this may solve it:
        default_gateway = gateways[netifaces.AF_INET][0][0]
        
        #default_gateway = gateways['default'][netifaces.AF_INET][0]
        #wifidx = self.get_primary_if_idx(netifaces.gateways()['default'][netifaces.AF_INET][1])
        
        routes_bat = path.join(MeileConfig.BASEBINDIR, 'delroutes.bat')
        
        batfile = open(routes_bat, 'w')
        
        batfile.write('route delete %s %s metric 5\n' % (SERVER, default_gateway))
        batfile.write('route delete 0.0.0.0 mask 0.0.0.0 10.10.10.1\n')
        batfile.write('netsh interface set interface name="tun00" disable\n')
        batfile.write('timeout /t 3\n')
        batfile.write('TASKKILL /F /IM tun2socks.exe\n')
        batfile.write('TASKKILL /F /IM v2ray.exe\n')
        batfile.flush()
        batfile.close()
        
        self.v2ray_script = routes_bat
        
        v2ray_daemon_cmd = 'gsudo.exe %s' %(self.v2ray_script)
        proc2 = Popen(v2ray_daemon_cmd, shell=True)
        proc2.wait(timeout=30)
        proc_out,proc_err = proc2.communicate()
        return proc2.returncode
        
    def read_v2ray_config(self, MeileConfig):
        
        with open(path.join(MeileConfig.SENTINELDIR, 'v2ray_config.json'), 'r') as V2RAYFILE:
            v2ray = V2RAYFILE.read()
        
        JSON = json.loads(v2ray)
        
        return JSON['outbounds'][0]['settings']['vnext'][0]['address']
    