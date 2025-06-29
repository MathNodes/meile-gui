from kivy.properties import ColorProperty

from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tooltip import MDTooltip
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivymd.uix.list import OneLineIconListItem

 
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivyoav.delayed import delayable
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.theming import ThemeManager
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabs
from kivymd.uix.button.button import MDIconButton

from kivy_garden.mapview import MapSource



Builder.load_string('''
#:import MapView kivy_garden.mapview
#: import get_color_from_hex kivy.utils.get_color_from_hex
<NodeCarousel>:
    name: "node_carousel"
    MDBoxLayout:
        orientation: "vertical"
        MDGridLayout:
            rows: 3
            cols: 2
            orientation: 'lr-tb'
            size_hint_y: .15
            MDLabel:
                text: "Moniker"
                #size_hint_x: .9
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#fcb711")
                font_size: sp(25)
            AnchorLayout:
                anchor_x: "right"
                TooltipMDIconButton:
                    icon: "earth"
                    tooltip_text: "Map"
                    #size_hint_x: .01
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#fcb711")
                    
            HSeparator:
            HSeparator:
            MDLabel:
                text: "sentnodeasjdhfwaiqy3493yasdfh9218ywaskljhf"
                size_hint_x: .95
                font_size: sp(11)
        MDFloatLayout
            size_hint_y: 1
            #row_default_height: 15
            #row_force_default: False
            #size: root.width * 0.8, root.height * 0.8
            #spacing: 1

            MDBoxLayout:
                orientation: "vertical"
                size_hint_x: .6
                size_hint_y: .95
                #padding: [0,35,0,50]
                spacing: 30             
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        
                        
                        MDLabel:
                            text: "[b]Gigabyte Prices[/b]"
                            halign: "center"
                            markup: True
                        
                        MDLabel:
                            text: "[b]Hourly Prices[/b]"
                            halign: "center"
                            markup: True
                        
                        MDLabel:
                            text: "0.25atom,100dec,90osmo,80scrt,11dvpn"
                            halign: "center"
                            font_size: sp(12)
                        
                        MDLabel:
                            text: "0.12atom,50dec,42osmo,80scrt,4dvpn"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        rows: 2
                        MDLabel:
                            text: "[b]Bandwidth Down[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "[b]Bandwidth Up[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "297.0Mb/s"
                            halign: "center"
                            font_size: sp(12)
                        MDLabel:
                            text: "97.0Mb/s"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        rows: 2
                        MDLabel:
                            text: "[b]Connected Peers[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "[b]Max Peers[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "4"
                            halign: "center"
                            font_size: sp(12)
                        MDLabel:
                            text: "250"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        rows: 2
                        MDLabel:
                            text: "[b]Protocol[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "[b]Version[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "WireGuard"
                            halign: "center"
                            font_size: sp(12)
                        MDLabel:
                            text: "0.7.1"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        rows: 2
                        MDLabel:
                            text: "[b]Handshake[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "[b]Health Checkp[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "True"
                            halign: "center"
                            font_size: sp(12)
                        MDLabel:
                            text: "Passed"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        rows: 2
                        MDLabel:
                            text: "[b]ISP Type[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "[b]Formula[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "Residential"
                            halign: "center"
                            font_size: sp(12)
                        MDLabel:
                            text: "97.1/100"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .03
                    MDGridLayout
                        cols: 2
                        rows: 2
                        MDLabel:
                            text: "[b]Votes[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "[b]Score[/b]"
                            halign: "center"
                            markup: True
                        MDLabel:
                            text: "77"
                            halign: "center"
                            font_size: sp(12)
                        MDLabel:
                            text: "9.1/10"
                            halign: "center"
                            font_size: sp(12)
                MDBoxLayout:
                    size_hint_y: .1
            MapView:
                id: mapview
                lat: 48.849943
                lon: 2.279793
                zoom: 8
                size_hint: .4, .6
                pos_hint: {"x": .575, "y": .4}
                
        
                #on_map_relocated: mapview2.sync_to(self)
                #on_map_relocated: mapview3.sync_to(self)
                
                MapMarker:
                    lat: 48.8566  # Latitude of Paris, France
                    lon: 2.3522   # Longitude of Paris, France
        
                
            
            MDLabel:
                text: "[b]Location:[/b] Paris, France"
                pos_hint: {"x" : .7, "y": -.125}
                markup: True
                    
            MDFlatButton:        
                md_bg_color: get_color_from_hex("#121212")
                pos_hint: {'x' : .67, 'y': .275}
                Image:
                    id: subscribe_button
                    size_hint: 3,3
                    source: "SubscribeButton.png"
            
            MDFlatButton:        
                md_bg_color: get_color_from_hex("#121212")
                pos_hint: {'x' : .87, 'y': .275}
                Image:
                    id: subscribe_button
                    size_hint: 3,3
                    source: "GetInfoButton.png"
                    
            
                
            
<TooltipMDRaisedButton>:

<TooltipMDIconButton>:

<Separator@Widget>:
    canvas:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
<HSeparator@Separator>:
    size_hint_y: None
    height: dp(2)

<NodeRV>:
    key_viewclass: "viewclass"
    bar_width: dp(12)
    scroll_type: ["bars", "content"]
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
class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class NodeRV(RecycleView):    
    pass
class TooltipMDRaisedButton(MDRaisedButton, MDTooltip):
    pass
class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass

class Tab(MDBoxLayout, MDTabsBase):
    pass

class IconButton(MDIconButton):
    pass

class NodeCarousel(Screen):

    def __init__(self, **kwargs):
        super(NodeCarousel, self).__init__()
        
        # Adjust latitude by offset -1 to center in size
        self.ids.mapview.center_on(47.849943,2.279793)
    
    
class WindowManager(ScreenManager):
    pass    
    
    
class TestApp(MDApp):
    title = "Blargy"
    
    def build(self):
        theme = ThemeManager()
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Dark" 
        #self.theme_cls.disabled_primary_color = "Amber"
        self.theme_cls.accent_palette = "DeepPurple"
        manager = WindowManager()
        manager.add_widget(NodeCarousel(name="node_carousel"))
        from kivy.core.window import Window
        Window.size = (1031, 708)
        
        return manager
    
if __name__ == "__main__":
    app = TestApp()
    app.run()