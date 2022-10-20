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
Config.set('kivy','window_icon',MeileConfig.resource_path("../imgs/icon.png"))
        
from screeninfo import get_monitors



class MyMainApp(MDApp):
    title = "Meile dVPN"
    icon  = MeileConfig.resource_path("../imgs/icon.png")
    manager = None
    def __init__(self,**kwargs):
        super(MyMainApp,self).__init__(**kwargs)
        from kivy.core.window import Window
        Window.size = (1010, 710)

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
        
        Window.left = int((dim[0] - 1010)/2)
        Window.top = int((dim[1] - 710)/2)
        
        
          
    def build(self):
        
        kv = Builder.load_file(MeileConfig.resource_path("../kv/meile.kv"))
        
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

    
    
    

    # Solution for multiple screens, but results in flickering which looks buggy
    '''
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
        
        
    
    '''     
app = MyMainApp()