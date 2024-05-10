from kivy.properties import BooleanProperty, StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from kivy.clock import Clock
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
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivyoav.delayed import delayable

from functools import partial
from subprocess import Popen, TimeoutExpired
from urllib3.exceptions import InsecureRequestWarning
from copy import deepcopy
from datetime import datetime, timedelta
from os import path
from time import sleep 
from threading import Thread
import requests
import re
import psutil
import time
from requests.auth import HTTPBasicAuth
import json
import webbrowser

from typedef.konstants import IBCTokens, HTTParams, MeileColors, NodeKeys
from typedef.win import CoinsList, WindowNames
from conf.meile_config import MeileGuiConfig
from cli.wallet import HandleWalletFunctions
from cli.sentinel import NodeTreeData
from cli.btcpay import BTCPayDB
import main.main as Meile
from adapters import HTTPRequests
from ui.interfaces import TXContent, ConnectionDialog
from coin_api.get_price import GetPriceAPI
from adapters.ChangeDNS import ChangeDNS
from kivy.uix.recyclegridlayout import RecycleGridLayout
from helpers.helpers import format_byte_size
from fiat.stripe_pay import scrtsxx

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
        UUID = Meile.app.root.get_screen(WindowNames.PRELOAD).UUID
        try:
            rating_dict = {'uuid' : "%s" % UUID, 'address' : "%s" % node_address, "rating" : rating}
            Request = HTTPRequests.MakeRequest()
            http = Request.hadapter()
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
            print("You have selected bandwidth (GB)")
            print(f"{self.price}\n{self.moniker}\n{self.naddress}")
            subscribe_dialog = SubscribeContent(self.price, self.moniker, self.naddress, False)
            
        else:
            print("You have selected hourly (days)")
            print(f"{self.hourly_price}\n{self.moniker}\n{self.naddress}")
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
        self.parse_coin_deposit(CoinsList.ibc_mu_coins[0])
        
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
            background_color=get_color_from_hex(MeileColors.BLACK),
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        self.ids.drop_item.current_item = CoinsList.ibc_mu_coins[0]
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
                mu_coin_amt = re.findall(r'[0-9]+.[0-9]+' + mu_coin, self.price_text)[0]
                if mu_coin_amt:
                    if not self.hourly:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(mu_coin_amt.split(mu_coin)[0])),4)) + self.ids.drop_item.current_item
                    else: 
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*24*(float(mu_coin_amt.split(mu_coin)[0])),4)) + self.ids.drop_item.current_item
                    return self.ids.deposit.text
                else:
                    if not self.hourly:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(self.ids.price.text.split(CoinsList.ibc_mu_coins[0])[0])),4)) + self.ids.drop_item.current_item
                    else:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*24*(float(self.ids.price.text.split(CoinsList.ibc_mu_coins[0])[0])),4)) + self.ids.drop_item.current_item
                    return self.ids.deposit.text
            else:
                self.ids.deposit.text = "0.0" + CoinsList.ibc_mu_coins[0]
                return self.ids.deposit.text
        except IndexError as e:
            #print(str(e))
            try: 
                if self.ids.price.text:
                    if not self.hourly:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(self.ids.price.text.split(CoinsList.ibc_mu_coins[0])[0])),4)) + CoinsList.ibc_mu_coins[0]
                    else:
                        self.ids.deposit.text = str(round(int(self.ids.slider1.value)*24*(float(self.ids.price.text.split(CoinsList.ibc_mu_coins[0])[0])),4)) + CoinsList.ibc_mu_coins[0]
                    return self.ids.deposit.text
                else:
                    self.ids.deposit.text = "0.0" + CoinsList.ibc_mu_coins[0]
                    return self.ids.deposit.text
            except ValueError as e:
                print(str(e))
                self.ids.deposit.text = "0.0" + CoinsList.ibc_mu_coins[0]
                return self.ids.deposit.text
        
    def return_deposit_text(self):
        if not self.hourly:
            return (self.ids.deposit.text, self.naddress, self.moniker, int(self.ids.slider1.value), self.hourly)
        else:
            return (self.ids.deposit.text, self.naddress, self.moniker, int(self.ids.slider1.value)*24, self.hourly)
    
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
        match = re.match(r"([0-9]+.[0-9]+)([a-z]+)", deposit_ret[0], re.I)
        if match:
            amt, coin = match.groups()
        else:
            amt    = 0.0
            coin   = "dvpn"
        
        self.refresh_price(coin, cache=30)
        self.ids.usd_price.text = '$' + str(round(float(self.price_cache[coin]["price"]) * float(amt),3))

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
            response = self.price_api.get_usd(mu_coin)
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
            value = float(price_text.rstrip(mu_coin).strip())
        else:
            value = round(float(price_text.rstrip("dvpn").strip()) * self.price_cache["dvpn"]["price"] / self.price_cache[mu_coin]["price"], 5)

        print(f"mu_coin={mu_coin}, month={month}, value={value}, price_cache={self.price_cache}")

        self.ids.deposit.text = str(round(month * value, 5))
        return self.ids.deposit.text


    def return_deposit_text(self):
        return (self.ids.deposit.text, self.nnodes)

    def on_checkbox_active(self, pay_with: str, checkbox, value):
        if value is True:
            self.pay_with = pay_with
            
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
        return Config.resource_path(MeileColors.FONT_FACE_ARIAL)
    
class NodeDetails(MDGridLayout):
    sub_id = StringProperty()
    allocated = StringProperty()
    consumed  = StringProperty()
    deposit = StringProperty()
    score = StringProperty()
    votes = StringProperty()
    formula = StringProperty()
    node_address = StringProperty()

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
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE_ARIAL)
    
    def get_button(self, text):
        Config = MeileGuiConfig()
        if text == "info":
            return Config.resource_path(MeileColors.GETINFO_BUTTON)
        elif text == "subscribe":
            return Config.resource_path(MeileColors.SUBSCRIBE_BUTTON)
    
    def open_subscribe(self):
        
        item =  { "price": self.cost, "white_label": self.plan_name, "nnodes": self.num_of_nodes, "logo_image": self.logo_image }
        
        subscribe_dialog = PlanSubscribeContent(**item)
        if not self.dialog:
            self.dialog = MDDialog(
                    title="Subscription Plan",
                    type="custom",
                    content_cls=subscribe_dialog,
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=MeileColors.MEILE,
                            on_release=self.closeDialog
                        ),
                        MDRaisedButton(
                            text="SUBCRIBE",
                            theme_text_color="Custom",
                            text_color=MeileColors.BLACK,
                            on_release=partial(self.subscribe, subscribe_dialog)
                        ),
                    ],
                )
            self.dialog.open()
            
    @delayable
    def add_wallet_2plan(self, wallet, plan_id, duration, sub_id, uuid, amt, denom):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        plan_details = {"data": {"wallet" : wallet, "plan_id" : plan_id, "duration" : duration, "sub_id" : sub_id, "uuid" : uuid, "amt" : amt, "denom" : denom}}
        print(plan_details)
        SERVER_ADDRESS = scrtsxx.MEILE_PLAN_API
        API            = scrtsxx.MEILE_PLAN_ADD
        USERNAME       = scrtsxx.PLANUSERNAME
        PASSWORD       = scrtsxx.PLANPASSWORD
        Request = HTTPRequests.MakeRequest()
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
    def subscribe(self, subscribe_dialog, *kwargs):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)

        deposit = subscribe_dialog.ids.deposit.text
        nnodes = subscribe_dialog.nnodes
        mu_coin = subscribe_dialog.ids.drop_item.current_item

        # Parse all the coins without u-unit
        if mu_coin.startswith("u"):
            mu_coin = mu_coin.lstrip('u')

        # use the price caching directly from subscribe_dialog
        usd = round(float(deposit) * subscribe_dialog.price_cache[mu_coin]["price"], 5)

        print(f"Deposit {deposit} {mu_coin} for {nnodes} nodes. usd value is: {usd}")
        # usd value must be multiplu for nnodes (?)

        # sub_node = subscribe_dialog.return_deposit_text()
        # deposit = self.reparse_coin_deposit(sub_node[0])

        # Declare method here so we can pass it as callback variable to methods
        def on_success_subscription():
            self.add_wallet_2plan(
                wallet=mw.address,
                plan_id=self.plan_id,
                duration=subscribe_dialog.ids.slider1.value,
                sub_id=self.id,
                uuid=self.uuid,
                amt=int(float(deposit) * IBCTokens.SATOSHI),
                denom=mu_coin
            )

        if subscribe_dialog.pay_with == "wallet":
            self.pay_meile_plan_with_wallet(deposit, mu_coin, usd, on_success_subscription)
        elif subscribe_dialog.pay_with == "btcpay":
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(
                    title="Waiting for invoice to be paid...",

                )
            self.dialog.open()
            yield 0.6
            invoice_result = self.pay_meile_plan_with_btcpay(usd)
            if invoice_result['success']:
                self.dialog.dismiss()
                self.dialog = None
                self.dialog = MDDialog(
                        title=f"Invoice {invoice_result['id']} has been marked as paid! Finishing up...",
                    )
                self.dialog.open()
                yield 0.6

                on_success_subscription()

                # self.add_wallet_2plan(
                #     wallet= mw.address,
                #     plan_id= self.plan_id,
                #     duration= subscribe_dialog.ids.slider1.value,
                #     sub_id= self.id,
                #     uuid= self.uuid,
                #     amt= int(float(deposit) * IBCTokens.SATOSHI),
                #     denom= mu_coin
                # )
        elif subscribe_dialog.pay_with == "pirate":
            self.pay_meile_plan_with_pirate(usd)
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
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
            )
        self.dialog.open()
        yield 0.6

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        hwf = HandleWalletFunctions()
        result, output = hwf.send_2plan_wallet(KEYNAME, self.plan_id, mu_coin, deposit)
        print("result", result)
        print("output", output)

        if result is True:
            if self.dialog:
                self.dialog.dismiss()
            self.dialog = None
            self.dialog = MDDialog(title=output["message"] + " Finishing up...",)
            self.dialog.open()
            yield 0.6
            on_success()
        else:
            if self.dialog:
                self.dialog.dismiss()

            self.dialog = MDDialog(
                title = ("Success" if output["success"] else "Failed") if isinstance(output, dict) else ("Error: %s" % "No wallet found!" if output == 1337 else output),
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
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
            client = BTCPay.unpickle_btc_client(pickled_client_data)
        else:
            return (False, "No pickeled client data")
            
        buyer = {"name" : mw.address, "email" : "freqnik@mathnodes.com", "notify" : True}
        
        new_invoice = client.create_invoice({"price": usd,
                                          "currency": "USD",
                                          "token" : "XMR",
                                          "merchantName" : "Meile dVPN",
                                          "itemDesc" : "MathNodes Subscription Plan",
                                          "notificationEmail" : scrtsxx.BTCPayEmail,
                                          "transactionSpeed" : "high",
                                          "buyer" : buyer})
        
        print(new_invoice)
        print(new_invoice['url'])
        btcpay_tx_id = new_invoice['id']
        
        webbrowser.open(new_invoice['url'])
        fetched_invoice = client.get_invoice(btcpay_tx_id)
        
        while fetched_invoice['status'] != "confirmed":
            fetched_invoice = client.get_invoice(btcpay_tx_id)
            print("invoice not yet confirmed....")
            sleep(10)

        # TODO: relay back to main thread invoice paid            
        print("invoice paid!")
        return {"success" : True, "id": new_invoice['id'] }

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

class PlanDetails(MDGridLayout):
    uuid = StringProperty()
    id = StringProperty()
    expires  = StringProperty()
    deposit = StringProperty()
    coin = StringProperty()
    
    def filter_nodes(self):
        from fiat.stripe_pay import scrtsxx
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

    def on_close(self, *args):
        """Called when a panel is closed."""

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
        
        gbprices = node[NodeKeys.NodesInfoKeys[2]].split(',')
        hrprices = node[NodeKeys.NodesInfoKeys[3]].split(',')
        
        g = gbprices[0]
        self.gb_prices = deepcopy(g)
        
        k=0
        for g in gbprices:
            if k == 0:
                k +=1
                continue
            self.gb_prices = '\n'.join([self.gb_prices,g])
            
        h = hrprices[0]
        self.hr_prices = deepcopy(h)
        
        k=0
        for h in hrprices:
            if k == 0:
                k +=1
                continue
            self.hr_prices = '\n'.join([self.hr_prices,h])
            
        
        self.moniker         = node[NodeKeys.NodesInfoKeys[0]]
        self.address         = node[NodeKeys.NodesInfoKeys[1]]
        #self.gb_prices       = node[NodeKeys.NodesInfoKeys[2]]
        #self.hr_prices       = node[NodeKeys.NodesInfoKeys[3]]
        self.download        = format_byte_size(node[NodeKeys.NodesInfoKeys[8]])+ "/s"
        self.upload          = format_byte_size(node[NodeKeys.NodesInfoKeys[9]])+ "/s"
        self.connected_peers = str(node[NodeKeys.NodesInfoKeys[10]])
        self.max_peers       = str(node[NodeKeys.NodesInfoKeys[11]])
        self.protocol        = node[NodeKeys.NodesInfoKeys[13]]
        self.version         = node[NodeKeys.NodesInfoKeys[14]]
        self.handshake       = str(node[NodeKeys.NodesInfoKeys[12]])
        self.health_check    = self.GetHealthCheck(node[NodeKeys.NodesInfoKeys[1]])
        self.isp_type        = node[NodeKeys.NodesInfoKeys[15]]
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
        return Config.resource_path(MeileColors.FONT_FACE_ARIAL)
    
    def get_button(self, text):
        Config = MeileGuiConfig()
        if text == "info":
            return Config.resource_path(MeileColors.GETINFO_BUTTON)
        elif text == "subscribe":
            return Config.resource_path(MeileColors.SUBSCRIBE_BUTTON)
            
    
    def GetHealthCheck(self, address):
        Request = HTTPRequests.MakeRequest(TIMEOUT=2.3)
        http = Request.hadapter()
        r = http.get(HTTParams.HEALTH_CHECK % address)
        health_check = r.json()
        print(health_check)
        if 'status' in health_check:
            if health_check['status'] != 1:
                return "Failed"
        elif "info_fetch_error " in health_check:
            return "Failed"
        elif "config_exchange_error" in health_check:
            return "Failed"
        elif "location_fetch_error" in health_check:
            return "Failed"
        else:
            return "Passed"
        
    def subscribe_to_node(self, price, hourly_price, naddress, moniker):
        subtype_dialog = SubTypeDialog(self,price,hourly_price,moniker, naddress)
        
        #subscribe_dialog = SubscribeContent(price, moniker , naddress )
        if not self.dialog:
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
        deposit = self.reparse_coin_deposit(sub_node[0])
        self.dialog.dismiss()
        self.dialog = None
        self.dialog = MDDialog(
                title="Subscribing...",
                type="custom",
                content_cls=spdialog,
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
            )
        self.dialog.open()
        yield 0.6

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)        
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        
        hwf = HandleWalletFunctions()
        returncode = hwf.subscribe(KEYNAME, sub_node[1], deposit, sub_node[3], sub_node[4])
        
        if returncode[0]:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Successful!",
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
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
            title="Error: %s" % "No wallet found!" if returncode[1] == 1337  else returncode[1],
            md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
            buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.closeDialog
                    ),])
            self.dialog.open()     
    
    def switch_carousel(self):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        mw.carousel.remove_widget(self)
        mw.carousel.load_slide(mw.NodeWidget)
        
    def closeDialogReturnToSubscriptions(self,inst):
        self.dialog.dismiss()
        self.dialog = None
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        mw.SubResult = None
    
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None
        
'''
Recycler of the node cards after clicking country
'''
class RecycleViewRow(MDCard,RectangularElevationBehavior,ThemableBehavior, HoverBehavior):
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
        
    def get_city_of_node(self, naddress):   
        
        Request = HTTPRequests.MakeRequest(TIMEOUT=2.3)
        http = Request.hadapter()
        endpoint = "/sentinel/nodes/" + naddress.lstrip().rstrip()
        try:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            r = http.get(HTTParams.APIURL + endpoint)
            remote_url = r.json()['node']['remote_url']
            r = http.get(remote_url + "/status", verify=False)
            print(remote_url)
    
            NodeInfoJSON = r.json()
            NodeInfoDict = {}
            
            NodeInfoDict['connected_peers'] = NodeInfoJSON['result']['peers']
            NodeInfoDict['max_peers']       = NodeInfoJSON['result']['qos']['max_peers']
            NodeInfoDict['version']         = NodeInfoJSON['result']['version']
            NodeInfoDict['city']            = NodeInfoJSON['result']['location']['city']

        except Exception as e:
            print(str(e))
            return None


        if not self.dialog:
            self.dialog = MDDialog(
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                text='''
City: %s
Connected Peers:  %s  
Max Peers: %s  
Node Version: %s 
                    ''' % (NodeInfoDict['city'], NodeInfoDict['connected_peers'],NodeInfoDict['max_peers'],NodeInfoDict['version']),
  
                buttons=[
                    MDRaisedButton(
                        text="OKAY",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.closeDialog,
                    )
                ],
            )
        self.dialog.open()
    '''    
    def subscribe_to_node(self, price, hourly_price, naddress, moniker):
        subtype_dialog = SubTypeDialog(self,price,hourly_price,moniker, naddress)
        
        #subscribe_dialog = SubscribeContent(price, moniker , naddress )
        if not self.dialog:
            self.dialog = MDDialog(
                    type="custom",
                    content_cls=subtype_dialog,
                    md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    )
            self.dialog.open()

    @delayable
    def subscribe(self, subscribe_dialog, *kwargs):
        sub_node = subscribe_dialog.return_deposit_text()
        spdialog = ProcessingSubDialog(sub_node[2], sub_node[1], sub_node[0] )
        deposit = self.reparse_coin_deposit(sub_node[0])
        self.dialog.dismiss()
        self.dialog = None
        self.dialog = MDDialog(
                title="Subscribing...",
                type="custom",
                content_cls=spdialog,
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
            )
        self.dialog.open()
        yield 0.6

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)        
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        
        hwf = HandleWalletFunctions()
        returncode = hwf.subscribe(KEYNAME, sub_node[1], deposit, sub_node[3], sub_node[4])
        
        if returncode[0]:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Successful!",
                md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.closeDialogReturnToSubscriptions
                        ),])
            self.dialog.open()

        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
            title="Error: %s" % "No wallet found!" if returncode[1] == 1337  else returncode[1],
            md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
            buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.closeDialog
                    ),])
            self.dialog.open()

    '''
    def reparse_coin_deposit(self, deposit):
        
        for k,v in CoinsList.ibc_coins.items():
            try: 
                coin = re.findall(k,deposit)[0]
                #print(coin)
                deposit = deposit.replace(coin, v)
                #print(deposit)
                mu_deposit_amt = int(float(re.findall(r'[0-9]+\.[0-9]+', deposit)[0])*CoinsList.SATOSHI)
                #print(mu_deposit_amt)
                tru_mu_deposit = str(mu_deposit_amt) + v
                #print(tru_mu_deposit)
                tru_mu_ibc_deposit = self.check_ibc_denom(tru_mu_deposit)
                #print(tru_mu_ibc_deposit)
                return tru_mu_ibc_deposit
            except:
                pass
            
    def check_ibc_denom(self, tru_mu_deposit):
        for ibc_coin in IBCTokens.IBCCOINS:
            k = ibc_coin.keys()
            v = ibc_coin.values()
            for coin,ibc in zip(k,v):
                print(coin)
                print(ibc)
                if coin in tru_mu_deposit:
                    tru_mu_deposit = tru_mu_deposit.replace(coin, ibc)
                    print(tru_mu_deposit)
        return tru_mu_deposit
    
    def closeDialogReturnToSubscriptions(self,inst):
        self.dialog.dismiss()
        self.dialog = None
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW
        mw.SubResult = None
    
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
     
class RecycleViewSubRow(MDCard,RectangularElevationBehavior):
    text = StringProperty()
    dialog = None
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
        
    def get_data_used(self, allocated, consumed, node_address, expirary_date):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        try:
            ''' Since this function is called when opening the Subscription tab,
                we need to do a little house keeping for the card switches and the
                data consumed
            '''         
            if mw.NodeSwitch['node'] == node_address:
                self.ids.node_switch.active = True
            else:
                self.ids.node_switch.active = False
            
            if not mw.clock and mw.NodeSwitch['id']:
                print("Not clock()")
                self.setQuotaClock(mw.NodeSwitch['id'],
                                   mw.NodeSwitch['node'])
            
            #End house keeping
            
            if "hrs" in allocated:
                allocated = int(allocated.split('hrs')[0].rstrip().lstrip())
                consumed  = float(consumed.split('hrs')[0].rstrip().lstrip())
                #consumed  = self.compute_consumed_hours(allocated, expirary_date)
            else:
                allocated = self.compute_consumed_data(allocated)
                consumed  = self.compute_consumed_data(consumed)
            
            if allocated == 0:
                self.ids.consumed_data.text = "0%"
                return 0
            
            self.ids.consumed_data.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
            return round(float(float(consumed/allocated)*100),3)
        except Exception as e:
            print(str(e))
            return float(50)
       
    def compute_consumed_hours(self, allocated, expirary_date):
        
        allocated       = allocated.split('hrs')[0].rstrip().lstrip()
        now             = datetime.now()
        expirary_date   = datetime.strptime(expirary_date,'%b %d %Y, %I:%M %p')
        sub_date        = expirary_date - timedelta(hours=float(allocated))
        subdelta        = now - sub_date
        remaining_hours = round(float(subdelta.total_seconds())/3600,3)
        consumed        = float(float(allocated) - remaining_hours)
        if consumed < 0:
            consumed = 0
        return round(float(subdelta.total_seconds())/3600,3)
    
        
        
    def compute_consumed_data(self, consumed):
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
        
        return consumed
    
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(title=title_text,md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR))
        self.dialog.open()
        
    def set_conn_dialog(self, cd, title):
        self.dialog = None
        self.dialog = MDDialog(
                        title=title,
                        type="custom",
                        content_cls=cd,
                        md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    )
        self.dialog.open() 
        
    def remove_loading_widget(self):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None

    def closeDialog(self, dt):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None
            
    def unsubscribe_to_node(self, subId):

        if not self.dialog:
            self.dialog = MDDialog(
                    title="Unsubscribe from ID: %s?" % subId,
                    md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.closeDialog
                        ),
                        MDRaisedButton(
                            text="UNSUBSCRIBE",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex("#000000"),
                            on_release=partial(self.unsubscribe, subId)
                        ),
                    ],
                )
            self.dialog.open()

    @delayable        
    def unsubscribe(self, subId, *kwargs):

        yield 0.3
        self.remove_loading_widget()
        yield 0.6
        self.add_loading_popup("Unsubscribing to subscription id: %s" % subId)
        yield 0.6
        sleep(1)

        Wallet = HandleWalletFunctions()
        unsub_value = Wallet.unsubscribe(int(subId))

        self.remove_loading_widget()

        TXDialog = TXContent()

        TXDialog.ids.message.text = unsub_value['message']
        TXDialog.ids.txhash.text  = unsub_value['hash']

        yield 0.3
        if not self.dialog:
            self.dialog = MDDialog(
                    title="Unsub Details",
                    type="custom",
                    content_cls=TXDialog,
                    md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    buttons=[
                        MDFlatButton(
                            text="OKAY",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.closeDialog
                        ),
                    ],
                )
            self.dialog.open()
            
    def ping(self):
        UUID = Meile.app.root.get_screen(WindowNames.PRELOAD).UUID
        try:
            uuid_dict = {'uuid' : "%s" % UUID, 'os' : "W"}
            Request = HTTPRequests.MakeRequest(TIMEOUT=3)
            http = Request.hadapter()
            ping = http.post(HTTParams.SERVER_URL + HTTParams.API_PING_ENDPOINT, json=uuid_dict)
            if ping.status_code == 200:
                print('ping')
            else:
                print("noping")
        except Exception as e:
            print(str(e))
            pass
        
    @delayable
    def connect_to_node(self, ID, naddress, moniker, type, switchValue, **kwargs):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        '''
           These two conditionals are needed to check
           and verify the switch in the sub card and ensure
           it is on, when connected, and does not try to disconnect
           or reconnect. 
        '''
        if mw.NodeSwitch['switch'] and naddress == mw.NodeSwitch['node'] and not switchValue:
            print("DISCONNECTING!!!")
            try:
                mw.clock.cancel()
                mw.clock = None
            except Exception as e:
                print(str(e))
            if mw.disconnect_from_node():
                self.connected_quota(None, None, None)
            return True
        
        if mw.CONNECTED:
            return 
        
        if switchValue:
            cd = ConnectionDialog()
            self.set_conn_dialog(cd, "Connecting...")
            yield 0.3
            
            hwf = HandleWalletFunctions()
            thread = Thread(target=lambda: self.ping())
            thread.start()
            t = Thread(target=lambda: hwf.connect(ID, naddress, type))
            t.start()

            while t.is_alive():
                yield 0.0365
                if "WireGuard" not in type:
                    cd.ids.pb.value += 0.001
                else:
                    cd.ids.pb.value += 0.00175

            cd.ids.pb.value = 1
               
            mw.ConnectedDict = deepcopy(hwf.connected)
            yield 0.420
            
            try:
                
                if hwf.connected['result']:
                    
                    mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
                    mw.CONNECTED                  = True
                    mw.NodeSwitch['moniker']      = moniker
                    mw.NodeSwitch['node']         = naddress
                    mw.NodeSwitch['switch']       = True
                    mw.NodeSwitch['id']           = ID
                    mw.NodeSwitch['allocated']    = self.allocated_text
                    mw.NodeSwitch['consumed']     = self.consumed_text
                    mw.NodeSwitch['og_consumed']  = deepcopy(self.consumed_text) 
                    mw.NodeSwitch['expirary']     = self.expirary_date
                    
                    # Determine if node has been connected to and if so report last data usage stats
                    # otherwise start a fresh count
                    if not ID in mw.PersistentBandwidth:
                        mw.PersistentBandwidth[ID] = mw.NodeSwitch
                    else:
                        mw.PersistentBandwidth[ID]['og_consumed'] = deepcopy(mw.PersistentBandwidth[ID]['consumed'])
                    
                    # Check if subscription is hourly
                    if "hrs" in self.allocated_text:
                        self.setQuotaClock(ID, naddress, True)
                    else:
                        self.setQuotaClock(ID, naddress, False)
    
                    self.remove_loading_widget()
                    self.dialog = MDDialog(
                        title="Connected!",
                        md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                        buttons=[
                                MDFlatButton(
                                    text="OK",
                                    theme_text_color="Custom",
                                    text_color=self.theme_cls.primary_color,
                                    on_release=partial(self.call_ip_get, True, moniker)
                                ),])
                    self.dialog.open()
                    
                else:
                    self.remove_loading_widget()
                    self.dialog = MDDialog(
                        title="Something went wrong. Not connected: %s" % hwf.connected['status'],
                        md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                        buttons=[
                                MDFlatButton(
                                    text="OK",
                                    theme_text_color="Custom",
                                    text_color=self.theme_cls.primary_color,
                                    on_release=partial(self.call_ip_get, False, "")
                                ),])
                    self.dialog.open()
                    
            except (TypeError, KeyError) as e:
                print(str(e))
                self.remove_loading_widget()
                self.dialog = MDDialog(
                    title="Something went wrong. Not connected: User cancelled",
                    md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    buttons=[
                            MDFlatButton(
                                text="OK",
                                theme_text_color="Custom",
                                text_color=self.theme_cls.primary_color,
                                on_release=partial(self.call_ip_get, False, "")
                            ),])
                self.dialog.open()
                
    def connected_quota(self, allocated, consumed, dt):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)        
        if mw.CONNECTED:
            #allocated = float(allocated.replace('GB',''))
            if "hrs" in allocated:
                allocated_str         = deepcopy(allocated)
                allocated             = float(allocated.split('hrs')[0].rstrip().lstrip())
                consumed              = self.compute_consumed_hours(allocated_str,mw.NodeSwitch['expirary'])
                mw.quota_pct.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
                mw.quota.value    = round(float(float(consumed/allocated)*100),2)
                try: 
                    mw.clock()
                except Exception as e:
                    print("Error running clock()")
                    return False 
            else:
                allocated = self.compute_consumed_data(allocated)
                consumed  = self.compute_consumed_data(consumed)
                mw.quota_pct.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
                return round(float(float(consumed/allocated)*100),3)
        else:
            mw.quota_pct.text = "0.00%"
            mw.quota.value    = 0
            return float(0)
        
            
    def setQuotaClock(self,ID, naddress, hourly):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
        if hourly:
            self.connected_quota(mw.PersistentBandwidth[ID]['allocated'],
                                 mw.PersistentBandwidth[ID]['consumed'],
                                 None)
            
            mw.clock = Clock.create_trigger(partial(self.connected_quota,
                                                    mw.PersistentBandwidth[ID]['allocated'],
                                                    mw.PersistentBandwidth[ID]['consumed']),120)
            mw.clock()
            return True
        
        BytesDict = self.init_GetConsumedWhileConnected(mw.PersistentBandwidth[ID]['og_consumed'])
        print(BytesDict)
        self.UpdateQuotaForNode(mw.NodeSwitch['id'],
                                mw.NodeSwitch['node'],
                                BytesDict,
                                None)
        
        mw.clock = Clock.create_trigger(partial(self.UpdateQuotaForNode,
                                                  mw.NodeSwitch['id'],
                                                  mw.NodeSwitch['node'],
                                                  BytesDict),120)

        mw.clock()
        
    def UpdateQuotaForNode(self, ID, naddress, BytesDict, dt):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        try:
            print("%s: Getting Quota: " % ID, end= ' ')
            startConsumption = mw.PersistentBandwidth[ID]['og_consumed']
            mw.PersistentBandwidth[ID]['consumed'] = self.GetConsumedWhileConnected(self.compute_consumed_data(startConsumption),BytesDict)
            
            mw.quota.value = self.connected_quota(mw.PersistentBandwidth[ID]['allocated'],
                                                      mw.PersistentBandwidth[ID]['consumed'],
                                                      None)
            print("%s,%s - %s%%" % (mw.PersistentBandwidth[ID]['consumed'],
                                  startConsumption,
                                  mw.quota.value))
        except Exception as e:
            print("Error getting bandwidth!")
            
        try: 
            mw.clock()
        except Exception as e:
            print("Error running clock()")
            pass 
        
    def init_GetConsumedWhileConnected(self, sConsumed):
        try: 
            bytes_sent = round(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_sent) / 1073741824),3)
            bytes_recvd = round(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_recv) / 1073741824),3)
            
            return {'sent' : bytes_sent, "rcvd" : bytes_recvd}
        except KeyError:
            for iface in psutil.net_if_addrs().keys():
                if "tun" in iface:
                    IFACE = iface
                    print(IFACE)
                    break
            try:     
                bytes_sent = round(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_sent) / 1073741824),3)
                bytes_recvd = round(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_recv) / 1073741824),3)
                
                return {'sent' : bytes_sent, "rcvd" : bytes_recvd}
            except Exception as e:
                print(str(e))
                return {'sent': 0, 'rcvd' : 0}
            
        
    def GetConsumedWhileConnected(self, sConsumed, Bytes):
        try: 
            bytes_sent = round(float(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_sent) / 1073741824) - Bytes['sent']),3) 
            bytes_recvd = round(float(float(float(psutil.net_io_counters(pernic=True)['wg99'].bytes_recv) / 1073741824) - Bytes['rcvd']),3)  
            
            total_data = str(round(float(bytes_sent + bytes_recvd)+ float(sConsumed),3)) + "GB"
        except KeyError:
            for iface in psutil.net_if_addrs().keys():
                if "tun" in iface:
                    IFACE = iface
                    break
                
            try: 
                bytes_sent = round(float(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_sent) / 1073741824) - Bytes['sent']),3) 
                bytes_recvd = round(float(float(float(psutil.net_io_counters(pernic=True)[IFACE].bytes_recv) / 1073741824) - Bytes['rcvd']),3)  
            
                total_data = str(round(float(bytes_sent + bytes_recvd)+ float(sConsumed),3)) + "GB"
            except Exception as e:
                print(str(e))
                total_data = "0GB"
                
        print("Total Data: %s" % total_data, end=' ')
        return total_data    
                
    def call_ip_get(self,result, moniker,  *kwargs):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        if result:
            mw.CONNECTED = True
            mw.set_protected_icon(True, moniker)
        else:
            mw.CONNECTED = False
            self.ids.node_switch.active = False
            
        if not mw.get_ip_address(None):
            self.remove_loading_widget()
            self.change_dns()
            mw.close_sub_window()
            mw.zoom_country_map()
        else:
            self.remove_loading_widget()
            mw.close_sub_window()
            mw.zoom_country_map()
            
    @delayable        
    def change_dns(self):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
        yield 0.6
        if self.dialog:
            self.dialog.dismiss()
        self.add_loading_popup("DNS Resolver error... Switching to Cloudflare")
        yield 2.6
        
        ChangeDNS(dns="1.1.1.1").change_dns()

        yield 1.2
        mw.get_ip_address(None)
        self.remove_loading_widget()
        
class MDMapCountryButton(MDFillRoundFlatButton,ThemableBehavior, HoverBehavior):
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex("#fcb711")
        Window.set_system_cursor('arrow')
        
    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.md_bg_color = get_color_from_hex(MeileColors.DIALOG_BG_COLOR)
        Window.set_system_cursor('arrow')
            