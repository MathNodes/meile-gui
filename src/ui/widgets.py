from kivy.properties import BooleanProperty, StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivyoav.delayed import delayable

from functools import partial
from subprocess import Popen, TimeoutExpired
from urllib3.exceptions import InsecureRequestWarning
from copy import deepcopy
from datetime import datetime, timedelta
from os import path
from time import sleep 
from threading import Thread, Event
import requests
import re
import psutil
import time
from requests.auth import HTTPBasicAuth
import json
import webbrowser
import sys
from timeit import default_timer as timer

from typedef.konstants import IBCTokens, HTTParams, MeileColors, NodeKeys, ConfParams
from typedef.win import WindowNames
from conf.meile_config import MeileGuiConfig
from cli.wallet import HandleWalletFunctions
from cli.sentinel import NodeTreeData
from cli.btcpay import BTCPayDB
import main.main as Meile
from adapters import HTTPRequests
from ui.interfaces import TXContent, ConnectionDialog, QRDialogContent
from coin_api.get_price import GetPriceAPI
from adapters.ChangeDNS import ChangeDNS
from kivy.uix.recyclegridlayout import RecycleGridLayout
from helpers.helpers import format_byte_size
from fiat.stripe_pay.dist import scrtsxx
from utils.qr import QRCode

class WalletInfoContent(BoxLayout):
    def __init__(self, seed_phrase, name, address, password, **kwargs):
        super(WalletInfoContent, self).__init__(**kwargs)
        self.seed_phrase = seed_phrase
        self.wallet_address = address
        self.wallet_password = password
        self.wallet_name = name
        
    def copy_seed_phrase(self):
        Clipboard.copy(self.seed_phrase)
        self.AnimateCopiedLabel()
        
    def AnimateCopiedLabel(self):
        label = MDLabel(text='Seed Phrase Copied!',
                      theme_text_color="Custom",
                      text_color=get_color_from_hex("#fcb711"),
                      font_size=dp(10))
        self.ids.seed_box.add_widget(label)

        anim = Animation(color=(0, 0, 0, 1), duration=.2) + Animation(color=get_color_from_hex("#fcb711"), duration=.2)
        anim.repeat = True
                
        anim.start(label)
            
        return label
    
class SeedInfoContent(BoxLayout):
    def __init__(self, seed_phrase, **kwargs):
        super(SeedInfoContent, self).__init__(**kwargs)
        self.seed_phrase = seed_phrase
        
    def copy_seed_phrase(self):
        Clipboard.copy(self.seed_phrase)
        self.AnimateCopiedLabel()
        
    def AnimateCopiedLabel(self):
        label = MDLabel(text='Seed Phrase Copied!',
                      theme_text_color="Custom",
                      text_color=get_color_from_hex("#fcb711"),
                      font_size=dp(10))
        self.ids.seed_box.add_widget(label)

        anim = Animation(color=(0, 0, 0, 1), duration=.2) + Animation(color=get_color_from_hex("#fcb711"), duration=.2)
        anim.repeat = True
                
        anim.start(label)
            
        return label
    
class RatingContent(MDBoxLayout):
    naddress = StringProperty()
    moniker  = StringProperty()
    
    def __init__(self, moniker, naddress):
        super(RatingContent, self).__init__()
        self.naddress = naddress
        self.moniker  = moniker
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def SubmitRating(self, rating, node_address):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        MNAPI = CONFIG['network'].get('mnapi', HTTParams.SERVER_URL)
        UUID = Meile.app.root.get_screen(WindowNames.PRELOAD).UUID
        try:
            rating_dict = {'uuid' : "%s" % UUID, 'address' : "%s" % node_address, "rating" : rating}
            Request = HTTPRequests.MakeRequest()
            http = Request.hadapter()
            if MNAPI != HTTParams.SERVER_URL:
                req = http.post(MNAPI + HTTParams.API_RATING_ENDPOINT, json=rating_dict)
            else:
                req = http.post(HTTParams.SERVER_URL + HTTParams.API_RATING_ENDPOINT, json=rating_dict)
            if req.status_code == 200:
                print("Rating Sent")
                return 0
            else:
                print("Error submitting rating")
                return 1
        except Exception as e:
            print(str(e))
            pass
        
    def return_rating_value(self):
        return self.ids.rating_slider.value
    
    
class HyperlinkLabel(ButtonBehavior, MDLabel, HoverBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_size)
        self.color = get_color_from_hex(MeileColors.MEILE)
        self.cursor = 'arrow'

    def on_enter(self, *args):
        Window.set_system_cursor('hand')

    def on_leave(self, *args):
        Window.set_system_cursor('arrow')
        
    def on_release(self):
        webbrowser.open(self.url)  # Open the URL when the label is clicked

    def update_size(self, *args):
        self.size = self.texture_size  # Ensure label size matches text size
    
class SubTypeDialog(BoxLayout):
    
    def __init__(self, rvclass, price, hourly_price, moniker, naddress):
        super(SubTypeDialog, self).__init__()
        self.rvclass      = rvclass
        self.price        = price
        self.hourly_price = hourly_price
        self.moniker      = moniker
        self.naddress     = naddress
        print(self.price)
        print(self.hourly_price)
        print(self.moniker)
        print(self.naddress)
        

        
    def select_sub_type(self,instance, value, type):
        self.rvclass.closeDialog(None)
        
        if type == "gb":
            #print("You have selected bandwidth (GB)")
            #print(f"{self.price}\n{self.moniker}\n{self.naddress}")
            subscribe_dialog = SubscribeContent(self.price, self.moniker, self.naddress, False)
            
        else:
            #print("You have selected hourly (days)")
            #print(f"{self.hourly_price}\n{self.moniker}\n{self.naddress}")
            subscribe_dialog = SubscribeContent(self.hourly_price, self.moniker, self.naddress, True)
            
        
        if not self.rvclass.dialog:
            self.rvclass.dialog = MDDialog(
                title="Node:",
                type="custom",
                content_cls=subscribe_dialog,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=Meile.app.theme_cls.primary_color,
                        on_release=self.rvclass.closeDialog
                    ),
                    MDRaisedButton(
                        text="SUBSCRIBE",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release=partial(self.rvclass.subscribe, subscribe_dialog)
                    ),
                ],
            )
            self.rvclass.dialog.open()
            
class SubscribeContent(BoxLayout):
    price_text = StringProperty()
    moniker = StringProperty()
    naddress = StringProperty()
    coin_price = "0.00"
    
    menu = None
    def __init__ (self, price, moniker, naddress, hourly):
        super(SubscribeContent, self).__init__()
        
        self.price_text = price
        self.moniker    = moniker
        self.naddress   = naddress
        self.hourly     = hourly
        self.price_api = GetPriceAPI()
        self.price_cache = {}
        self.parse_coin_deposit(IBCTokens.ibc_coins[0])
        
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "circle-multiple",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in IBCTokens.ibc_coins #+ ['xmr']
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            background_color=get_color_from_hex(MeileColors.BLACK),
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        self.ids.drop_item.current_item = IBCTokens.ibc_coins[0]
        self.parse_coin_deposit(self.ids.drop_item.current_item)
        self.build()
        
    def build(self):
        if self.hourly:
            self.ids.slider1_value.text = str(int(self.ids.slider1.value)) + " days"
            self.ids.slider1.max = 30
            self.ids.slider1.value = 7
            
        self.get_usd() 

    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.ids.deposit.text = self.parse_coin_deposit(text_item)
        self.get_usd()
        self.menu.dismiss()

    def parse_coin_deposit(self, mu_coin):
        try:
            if self.price_text:
                mu_coin_amt = re.findall(r'([0-9]+.[0-9]+)' + mu_coin, self.price_text)[0]
                if mu_coin_amt:
                    if not self.hourly:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(mu_coin_amt)),4))
                    else: 
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*24*(float(mu_coin_amt)),4))
                    return self.ids.deposit.text
                else:
                    if not self.hourly:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(self.ids.price.text.split(IBCTokens.ibc_coins[0])[0])),4))
                    else:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*24*(float(self.ids.price.text.split(IBCTokens.ibc_coins[0])[0])),4))
                    return self.ids.deposit.text
            else:
                self.ids.deposit.text = "0.0"
                return self.ids.deposit.text
        except IndexError as e:
            #print(str(e))
            try: 
                if self.ids.price.text:
                    if not self.hourly:
                        if mu_coin == "xmr":
                            self.refresh_price('xmr', cache=30)
                            mu_coin_amt = re.findall(r'([0-9]+.[0-9]+)' + IBCTokens.ibc_coins[0], self.price_text)[0]
                            deposit_dvpn = round(int(self.ids.slider1.value)*float(mu_coin_amt),4)
                            deposit_xmr = round((deposit_dvpn*self.price_cache[IBCTokens.ibc_coins[0]]["price"]*ConfParams.XMRPAYADJ)/self.price_cache['xmr']['price'],12)
                            self.ids.deposit.text = str(deposit_xmr)
                        else:    
                            self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(self.ids.price.text.split(IBCTokens.ibc_coins[0])[0])),4)) 
                    else:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*24*(float(self.ids.price.text.split(IBCTokens.ibc_coins[0])[0])),4))
                    return self.ids.deposit.text
                else:
                    self.ids.deposit.text = "0.0" 
                    return self.ids.deposit.text
            except ValueError as e:
                print(str(e))
                self.ids.deposit.text = "0.0" 
                return self.ids.deposit.text    
    def return_deposit_text(self):
        if not self.hourly:
            return (self.ids.deposit.text, self.naddress, self.moniker, int(self.ids.slider1.value), self.hourly, self.ids.drop_item.current_item)
        else:
            return (self.ids.deposit.text, self.naddress, self.moniker, int(self.ids.slider1.value)*24, self.hourly, self.ids.drop_item.current_item)
    
    def return_sub_type(self):
        try: 
            if self.hourly:
                return " days"
            else:
                return " GB" 
        except AttributeError:
            return " GB"   
        
    def refresh_price(self, mu_coin: str = "dvpn", cache: int = 30):
        # Need check on cache or trought GetPrice api
        # We don't need to call the price api if the cache is younger that 30s

        if mu_coin not in self.price_cache or time.time() - self.price_cache[mu_coin]["time"] > cache:
            response = self.price_api.get_usd(mu_coin)
            self.price_cache[mu_coin] = {
                "price": float(response['price']),
                "time": time.time()
            }
            
    def get_usd(self):
        deposit_ret = self.return_deposit_text()
        
        self.refresh_price(deposit_ret[-1], cache=30)
        self.ids.usd_price.text = '$' + str(round(float(self.price_cache[deposit_ret[-1]]["price"]) * float(deposit_ret[0]),3))

        return True
    
class PlanSubscribeContent(BoxLayout):

    price_text = StringProperty()
    white_label = StringProperty()
    nnodes = StringProperty()
    logo_image = StringProperty()

    menu = None
    def __init__ (self, price, white_label, nnodes, logo_image):
        super(PlanSubscribeContent, self).__init__()

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
            } for i in IBCTokens.ibc_coins
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            background_color=get_color_from_hex(MeileColors.BLACK),
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        self.ids.drop_item.current_item = IBCTokens.ibc_coins[0]
        self.parse_coin_deposit(self.ids.drop_item.current_item)

    def refresh_price(self, mu_coin: str = "dvpn", cache: int = 30):
        # Need check on cache or trought GetPrice api
        # We don't need to call the price api if the cache is younger that 30s

        if mu_coin not in self.price_cache or time.time() - self.price_cache[mu_coin]["time"] > cache:
            response = self.price_api.get_usd(mu_coin)
            self.price_cache[mu_coin] = {
                "price": float(response['price']),
                "time": time.time()
            }

    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.ids.deposit.text = self.parse_coin_deposit(text_item)
        self.get_usd(text_item)
        try: 
            self.menu.dismiss()
        except TypeError as e:
            print(str(e))

    def parse_coin_deposit(self, mu_coin):
        
        # Save a copy, so we can edit the value without update the ui
        price_text = self.price_text
        # Parse all the coins without u-unit
        #if mu_coin.startswith("u"):
        #    if mu_coin in price_text:
        #        price_text = price_text.replace(mu_coin, mu_coin.lstrip('u'))
        #    mu_coin = mu_coin.lstrip('u')

        self.refresh_price("dvpn", cache=30)

        if mu_coin != "dvpn":
            self.refresh_price(mu_coin, cache=30)

        month = int(self.ids.slider1.value) # Months
        if mu_coin == "dvpn":
            value = float(price_text.rstrip(mu_coin).strip())
        else:
            value = round(float(price_text.rstrip("dvpn").strip()) * self.price_cache["dvpn"]["price"] / self.price_cache[mu_coin]["price"], 8)

        print(f"mu_coin={mu_coin}, month={month}, value={value}, price_cache={self.price_cache}")

        # display satoshis for BTC
        self.ids.deposit.text = str(format(round(month * value, 8),'8f')) 
        return self.ids.deposit.text


    def return_deposit_text(self):
        return (self.ids.deposit.text, self.nnodes)

    def on_checkbox_active(self, pay_with: str, checkbox, value):
        if value is True:
            self.pay_with = pay_with
            if pay_with == "now":
                self.ids.drop_item.text = "firo"
                menu_items = [
                    {
                        "viewclass": "IconListItem",
                        "icon": "circle-multiple",
                        "text": f"{i}",
                        "height": dp(56),
                        "on_release": lambda x=f"{i}": self.set_item(x),
                    } for i in IBCTokens.NOWCOINS    
                ]
                self.menu.items = menu_items
                self.set_item(IBCTokens.NOWCOINS[0])
                
            elif pay_with == "btcpay":
                self.ids.drop_item.text = "xmr"
                menu_items = [
                    {
                        "viewclass": "IconListItem",
                        "icon": "circle-multiple",
                        "text": f"{i}",
                        "height": dp(56),
                        "on_release": lambda x=f"{i}": self.set_item(x),
                    } for i in IBCTokens.BTCPAYCOINS    
                ]
                self.menu.items = menu_items
                self.set_item(IBCTokens.BTCPAYCOINS[0])
                
            elif pay_with == "pirate":
                self.ids.drop_item.text = "arrr"
                menu_items = [
                    {
                        "viewclass": "IconListItem",
                        "icon": "circle-multiple",
                        "text": f"{i}",
                        "height": dp(56),
                        "on_release": lambda x=f"{i}": self.set_item(x),
                    } for i in ["arrr"]  
                ]
                self.menu.items = menu_items
                self.set_item("arrr")
                
            else:
                self.ids.drop_item.text = "dvpn"
                menu_items = [
                    {
                        "viewclass": "IconListItem",
                        "icon": "circle-multiple",
                        "text": f"{i}",
                        "height": dp(56),
                        "on_release": lambda x=f"{i}": self.set_item(x),
                    } for i in IBCTokens.ibc_coins
                ]
                self.menu.items = menu_items
                self.set_item(IBCTokens.ibc_coins[0])
                
                
    def get_usd(self, coin):
        deposit_ret = self.return_deposit_text()
        match = re.match(r"([0-9]+.[0-9]+)", deposit_ret[0], re.I)
        if match:
            amt    = match.groups()[0]
        else:
            amt    = 0.0
            coin   = "dvpn"
        
        self.refresh_price(coin, cache=30)
        self.ids.usd_price.text = '$' + str(round(float(self.price_cache[coin]["price"]) * float(amt),3))
                
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
            
class ProcessingSubDialog(BoxLayout):
    moniker = StringProperty()
    naddress = StringProperty()
    deposit = StringProperty()
    
    def __init__(self, moniker, naddress, deposit):
        super(ProcessingSubDialog, self).__init__()
        self.moniker = moniker
        self.naddress = naddress
        self.deposit = deposit
        
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
        
    
class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class NodeRV(RecycleView):    
    pass

class NodeRV2(RecycleView):    
    pass

class NodeRVSub(RecycleView):    
    pass

class OnHoverMDRaisedButton(MDFlatButton, HoverBehavior):
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex("#fad783")
        Window.set_system_cursor('arrow')
        
    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.md_bg_color = get_color_from_hex("#fcb711")
        Window.set_system_cursor('arrow')


class NodeRow(MDGridLayout):
    moniker = StringProperty()
    location = StringProperty()
    protocol = StringProperty()
    node_type = StringProperty()
    expires = StringProperty()
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
class NodeDetails(MDGridLayout):
    sub_id = StringProperty()
    allocated = StringProperty()
    consumed  = StringProperty()
    deposit = StringProperty()
    score = StringProperty()
    votes = StringProperty()
    formula = StringProperty()
    node_address = StringProperty()
    dialog = None

    def unsubscribe_from_node(self, subId):

        self.dialog = MDDialog(
                title="Unsubscribe from ID: %s?" % subId,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.MEILE),
                        on_release=self.closeDialog
                    ),
                    MDRaisedButton(
                        text="UNSUBSCRIBE",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release=partial(self.unsubscribe, subId)
                    ),
                ],
            )
        self.dialog.open()

    @delayable        
    def unsubscribe(self, subId, *kwargs):

        yield 0.3
        self.closeDialog(None)
        yield 0.6
        self.add_loading_popup("Unsubscribing to subscription id: %s" % subId)
        yield 0.6
        sleep(1)

        hwf = HandleWalletFunctions()
        t = Thread(target=lambda: hwf.unsubscribe(int(subId)))
        t.start()
        
        while t.is_alive():
            print(".", end="")
            sys.stdout.flush()
            yield 0.5

        self.closeDialog(None)

        TXDialog = TXContent()
        TXDialog.ids.message.text = hwf.unsub_result['message']
        TXDialog.ids.txhash.text  = hwf.unsub_result['hash']
        
        yield 0.3
        if not self.dialog:
            self.dialog = MDDialog(
                    title="Unsub Details",
                    type="custom",
                    content_cls=TXDialog,
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                        MDRaisedButton(
                            text="OKAY",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex(MeileColors.BLACK),
                            on_release=self.closeDialog
                        ),
                    ],
                )
            self.dialog.open()
            
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(title=title_text,md_bg_color=get_color_from_hex(MeileColors.BLACK))
        self.dialog.open()
                
    def closeDialog(self, dt):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None
        
class NodeAccordion(ButtonBehavior, MDGridLayout):
    node = ObjectProperty()  # Main node info

    # https://github.com/kivymd/KivyMD/blob/master/kivymd/uix/expansionpanel/expansionpanel.py
    content = ObjectProperty()  # Node details....
    """
    Content of panel. Must be `Kivy` widget.

    :attr:`content` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    opening_transition = StringProperty("out_cubic")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` `'open'`.

    :attr:`opening_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_cubic'`.
    """

    opening_time = NumericProperty(0.2)
    """
    The time taken for the panel to slide to the :attr:`state` `'open'`.

    :attr:`opening_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """

    closing_transition = StringProperty("out_sine")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` 'close'.

    :attr:`closing_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_sine'`.
    """

    closing_time = NumericProperty(0.2)
    """
    The time taken for the panel to slide to the :attr:`state` `'close'`.

    :attr:`closing_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """
    
    _state = StringProperty("close")
    _anim_playing = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        self.register_event_type("on_open")
        self.register_event_type("on_close")
        
        Clock.schedule_once(self.finish_init,0)

    def finish_init(self, dt):    
        self.add_widget(self.node)        

    def on_release(self):
        '''TODO:
        in first logic statement populate a MainScreen dictionary
        with current node address and ID.
        THis will be used when the user clicks on the subscription
        which expands it's contents, the MainScreen dictionary
        will be used to connect to subscription when the user
        clicks "Connect"
        Second logic statement (else) should reset the MainScreen
        dictionary to prior state.
        
        Use:
        content.node_address
        content.sub_id
        '''
        if len(self.children) == 1:
            self.add_widget(self.content)
            self.open_panel()
            self.dispatch("on_open")
        else:
            self.remove_widget(self.children[0])
            self.close_panel()
            self.dispatch("on_close")

    def on_open(self, *args):
        """Called when a panel is opened."""
        
        # Register the subscription for the connect button
        self.mw.SelectedSubscription['id']         = self.content.sub_id
        self.mw.SelectedSubscription['address']    = self.content.node_address
        self.mw.SelectedSubscription['protocol']   = self.node.protocol
        self.mw.SelectedSubscription['moniker']    = self.node.moniker
        self.mw.SelectedSubscription['allocated']  = self.content.allocated
        self.mw.SelectedSubscription['consumed']   = self.content.consumed
        self.mw.SelectedSubscription['expires']    = self.node.expires
        self.mw.SelectedSubscription['deposit']    = self.content.deposit
        
        

    def on_close(self, *args):
        """Called when a panel is closed."""
        
        # Unregister the subscription for the connect button
        self.mw.SelectedSubscription['id']          = None
        self.mw.SelectedSubscription['address']     = None
        self.mw.SelectedSubscription['protocol']    = None
        self.mw.SelectedSubscription['moniker']     = None
        self.mw.SelectedSubscription['allocated']   = None
        self.mw.SelectedSubscription['consumed']    = None
        self.mw.SelectedSubscription['expires']     = None
        self.mw.SelectedSubscription['deposit']     = None

    def close_panel(self) -> None:
        """Method closes the panel."""

        if self._anim_playing:
            return

        self._anim_playing = True
        self._state = "close"

        anim = Animation(
            height=self.children[0].height,
            d=self.closing_time,
            t=self.closing_transition,
        )
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

    def open_panel(self, *args) -> None:
        """Method opens a panel."""

        if self._anim_playing:
            return

        self._anim_playing = True
        self._state = "open"

        anim = Animation(
            height=self.content.height + self.height,
            d=self.opening_time,
            t=self.opening_transition,
        )
        # anim.bind(on_complete=self._add_content)
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

    def get_state(self) -> str:
        """Returns the state of panel. Can be `close` or `open` ."""

        return self._state

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, NodeDetails):
            self.height = widget.height
        return super().add_widget(widget)

    def _disable_anim(self, *args):
        self._anim_playing = False

    def _add_content(self, *args):
        if self.content:
            self.content.y = dp(72)
            self.add_widget(self.content)
            
class PlanRow(MDGridLayout):
    
    plan_name = StringProperty()
    num_of_nodes = StringProperty()
    num_of_countries = StringProperty()
    cost = StringProperty()
    logo_image = StringProperty()
    uuid = StringProperty()
    id = StringProperty()
    plan_id = StringProperty()
    
    dialog = None
    
    def __init__(self, plan_name,
                       num_of_nodes,
                       num_of_countries,
                       cost,
                       logo_image,
                       uuid,
                       id,
                       plan_id):
        super(PlanRow, self).__init__()
        self.stop_event = Event()
        self.plan_name = plan_name
        self.num_of_nodes = num_of_nodes
        self.num_of_countries = num_of_countries
        self.cost = cost
        self.logo_image = logo_image 
        self.uuid = uuid 
        self.id = id
        self.plan_id = plan_id
    
        self.invoice_result = {"success" : False, "id": None }
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def get_button(self, text):
        Config = MeileGuiConfig()
        if text == "info":
            return Config.resource_path(MeileColors.GETINFO_BUTTON)
        elif text == "subscribe":
            return Config.resource_path(MeileColors.SUBSCRIBE_BUTTON)
    
    def open_subscribe(self):
        
        item =  { "price": self.cost, "white_label": self.plan_name, "nnodes": self.num_of_nodes, "logo_image": self.logo_image }
        
        subscribe_dialog = PlanSubscribeContent(**item)
        self.dialog = None
        self.dialog = MDDialog(
                title="Subscription Plan",
                type="custom",
                content_cls=subscribe_dialog,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.MEILE),
                        on_release=self.closeDialog
                    ),
                    MDRaisedButton(
                        text="SUBCRIBE",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        #on_release=partial(self.subscribe, subscribe_dialog=subscribe_dialog)
                        on_release=lambda x: self.subscribe(subscribe_dialog)
                    ),
                ],
            )
        self.dialog.open()
        
    
    @delayable
    def add_wallet_2plan(self, wallet, plan_id, duration, sub_id, uuid, amt, denom):
        plan_details = {"data": {"wallet" : wallet, "plan_id" : plan_id, "duration" : duration, "sub_id" : sub_id, "uuid" : uuid, "amt" : amt, "denom" : denom}}
        print(plan_details)
        SERVER_ADDRESS = scrtsxx.MEILE_PLAN_API
        API            = scrtsxx.MEILE_PLAN_ADD
        USERNAME       = scrtsxx.PLANUSERNAME
        PASSWORD       = scrtsxx.PLANPASSWORD
        Request = HTTPRequests.MakeRequest(TIMEOUT=120)
        http = Request.hadapter()
        try:
            print("Sending plan add request...")
            tx = http.post(SERVER_ADDRESS + API, json=plan_details, auth=HTTPBasicAuth(USERNAME, PASSWORD))
            txJSON = tx.json()
            if txJSON['status']:
                self.dialog.dismiss()
                self.dialog = None
                self.dialog = MDDialog(
                        title=f"{wallet} added to plan: {plan_id}",
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                        buttons=[
                            MDRaisedButton(
                                text="CLOSE",
                                theme_text_color="Custom",
                                text_color=MeileColors.BLACK,
                                on_release=self.closeDialog
                            ),
                        ],
                    )
                self.dialog.open()
                yield 0.6
            else:
                self.dialog.dismiss()
                self.dialog = None
                self.dialog = MDDialog(
                        title=f"Error processing adding wallet to plan. If the invoice was paid, please email support@mathnodes.com to gain assistance",
                        buttons=[
                            MDRaisedButton(
                                text="CLOSE",
                                theme_text_color="Custom",
                                text_color=MeileColors.BLACK,
                                on_release=self.closeDialog
                            ),
                        ],
                    )
                self.dialog.open()
                yield 0.6
        except Exception as e:
            print(str(e))
            self.dialog.dismiss()
            self.dialog = None
            
    @delayable
    def add_wallet_2alloc(self, wallet, node, gb):
        plan_details = {'wallet' : wallet, 'gb' : gb, 'node' : node}
        print(plan_details)
        SERVER_ADDRESS = HTTParams.PLAN_API
        API            = "/v1/allocate"
        USERNAME       = scrtsxx.PLANUSERNAME
        PASSWORD       = scrtsxx.PLANPASSWORD
        Request = HTTPRequests.MakeRequest(TIMEOUT=120)
        http = Request.hadapter()
        try:
            print("Sending allocate add request...")
            tx = http.post(SERVER_ADDRESS + API, json=plan_details, auth=HTTPBasicAuth(USERNAME, PASSWORD))
            txJSON = tx.json()
            if txJSON['status']:
                self.dialog.dismiss()
                self.dialog = None
                self.dialog = MDDialog(
                        title=f"{wallet} successfully added to subscription.",
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                        buttons=[
                            MDRaisedButton(
                                text="CLOSE",
                                theme_text_color="Custom",
                                text_color=MeileColors.BLACK,
                                on_release=self.closeDialog
                            ),
                        ],
                    )
                self.dialog.open()
                yield 0.6
            else:
                self.dialog.dismiss()
                self.dialog = None
                self.dialog = MDDialog(
                        title=f"Error processing adding wallet to plan. If the invoice was paid, please email support@mathnodes.com to gain assistance",
                        buttons=[
                            MDRaisedButton(
                                text="CLOSE",
                                theme_text_color="Custom",
                                text_color=MeileColors.BLACK,
                                on_release=self.closeDialog
                            ),
                        ],
                    )
                self.dialog.open()
                yield 0.6
        except Exception as e:
            print(str(e))
            self.dialog.dismiss()
            self.dialog = None

    
    @delayable
    def subscribe(self, subscribe_dialog, payg=False, payg_dialog=None, data=None, *kwargs):
        CONFIG = MeileGuiConfig()
        conf = CONFIG.read_configuration(MeileGuiConfig.CONFFILE)
        self.ADDRESS = conf['wallet'].get("address")
        
        self.payg = payg
        print(f"self.payg: {self.payg}")
        
        if not self.ADDRESS:
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(
                    title="Please create a Sentinel wallet before subscribing to a plan. The wallet is used for gas fees on the Sentinel network. We provide you with coins for gas fees after subscribing to a plan.",
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                        MDFlatButton(
                            text="OKAY",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex(MeileColors.MEILE),
                            on_release=self.closeDialog
                        ),
                    ]
                )
            self.dialog.open()
            return
        
        if not self.payg:
            deposit = subscribe_dialog.ids.deposit.text
            nnodes = subscribe_dialog.nnodes
            mu_coin = subscribe_dialog.ids.drop_item.current_item
            usd = round(float(deposit) * subscribe_dialog.price_cache[mu_coin]["price"], 5)
            
        else:
            deposit = data[0]
            mu_coin = data[-1]
            nnodes = 1
            usd = round(float(deposit) * payg_dialog.price_cache[mu_coin]["price"], 5)
            
        
        # Parse all the coins without u-unit
        #if mu_coin.startswith("u"):
        #    mu_coin = mu_coin.lstrip('u')

        # use the price caching directly from subscribe_dialog
        
        
        print(f"Deposit {deposit} {mu_coin} for {nnodes} nodes. usd value is: {usd}")
        
        # usd value must be multiplu for nnodes (?)

        # sub_node = subscribe_dialog.return_deposit_text()
        # deposit = self.reparse_coin_deposit(sub_node[0])

        # Declare method here so we can pass it as callback variable to methods
        if not self.payg:
            self.on_success_subscription = lambda: self.add_wallet_2plan(
                                                                        wallet=self.ADDRESS,
                                                                        plan_id=self.plan_id,
                                                                        duration=subscribe_dialog.ids.slider1.value,
                                                                        sub_id=self.id,
                                                                        uuid=self.uuid,
                                                                        amt=int(float(deposit) * IBCTokens.SATOSHI) if mu_coin in IBCTokens.ibc_coins else float(deposit),
                                                                        denom=mu_coin
                                                                    )
        else:
            self.on_success_subscription_payg = lambda: self.add_wallet_2alloc(
                                                                        wallet=self.ADDRESS,
                                                                        node=data[1],
                                                                        gb=data[3]
                                                                    )
        if not subscribe_dialog:
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(
                    title="Waiting for invoice to be paid...",
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex(MeileColors.MEILE),
                            on_release=self.cancel_payment
                        ),
                    ]
                )
            self.dialog.open()
            yield 0.6
            self.start_payment_thread(usd)
            return
        
        elif subscribe_dialog.pay_with == "wallet":
            self.pay_meile_plan_with_wallet(deposit, mu_coin, usd, self.on_success_subscription)
            
        elif subscribe_dialog.pay_with == "btcpay":
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(
                    title="Waiting for invoice to be paid...",
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex(MeileColors.MEILE),
                            on_release=self.cancel_payment
                        ),
                    ]
                )
            self.dialog.open()
            yield 0.6
            self.start_payment_thread(usd*ConfParams.BTCPAYADJ)
            
        elif subscribe_dialog.pay_with == "pirate":
            
            zaddress = self.check_invoice_status_pirate(address=True)
            
            price_api = GetPriceAPI()
            arrrusd = price_api.get_usd("arrr")
            cost = usd*ConfParams.BTCPAYADJ
            total_arrr = round(float(cost) / float(arrrusd['price']),2)
            
            
            if self.dialog:
                self.dialog.dismiss()
                
            self.dialog = None
                
            self.invoice_content = QRDialogContent()
            self.invoice_content.ids.zaddress_field.text = zaddress
            self.invoice_content.ids.price_field.text = f"{total_arrr} ARRR"

            # Generate QR Code
            QRcode = QRCode()
            self.invoice_content.ids.qr_img.source = QRcode.generate_qr_code(zaddress, "arrr") 

            self.dialog = MDDialog(
                title="Waiting for invoice to be paid...",
                type="custom",
                content_cls=self.invoice_content,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex(MeileColors.MEILE),
                            on_release=self.cancel_payment
                        ),
                    ]
            )
            self.dialog.open()
            yield 0.6
            self.start_payment_thread_pirate(total_arrr)
            
        elif subscribe_dialog.pay_with == "now":
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(
                    title="Waiting for invoice to be paid...",
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex(MeileColors.MEILE),
                            on_release=self.cancel_payment
                        ),
                    ]
                )
            self.dialog.open()
            yield 0.6
            self.start_payment_thread_now(usd*ConfParams.BTCPAYADJ, mu_coin)

        else:
            MDDialog(text="[color=#FF0000]Please select a payment option[/color]").open()

        # self.dialog.dismiss()
        # self.dialog = None
        # self.dialog = MDDialog(title="Subscribing...\n\n%s\n %s" %( deposit, sub_node[1]))
        # self.dialog.open()

        # Run Subscription method
        # self.subscribe

    @delayable
    def pay_meile_plan_with_wallet(self, deposit, mu_coin, usd, on_success: callable):
        print(f"Method: 'pay_meile_plan_with_wallet', usd: {usd}, {deposit} {mu_coin}")

        # moniker, naddress, deposit
        # spdialog = ProcessingSubDialog(sub_node[2], sub_node[1], f"{deposit}{mu_coin}" )
        self.dialog.dismiss()
        self.dialog = None
        self.dialog = MDDialog(
                title="Subscribing...",
                type="custom",
                # content_cls=spdialog,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
            )
        self.dialog.open()
        yield 0.6

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        hwf = HandleWalletFunctions()
        result, output = hwf.send_2plan_wallet(KEYNAME, self.plan_id, mu_coin, int(round(float(deposit),4)*IBCTokens.SATOSHI))
        print("result", result)
        print("output", output)

        if result is True:
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(title=output["message"] + " Finishing up...",
                                   md_bg_color=get_color_from_hex(MeileColors.BLACK)
                                   )
            self.dialog.open()
            yield 0.6
            on_success()
        else:
            if self.dialog:
                self.dialog.dismiss()

            self.dialog = MDDialog(
                title = ("Success" if output["success"] else "Failed") if isinstance(output, dict) else ("Error: %s" % "No wallet found!" if output == 1337 else output),
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=MeileColors.MEILE,
                            on_release=self.closeDialog
                        ),])
            if isinstance(output, dict) is True:
                self.dialog.text = output["message"]
            self.dialog.open()

    def pay_meile_plan_with_btcpay(self, usd):
        print(f"Method: 'pay_meile_plan_with_btcpay', usd: {usd}")
        
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
        BTCPay = BTCPayDB()
        
        pickled_client_data = BTCPay.get_remote_btcpay_client()
        
        if pickled_client_data:
            self.client = BTCPay.unpickle_btc_client(pickled_client_data)
        else:
            return (False, "No pickeled client data")
        
        print(self.client)
            
        buyer = {"name" : mw.address, "email" : "freqnik@mathnodes.com", "notify" : True}
        print(f"buyer: {buyer}")
        
        data = {"price": usd,
              "currency": "USD",
              "token" : "XMR",
              "merchantName" : "Meile dVPN",
              "itemDesc" : "MathNodes Subscription Plan",
              "notificationEmail" : scrtsxx.BTCPayEmail,
              "transactionSpeed" : "high",
              "buyer" : buyer}
        
        print(f"data: {data}")
        
        self.new_invoice = self.client.create_invoice(data)
        
        print(self.new_invoice)
        print(self.new_invoice['url'])
        self.btcpay_tx_id = self.new_invoice['id']
        
        webbrowser.open(self.new_invoice['url'])
        self.fetched_invoice = self.client.get_invoice(self.btcpay_tx_id)
        
        while not self.stop_event.is_set():
            sleep(10)
            self.check_invoice_status()
            
            if self.invoice_result['success']:
                self.stop_event.set()
                Clock.schedule_once(lambda dt: self.update_ui_after_payment(False), 0)
                print(self.invoice_result)
                return
        
        if self.stop_event.is_set() and self.invoice_result['success']:
            print("Invoice has been paid.")
            Clock.schedule_once(lambda dt: self.update_ui_after_payment(False), 0)
        elif self.stop_event.is_set():
            print("Payment process was canceled.")
            Clock.schedule_once(lambda dt: self.update_ui_after_payment(True), 0)
        
    def pay_meile_plan_with_now(self, usd, coin):
        print(f"Method: 'pay_meile_plan_with_now', usd: {usd}")
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        buyer = mw.address
        
        Request = HTTPRequests.MakeRequest(TIMEOUT=120)
        http = Request.hadapter()
        
        headers = {
                "x-api-key": scrtsxx.NOWPAYMENTS,
                "Content-Type": "application/json"
                }
        
        USD = round(usd, 2)
        
        # Create the Invoice
        idata = {"price_amount": USD,
                "price_currency": "usd",
                "pay_currency" : f"{coin}", 
                "order_id": f"{buyer}", 
                "order_description": "Meile Subscription Plan",
                "cancel_url": "https://nowpayments.io",
                }
        
        #print(idata)
        
        try:
            response = http.post(HTTParams.NOWINVOICE, headers=headers, json=idata)
            invoice_response = response.json()
            #print(invoice_response)
            invoiceID = invoice_response['id']
        except Exception as e:
            print(str(e))
            self.ret_now = (False, "Error creating NOW invoice request")
            return
        
        # Create the payment request from Invoice ID    
        pdata = {
                  "iid": int(invoiceID),
                  "pay_currency": f"{coin}",
                  "order_description": "Meile Subscription Plan",
                  "customer_email": f"{buyer}"
                }
        
        #print(pdata)
        
        try:
            response = http.post(HTTParams.NOWPAYMENT, headers=headers, json=pdata)
            payment_response = response.json()
            print(payment_response)
            self.paymentID = payment_response['payment_id']
        except Exception as e:
            print(str(e))
            self.ret_now = (False, "Error creating NOW payment request")
            return
        
        
        url = HTTParams.NOWURL % (invoiceID, self.paymentID)
        webbrowser.open(url)    
        
        try:
            headers = {
                        "x-api-key": scrtsxx.NOWPAYMENTS
                      }
            response = http.get(HTTParams.NOWSTATUS % self.paymentID, headers=headers)
            self.now_status = response.json()
        except Exception as e:
            print(str(e))
            self.ret_now = (False, "Error getting NOW invoice status")
            
        while not self.stop_event.is_set():
            sleep(10)
            self.check_invoice_status_now()
            
            if self.invoice_result['success']:
                self.stop_event.set()
                Clock.schedule_once(lambda dt: self.update_ui_after_payment(False), 0)
                print(self.invoice_result)
                return
        
        if self.stop_event.is_set() and self.invoice_result['success']:
            print("Invoice has been paid.")
            Clock.schedule_once(lambda dt: self.update_ui_after_payment(False), 0)
        elif self.stop_event.is_set():
            print("Payment process was canceled.")
            Clock.schedule_once(lambda dt: self.update_ui_after_payment(True), 0)
         
    def pay_meile_plan_with_pirate(self, arrr):
        print(f"Method: 'pay_meile_plan_with_pirate', arrr: {arrr}")
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        buyer = mw.address
        
        self.zaddress_balance = 0
        self.mempool = False
        
        while not self.stop_event.is_set():
            sleep(10)
            self.check_invoice_status_pirate(invoice=True, arrr=arrr)
            
            if self.invoice_result['success']:
                self.stop_event.set()
                Clock.schedule_once(lambda dt: self.update_ui_after_payment(False), 0)
                print(self.invoice_result)
                return
        
        if self.stop_event.is_set() and self.invoice_result['success']:
            print("Invoice has been paid.")
            Clock.schedule_once(lambda dt: self.update_ui_after_payment(False), 0)
        elif self.stop_event.is_set():
            print("Payment process was canceled.")
            Clock.schedule_once(lambda dt: self.update_ui_after_payment(True), 0)
            
    ''' In the future the following two routines should be merged
        into one with conditional logic to check which payment
        processor we are using
    '''
                
    def start_payment_thread(self, usd):
        self.stop_event.clear()
        self.invoice_thread = Thread(target=lambda: self.pay_meile_plan_with_btcpay(usd))
        self.invoice_thread.start()
        Clock.schedule_interval(self.check_thread_status, 0.1)
        
    def start_payment_thread_now(self, usd, coin):
        self.stop_event.clear()
        self.invoice_thread = Thread(target=lambda: self.pay_meile_plan_with_now(usd, coin))
        self.invoice_thread.start()
        Clock.schedule_interval(self.check_thread_status, 0.1)
        
    def start_payment_thread_pirate(self, arrr):
        self.stop_event.clear()
        self.invoice_thread = Thread(target=lambda: self.pay_meile_plan_with_pirate(arrr))
        self.invoice_thread.start()
        Clock.schedule_interval(self.check_thread_status, 0.1)
        
    def check_thread_status(self, dt):
        if self.stop_event.is_set() and not self.invoice_thread.is_alive():
            return False  # Stop checking once the thread has finished
    
    ''' In the future the following two routines should be merged
        into one with conditional logic to check which payment
        processor we are using
    '''
        
    def check_invoice_status(self):
        print("Checking if invoice is paid...")
        if self.fetched_invoice['status'] != "confirmed":
            print("invoice not yet confirmed....")
            self.fetched_invoice = self.client.get_invoice(self.btcpay_tx_id)
        else:
            print(self.fetched_invoice)
            self.invoice_result = {"success" : True, "id": self.new_invoice['id'] }
            
    def check_invoice_status_now(self):
        print("Checking if invoice is paid...")
        Request = HTTPRequests.MakeRequest(TIMEOUT=120)
        http = Request.hadapter()
            
        if self.now_status['payment_status'] != "confirming":
            print("invoice not yet confirmed....")
            try:
                headers = {
                            "x-api-key": scrtsxx.NOWPAYMENTS
                          }
                response = http.get(HTTParams.NOWSTATUS % self.paymentID, headers=headers)
                self.now_status = response.json()
                print(self.now_status)
            except Exception as e:
                print(str(e))
                self.ret_now = (False, "Error getting NOW invoice status")
        else:
            #print(self.fetched_invoice)
            self.invoice_result = {"success" : True, "id": self.now_status['payment_id'] }
    
        
    def check_invoice_status_pirate(self, address=False, invoice=False, arrr=0):
        Request = HTTPRequests.MakeRequest(TIMEOUT=120)
        http = Request.hadapter()
        USERNAME       = scrtsxx.PLANUSERNAME
        PASSWORD       = scrtsxx.PLANPASSWORD
        
        def check_balance(conf: int):
            try: 
                data = {'address' : f"{self.zaddress}",
                        'conf'    : conf}
                print(data)
                endpoint = '/v1/pirate/getbalance'
                response = http.post(HTTParams.PLAN_API + endpoint, json=data, auth=HTTPBasicAuth(USERNAME, PASSWORD))
                self.zaddress_balance = float(response.json()['result'])
                
                if self.zaddress_balance > 0:
                    self.mempool = True
                else:
                    self.mempool = False
                    
            except Exception as e:
                print(str(e))
                
        if address == True:
            print("Getting new pirate chain address...")

            try: 
                endpoint = '/v1/pirate/newaddress'
                response = http.get(HTTParams.PLAN_API + endpoint, auth=HTTPBasicAuth(USERNAME, PASSWORD))
                self.zaddress = response.json()['result']
                return self.zaddress
            except Exception as e:
                print(str(e))
                self.zaddress = "NULL"
                return self.zaddress
            
        elif invoice == True:
            if not self.mempool:
                print(f"Checking balance of: {self.zaddress}")
                check_balance(0)
                    
            elif self.mempool and self.zaddress_balance < arrr:
                remaining_amt = float(arrr) - float(self.zaddress_balance)
                self.dialog.title = "Deposit detected, but not full amount... waiting for remaining balance..."
                #self.invoice_content.ids.price_field.text = f"{remaining_amt} ARRR"
                self.invoice_content.ids.status.text = "Deposit detected, but not full amount... waiting for remaining balance..."
                check_balance(0)
                
            else:
                self.dialog.title = "Deposit detected... waiting for confirmations..."
                self.invoice_content.ids.status.text = "Deposit detected... waiting for confirmations..."
                remaining_amt = float(arrr) - float(self.zaddress_balance)
                #self.invoice_content.ids.price_field.text = f"{remaining_amt} ARRR"
                check_balance(1)
                if self.zaddress_balance >= arrr:
                    self.invoice_result = {"success" : True, "id": self.zaddress_balance }
            
    def update_ui_after_payment(self, canceled):
        if canceled:
            if self.dialog:
                self.dialog.title = "Payment was canceled."
                self.dialog.buttons[0].text = "OK"
        else:
            if self.dialog:
                self.dialog.dismiss()
                self.dialog = None
            self.dialog = MDDialog(
                title=f"Invoice {self.invoice_result['id']} has been marked as paid! Finishing up...",
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
            )
            self.dialog.open()

            # Simulate some delay before calling on_success_subscription
            Clock.schedule_once(self.call_on_success_subscription, 0.6)
            
    def call_on_success_subscription(self, dt):
        if not self.payg:
            if self.on_success_subscription:
                self.on_success_subscription()
        else:
            if self.on_success_subscription_payg:
                self.on_success_subscription_payg()
    '''
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
    '''
    def closeDialog(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        
    def cancel_payment(self, *args):
        self.stop_event.set()
        if self.invoice_thread:
            self.invoice_thread.join()  # Wait for the thread to finish

        # Close the dialog if needed
        if self.dialog:
            self.dialog.dismiss()

class PlanDetails(MDGridLayout):
    uuid = StringProperty()
    id = StringProperty()
    expires  = StringProperty()
    deposit = StringProperty()
    coin = StringProperty()
    
    def filter_nodes(self):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        req = http.get(HTTParams.PLAN_API + HTTParams.API_PLANS_NODES % self.uuid, auth=HTTPBasicAuth(scrtsxx.PLANUSERNAME, scrtsxx.PLANPASSWORD))
    
        plan_nodes_data = req.json()
            
        mw.NodeTree.search(key=NodeKeys.NodesInfoKeys[1], value=plan_nodes_data, perfect_match=True, is_list=True)
        
        mw.refresh_country_recycler()
    
        
class PlanAccordion(ButtonBehavior, MDGridLayout):
    node = ObjectProperty()  # Main node info

    # https://github.com/kivymd/KivyMD/blob/master/kivymd/uix/expansionpanel/expansionpanel.py
    content = ObjectProperty()  # Node details....
    """
    Content of panel. Must be `Kivy` widget.

    :attr:`content` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    opening_transition = StringProperty("out_cubic")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` `'open'`.

    :attr:`opening_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_cubic'`.
    """

    opening_time = NumericProperty(0.2)
    """
    The time taken for the panel to slide to the :attr:`state` `'open'`.

    :attr:`opening_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """

    closing_transition = StringProperty("out_sine")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` 'close'.

    :attr:`closing_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_sine'`.
    """

    closing_time = NumericProperty(0.2)
    """
    The time taken for the panel to slide to the :attr:`state` `'close'`.

    :attr:`closing_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """
    
    _state = StringProperty("close")
    _anim_playing = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        self.register_event_type("on_open")
        self.register_event_type("on_close")
        
        Clock.schedule_once(self.finish_init,0)

    def finish_init(self, dt):    
        self.add_widget(self.node)        

    def on_release(self):
        '''TODO:
        in first logic statement populate a MainScreen dictionary
        with current node address and ID.
        THis will be used when the user clicks on the subscription
        which expands it's contents, the MainScreen dictionary
        will be used to connect to subscription when the user
        clicks "Connect"
        Second logic statement (else) should reset the MainScreen
        dictionary to prior state.
        
        Use:
        content.node_address
        content.sub_id
        '''
        if len(self.children) == 1:
            self.add_widget(self.content)
            self.open_panel()
            self.dispatch("on_open")
        else:
            self.remove_widget(self.children[0])
            self.close_panel()
            self.dispatch("on_close")

    def on_open(self, *args):
        """Called when a panel is opened."""
        self.mw.PlanID = self.content.id

    def on_close(self, *args):
        """Called when a panel is closed."""
        self.mw.PlanID = None

    def close_panel(self) -> None:
        """Method closes the panel."""

        if self._anim_playing:
            return

        self._anim_playing = True
        self._state = "close"

        anim = Animation(
            height=self.children[0].height,
            d=self.closing_time,
            t=self.closing_transition,
        )
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

    def open_panel(self, *args) -> None:
        """Method opens a panel."""

        if self._anim_playing:
            return

        self._anim_playing = True
        self._state = "open"

        anim = Animation(
            height=self.content.height + self.height,
            d=self.opening_time,
            t=self.opening_transition,
        )
        # anim.bind(on_complete=self._add_content)
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

    def get_state(self) -> str:
        """Returns the state of panel. Can be `close` or `open` ."""

        return self._state

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, NodeDetails):
            self.height = widget.height
        return super().add_widget(widget)

    def _disable_anim(self, *args):
        self._anim_playing = False

    def _add_content(self, *args):
        if self.content:
            self.content.y = dp(72)
            self.add_widget(self.content)


class NodeCarousel(MDBoxLayout):
    moniker         = StringProperty()
    address         = StringProperty()
    gb_prices       = StringProperty()
    hr_prices       = StringProperty()
    download        = StringProperty()
    upload          = StringProperty()
    connected_peers = StringProperty()
    max_peers       = StringProperty()
    protocol        = StringProperty()
    version         = StringProperty()
    handshake       = StringProperty()
    health_check    = StringProperty()
    isp_type        = StringProperty()
    node_formula    = StringProperty()
    votes           = StringProperty()
    score           = StringProperty()
    location        = StringProperty()
    dialog          = None
    
    def __init__(self, node, **kwargs):
        super(NodeCarousel, self).__init__()
        
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        if node:
            mw.NodeCarouselData = {"moniker"   : node[NodeKeys.NodesInfoKeys[0]],
                                   "address"   : node[NodeKeys.NodesInfoKeys[1]],
                                   "gb_prices" : node[NodeKeys.NodesInfoKeys[2]],
                                   "hr_prices" : node[NodeKeys.NodesInfoKeys[3]],
                                   "protocol"  : node[NodeKeys.NodesInfoKeys[13]]}
            
            gbprices = node[NodeKeys.NodesInfoKeys[2]].split(',')
            hrprices = node[NodeKeys.NodesInfoKeys[3]].split(',')
            
            self.gb_prices = ""
            self.hr_prices = ""
            
            for g in gbprices:
                self.gb_prices = self.gb_prices + g.lstrip() + '\n'
            
            for h in hrprices:
                self.hr_prices = self.hr_prices + h.lstrip() + '\n'
                
            
            self.moniker         = node[NodeKeys.NodesInfoKeys[0]]
            self.address         = node[NodeKeys.NodesInfoKeys[1]]
            self.download        = format_byte_size(node[NodeKeys.NodesInfoKeys[8]])+ "/s"
            self.upload          = format_byte_size(node[NodeKeys.NodesInfoKeys[9]])+ "/s"
            self.connected_peers = str(node[NodeKeys.NodesInfoKeys[10]])
            self.max_peers       = str(node[NodeKeys.NodesInfoKeys[11]])
            self.protocol        = node[NodeKeys.NodesInfoKeys[13]]
            self.version         = node[NodeKeys.NodesInfoKeys[14]]
            self.handshake       = str(node[NodeKeys.NodesInfoKeys[12]])
            self.health_check    = self.GetHealthCheck(node[NodeKeys.NodesInfoKeys[1]])
            self.isp_type        = node[NodeKeys.NodesInfoKeys[15]] if node[NodeKeys.NodesInfoKeys[15]] else "Unknown" 
            self.node_formula    = str(node[NodeKeys.NodesInfoKeys[18]]) if node[NodeKeys.NodesInfoKeys[18]] else "NULL"
            self.votes           = str(node[NodeKeys.NodesInfoKeys[17]]) if node[NodeKeys.NodesInfoKeys[17]] else "0"
            self.score           = str(node[NodeKeys.NodesInfoKeys[16]]) if node[NodeKeys.NodesInfoKeys[16]] else "NULL"
            self.location        = f"[b]Location:[/b] {node[NodeKeys.NodesInfoKeys[5]]}, {node[NodeKeys.NodesInfoKeys[4]]}"
            
            try:
                self.ids.mapview.center_on(float(node[NodeKeys.NodesInfoKeys[6]])-1,float(node[NodeKeys.NodesInfoKeys[7]]))
            except Exception as e:
                print(str(e))
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def get_button(self, text):
        Config = MeileGuiConfig()
        if text == "info":
            return Config.resource_path(MeileColors.GETINFO_BUTTON)
        elif text == "subscribe":
            return Config.resource_path(MeileColors.SUBSCRIBE_BUTTON)
            
    
    def GetHealthCheck(self, address):
        try:
            Request = HTTPRequests.MakeRequest(TIMEOUT=2.7)
            http = Request.hadapter()
            r = http.get(HTTParams.HEALTH_CHECK % address)
            health_check = r.json()['result']
            print(health_check)
            if 'status' in health_check:
                if health_check['status'] != 1:
                    return "Failed"
            if "info_fetch_error" in health_check:
                return "Failed"
            elif "config_exchange_error" in health_check:
                return "Failed"
            elif "location_fetch_error" in health_check:
                return "Failed"
            else:
                return "Passed"
        except:
            return "Error"    
        
    def get_realtime_of_node(self, naddress):   
        
        Request = HTTPRequests.MakeRequest(TIMEOUT=2.7)
        http = Request.hadapter()
        endpoint = "/sentinel/nodes/" + naddress.lstrip().rstrip()
        MeileConfig = MeileGuiConfig()
        try:
            '''
            Add get from config.ini for API when settings is  merged. 
            '''
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
            API = CONFIG['network'].get('api', HTTParams.APIURL)
            r = http.get(API + endpoint)
            remote_url = r.json()['node']['remote_url']
            start = timer()
            r = http.get(remote_url + "/status", verify=False)
            end = timer()
            latency = int(round((end-start), 4)*1000)
            print(remote_url)
    
            NodeInfoJSON = r.json()
            NodeInfoDict = {}
            
            NodeInfoDict['connected_peers'] = NodeInfoJSON['result']['peers']
            NodeInfoDict['max_peers']       = NodeInfoJSON['result']['qos']['max_peers']
            NodeInfoDict['version']         = NodeInfoJSON['result']['version']
            NodeInfoDict['city']            = NodeInfoJSON['result']['location']['city']
            NodeInfoDict['latency']         = latency

        except Exception as e:
            print(str(e))
            return None


        if not self.dialog:
            self.dialog = MDDialog(
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                text='''
                    City: %s
                    Connected Peers:  %s  
                    Max Peers: %s  
                    Node Version: %s 
                    Latency: %sms
                    ''' % (NodeInfoDict['city'], 
                           NodeInfoDict['connected_peers'],
                           NodeInfoDict['max_peers'],
                           NodeInfoDict['version'],
                           NodeInfoDict['latency']),
  
                buttons=[
                    MDRaisedButton(
                        text="OKAY",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release= self.closeDialog,
                    )
                ],
            )
        self.dialog.open()
        
    @mainthread
    def subscribe_to_node(self, price, hourly_price, naddress, moniker):
        print("Running NodeCarousel.subscribe_to_node()...")
        subtype_dialog = SubTypeDialog(self,price,hourly_price,moniker, naddress)
        
        #subscribe_dialog = SubscribeContent(price, moniker , naddress )
        self.dialog = None
        self.dialog = MDDialog(
                type="custom",
                content_cls=subtype_dialog,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                )
        self.dialog.open()

    @delayable
    def subscribe(self, subscribe_dialog, *kwargs):
        sub_node = subscribe_dialog.return_deposit_text()
        spdialog = ProcessingSubDialog(sub_node[2], sub_node[1], sub_node[0] )
        deposit = self.reparse_coin_deposit(sub_node[0], sub_node[-1])
        try:
            self.dialog.dismiss()
            self.dialog = None
        except:
            mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
            mw.dialog.dismiss()
            mw.dialog = None
            
        if sub_node[-1] == "xmr":
            plan_sub = PlanRow("payg", str(1), str(1), deposit, "1.jpg", str(420), str(0), str(0))
            plan_sub.subscribe(None, payg=True, payg_dialog=subscribe_dialog, data=sub_node)
            
        else:        
            self.dialog = MDDialog(
                    title="Subscribing...",
                    type="custom",
                    content_cls=spdialog,
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                )
            self.dialog.open()
            yield 0.6
    
            CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)        
            KEYNAME = CONFIG['wallet'].get('keyname', '')
            
            hwf = HandleWalletFunctions()
            t = Thread(target=lambda: hwf.subscribe(KEYNAME, sub_node[1], deposit, sub_node[3], sub_node[4]))
            t.start()
            
            while t.is_alive():
                print(".", end="")
                sys.stdout.flush()
                yield 0.5
            try: 
                if hwf.returncode[0]:
                    self.dialog.dismiss()
                    self.dialog = MDDialog(
                        title="Successful!",
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                        buttons=[
                                MDFlatButton(
                                    text="OK",
                                    theme_text_color="Custom",
                                    text_color=Meile.app.theme_cls.primary_color,
                                    on_release=self.closeDialogReturnToSubscriptions
                                ),])
                    self.dialog.open()
        
                else:
                    self.dialog.dismiss()
                    self.dialog = MDDialog(
                    title="Error: %s" % "No wallet found!" if hwf.returncode[1] == 1337  else hwf.returncode[1],
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                            MDFlatButton(
                                text="OK",
                                theme_text_color="Custom",
                                text_color=Meile.app.theme_cls.primary_color,
                                on_release=self.closeDialog
                            ),])
                    self.dialog.open()
            except AttributeError as e:
                print(str(e))
                self.dialog.dismiss()
                self.dialog = MDDialog(
                title="Error Processing subscription",
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=Meile.app.theme_cls.primary_color,
                            on_release=self.closeDialog
                        ),])
                self.dialog.open()
                
    def reparse_coin_deposit(self, deposit, coin):
        ibcaddy = self.check_ibc_denom(coin)
        if ibcaddy == "xmr":
            print("Paying with Monero gateway")
            return deposit
        else:
            return str(deposit) + str(ibcaddy)
            
    def check_ibc_denom(self, coin):
        if coin == "xmr":
            return coin
        
        for k,val in IBCTokens.ibc_mu_coins.items():
            if k == coin:
                mu_coin = val
                
        for key,v in IBCTokens.IBCUNITTOKEN.items():
            if key == mu_coin:
                return v
    
    def switch_carousel(self):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        mw.clear_node_carousel()
        mw.carousel.remove_widget(self)
        mw.carousel.load_slide(mw.carousel.slides[-1])
        
    def closeDialogReturnToSubscriptions(self,inst):
        self.dialog.dismiss()
        self.dialog = None
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        mw.NodeTree.SubResult = []
        
        if mw.SubCaller:
            mw.switch_to_sub_window()
                
        else:
            mw.clear_node_carousel()
            
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None

#class WalletCoinRow(MDCard,RectangularElevationBehavior,ThemableBehavior, HoverBehavior):
class WalletCoinRow(MDCard,HoverBehavior):
    logo = StringProperty('')
    text = StringProperty('')
    
class RowContainer(MDBoxLayout):
    logo = StringProperty('')
    text = StringProperty('')
        
'''
Recycler of the node cards after clicking country
'''
#class RecycleViewRow(MDCard,RectangularElevationBehavior,ThemableBehavior, HoverBehavior):
class RecycleViewRow(MDCard,HoverBehavior):
    dialog = None
    node_data = ObjectProperty()
    #node_types = ObjectProperty()
    #node_scores = ObjectProperty()
    #node_formula = ObjectProperty()
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex(MeileColors.ROW_HOVER)
        Window.set_system_cursor('hand')
        
    def on_leave(self, *args):
        self.md_bg_color = get_color_from_hex(MeileColors.DIALOG_BG_COLOR)
        Window.set_system_cursor('arrow')
 
    def closeDialogReturnToSubscriptions(self,inst):
        self.dialog.dismiss()
        self.dialog = None
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW
        mw.SubResult = []
    
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None
            
    def switch_to_node_carousel(self, node_data):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        NodeWidget = NodeCarousel(name=WindowNames.NODE_CAROUSEL, node=node_data)
        mw.carousel.add_widget(NodeWidget)
        mw.carousel.load_slide(NodeWidget)

class MDMapCountryButton(MDFillRoundFlatButton, HoverBehavior):
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex("#fcb711")
        Window.set_system_cursor('arrow')
        
    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.md_bg_color = get_color_from_hex(MeileColors.BLACK)
        Window.set_system_cursor('arrow')

class LoadingSpinner(MDFloatLayout):
    angle = NumericProperty(0)
    def __init__(self, **kwargs):
        super(LoadingSpinner, self).__init__(**kwargs)
        anim = Animation(angle = 360, duration=2) 
        anim += Animation(angle = 360, duration=2)
        anim.repeat = True
        anim.start(self)
        
    def on_angle(self, item, angle):
        if angle == 360:
            item.angle = 0
            
    def get_spinner_image(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.SPINNER)
            