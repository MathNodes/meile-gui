from kivy.properties import ColorProperty
from kivy.lang import Builder

from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem
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
from kivymd.icon_definitions import md_icons


 
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
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.tab import MDTabs
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.uix.recyclegridlayout import RecycleGridLayout

import sys
from os import path, chdir

'''
Builder.load_string(
<MainWindow>:
    name: "main"
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: get_color_from_hex("#0d021b")
        MDFloatLayout:
            orientation: "horizontal"
            size_hint_y: .18
            MDTextField:
                canvas.after:
                    Color:
                        rgba: root.box_color if not self.focus else (0, 0, 0, 0)
                    Line:
                        width: dp(1)
                        rectangle: (*self.pos, *self.size)
                hint_text: "IP Address"
                id: new_ip
                size_hint_x: .15
                size_hint_y: .45
                font_size: 11
                pos_hint: {"x" : 0.01, "center_y": .65}                
                readonly: True
                opacity: 1
                text: "192.168.4.20"
                mode: "fill"
                text_color_focus: '#fcb711'
                text_color_normal: '#fcb711'
                hint_text: 'IP Address:'
                hint_text_color_normal: '#fcb711'
                hint_text_color_focus: '#fcb711'
                fill_color_normal: get_color_from_hex("#0d021b")
                fill_color_focus: get_color_from_hex("#000000")
            MDTextField:
                canvas.after:
                    Color:
                        rgba: root.box_color if not self.focus else (0, 0, 0, 0)
                    Line:
                        width: dp(1)
                        rectangle: (*self.pos, *self.size)
                hint_text: "Node:"
                #font_name:'arial-unicode-ms.ttf'
                text: "ClaudeBarrosIII"
                id: connected_node
                mode: "fill"
                size_hint_x: .4
                size_hint_y: .45
                font_size: 11
                pos_hint: {"x" : .18, "center_y": .65}                
                readonly: True
                opacity: 1
                text_color_focus: '#fcb711'
                text_color_normal: '#fcb711'
                
                hint_text_color_normal: '#fcb711'
                hint_text_color_focus: '#fcb711'
                fill_color_normal: get_color_from_hex("#0d021b")
                fill_color_focus: get_color_from_hex("#000000")
            MDLabel:
                text: "Bandwidth"
                font_size: 11
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#fcb711")
                normal_color: app.theme_cls.accent_color
                pos_hint: {"x" : .01, "center_y": .2}
            MDProgressBar:
                id: quota
                value: 80
                color: app.theme_cls.accent_color
                #back_color: get_color_from_hex("#ffffff")
                pos_hint: {"x" : .085, "center_y" : .2 }
                size_hint_x: .475
                size_hint_y: .06
            MDLabel:
                text: "80.25%"
                font_size: 11
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#fcb711")
                normal_color: app.theme_cls.accent_color
                pos_hint: {"x" : .57, "center_y": .2}
            MDLabel:
                text: "Sort"
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#fcb711")
                normal_color: app.theme_cls.accent_color
                pos_hint: {"x" : .65, "y": .25}
            MDDropDownItem:
                id: drop_item
                pos_hint: {'x': .625, 'y': .25}
                text: "None"
                on_release: root.menu.open()  
            TooltipMDRaisedButton:
                tooltip_text: "VPNs encrypt your internet traffic, however DNS traffic is still in plaintext. Cloudflare's WARP will encrypt your DNS traffic ensuring no one can see your browsing history."
                md_bg_color: get_color_from_hex("#0d021b")
                pos_hint: {'x' : .72, 'center_y': .5}
                on_press: root.start_warp()
                
                Image:
                    id: warp
                    size_hint: 2,2
                    source: root.set_warp_icon()
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                            
            Image:
                id: protected
                source: root.set_protected_icon(False, "")
                opacity: 0
                size_hint: None, None
                height: "65dp"
                pos_hint: {'x' : .8, 'center_y' : .5}    
            Image:
                source: root.get_logo()
                size_hint: None, None
                height: "75dp"
                pos_hint: {'x' : .9, 'center_y' : .5}
        


        MDTabs:
            id: android_tabs
            on_tab_switch: root.on_tab_switch(*args)
            size_hint_y: None
            height: "48dp"
            tab_indicator_anim: True
            color: 1,1,1,1
            normal_color: get_color_from_hex("#fcb711")
            background_color: get_color_from_hex("#fcb711")
        
        MDBoxLayout:
            id: country_map
            orientation: "horizontal"
            NodeRV:
                md_bg_color: get_color_from_hex("#0d021b")    
                id: rv
         
        MDBottomNavigation:
            size_hint_y: .1
            panel_color: get_color_from_hex("#0d021b")
            text_color_normal: get_color_from_hex("#fcb711")
            text_color_active: get_color_from_hex("#fad783")
            selected_color_background: get_color_from_hex("#200c3a")
            MDBottomNavigationItem:
                name: "wallet"
                text: "Wallet"
                icon: "wallet"
                on_tab_release: root.wallet_dialog()
                on_tab_press: 
            MDBottomNavigationItem:
                name: "Refresh"
                text: "Refresh"
                icon: "shield-refresh"
                on_tab_release: root.refresh_nodes_and_subs()
                
            MDBottomNavigationItem:
                name: "help"
                text: "Help"
                icon: "account-question"
                on_tab_release: root.build_help_screen_interface()
                
<TooltipMDRaisedButton>:

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
        
)
'''
def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
        return path.join(base_path, relative_path)
    
class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class NodeRV(RecycleView):    
    pass
class TooltipMDRaisedButton(MDRaisedButton, MDTooltip):
    pass
class MainWindow(Screen):
    menu = None
    SortOptions = ['None', "Moniker", "Price"]
    box_color = ColorProperty('#fcb711')

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__()
        sort_icons = ["sort-variant", "sort-alphabetical-ascending", "sort-numeric-ascending"]
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": f"{k}",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i,k in zip(self.SortOptions, sort_icons)
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            background_color=get_color_from_hex("#0d021b"),
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
    def build_help_screen_interface(self):
        pass
    def refresh_nodes_and_subs(self):
        pass
    def wallet_dialog(self):
        pass
    def on_tab_switch(self, **args):
        pass
    def get_logo(self):
        pass
    def set_warp_icon(self):
        pass
    def set_protected_icon(self, blah, blah2, **kwargs):
        pass
    def start_warp(self):
        pass
    
    
class WindowManager(ScreenManager):
    pass    
    
    
class TestApp(MDApp):
    title = "Blargy"
    
    def build(self):
        Builder.load_file(resource_path("./kv/main.kv"))
        theme = ThemeManager()
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Dark" 
        #self.theme_cls.disabled_primary_color = "Amber"
        self.theme_cls.accent_palette = "DeepPurple"
        manager = WindowManager()
        manager.add_widget(MainWindow(name="main"))
        
        return manager
    
if __name__ == "__main__":
    app = TestApp()
    app.run()