from os import path,environ,mkdir
from subprocess import Popen
import configparser
import shutil

import sys


class MeileGuiConfig():
    USER = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
    BASEDIR   = path.join(path.expanduser('~' + USER), '.meile-gui')
    CONFFILE  = path.join(BASEDIR, 'config.ini')
    IMGDIR    = path.join(BASEDIR, 'img')
    CONFIG    = configparser.ConfigParser()
    '''
    WASMSO    = "libwasmvm.x86_64.so"
    LIBDIR    = "/usr/local/lib"
    '''
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
        
    
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
        '''    
        if not path.isfile(path.join(LIBDIR,self.WASMSO)):
            print("Copying libwasmvm.x86_64.so to system library...")
            wasmso_copy = ['pkexec', 'cp', self.resource_path(path.join('lib', self.WASMSO)), self.LIBDIR]
            ldconfig    = ['pkexec', 'ldconfig']
            
            proc1 = Popen(wasmso_copy)
            proc1.wait(timeout=30)
            print("Running ldconfig...")
            proc2 = Popen(ldconfig)
            proc2.wait(timeout=30)
        ''' 
        
            
        self.CONFIG.read(confpath)
        return self.CONFIG
