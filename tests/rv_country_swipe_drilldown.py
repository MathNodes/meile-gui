from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard, MDCardSwipe
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen, SlideTransition


Builder.load_string('''
#:kivy 1.10.0
#:import get_color_from_hex kivy.utils.get_color_from_hex



    
<MainScreen>:
    name: "main"
    MDLabel:
        text: "BLARG"

    CountryRV:
        id: rv
        
<NodeScreen>
    name: "nodes"
    MDBoxLayout:
        orientation: "vertical"
        NodeRV:
            id: rv
    ActionBar:
        ActionView:
            ActionPrevious:
                title: 'Go Back'
                with_previous: True
                on_release: root.set_previous_screen() 
    
    
<CountryRV>:
    viewclass: 'RecycleViewRow'
    RecycleGridLayout:
        
        cols:1
        default_size: dp(200), dp(150)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'lr-tb'
<NodeRV>:
    viewclass: 'NodeViewRow'
    RecycleGridLayout:
        
        cols:1
        default_size: dp(200), dp(150)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'lr-tb'
        
<RecycleViewRow>:
    size_hint_y: None
    height: self.height
    type_swipe: "hand"


    MDCardSwipeLayerBox:
        padding: "8dp"

        MDIconButton:
            icon: "server-security"
            pos_hint: {"center_y": .5}
            on_release: root.show_country_nodes(root.ids.country)
            
    MDCardSwipeFrontBox:
        md_bg_color: get_color_from_hex("#0d021b")
        MDGridLayout:
            cols: 1
            padding: 20,0,0,0
            MDFloatLayout:
                
                MDLabel:
                    text: "Austria"
                    id: country
                    theme_text_color: "Custom"
                    font_style: "H6"
                    font_size: "24sp"
                    text_color: get_color_from_hex("#fcb711")
                    pos_hint: {"x" : 0, "top" : 1.3}
                    size_hint_x: None
                    width: "200dp"
                MDLabel:
                    text: "10 Nodes"
                    id: country
                    theme_text_color: "Custom"
                    font_style: "H6"
                    font_size: "18sp"
                    text_color: get_color_from_hex("#ffffff")
                    pos_hint: {"x" : 0, "top" : 1.0}
                    size_hint_x: None
                    width: "200dp"
                Image:
                    source: "../src/imgs/at.png"
                    # {"x", "y", "top", "bottom", "left", "right" }
                    pos_hint: {"x" : .3, "top" : 1 }
                    


<NodeViewRow>:
    size_hint_y: None
    pos_hint: {"center_x": .5, "center_y": .5}
    orientation: "vertical"
    padding: 10
    border_radius: 20
    elevation:0
    md_bg_color: get_color_from_hex("#0d021b")
    MDGridLayout:
        cols: 1
        MDFloatLayout:
            
            MDLabel:
                text: "Schrodinger's Cat"
                theme_text_color: "Custom"
                font_style: "H6"
                font_size: "24sp"
                text_color: get_color_from_hex("#fcb711")
                pos_hint: {"x" : 0, "top" : 1.3}
                size_hint_x: None
                width: "200dp"
            Image:
                source: "../src/imgs/at.png"
                # {"x", "y", "top", "bottom", "left", "right" }
                pos_hint: {"x" : .3, "top" : 1 }
                
            MDLabel:
                text: "50.42 MB/s, 75.2 MB/s "
                theme_text_color: "Custom"
                font_style: "Subtitle2"
                font_size: "12sp"
                text_color: 1,1,1,1
                pos_hint: {"x" : .42 , "top": .9 }
            MDLabel:    
                text: "Austria"
                theme_text_color: "Custom"
                font_style: "H6"
                font_size: "22sp"
                text_color: (1,1,1,1)
                pos_hint: {"right" : 1.75 , "top": 0 }  
            MDLabel:
                text: "sentnode19887294712394719phfndkashfk"
                theme_text_color: "Custom"
                font_style: "Subtitle2"
                font_size: "10sp"
                text_color: (0/255.0,141/255.0,155/255.0,255/255.0)
                pos_hint: {"x" : 0, "top" : .85}
                               
    MDGridLayout:
        cols: 3
        padding: 0,0,0,10
        MDLabel:
            text: "1000000udvpn/GB,10000utom,15000uosmo,10000000udec,10000uscrt"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "13sp"
            text_color: get_color_from_hex("#fcb711")
        Image:
            source: "../src/imgs/fast.png"
        MDBoxLayout:
            padding: 80,30,0,0

                
    MDRaisedButton:
        text: "Get Details"
        md_bg_color: get_color_from_hex("#fcb711")
        text_color: 0,0,0,1
        
    MDSeparator:
        color: 1,1,1,1
''')
    

class NodeViewRow(MDCard):
    text = StringProperty()

class WindowManager(ScreenManager):
    pass
    
    
class RecycleViewRow(MDCardSwipe):
    text = StringProperty()
    
    
    def show_country_nodes(self, country):
        print(country)
        self.switch_window()
    def switch_window(self):
        Test.root.add_widget(NodeScreen(name="nodes"))

        Test.root.transition = SlideTransition(direction = "up")
        Test.root.current = "nodes"
    
class CountryRV(RecycleView):
    pass
class NodeRV(RecycleView):
    pass
class NodeScreen(Screen):
    def __init__(self, **kwargs):
        super(NodeScreen, self).__init__()
        print("Node Blargy")
        self.build()
        
    def build(self):
        print("Node SHIMARGLY")
        self.ids.rv.data  = [{'text': "Button " + str(x), 'id': str(x)} for x in range(10)]
        print("DATA: %s" % self.ids.rv.data)
        
    def set_previous_screen(self):
        
        Test.root.remove_widget(self)
        Test.root.transistion = SlideTransition(direction="down")
        Test.root.current = "main"

class MainScreen(Screen):    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__()
        print("Blargy")
        self.build()
        
    def build(self):
        print("SHIMARGLY")
        self.ids.rv.data  = [{'text': "Button " + str(x), 'id': str(x)} for x in range(10)]
        print("DATA: %s" % self.ids.rv.data)

    
class TestApp(MDApp):
    title = "RecycleView Direct Test"
    
    def build(self):
        manager = WindowManager()
        manager.add_widget(MainScreen(name="main"))
        return manager
    
if __name__ == "__main__":
    Test = TestApp()
    
    Test.run()
    