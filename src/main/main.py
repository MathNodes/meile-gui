from src.ui.interfaces import WindowManager
from src.ui.screens import MainWindow,  PreLoadWindow, WalletRestore
from src.typedef.win import WindowNames
from src.conf.meile_config import MeileGuiConfig

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivy.utils import get_color_from_hex
from kivy.config import Config
MeileConfig = MeileGuiConfig()
Config.set('kivy','window_icon',MeileConfig.resource_path("../imgs/icon.png"))
        
#import tkinter as tk

from AppKit import NSScreen
 
import threading
class MyMainApp(MDApp):
    title = "Meile dVPN"
    icon  = MeileConfig.resource_path("../imgs/icon.png")
    manager = None
    def __init__(self,**kwargs):
        super(MyMainApp,self).__init__(**kwargs)
        from kivy.config import Config
        from kivy.core.window import Window
        Window.size = (1010, 710)
        
        # Tkinter error on OS X
        #dim = self.get_curr_screen_geometry()
        
        dim = []
        dim.append(NSScreen.mainScreen().frame().size.width)
        dim.append(NSScreen.mainScreen().frame().size.height)

        Window.left = int((dim[0] - 1010)/2)
        Window.top = int((dim[1] - 710)/2)
        
        
          
    def build(self):

        kv = Builder.load_file(MeileConfig.resource_path("../kivy/meile.kv"))
        
        self.manager = WindowManager()
        theme = ThemeManager()
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Dark" 
        #self.theme_cls.disabled_primary_color = "Amber"
        self.theme_cls.accent_palette = "DeepPurple"
        #self.theme_cls.opposite_disabled_primary_color = "Amber"
        self.manager.add_widget(PreLoadWindow(name=WindowNames.PRELOAD))
        #manager.add_widget(MainWindow(name=WindowNames.MAIN_WINDOW))
        #manager.add_widget(WalletRestore(name=WindowNames.WALLET_RESTORE))
        #MeileConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        return self.manager
    
    



     
app = MyMainApp()
