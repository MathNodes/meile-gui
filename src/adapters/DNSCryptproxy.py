import subprocess
from typedef.konstants import Arch, ConfParams
from os import chdir, path
import platform
import multiprocessing
from multiprocessing import Process
from time import sleep

class HandleDNSCryptProxy():
    lh = "127.0.0.1"
    lhv6 = "::1"
    cf = "1.1.1.1"
    cfv6 = "2606:4700:4700::1111"
    dnscrypt_pid = 0
    dnscryptcmd = None
    
    def __init__(self, default: str = "1.1.1.1", defaultv6: str = "2606:4700:4700::1111"):
        self.default = default
        self.defaultv6 = defaultv6
        pass
    
    def fork_dnscrypt(self):
        dnscryptcmd = f"{self.dnscryptcmd}"
        process = subprocess.Popen(dnscryptcmd, shell=True,close_fds=True)
        print(f"DNSCryptProxy: {process.pid}")
        self.dnscrypt_pid = process.pid
    
    # Be sure to run in thread or concurent.futures
    def dnscrypt(self, state: bool = False):
        chdir(ConfParams.BASEBINDIR)
        dnscrypt_proxy_executable = path.join(ConfParams.BASEBINDIR, 'run_dnscrypt.sh')
        pltfrm = platform.system()
        if state == True:
            if pltfrm == Arch.LINUX:
                dnscrypt_start = dnscrypt_proxy_executable + " up"
                print("Startin DNScrypt-proxy...", end=' ')
                self.dnscryptcmd = f"pkexec sh -c '{dnscrypt_start}'"
                multiprocessing.get_context('spawn')
                fork = Process(target=self.fork_dnscrypt)
                fork.run()
                sleep(1.5)
                
            # TODO: OS/X

                
                
                
        else:
            if pltfrm == Arch.WINDOWS:
                kill_dns_crypt = "change_dns.ps1"
                if self.default != self.cf:
                    dns_bat = self.dns_ps1 % (self.default, self.defaultv6)
                else:
                    dns_bat = self.dns_ps1 % (self.cf, self.cfv6)
                with open(kill_dns_crypt, "w") as DNSFILE:
                    DNSFILE.write(f"{dns_bat}\n")
                    DNSFILE.write(f"{self.dnscrypt_stop}")
                    
                    
                print(dns_bat)
                print(self.dnscrypt_stop)    
                print("Killing dnscrypt-proxy.exe...")
                self.dnscryptcmd = path.join(ConfParams.BASEBINDIR, "change_dns.ps1")
                end_daemon_cmd = [ConfParams.GSUDO, "powershell.exe", self.dnscryptcmd]
                proc2 = subprocess.Popen(end_daemon_cmd, shell=True)
                proc2.wait(timeout=30)
                proc_out,proc_err = proc2.communicate()
                
                #dnscmd = [ConfParams.GSUDO, path.join(ConfParams.BASEBINDIR, "change_dns.bat")]
                #process = subprocess.Popen(dnscmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.dnscrypt_pid = 0
                
            elif pltfrm == Arch.LINUX:
                dnscrypt_start = dnscrypt_proxy_executable + " down"
                print("Stopping DNScrypt-proxy...", end=' ')
                self.dnscryptcmd = f"pkexec sh -c '{dnscrypt_start}'"
                multiprocessing.get_context('spawn')
                fork = Process(target=self.fork_dnscrypt)
                fork.run()
                sleep(1.5)
            # TODO: OS/X 
            
        chdir(ConfParams.KEYRINGDIR)
                    
                    
                