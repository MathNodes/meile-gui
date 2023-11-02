from kivy.lang import Builder

from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tooltip import MDTooltip
from kivy.properties import  StringProperty
from kivy.metrics import dp

from kivymd.uix.menu import MDDropdownMenu
from win import CoinsList
from kivymd.uix.list import OneLineIconListItem
from functools import partial

import asyncio
import random
import time
import re

# Warning, the sys.path.append should be use only for test :)
# If you run from main folder python tests/slidery_months.py, leave as is
# If you are in /tests folder and run python slidery_months.py the path should be ../src/
import sys, os
sys.path.append(os.path.join(os.getcwd(), "src/"))

from coin_api.get_price import GetPriceAPI

KV = '''
<TooltipMDIconButton@MDIconButton+MDTooltip>

<Check@MDCheckbox>:
    group: 'group'
    size_hint: None, None
    size: dp(48), dp(48)

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

    white_label: " "
    nnodes: " "

    GridLayout:
        cols: 3
        padding: 0
        spacing: 10
        rows: 1

        AsyncImage:
            size_hint_x: None
            width: 100
            source: root.logo_image

        MDBoxLayout:
            orientation: "vertical"
            MDLabel:
                id: white_label_text
                text: root.white_label
                font_size: 24
            MDLabel:
                id: nnodes_text
                text: root.nnodes + " Nodes"

        MDBoxLayout:
            orientation: "vertical"

            MDBoxLayout:
                orientation: "horizontal"
                Check:
                    on_active: root.on_checkbox_active("wallet", *args)
                MDLabel:
                    text: "Wallet"
                    size_hint: (None, 1.75)
                TooltipMDIconButton:
                    icon: "help-circle"
                    tooltip_text: "Pay with Wallet in DVPN or IBC enabled coins"

            MDBoxLayout:
                orientation: "horizontal"
                Check:
                    on_active: root.on_checkbox_active("btcpay", *args)
                MDLabel:
                    text: "BTCPay"
                    size_hint: (None, 1.75)
                TooltipMDIconButton:
                    icon: "help-circle"
                    tooltip_text: "Pay an invoice in BTC, BTC (lightning), XMR, LTC, DASH, or DOGE"

            MDBoxLayout:
                orientation: "horizontal"
                Check:
                    on_active: root.on_checkbox_active("pirate", *args)
                MDLabel:
                    text: "Pirate Chain"
                    size_hint: (None, 1.75)
                TooltipMDIconButton:
                    icon: "help-circle"
                    tooltip_text: "Pay using Pirate chain. Note: processing for ARRR payments could take up to 72 hours"


    MDBoxLayout:
        orientation: "horizontal"
        MDSlider:
            id: slider1
            min: 1
            max: 12
            value: 2
            on_value: root.parse_coin_deposit(root.ids.drop_item.current_item)

        MDLabel:
            text: str(int(slider1.value)) + " Months"
            size_hint_x: None
            width: 90

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

class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class SubscribeContent(BoxLayout):

    price_text = StringProperty()
    white_label = StringProperty()
    nnodes = StringProperty()
    logo_image = StringProperty()

    menu = None
    def __init__ (self, price, white_label, nnodes, logo_image):
        super(SubscribeContent, self).__init__()

        # Init the class
        self.price_api = GetPriceAPI()
        self.price_cache = {}

        self.price_text = price
        self.parse_coin_deposit("dvpn")

        self.white_label = white_label
        self.nnodes = str(nnodes)
        self.logo_image = logo_image

        self.pay_with = None

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

    def refresh_price(self, mu_coin: str = "dvpn", cache: int = 30):
        # Need check on cache or trought GetPrice api
        # We don't need to call the price api if the cache is younger that 30s

        if mu_coin not in self.price_cache or time.time() - self.price_cache[mu_coin]["time"] > cache:
            response = asyncio.run(self.price_api.get_usd(mu_coin))
            self.price_cache[mu_coin] = {
                "price": float(response['price']),
                "time": time.time()
            }


    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.ids.deposit.text = self.parse_coin_deposit(text_item)
        self.menu.dismiss()

    def parse_coin_deposit(self, mu_coin):
        # Save a copy, so we can edit the value without update the ui
        price_text = self.price_text
        # Parse all the coins without u-unit
        if mu_coin.startswith("u"):
            if mu_coin in price_text:
                price_text = price_text.replace(mu_coin, mu_coin.lstrip('u'))
            mu_coin = mu_coin.lstrip('u')

        self.refresh_price("dvpn", cache=30)

        if mu_coin != "dvpn":
            self.refresh_price(mu_coin, cache=30)

        month = int(self.ids.slider1.value) # Months
        if mu_coin == "dvpn":
            value = int(price_text.rstrip(mu_coin).strip())
        else:
            value = round(int(price_text.rstrip("dvpn").strip()) * self.price_cache["dvpn"]["price"] / self.price_cache[mu_coin]["price"], 4)
        print(mu_coin, month, value, self.price_cache)
        self.ids.deposit.text = str(month * value)
        return self.ids.deposit.text


    def return_deposit_text(self):
        return (self.ids.deposit.text, self.nnodes)

    def on_checkbox_active(self, pay_with: str, checkbox, value):
        if value is True:
            self.pay_with = pay_with

class Test(MDApp):
    dialog = None
    def build(self):
        Builder.load_string(KV)

        item = random.choice([
            { "price": "10500dvpn", "white_label": "Math nodes", "nnodes": 34, "logo_image": "logo.png" },
            { "price": "19500dvpn", "white_label": "Tkd-Alex", "nnodes": 23, "logo_image": "https://avatars.githubusercontent.com/u/14061593?v=4" }
        ])

        subscribe_dialog = SubscribeContent(**item)
        if not self.dialog:
            self.dialog = MDDialog(
                    title="Subscription Plan",
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
                            text="SUBCRIBE",
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

        if subscribe_dialog.pay_with == "wallet":
            self.pay_meile_plan_with_wallet(0)
        elif subscribe_dialog.pay_with == "btcpay":
            self.pay_meile_plan_with_btcpay(0)
        elif subscribe_dialog.pay_with == "pirate":
            self.pay_meile_plan_with_pirate(0)
        else:
            MDDialog(text="[color=#FF0000]Please select a payment option[/color]").open()

        # self.dialog.dismiss()
        # self.dialog = None
        # self.dialog = MDDialog(title="Subscribing...\n\n%s\n %s" %( deposit, sub_node[1]))
        # self.dialog.open()

        # Run Subscription method
        # self.subscribe

    def pay_meile_plan_with_wallet(self, usd):
        print(f"Method: 'pay_meile_plan_with_wallet', usd: {usd}")

    def pay_meile_plan_with_btcpay(self, usd):
        print(f"Method: 'pay_meile_plan_with_btcpay', usd: {usd}")

    def pay_meile_plan_with_pirate(self, usd):
        print(f"Method: 'pay_meile_plan_with_pirate', usd: {usd}")

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