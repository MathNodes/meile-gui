from os import path,environ,mkdir

import configparser
import shutil

import sys


class MeileGuiConfig():
    USER = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
    BASEDIR   = path.join(path.expanduser('~' + USER), '.meile-gui')
    BASEBINDIR = path.join(BASEDIR, 'bin')
    CONFFILE  = path.join(BASEDIR, 'config.ini')
    IMGDIR    = path.join(BASEDIR, 'img')
    CONFIG    = configparser.ConfigParser()
    
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
        
        if not self.CONFIG.has_section('network'):
            self.CONFIG.add_section('network')
            self.CONFIG.set('network', 'rpc', 'https://rpc.mathnodes.com:443')
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE)
        else:
            if not self.CONFIG.has_option('network', 'grpc'):
                self.CONFIG.set('network', 'grpc', 'grpc.mathnodes.com:443')
            if not self.CONFIG.has_option('network', 'api'):
                self.CONFIG.set('network', 'api', 'https://api.sentinel.mathnodes.com:443')
            if not self.CONFIG.has_option('network', 'mnapi'):
                self.CONFIG.set('network', 'mnapi', 'https://aimokoivunen.mathnodes.com')
            if not self.CONFIG.has_option('network', 'cache'):
                self.CONFIG.set('network', 'cache', 'https://metabase.bluefren.xyz/api/public/card/4a891454-51da-462a-a5df-e85ca17c05d5/query/json')
            FILE = open(self.CONFFILE, 'w')    
            self.CONFIG.write(FILE)    
        return self.CONFIG
