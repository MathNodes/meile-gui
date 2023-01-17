from os import path,environ,mkdir

import configparser
import shutil

import sys


class MeileGuiConfig():
    BASEDIR    = path.join(path.expanduser('~'), '.meile-gui')
    BASEBINDIR = path.join(BASEDIR, 'bin')
    CONFFILE   = path.join(BASEDIR, 'config.ini')
    IMGDIR     = path.join(BASEDIR, 'img')
    CONFIG     = configparser.ConfigParser()
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
    
    
    def copy_and_overwrite(self, from_path, to_path):
        if path.exists(to_path):
            return
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
        self.copy_and_overwrite(self.resource_path("bin"), self.BASEBINDIR)
        self.CONFIG.read(confpath)
        return self.CONFIG
