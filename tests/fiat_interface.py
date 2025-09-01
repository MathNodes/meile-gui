from kivymd.uix.menu import MDDropdownMenu
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.list import OneLineIconListItem

 
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivyoav.delayed import delayable
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.metrics import dp




Builder.load_string('''
#: import get_color_from_hex kivy.utils.get_color_from_hex

<FiatInterface>:
    name: "fiatgateway"
    title: "Blargy"
    wallet_address: "secret1uhwwgwc7x5cm5xdmn99xnucxz296lyua688wjj"
    MDBoxLayout:
        orientation: "vertical"
        MDToolbar:
            id: toolbar
            title: "Wallet"
            md_bg_color: get_color_from_hex("#FFB908")
            height: "100dp"
            type: "top"
    
            MDTextField:
                hint_text: "Address"
                mode: "fill"
                size_hint_x: 1.2
                pos_hint: {"center_x" : .5, "center_y": .5}
                text: root.wallet_address
                readonly: True
                opacity: 1
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                normal_color: app.theme_cls.accent_color
            

    ClickableTextFieldRoundCC:
        id: ccnum
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Credit Card Number"
        pos_hint: {"center_x": .5, "center_y": .80}
 
    MDLabel:
        id: credit_card_number_warning
        opacity: 0
        text: "Sixteen digit number"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#fcb711")
        pos_hint: {"x": .47, "center_y": .74}
        font_size: "12dp"
     
    MDLabel:
        opacity: 1
        text: "Month"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#fcb711")
        pos_hint: {"x": .30, "center_y": .7}
        font_size: "12dp"
     
    MDDropDownItem:
        id: month_list
        pos_hint: {'center_x': .33, 'center_y': .67}
        text: '01'
        on_release: root.menu_month.open()
        
    MDLabel:
        opacity: 1
        text: "Year"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#fcb711")
        pos_hint: {"x": .40, "center_y": .7}
        font_size: "12dp"
    
    MDDropDownItem:
        id: year_list
        pos_hint: {'center_x': .43, 'center_y': .67}
        text: '2022'
        on_release: root.menu_year.open()
        
    ClickableTextFieldRoundCVV:
        id: cvvnum
        size_hint_x: None
        width: "100dp"
        height: "300dp"
        hint_text: "CVV"
        pos_hint: {"center_x": .6, "center_y": .69}
        
    MDLabel:
        id: cvv_code_warning
        opacity: 0
        text: "Wrong CVV. 3 or 4 digit code"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("f42121")
        pos_hint: {"x": .47, "center_y": .54}
        font_size: "12dp"
    
        
    MDRaisedButton:
        id: restore_wallet_button
        text: "PURCHASE"
        pos_hint: {"center_x": .5, "center_y": .25}
        on_press: root.pay()
        
<ClickableTextFieldRoundCC>:
    size_hint_y: None
    height: ccnum.height

    MDTextField:
        id: ccnum
        hint_text: root.hint_text
        text: root.text
        password: True
        icon_left: "key-variant"
        mode: "rectangle"

    MDIconButton:
        icon: "eye-off"
        pos_hint: {"center_y": .5}
        pos: ccnum.width - self.width + dp(8), 0
        theme_text_color: "Hint"
        on_release:
            self.icon = "eye" if self.icon == "eye-off" else "eye-off"
            ccnum.password = False if ccnum.password is True else True



<ClickableTextFieldRoundCVV>:
    size_hint_y: None
    height: cvvnum.height

    MDTextField:
        id: cvvnum
        hint_text: root.hint_text
        text: root.text
        password: True
        icon_left: "key-variant"
        mode: "rectangle"

    MDIconButton:
        icon: "eye-off"
        pos_hint: {"center_y": .5}
        pos: cvvnum.width - self.width + dp(8), 0
        theme_text_color: "Hint"
        on_release:
            self.icon = "eye" if self.icon == "eye-off" else "eye-off"
            cvvnum.password = False if cvvnum.password is True else True

<IconListItem>

    IconLeftWidget:
        icon: root.icon

 '''
) 
class IconListItem(OneLineIconListItem):
    icon = StringProperty()
class WindowManager(ScreenManager):
    pass
 
class ClickableTextFieldRoundCC(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    
'''
class ClickableTextFieldRoundName(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

'''
class ClickableTextFieldRoundCVV(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

class FiatInterface(Screen):
    dialog = None
    menu_month = None
    menu_year = None
    month = None
    year = None
    
    def __init__(self, **kwargs):
        super(FiatInterface, self).__init__()
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "git",
                "text": f"{i}" if i > 9 else f"%s" % ("0" + str(i)),
                "height": dp(56),
                "on_release": lambda x=f"{i}" if i > 9 else f"%s" % ("0" + str(i)): self.set_month(x),
            } for i in range(1,13)
        ]
        self.menu_month = MDDropdownMenu(
            caller=self.ids.month_list,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_month.bind()
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "git",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_year(x),
            } for i in range(2022,2035)
        ]
        self.menu_year = MDDropdownMenu(
            caller=self.ids.year_list,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_year.bind()
       
       
    def pay(self):
        print(len(str(self.ids.ccnum.ids.ccnum.text)))
        if len(self.ids.ccnum.ids.ccnum.text) < 16 or len(self.ids.ccnum.ids.ccnum.text) > 16:
            self.ids.credit_card_number_warning.opacity = 1
        if len(self.ids.cvvnum.ids.cvvnum.text) > 4 or len(self.ids.cvvnum.ids.cvvnum.text) < 3:
            self.ids.cvv_code_warning.opacity = 1
            
        
        
        
        
    def set_month(self, text_item):
        self.ids.month_list.set_item(text_item)
        self.menu_month.dismiss()
        
        print("Month: %s "  % text_item[0])
        self.month = text_item
        
    def set_year(self, text_item):
        self.ids.year_list.set_item(text_item)
        self.menu_year.dismiss()
        
        print("Year: %s" % text_item[-2:])
        self.year = text_item[-2:]
    def cancel(self):
        self.dialog.dismiss()
        
    def wallet_restore(self):
        pass
    
class TestApp(MDApp):
    title = "Blargy"
    
    def build(self):
        
        manager = WindowManager()
        manager.add_widget(FiatInterface(name="fiatgateway"))
        
        return manager
    
if __name__ == "__main__":
    app = TestApp()
    app.run()