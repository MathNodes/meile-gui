from os import path,environ,mkdir

import configparser
import shutil

import sys


class MeileGuiConfig():
    USER       = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
    BASEDIR    = path.join(path.expanduser('~' + USER), '.meile-gui')
    BASEBINDIR = path.join(BASEDIR, 'bin')
    AWGQUICK   = path.join(BASEBINDIR, 'awg-quick')
    CONFFILE   = path.join(BASEDIR, 'config.ini')
    IMGDIR     = path.join(BASEDIR, 'img')
    CONFIG     = configparser.ConfigParser()
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
    
    def copy_bin_dir(self):
        self.copy_and_overwrite(self.resource_path("../bin"), self.BASEBINDIR)

    def copy_and_overwrite(self, from_path, to_path):
        if path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)
        
    def update_bin(self, from_path, to_path):
        try:
            procs = self.process_exists()
            if len(procs) > 0: 
                for p in procs:
                    self.kill_process(p.split(' ')[0].rstrip().lstrip())
                sleep(10)
                if path.exists(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)
            else: 
                if path.exists(to_path):
                    shutil.rmtree(to_path)
                shutil.copytree(from_path, to_path)
        except Exception as e:
            print("Process name codec error... Defaulting....")
            print(str(e))
            if path.exists(to_path):
                shutil.rmtree(to_path)
            shutil.copytree(from_path, to_path)
    
    # MacOS        
    def is_plist_exists(self):
        
        wg_plist_content = {
            "Label": self.WG_LAUNCHDAEMON_LABEL,
            "ProgramArguments": [
                str(self.WIREGUARD_BIN_PATH),
                "up",
                str(self.WIREGUARD_CONF_PATH)
            ],
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardOutPath": "/var/log/wireguard-wg99.log",
            "StandardErrorPath": "/var/log/wireguard-wg99.err",
            "EnableTransactions": True,
            "AbandonProcessGroup": True,
        }
        
        awg_plist_content = {
            "Label": self.AWG_LAUNCHDAEMON_LABEL,
            "ProgramArguments": [
                str(self.AWIREGUARD_BIN_PATH),
                "up",
                str(self.WIREGUARD_CONF_PATH)
            ],
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardOutPath": "/var/log/amnezia-wg99.log",
            "StandardErrorPath": "/var/log/amnezia-wg99.err",
            "EnableTransactions": True,
            "AbandonProcessGroup": True,
        }
        
        xray_plist_content = {
            "Label": self.XRAY_LAUNCHDAEMON_LABEL,
            "ProgramArguments": [
                str(self.XRAY_BIN_PATH),
                "run",
                "-c",
                str(self.XRAY_CONF_PATH)
            ],
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardOutPath": "/var/log/xray.log",
            "StandardErrorPath": "/var/log/xray.err",
            "EnableTransactions": True,
            "AbandonProcessGroup": True,
        }
        
        nic_cmd = "route get default | grep 'interface' | cut -d ':' -f 2 | tr -d ' '"
        nic = subprocess.check_output(nic_cmd, shell=True, text=True).strip()
        
        tun2socks_plist_content = {
            "Label": self.TUN2SOCKS_LAUNCHDAEMON_LABEL,
            "ProgramArguments": [
                str(self.TUN2SOCKS_BIN_PATH),
                "-device",
                "utun123",
                "-proxy",
                "socks5://127.0.0.1:1080",
                "-interface",
                f"{nic}"
            ],
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardOutPath": "/var/log/tun2socks.log",
            "StandardErrorPath": "/var/log/tun2socks.err",
            "EnableTransactions": True,
            "AbandonProcessGroup": True,
        }
        
        if path.isfile(self.WG_LAUNCHDAEMON_PATH) and path.isfile(self.AWG_LAUNCHDAEMON_PATH) and path.isfile(self.XRAY_LAUNCHDAEMON_PATH) and path.isfile(self.TUN2SOCKS_LAUNCHDAEMON_PATH):
            print("EXISTS")
            return True
        else:
            print("WRITING network plists....")
            with open(self.WG_LAUNCHDAEMON_PATH, "wb") as f:
                plistlib.dump(wg_plist_content, f)
            with open(self.AWG_LAUNCHDAEMON_PATH, "wb") as f:
                plistlib.dump(awg_plist_content, f)
            with open(self.XRAY_LAUNCHDAEMON_PATH, "wb") as f:
                plistlib.dump(xray_plist_content, f)
            with open(self.TUN2SOCKS_LAUNCHDAEMON_PATH, "wb") as f:
                plistlib.dump(tun2socks_plist_content, f)
            return False
            
            
            
    def rewrite_bin(self):
        self.update_bin(self.resource_path("bin"), self.BASEBINDIR)
        
    def read_configuration(self, confpath):
        """Read the configuration file at given path."""
        # copy our default config file
        
        if path.isdir(self.BASEDIR):
            if not path.isfile(confpath):
                defaultconf = self.resource_path(path.join('config', 'config.ini'))
                shutil.copyfile(defaultconf, self.CONFFILE)
                
        else:
            mkdir(self.BASEDIR)
            defaultconf = self.resource_path(path.join('config', 'config.ini'))
            shutil.copyfile(defaultconf, self.CONFFILE)
            
        if not path.isdir(self.IMGDIR):
            mkdir(self.IMGDIR)
        
        dnscrypt_confile = path.join(self.BASEDIR, 'dnscrypt-proxy.toml')
        
        if not path.isfile(dnscrypt_confile):
            dnscryptconf = self.resource_path(path.join('config', 'dnscrypt-proxy.toml'))
            shutil.copyfile(dnscryptconf, dnscrypt_confile)
        
        
        self.CONFIG.read(confpath)
        
        if not self.CONFIG.has_section('subscription'):
            self.CONFIG.add_section('subscription')
            self.CONFIG.set('subscription', 'gb', '5')
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE)
            FILE.close()
        
        if not self.CONFIG.has_section('network'):
            self.CONFIG.add_section('network')
            self.CONFIG.set('network', 'rpc', 'https://rpc.mathnodes.com:443')
            self.CONFIG.set('network', 'grpc', 'grpc.ungovernable.dev:443')
            self.CONFIG.set('network', 'api', 'https://api.sentinel.mathnodes.com')
            self.CONFIG.set('network', 'mnapi', 'https://aimokoivunen.mathnodes.com')
            self.CONFIG.set('network', 'cache', 'https://metabase.bluefren.xyz/api/public/card/4a891454-51da-462a-a5df-e85ca17c05d5/query/json')
            self.CONFIG.set('network', 'fragment', '1')
            self.CONFIG.set('network', 'dns', '1.1.1.1')
            self.CONFIG.set('network', 'ringsessions', '0')
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE)
            FILE.close()
        else:
            if not self.CONFIG.has_option('network', 'grpc'):
                self.CONFIG.set('network', 'grpc', 'grpc.ungovernable.dev:443')
            if not self.CONFIG.has_option('network', 'api'):
                self.CONFIG.set('network', 'api', 'https://api.sentinel.mathnodes.com')
            if not self.CONFIG.has_option('network', 'mnapi'):
                self.CONFIG.set('network', 'mnapi', 'https://aimokoivunen.mathnodes.com')
            if not self.CONFIG.has_option('network', 'cache'):
                self.CONFIG.set('network', 'cache', 'https://metabase.bluefren.xyz/api/public/card/4a891454-51da-462a-a5df-e85ca17c05d5/query/json')
            if not self.CONFIG.has_option('network', 'resolver1'):
                self.CONFIG.set('network', 'resolver1', 'cs-ch')
            if not self.CONFIG.has_option('network', 'resolver2'):
                self.CONFIG.set('network', 'resolver2', 'uncensoreddns-ipv4')
            if not self.CONFIG.has_option('network', 'resolver3'):
                self.CONFIG.set('network', 'resolver3', 'doh-ibksturm')
            if not self.CONFIG.has_option('network', 'fragment'):
                self.CONFIG.set('network', 'fragment', '1')
            if self.CONFIG.has_option('network', 'fragment'):
                self.CONFIG.set('network', 'fragment', '1')
            if not self.CONFIG.has_option('network', 'dns'):
                self.CONFIG.set('network', 'dns', '1.1.1.1')
            if not self.CONFIG.has_option('network', 'ringsessions'):
                self.CONFIG.set('network', 'ringsessions', '1')
            if self.CONFIG.has_option('network', 'ringsessions'):
                self.CONFIG.set('network', 'ringsessions', '1')
            
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE)
            FILE.close() 
            
           
        return self.CONFIG
