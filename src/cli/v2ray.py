from subprocess import Popen
from src.conf.meile_config import MeileGuiConfig
import multiprocessing
from multiprocessing import Process
from time import sleep
import psutil

class V2RayHandler():
    v2ray_script = None
    v2ray_pid    = None
    
    def __init__(self, **kwargs):
        MeileConfig = MeileGuiConfig()
        self.v2ray_script = MeileConfig.resource_path("../bin/v2ray.sh")
    
    def fork_v2ray(self):
        v2ray_daemon_cmd = "%s" % self.v2ray_script
        v2ray_srvc_proc = Popen(v2ray_daemon_cmd, shell=True,close_fds=True)
        
        print("V2Ray PID: %s" % v2ray_srvc_proc.pid)
    
        self.v2ray_pid = v2ray_srvc_proc.pid

        
    def start_daemon(self):
        
        print("Starting v2ray service...")
        
        multiprocessing.get_context('fork')
        warp_fork = Process(target=self.fork_v2ray)
        warp_fork.run()
        sleep(10)
        return True
    
    def kill_daemon(self):
        p = psutil.Process(self.v2ray_pid)
        p.terminate()
        