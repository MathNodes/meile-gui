from subprocess import Popen
import multiprocessing
from multiprocessing import Process
from time import sleep
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
        v2ray_daemon_cmd = 'gsudo %s' %(self.v2ray_script)
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True,close_fds=True)
        
        print("PID: %s" % v2ray_srvc_proc.pid)
    
        self.v2ray_pid = v2ray_srvc_proc.pid

        
    def start_daemon(self):
        
        print("Starting v2ray service...")
        
        
        routes_bat = path.join(MeileConfig.BASEBINDIR, 'routes.bat')
        MeileConfig = MeileGuiConfig()
        import netifaces
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        
        batfile = open(routes_bat, 'w')
        
        batfile.write('START /B %s/v2ray run -c %s/v2ray_config.json' % (MeileConfig.BASEBINDIR, MeileConfig.SENTINELDIR))
        batfile.write('START /B %s/tun2socks -device wintun -proxy socks5://127.0.0.1:1080\n' % MeileConfig.BASEBINDIR)
        batfile.write('netsh interface ip set address name="wintun" source=static addr=192.168.123.1 mask=255.255.255.0 gateway=none\n')
        batfile.write('route add 0.0.0.0 mask 0.0.0.0 192.168.123.1 if 0 metric 5\n')
        batfile.write('route add %s mask 255.255.255.255 %s' % (SERVER, default_gateway))
        batfile.flush()
        batfile.close()
        
        self.v2ray_script = routes_bat

        
        
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