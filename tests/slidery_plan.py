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
from functools import partial


import re

KV = '''
MDScreen
<IconListItem>

    IconLeftWidget:
        icon: root.icon

<SubscribeContent>
    orientation: "vertical"
    spacing: "1dp"
    size_hint_y: None
    height: "260dp"
    price_text: ""
    naddress: " "
    
    MDBoxLayout:
        orientation: "vertical"
        MDLabel:
            id: moniker_text
            text: root.naddress
    
    MDBoxLayout:
        orientation: "horizontal"
        MDSlider:
            
            id: slider1
            min: 1
            max: 314
            value: 34
            on_value: root.parse_coin_deposit(root.ids.drop_item.current_item)
            
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
            text: ""
            size_hint_y: .65
            width: "50dp"
            height: "30dp"
            readonly: True
        
        MDTextField:
            id: price
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
            text: "udvpn"
            on_release: root.menu.open()
    
'''
class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class SubscribeContent(BoxLayout):
    
    
    price_text = StringProperty()
    moniker = StringProperty()
    naddress = StringProperty()
    
    menu = None
    def __init__ (self, price, moniker, naddress):
        super(SubscribeContent, self).__init__()
        
        self.price_text = price
        self.moniker = moniker
        self.naddress = naddress
        self.parse_coin_deposit("udvpn")
        
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "circle-multiple",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in CoinsList.ibc_mu_coins
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        self.ids.drop_item.current_item = CoinsList.ibc_mu_coins[0]
        self.parse_coin_deposit(self.ids.drop_item.current_item)


    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.ids.deposit.text = self.parse_coin_deposit(text_item)
        self.menu.dismiss()
        
    def parse_coin_deposit(self, mu_coin):
        mu_coin_amt = re.findall(r'[0-9]+' + mu_coin, self.price_text)[0]
        print(mu_coin_amt)
        if mu_coin_amt:
            self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(mu_coin_amt.split(mu_coin)[0])/1000000)),3)) + self.ids.drop_item.current_item.replace('u','') 
            return self.ids.deposit.text
        else:
            print("Start with udvpn: %s" % self.ids.drop_item.current_item)
            self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(self.ids.price.text.split("udvpn")[0])/1000000)),3)) + self.ids.drop_item.current_item.replace('u','')
            return self.ids.deposit.text
        

    def return_deposit_text(self):
        return (self.ids.deposit.text, self.naddress)

class Test(MDApp):
    dialog = None
    def build(self):
        Builder.load_string(KV)
        
        price = "10000uscrt,1000uatom,50000udec,10000uosmo,10000udvpn"
        moniker = "Adriel's Forest"
        naddress = "sentnode298379hasdfjhaf98y3khasdf98y32jhior"
        subscribe_dialog = SubscribeContent(price, moniker , naddress )
        if not self.dialog:
            self.dialog = MDDialog(
                    title="Address:",
                    type="custom",
                    content_cls=subscribe_dialog,
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.closeDialog
                        ),
                        MDFlatButton(
                            text="Subscribe",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=partial(self.subscribe, subscribe_dialog)
                        ),
                    ],
                )
            self.dialog.open()
        
    def subscribe(self, subscribe_dialog, *kwargs):
        sub_node = subscribe_dialog.return_deposit_text()
        deposit = self.reparse_coin_deposit(sub_node[0])
        print("DEPOSIT IS: %s, for: %s " % ( deposit, sub_node[1] ))
        self.dialog.dismiss()
        self.dialog = None
        self.dialog = MDDialog(title="Subscribing...\n\n%s\n %s" %( deposit, sub_node[1]))
        self.dialog.open()
        
        # Run Subscription method
        self.subscribe
    
    def reparse_coin_deposit(self, deposit):
        
        for k,v in CoinsList.ibc_coins.items():
            try: 
                coin = re.findall(k,deposit)[0]
                deposit = deposit.replace(coin, v)
                mu_deposit_amt = int(float(re.findall(r'[0-9]+\.[0-9]+', deposit)[0])*CoinsList.SATOSHI)
                tru_mu_deposit = str(mu_deposit_amt) + v
                return tru_mu_deposit
            except:
                pass
        
    def closeDialog(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        

Test().run()