from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
Builder.load_string('''
#:kivy 1.10.0
#:import get_color_from_hex kivy.utils.get_color_from_hex
<-FullImage>:
    canvas:
        Rectangle:
            texture: self.texture
            size: self.width-45 , self.height +30
            pos: self.x - 150, self.y - 30             
<-FullImage2>:
    canvas:
        Rectangle:
            texture: self.texture
            size: self.width - 170, self.height -25
            pos: self.x + 80 , self.y           
                
<RecycleViewRow>:
    size_hint_y: None
    size: "180dp", "180dp"
    pos_hint: {"center_x": .5, "center_y": .5}
    orientation: "vertical"
    padding: 10
    border_radius: 20
    radius: [15]
    elevation:0
    md_bg_color: get_color_from_hex("#0d021b")
    MDGridLayout:
        cols: 3
        rows: 2
        padding: 40,0,0,0
        MDLabel:
            text: "Schrodinger's Cat"
            theme_text_color: "Custom"
            font_style: "H6"
            font_size: "24sp"
            text_color: get_color_from_hex("#fcb711")
            width: "350dp"
            size_hint_x: None
        FullImage:
            source: "../src/imgs/at.png"
            
        MDLabel:    
            text: "Austria"
            theme_text_color: "Custom"
            font_style: "H6"
            font_size: "22sp"
            text_color: (1,1,1,1)  
        MDLabel:
            text: "sentnode19887294712394719phfndkashfk"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            text_color: (0/255.0,141/255.0,155/255.0,255/255.0)
        MDLabel:
            text: " "
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            text_color: (0/255.0,141/255.0,155/255.0,255/255.0)
        MDLabel:
            text: "Vienna"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            text_color: (0/255.0,141/255.0,155/255.0,255/255.0)                                    
    MDGridLayout:
        cols: 3
        padding: 40,0,0,0
        MDLabel:
            text: "1000000udvpn/GB"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            text_color: get_color_from_hex("#fcb711")
        FullImage2:
            source: "../src/imgs/fastavg.png"
        MDBoxLayout:
            padding: 80,30,0,0
            MDLabel:
                text: "50.42 MB/s, 75.2 MB/s ."
                theme_text_color: "Custom"
                font_style: "Subtitle2"
                font_size: "12sp"
                text_color: 1,1,1,1
                



    MDRaisedButton:
        text: "Get Details"
        md_bg_color: get_color_from_hex("#fcb711")
        text_color: 0,0,0,1
        
    MDSeparator:
        color: 1,1,1,1
    
<MainScreen>:
    viewclass: 'RecycleViewRow'
    RecycleGridLayout:
        
        cols:1
        default_size: dp(200), dp(180)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'lr-tb'                    
''')
    
class FullImage(Image):
    pass
class FullImage2(Image):
    pass
class RecycleViewRow(MDCard):
    text = StringProperty()   
    
class MainScreen(RecycleView):    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.data = [{'text': "Button " + str(x), 'id': str(x)} for x in range(100)]
    

    
class TestApp(MDApp):
    title = "RecycleView Direct Test"
    
    def build(self):
        return MainScreen()
    
if __name__ == "__main__":
    TestApp().run()