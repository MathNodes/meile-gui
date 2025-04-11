from ui.interfaces import WindowManager
from ui.screens import MainWindow,  PreLoadWindow, WalletRestore
from typedef.win import WindowNames
from conf.meile_config import MeileGuiConfig
from helpers.res import Resolution

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivy.config import Config

class MyMainApp(MDApp):
    title = "Meile dVPN"
    manager = None
    
    def __init__(self,**kwargs):
        super(MyMainApp,self).__init__(**kwargs)
        from kivy.core.window import Window
        
        global MeileConfig
        self.icon = MeileConfig.resource_path("imgs/icon.png")
        
        global dim
        if Window.size[0] != dim[0] and Window.size[1] != dim[1]:
            Window.size = (dim[0], dim[1])

        if Window.left != dim[2] and Window.top != dim[3]:
            Window.left = dim[2]
            Window.top  = dim[3]
          
    def build(self):
        global MeileConfig
        kv = Builder.load_file(MeileConfig.resource_path("kv/meile.kv"))
        
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
    
# Get Primary Monitor Resolution
# Scaled down and not using tkinter library
            
global MeileConfig
MeileConfig = MeileGuiConfig()

global dim
dim = Resolution().set_dimensions()

Config.set('kivy','window_icon',MeileConfig.resource_path("imgs/icon.png"))
Config.set('kivy', 'exit_on_escape', 0)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'width', dim[0])
Config.set('graphics', 'height', dim[1])
Config.set('graphics', 'left', dim[2])
Config.set('graphics', 'top', dim[3])

#Config.write()

app = MyMainApp()