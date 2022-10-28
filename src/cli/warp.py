
from subprocess import Popen
from conf.meile_config import MeileGuiConfig
import multiprocessing
from multiprocessing import Process
from time import sleep
class WarpHandler():
    warp_daemon = None
    warp_cli    = None
    
    def __init__(self, **kwargs):
        MeileConfig = MeileGuiConfig()
        self.warp_daemon = MeileConfig.resource_path("../bin/warp-svc")
        self.warp_cli    = MeileConfig.resource_path("../bin/warp-cli")
    
    def fork_warp(self):
        warp_daemon_cmd = "pkexec %s" % self.warp_daemon
        warp_srvc_proc = Popen(warp_daemon_cmd, shell=True,close_fds=True)
        
        
        
    def start_warp_daemon(self):
        
        print("Starting WARP service...")
        
        multiprocessing.get_context('fork')
        warp_fork = Process(target=self.fork_warp)
        warp_fork.run()
        sleep(7)
        return True
        
        
    def register_warp(self):
        warp_cli_register_cmd = "%s --accept-tos register" % self.warp_cli
        proc = Popen(warp_cli_register_cmd, shell=True)
        
        proc.wait(timeout=20)
        
        if proc.returncode == 0:
            print("Successfully Registered WARP")
            return True
        else:
            print("ERROR: Could not register WARP")
            return False
        
    def run_warp(self):
        warp_cli_set_doh = "%s --accept-tos set-mode doh" % self.warp_cli
        warp_cli_connect = "%s --accept-tos connect" % self.warp_cli
        
        doh_proc = Popen(warp_cli_set_doh, shell=True)
        doh_proc.wait(timeout=7)
        
        sleep(3)
        if doh_proc.returncode == 0:
            print("Successfully set DoH mode")
        else:
            print("ERROR: Could not set DoH mode")
            return False
        
        connect_proc = Popen(warp_cli_connect, shell=True)
        connect_proc.wait(timeout=7)
        
        sleep(3)
        if connect_proc.returncode == 0:
            print("Successfully connected to WARP in DoH mode")
            return True
        else:
            print("ERROR: Could not connect to WARP")
            return False

    def warp_disconnect(self):
        warp_cli_disconnect = "%s --accept-tos disconnect" % self.warp_cli
        
        wdis_proc = Popen(warp_cli_disconnect, shell=True)
        wdis_proc.wait(timeout=10)
        
        sleep(3)
        if wdis_proc.returncode == 0:
            print("Successfully disconnected from WARP")
            return True
        else:
            print("ERROR: On disconnect from WARP")
            return False
        
        
        