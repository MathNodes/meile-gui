from ui.interfaces import WindowManager
from ui.screens import MainWindow,  PreLoadWindow, WalletRestore
from typedef.win import WindowNames
from conf.meile_config import MeileGuiConfig
from helpers.res import Resolution

from kivy.lang import Builder
from kivymd.theming import ThemeManager
from kivy.utils import get_color_from_hex
from kivy.config import Config
from kivymd.app import MDApp




class MyMainApp(MDApp):
    title = "Meile dVPN"
    manager = None
    def __init__(self,**kwargs):
        super(MyMainApp,self).__init__(**kwargs)
        from kivy.core.window import Window
        
        if Window.size[0] != dim[0] and Window.size[1] != dim[1]:
            Window.size = (dim[0], dim[1])

        '''
        # Get Primary Monitor Resolution
        # Scaled down and not using tkinter library
        if len(get_monitors()) == 1:
            print("ONE MONITOR")
            primary_monitor = get_monitors()[0]
        else:
            for m in get_monitors():
                print(str(m))
                if m.is_primary:
                    primary_monitor = m
                    
        dim = []
        dim.append(primary_monitor.width)
        dim.append(primary_monitor.height)
        
        #Window.left = int((dim[0] - 1280)/2)
        #Window.top = int((dim[1] - 800)/2)
        '''
        
          
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

MeileConfig = MeileGuiConfig()

dim = Resolution().set_dimensions()

Config.set('kivy','window_icon',MeileConfig.resource_path("imgs/icon.png"))
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'width', dim[0])
Config.set('graphics', 'height', dim[1])
Config.set('graphics', 'left', dim[2])
Config.set('graphics', 'top', dim[3])
Config.write()

app = MyMainApp()