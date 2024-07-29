from os import path,environ,mkdir

import configparser
import shutil

import sys


class MeileGuiConfig():
    BASEDIR            = path.join(path.expanduser('~'), '.meile-gui')
    BASEBINDIR         = path.join(BASEDIR, 'bin')
    WIREGUARD_BIN      = path.join(BASEBINDIR, "WireGuard", "wireguard.exe")
    WG_BIN             = path.join(BASEBINDIR, "WireGuard", "wg.exe")
    CONFFILE           = path.join(BASEDIR, 'config.ini')
    IMGDIR             = path.join(BASEDIR, 'img')
    CONFIG             = configparser.ConfigParser()
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
    
    def process_exists(self, process_name):
        call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
        try:
            output = subprocess.check_output(call).decode('windows-1252')
        except:
            print("Decoding error, reverting....")
            output = subprocess.check_output(call).decode(errors='ignore')
        
        last_line = output.strip().split('\r\n')[-1]
        return last_line.lower().startswith(process_name.lower())
    
    def kill_process(self, process_name):
        call = '%s TASKKILL /F /IM %s' % (self.resource_path("bin/gsudo.exe"),process_name)
        subprocess.Popen(call, shell=True)
        
    def update_bin(self, from_path, to_path):
        try:
            if self.process_exists("WireGuard.exe"):
                print("WireGuard is running!")
                self.kill_process("WireGuard.exe")
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
        
        if not self.CONFIG.has_section('network'):
            self.CONFIG.add_section('network')
            self.CONFIG.set('network', 'rpc', 'https://rpc.mathnodes.com:443')
            self.CONFIG.set('network', 'grpc', 'grpc.ungovernable.dev:443')
            self.CONFIG.set('network', 'api', 'https://api.sentinel.mathnodes.com')
            self.CONFIG.set('network', 'mnapi', 'https://aimokoivunen.mathnodes.com')
            self.CONFIG.set('network', 'cache', 'https://metabase.bluefren.xyz/api/public/card/4a891454-51da-462a-a5df-e85ca17c05d5/query/json')
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE)
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
            
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE) 
            
           
        return self.CONFIG
