from subprocess import Popen
from src.conf.meile_config import MeileGuiConfig
import multiprocessing
from multiprocessing import Process
from time import sleep
import psutil

class Tun2socksHandler():
    tun2socks_script = None
    tun2socks_pid    = None
    
    def __init__(self, **kwargs):
        MeileConfig = MeileGuiConfig()
        self.tun2socks_script = MeileConfig.resource_path("../bin/tun2socks.sh")
    
    def fork_tun2socks(self):
        tun2socks_daemon_cmd = "%s" % self.tun2socks_script
        tun2socks_srvc_proc = Popen(tun2socks_daemon_cmd, shell=True,close_fds=True)
        
        print("tun2socks PID: %s" % tun2socks_srvc_proc.pid)
    
        self.tun2socks_pid = tun2socks_srvc_proc.pid

        
    def start_daemon(self):
        
        print("Starting tun2socks service...")
        
        multiprocessing.get_context('fork')
        warp_fork = Process(target=self.fork_tun2socks)
        warp_fork.run()
        sleep(10)
        return True
        
    def kill_daemon(self):
        p = psutil.Process(self.tun2socks_pid)
        p.terminate()