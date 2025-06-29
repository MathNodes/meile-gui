from kivy.lang import Builder
from kivymd.theming import ThemeManager
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty



KV = '''
MyLayout:

    # Will always be at the bottom of the screen.
    MDBottomAppBar:

        MDToolbar:
            title: "Title"
            icon: "git"
            type: "bottom"
            left_action_items: [["menu", lambda x: x]]
    ScreenManager:
        id: scr_mngr
        Screen:
            name: 'screen1'
            Toolbar:
                title: "Screen 1"
        Screen:
            name: 'screen2'
            Toolbar:
                title: "Screen 2"
'''

class MyLayout(BoxLayout):

    scr_mngr = ObjectProperty(None)

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen



class Test(MDApp):
    theme_cls = ThemeManager()

    def build(self):
        return Builder.load_string(KV)


Test().run()