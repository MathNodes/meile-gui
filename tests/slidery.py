from kivy.lang import Builder

from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import  StringProperty
from kivy.metrics import dp

from kivymd.uix.menu import MDDropdownMenu
from win import CoinsList
from kivymd.uix.list import OneLineIconListItem

KV = '''
MDScreen
<IconListItem>

    IconLeftWidget:
        icon: root.icon

<SubscribeContent>
    orientation: "vertical"
    spacing: "5dp"
    size_hint_y: None
    height: "180dp"
    price_text: "5udvpn"
    MDBoxLayout:
        orientation: "horizontal"
        MDSlider:
            
            id: slider1
            min: 1
            max: 314
            value: 40
            
        MDLabel:
            text: str(int(slider1.value)) + " GB" 
            size_hint_x: None
            width: 75
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_x: .8
        spacing: 20
        
        MDTextField:
            id: deposit
            hint_text: "Deposit"
            mode: "fill"
            text: str(round(int(slider1.value)*int(glargy.text.split('udvpn')[0])/1000000,3)) + root.ids.drop_item.current_item + "/GB"
            size_hint_y: .65
            width: "50dp"
            height: "30dp"
            readonly: True
        
        MDTextField:
            id: glargy
            hint_text: "Price"
            mode: "fill"
            text: root.price_text
            size_hint_y: .65
            width: "50dp"
            height: "30dp"
            readonly: True
            
        MDDropDownItem:
            id: drop_item
            pos_hint: {'center_x': .5, 'center_y': .5}
            text: 'dvpn'
            on_release: root.menu.open()
    
'''
class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class SubscribeContent(BoxLayout):
    
    
    price_text = StringProperty()
    menu = None
    def __init__ (self, price):
        super(SubscribeContent, self).__init__()
        self.price_text = price
        
        
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "circle-multiple",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in CoinsList.Coins
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()

    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.menu.dismiss()

        

class Test(MDApp):
    def build(self):
        Builder.load_string(KV)
        
        subscribe_dialog = SubscribeContent("1000000udvpn")
        
        self.dialog = MDDialog(
                title="Address:",
                type="custom",
                content_cls=subscribe_dialog,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        self.dialog.open()


Test().run()