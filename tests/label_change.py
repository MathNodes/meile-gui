from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

Builder.load_string('''
<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        Button:
            text: 'Goto strategy'
            on_press: root.manager.current = 'strategy'
        Button:
            text: 'Set text'
            on_press: root.SetText()

<StrategyScreen>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.labelText
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'main'
''')

class MainScreen(Screen):
    def SetText(self):
        text = 'Total=' + str(17*21)
        self.manager.get_screen('strategy').labelText = text

class StrategyScreen(Screen):
    labelText = StringProperty('My label')

class TestApp(App):
    def build(self):
        # Create the screen manager
        screenManager = ScreenManager()
        screenManager.add_widget(MainScreen(name='main'))
        screenManager.add_widget(StrategyScreen(name='strategy'))
        return screenManager

if __name__ == '__main__':
    TestApp().run()