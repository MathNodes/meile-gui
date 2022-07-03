from src.ui.interfaces import WindowManager
from src.ui.screens import MainWindow,  PreLoadWindow, WalletRestore
from src.typedef.win import WindowNames
from src.conf.meile_config import MeileGuiConfig

from kivy.lang import Builder
from kivymd.app import MDApp

import tkinter as tk

import asyncio 
import threading
class MyMainApp(MDApp):
    title = "Meile dVPN"
    def __init__(self,**kwargs):
        super(MyMainApp,self).__init__(**kwargs)
        from kivy.config import Config
        from kivy.core.window import Window
        Window.size = (1010, 710)
        
        dim = self.get_curr_screen_geometry()
        
        Window.left = int((dim[0] - 1010)/2)
        Window.top = int((dim[1] - 710)/2)
        
        
          
    def build(self):
        MeileConfig = MeileGuiConfig()
        kv = Builder.load_file(MeileConfig.resource_path("../kivy/meile.kv"))
        
        
        manager = WindowManager()
        manager.add_widget(PreLoadWindow(name=WindowNames.PRELOAD))
        #manager.add_widget(MainWindow(name=WindowNames.MAIN_WINDOW))
        manager.add_widget(WalletRestore(name=WindowNames.WALLET_RESTORE))
        #MeileConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        return manager

    
    
    



    def get_curr_screen_geometry(self):
        """
        Workaround to get the size of the current screen in a multi-screen setup.
    
        Returns:
            geometry (str): The standard Tk geometry string.
                [width]x[height]+[left]+[top]
        """
        root = tk.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        geometry = root.winfo_geometry()
        width = int(geometry.split('x')[0])
        height = int(geometry.split('x')[1].split('+')[0])
        root.destroy()
        
        return (width, height)
        
        
    
     
app = MyMainApp()