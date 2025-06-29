from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder

from kivy.uix.screenmanager import Screen, SlideTransition

kv = """
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Gradient kivy_gradient.Gradient

WindowManager:

<MainScreen>:
    name: "main"
    canvas:
        Rectangle:
            size: self.size
            pos: self.pos
            texture: Gradient.horizontal(get_color_from_hex("E91E63"), get_color_from_hex("FCE4EC"))
  
    MDLabel:
        text: "BLARGY"
        id: country
        theme_text_color: "Custom"
        font_style: "H6"
        font_size: "18sp"
        text_color: get_color_from_hex("#000000")
"""                 


class WindowManager(ScreenManager):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        print("Blargy")
class Test(MDApp):
    def build(self):
        kv2 = Builder.load_string(kv)
        manager = WindowManager()
        manager.add_widget(MainScreen(name="main"))
        return manager
        
if __name__ == "__main__":
    app = Test()
    app.run()
