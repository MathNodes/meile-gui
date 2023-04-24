from os import path,environ,mkdir

import configparser
import shutil
import subprocess
import sys
from time import sleep


class MeileGuiConfig():
    BASEDIR     = path.join(path.expanduser('~'), '.meile-gui')
    SENTINELDIR = path.join(path.expanduser('~'), '.sentinelcli')
    BASEBINDIR  = path.join(BASEDIR, 'bin')
    CONFFILE    = path.join(BASEDIR, 'config.ini')
    IMGDIR      = path.join(BASEDIR, 'img')
    CONFIG      = configparser.ConfigParser()
    
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
        self.CONFIG.read(confpath)
        return self.CONFIG
