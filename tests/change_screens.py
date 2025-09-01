from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivyoav.delayed import delayable


class MainWindow(Screen):
    
    StatusMessages = ["Calculating π...", "Squaring the Circle...", "Solving the Riemann Hypothesis...", "Done"]
    title = "Meile dVPN"
    k = 0
    j = 0
    
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__()
        
        # Schedule the functions to be called every n seconds
        Clock.schedule_interval(self.update_status_text, 1)

    @delayable
    def update_status_text(self, dt):
        yield 1.0
        if self.j == 2:
            self.manager.get_screen('main').label_text = self.StatusMessages[3]
            return
            
        if self.k == 3:
            self.k = 0
            self.j += 1
        else:
            self.manager.get_screen('main').label_text = self.StatusMessages[self.k]
            self.k += 1
    
    
class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


canvas = '''
WindowManager:
    MainWindow:
    SecondWindow:

<MainWindow>:
    name: "main"
    label_text: "Password:"
    
    GridLayout:
        cols:1

        GridLayout:
            cols: 2

            Label:
                text: root.label_text

            TextInput:
                id: passw
                multiline: False

        Button:
            text: "Submit"
            on_release:
                app.root.current = "second" if passw.text == "tim" else "main"
                root.manager.transition.direction = "left"


<SecondWindow>:
    name: "second"

    Button:
        text: "Go Back"
        on_release:
            app.root.current = "main"
            root.manager.transition.direction = "right"
'''



class MyMainApp(App):
    def build(self):
        kv = Builder.load_string(canvas)

        screenManager = ScreenManager()
        screenManager.add_widget(MainWindow(name='main'))
        screenManager.add_widget(SecondWindow(name='second'))
        return screenManager

if __name__ == "__main__":
    MyMainApp().run()