from src.ui.interfaces import WindowManager
from src.ui.screens import MainWindow,  PreLoadWindow, WalletRestore
from src.typedef.win import WindowNames

from kivy.lang import Builder
from kivymd.app import MDApp



class MyMainApp(MDApp):
    title = "Meile dVPN"

    def build(self):
        kv = Builder.load_file("./src/kivy/meile.kv")

        manager = WindowManager()
        manager.add_widget(PreLoadWindow(name=WindowNames.PRELOAD))
        manager.add_widget(MainWindow(name=WindowNames.MAIN_WINDOW))
        manager.add_widget(WalletRestore(name=WindowNames.WALLET_RESTORE))
        return manager

 
app = MyMainApp()