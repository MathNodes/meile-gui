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