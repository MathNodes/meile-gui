from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<SwipeToDeleteItem>:
    size_hint_y: None
    height: self.height
    type_swipe: "hand"


    MDCardSwipeLayerBox:
        padding: "8dp"

        MDIconButton:
            icon: "trash-can"
            pos_hint: {"center_y": .5}
            on_release: root.show_country_nodes(root.ids.country)
            
    MDCardSwipeFrontBox:
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
                    id: country
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

MDScreen:

    MDBoxLayout:
        orientation: "vertical"
        spacing: "10dp"

        MDToolbar:
            elevation: 10
            title: "MDCardSwipe"

        ScrollView:

            MDList:
                id: md_list
                padding: 0
'''


class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()


class TestCard(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)

    def build(self):
        return self.screen

    def remove_item(self, instance):
        self.screen.ids.md_list.remove_widget(instance)

    def on_start(self):
        for i in range(20):
            self.screen.ids.md_list.add_widget(
                SwipeToDeleteItem(text=f"One-line item {i}")
            )


TestCard().run()