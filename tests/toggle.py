from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.togglebutton import ToggleButton

KV = '''
BoxLayout:
    CustomToggle:
        id: toggle_button
        text: "click on me"
'''


class CustomToggle(ToggleButton):

    def on_state(self, *args):
        print('State changed!', self.state)

    def on_press(self):
        print("Button pressed!", self.state)


class ExampleApp(MDApp):
    loading_layout = None

    def build(self):
        screen = Builder.load_string(KV)
        screen.ids["toggle_button"].state = "down"
        return screen


ExampleApp().run()