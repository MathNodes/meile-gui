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
            size: self.width, self.height 
                         
<-FullImage2>:
    canvas:
        Rectangle:
            texture: self.texture
            size: self.width - 170, self.height -25
            pos: self.x + 80 , self.y           

<RecycleViewSubRow>:
    size_hint_y: None
    size: "180dp", "180dp"
    pos_hint: {"center_x": .5, "center_y": .5}
    orientation: "vertical"
    padding: 10,10
    border_radius: 20
    radius: [10]
    shadow_pos: 0,0
    elevation: 42
    md_bg_color: get_color_from_hex("#0d021b")
    moniker_text: "Tate-Shafarevich Group"
    sub_id_text: "99999"
    country_text: "Ukraine"
    price_text: "585685452dvpn"
    address_text: "sent1qn3ttsppgdur7akarsx2463dj5pucmtxr3sc4a"
    city_text: " "
    allocated_text: "31GB"
    consumed_text: "3.28GB"
    source_image: " "
    speed_image: " "
    speed_text: " "
    MDFloatLayout
        MDLabel:
            text: root.moniker_text
            theme_text_color: "Custom"
            font_style: "H6"
            font_size: "24sp"
            text_color: get_color_from_hex("#fcb711")
            width: "300dp"
            pos_hint: {"x" : 0, "top" : 1.45}
            size_hint_x: None
        Image:
            source: "../src/imgs/at.png"
            pos_hint: {"x" : .3, "top" : 1.25}
            
        MDLabel:    
            text: root.country_text
            theme_text_color: "Custom"
            font_style: "H6"
            font_size: "22sp"
            text_color: get_color_from_hex("#b2b1b1")  
            pos_hint: {"x" : .75, "top" : 0.7}
        MDLabel:
            text: root.address_text
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "9sp"
            text_color: get_color_from_hex("#3c3c3c")
            pos_hint: {"x" : 0, "top" : 1.29}
        MDLabel:
            text: root.sub_id_text
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            opacity: 0
            text_color: (0/255.0,141/255.0,155/255.0,255/255.0)
        MDLabel:
            text: "Deposit: "
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: get_color_from_hex("#b2b1b1")
            pos_hint: {"x" : 0, "top" : 1.15}
        MDLabel:
            text: root.price_text
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: get_color_from_hex("#fcb711")
            pos_hint: {"x" : .08, "top" : 1.15}
        
        MDLabel:
            text: "Allocated: "
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: 1,1,1,1
            pos_hint: {"x" : 0, "top" : 1.03}
        MDLabel:
            text: root.allocated_text
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: 1,1,1,1
            pos_hint: {"x" : .08, "top" : 1.03}
                
        MDLabel:
            text: "Used: "
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: 1,1,1,1
            pos_hint: {"x" : 0.15, "top" : 1.03}

        MDLabel:
            text: root.consumed_text
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: 1,1,1,1
            pos_hint: {"x" : 0.2, "top" : 1.03 }
            
        MDProgressBar:
            value: root.get_data_used(root.allocated_text, root.consumed_text)
            color: app.theme_cls.accent_color
            back_color: get_color_from_hex("#ffffff")
            pos_hint: {"x" : 0, "top" : .95 }
            size_hint_x: .5
        MDLabel:
            id: consumed_data
            text: " "
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "11sp"
            text_color: 1,1,1,1
            pos_hint: {"x" : .5, "top" : 1.03 }

    

        MDRaisedButton:
            text: "Connect"
            md_bg_color: get_color_from_hex("#fcb711")
            text_color: 0,0,0,1
            on_press: root.connect_to_node(root.sub_id_text,root.address_text, root.moniker_text)
            pos_hint: {"x" : 0, "top" : .35 }

            
            
        MDSeparator:
            color: 1,1,1,1
            pos_hint: {"x" : 0, "top" : .0 }

             
        

    
<MainScreen>:
    viewclass: 'RecycleViewSubRow'
    canvas.before:
        Color:
            rgba: get_color_from_hex("#fccf62")
        Rectangle:
            pos: self.pos
            size: self.size
    RecycleGridLayout:
        md_bg_color: get_color_from_hex("#0d021b")
        cols:1
        default_size: dp(200), dp(150)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'lr-tb' 
        spacing: 15
        padding: 4,4,4,4
                          
''')
    
class FullImage(Image):
    pass
class FullImage2(Image):
    pass
class RecycleViewRow(MDCard):
    text = StringProperty()   
class RecycleViewSubRow(MDCard):
    text = StringProperty()
    dialog = None
    
    
    def get_data_used(self, allocated, consumed):
        try:         
            allocated = float(allocated.replace('GB',''))
            
            if "GB" in consumed:
                consumed  = float(consumed.replace('GB', ''))
            elif "MB" in consumed:
                consumed = float(float(consumed.replace('MB', '')) / 1024)
            elif "KB" in consumed:
                consumed = float(float(consumed.replace('KB', '')) / (1024*1024))
            elif "0.00B" in consumed:
                consumed = 0.0
            else:
                consumed = float(float(re.findall(r'[0-9]+\.[0-9]+', consumed)[0].replace('B', '')) / (1024*1024*1024))
            self.ids.consumed_data.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
            return float(float(consumed/allocated)*100)
        except Exception as e:
            print(str(e))
            return float(50)
  
class MainScreen(RecycleView):    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.data = [{'text': "Button " + str(x), 'id': str(x)} for x in range(10)]
    

    
class TestApp(MDApp):
    title = "RecycleView Direct Test"
    
    def build(self):
        return MainScreen()
    
if __name__ == "__main__":
    TestApp().run()