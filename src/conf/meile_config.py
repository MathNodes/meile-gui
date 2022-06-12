from os import path

import configparser
import pkg_resources
import shutil
import os

class MeileGuiConfig():
    BASEDIR = path.join(path.expanduser('~'), '.meile-gui')
    CONFFILE = path.join(BASEDIR, 'config.ini')
    CONFIG = configparser.ConfigParser()

    def read_configuration(self, confpath):
        """Read the configuration file at given path."""
        # copy our default config file
        
        if path.isdir(self.BASEDIR):
            if not path.isfile(confpath):
                defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
                shutil.copyfile(defaultconf, self.CONFFILE)
                
        else:
            os.mkdir(self.BASEDIR)
            defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
            shutil.copyfile(defaultconf, self.CONFFILE)
            
        self.CONFIG.read(confpath)
        return self.CONFIG
