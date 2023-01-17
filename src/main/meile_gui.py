import main.main as Meile
from threading import Thread
import os, sys
from kivy.resources import resource_add_path, resource_find
from charset_normalizer import md__mypyc


def main():
    print("Running Meile...")
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    #Meile.app.run()
    meilethread = Thread(target=Meile.app.run())
    meilethread.start()
    
if __name__ == "__main__":
    main()