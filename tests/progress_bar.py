from kivymd.app import MDApp 
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
KV = '''
#: import get_color_from_hex kivy.utils.get_color_from_hex
<home>:
    progression_value:25
    
    BoxLayout:
        orientation:'vertical'
        padding:dp(24),0,dp(24),0
        Widget:
        
        MDProgressBar:
            value: root.progression_value
            color: 0,0,0,0
            size_hint_y:None
            height:dp(10)                                   
            canvas:
    
                Color: 
                    rgba: 0,0,0,.3
                BorderImage:
                    border: (dp(10), dp(10), dp(10), dp(10))
                    pos: self.x, self.center_y - dp(5)
                    size: self.width, dp(10)
                Color:
                    rgba: get_color_from_hex("#fcb711")                        
                BorderImage:
                    border: [int(min(self.width * (self.value / float(self.max)) if self.max else 0, dp(10)))] * 4
                    pos: self.x, self.center_y -dp(5)
                    size: self.width * (self.value / float(self.max)) if self.max else 0, dp(10)
    
        Widget:            
''' 
class home(Screen):
    pass

class Test(MDApp): 
    def build(self): 
        Builder.load_string(KV)
        self.sm = ScreenManager()
        self.sm.add_widget(home(name="home"))

        return self.sm
    
Test().run() 