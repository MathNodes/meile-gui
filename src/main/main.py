from ui.interfaces import WindowManager
from ui.screens import MainWindow,  PreLoadWindow, WalletRestore
from typedef.win import WindowNames
from conf.meile_config import MeileGuiConfig

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivy.utils import get_color_from_hex
from kivy.config import Config
MeileConfig = MeileGuiConfig()
from AppKit import NSScreen
 
class MyMainApp(MDApp):
    title = "Meile dVPN"
    icon  = MeileConfig.resource_path("imgs/icon.png")
    manager = None
    def __init__(self,**kwargs):
        super(MyMainApp,self).__init__(**kwargs)
          
    def build(self):

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
            
dim = []
dim.append(NSScreen.mainScreen().frame().size.width)
dim.append(NSScreen.mainScreen().frame().size.height)        
l = int((dim[0] - 1280)/2)
t = int((dim[1] - 800)/2)

Config.set('kivy','window_icon',MeileConfig.resource_path("imgs/icon.png"))
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'left', l)
Config.set('graphics', 'top', t)
Config.write()

app = MyMainApp()
