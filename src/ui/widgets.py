from kivy.properties import BooleanProperty, StringProperty
from kivy.metrics import dp
from kivyoav.delayed import delayable
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.theming import ThemableBehavior

import requests
import re
import psutil
from functools import partial
from urllib3.exceptions import InsecureRequestWarning
from os import path
from subprocess import Popen, TimeoutExpired

from typedef.konstants import IBCTokens, HTTParams, MeileColors
from typedef.win import CoinsList, WindowNames
from conf.meile_config import MeileGuiConfig
from cli.wallet import HandleWalletFunctions
from cli.sentinel import NodeTreeData
import main.main as Meile
from adapters import HTTPRequests

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
    
    
    
class SubscribeContent(BoxLayout):
    
    
    price_text = StringProperty()
    moniker = StringProperty()
    naddress = StringProperty()
    coin_price = "0.00"

    
    menu = None
    def __init__ (self, price, moniker, naddress):
        super(SubscribeContent, self).__init__()
        
        self.price_text = price
        self.moniker = moniker
        self.naddress = naddress
        self.parse_coin_deposit("dvpn")
        
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
            background_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        self.ids.drop_item.current_item = CoinsList.ibc_mu_coins[0]
        self.parse_coin_deposit(self.ids.drop_item.current_item)

    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.ids.deposit.text = self.parse_coin_deposit(text_item)
        self.menu.dismiss()
        
    def parse_coin_deposit(self, mu_coin):
        try:
            if self.price_text:
                mu_coin_amt = re.findall(r'[0-9]+.[0-9]+' + mu_coin, self.price_text)[0]
                if mu_coin_amt:
                    self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(mu_coin_amt.split(mu_coin)[0])),4)) + self.ids.drop_item.current_item.replace('u','') 
                    return self.ids.deposit.text
                else:
                    self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(self.ids.price.text.split("dvpn")[0])),4)) + self.ids.drop_item.current_item.replace('u','')
                    return self.ids.deposit.text
            else:
                self.ids.deposit.text = "0.0dvpn"
                return self.ids.deposit.text
        except IndexError as e:
            print(str(e))
            try: 
                if self.ids.price.text:
                    self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(self.ids.price.text.split("dvpn")[0])),4)) + CoinsList.ibc_mu_coins[0].replace('u','')
                    return self.ids.deposit.text
                else:
                    self.ids.deposit.text = "0.0dvpn"
                    return self.ids.deposit.text
            except ValueError as e:
                print(str(e))
                self.ids.deposit.text = "0.0dvpn"
                return self.ids.deposit.text
        
        

    def return_deposit_text(self):
        return (self.ids.deposit.text, self.naddress, self.moniker)
    
    # Should be async
    def get_usd(self):
        depost_ret = self.return_deposit_text()
        amt = re.findall(r"[0-9]+.[0-9]+",depost_ret[0])[0]
        coin = self.ids.drop_item.current_item

        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        if coin == "dec":
            URL = "https://ascendex.com/api/pro/v1/spot/ticker?symbol=DEC/USDT"
            try: 
                r = http.get(URL)
                print(r.json())
                self.coin_price = r.json()['data']['high']
            except:
                self.coin_price = 0.0
        else:
            URL = "https://api.coinstats.app/public/v1/tickers?exchange=KuCoin&pair=%s-USDT" % coin.upper()
            try: 
                r = http.get(URL)
                print(r.json())
                self.coin_price = r.json()['tickers'][0]['price']
            except:
                self.coin_price = 0.0

            
        self.ids.usd_price.text = '$' + str(round(float(self.coin_price) * float(amt),3))

        return True

    def CGCallback(self, cgid, dt):
        cg = CoinGeckoAPI()
        cg_price = cg.get_price(ids=[cgid], vs_currencies='usd')
        self.coin_price = cg_price[cgid]['usd']


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

class OnHoverMDRaisedButton(MDRaisedButton, HoverBehavior):
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex("#fad783")
        Window.set_system_cursor('arrow')
        
    def on_leave(self, *args):
        '''The method will be called when the mouse cursor goes beyond
        the borders of the current widget.'''

        self.md_bg_color = get_color_from_hex("#fcb711")
        Window.set_system_cursor('arrow')

class RecycleViewRow(MDCard,RectangularElevationBehavior,ThemableBehavior, HoverBehavior):
    text = StringProperty()    
    dialog = None
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex("#200c3a")
        Window.set_system_cursor('hand')
        
    def on_leave(self, *args):
        self.md_bg_color = get_color_from_hex(MeileColors.DIALOG_BG_COLOR)
        Window.set_system_cursor('arrow')
        
    def get_city_of_node(self, naddress):   
        
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        endpoint = "/nodes/" + naddress.lstrip().rstrip()
        try:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            r = http.get(HTTParams.APIURL + endpoint)
            remote_url = r.json()['result']['node']['remote_url']
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

    def subscribe_to_node(self, price, naddress, moniker):
        subscribe_dialog = SubscribeContent(price, moniker , naddress )
        if not self.dialog:
            self.dialog = MDDialog(
                    title="Node:",
                    type="custom",
                    content_cls=subscribe_dialog,
                    md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.closeDialog
                        ),
                        MDRaisedButton(
                            text="SUBSCRIBE",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex("#000000"),
                            on_release=partial(self.subscribe, subscribe_dialog)
                        ),
                    ],
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
        
        returncode = HandleWalletFunctions.subscribe(HandleWalletFunctions, KEYNAME, sub_node[1], deposit)
        
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

    
    def reparse_coin_deposit(self, deposit):
        
        for k,v in CoinsList.ibc_coins.items():
            try: 
                coin = re.findall(k,deposit)[0]
                print(coin)
                deposit = deposit.replace(coin, v)
                print(deposit)
                mu_deposit_amt = int(float(re.findall(r'[0-9]+\.[0-9]+', deposit)[0])*CoinsList.SATOSHI)
                print(mu_deposit_amt)
                tru_mu_deposit = str(mu_deposit_amt) + v
                print(tru_mu_deposit)
                tru_mu_ibc_deposit = self.check_ibc_denom(tru_mu_deposit)
                print(tru_mu_ibc_deposit)
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
        #Change this to switch_tab by ids
        mw.ids.android_tabs.switch_tab("Subscriptions")
    
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            self.dialog = None
     
class RecycleViewSubRow(MDCard,RectangularElevationBehavior):
    text = StringProperty()
    dialog = None
    
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
        
    def get_data_used(self, allocated, consumed, node_address):
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
            
            allocated = self.compute_consumed_data(allocated)
            consumed = self.compute_consumed_data(consumed)
            
            if allocated == 0:
                self.ids.consumed_data.text = "0%"
                return 0
            
            self.ids.consumed_data.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
            return round(float(float(consumed/allocated)*100),3)
        except Exception as e:
            print(str(e))
            return float(50)
        
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
        
    def remove_loading_widget(self):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            return
        
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
                self.connected_quota(None, None)
            return True
        
        if mw.CONNECTED:
            return 
        
        if switchValue:
            self.add_loading_popup("Connecting...")
            
            yield 0.6
            UUID = Meile.app.root.get_screen(WindowNames.PRELOAD).UUID
            try:
                uuid_dict = {'uuid' : "%s" % UUID, 'os' : "L"}
                Request = HTTPRequests.MakeRequest()
                http = Request.hadapter()
                ping = http.post(HTTParams.SERVER_URL + HTTParams.API_PING_ENDPOINT, json=uuid_dict)
                if ping.status_code == 200:
                    print('ping')
                else:
                    print("noping")
            except Exception as e:
                print(str(e))
                pass
            
            from copy import deepcopy
            connected = HandleWalletFunctions.connect(HandleWalletFunctions, ID, naddress, type)
            mw.ConnectedDict = deepcopy(connected)
            
            if connected['result']:
                
                mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
                mw.CONNECTED               = True
                mw.NodeSwitch['moniker']   = moniker
                mw.NodeSwitch['node']      = naddress
                mw.NodeSwitch['switch']    = True
                mw.NodeSwitch['id']        = ID
                mw.NodeSwitch['allocated'] = self.allocated_text
                mw.NodeSwitch['consumed']  = self.consumed_text
                #mw.NodeSwitch['og_consumed']  = deepcopy(mw.NodeSwitch['consumed']) 
                mw.NodeSwitch['og_consumed']  = deepcopy(self.consumed_text) 
                
                if not ID in mw.PersistentBandwidth:
                    mw.PersistentBandwidth[ID] = mw.NodeSwitch
                else:
                    mw.PersistentBandwidth[ID]['og_consumed'] = deepcopy(mw.PersistentBandwidth[ID]['consumed'])
                
                
                self.setQuotaClock(ID, naddress)

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
                    title="Something went wrong. Not connected",
                    md_bg_color=get_color_from_hex(MeileColors.DIALOG_BG_COLOR),
                    buttons=[
                            MDFlatButton(
                                text="OK",
                                theme_text_color="Custom",
                                text_color=self.theme_cls.primary_color,
                                on_release=partial(self.call_ip_get, False, "")
                            ),])
                self.dialog.open()
                
    def connected_quota(self, allocated, consumed):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)        
        if mw.CONNECTED:
            #allocated = float(allocated.replace('GB',''))
            allocated = self.compute_consumed_data(allocated)
            consumed  = self.compute_consumed_data(consumed)
            mw.ids.quota_pct.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
            return round(float(float(consumed/allocated)*100),3)
        else:
            mw.ids.quota_pct.text = "0.00%"
            mw.ids.quota.value    = 0
            return float(0)
        
            
    def setQuotaClock(self,ID, naddress):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
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
            
            mw.ids.quota.value = self.connected_quota(mw.PersistentBandwidth[ID]['allocated'],
                                                      mw.PersistentBandwidth[ID]['consumed'])
            print("%s,%s - %s%%" % (mw.PersistentBandwidth[ID]['consumed'],
                                  startConsumption,
                                  mw.ids.quota.value))
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
        else:
            self.remove_loading_widget()
            
    @delayable        
    def change_dns(self):
        MeileConfig = MeileGuiConfig()
        RESOLVFILE = path.join(MeileConfig.BASEDIR, "dns")
        DNSFILE = open(RESOLVFILE, 'w')
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
        DNSFILE.write('nameserver 1.1.1.1')
        DNSFILE.flush()
        DNSFILE.close()
        
        yield 0.6
        if self.dialog:
            self.dialog.dismiss()
        self.add_loading_popup("DNS Resolver error... Switching to Cloudflare")
        yield 2.6

        dnsCMD = "pkexec bash -c 'cat %s | resolvconf -a wg99 && resolvconf -u'" % RESOLVFILE

        try: 
            dnsPROC = Popen(dnsCMD, shell=True)
            dnsPROC.wait(timeout=60)
        except TimeoutExpired as e:
            print(str(e))
            pass
        
        proc_out,proc_err = dnsPROC.communicate()
            

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
            