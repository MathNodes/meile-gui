from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineIconListItem
from kivy.metrics import dp
from kivyoav.delayed import delayable
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.utils import get_color_from_hex

from functools import partial
from urllib3.exceptions import InsecureRequestWarning
import requests
import re


from cli.sentinel import IBCCOINS
#from ui.interfaces import SubscribeContent
from typedef.win import CoinsList, WindowNames
from conf.meile_config import MeileGuiConfig
from cli.wallet import HandleWalletFunctions
import main.main as Meile

class WalletInfoContent(BoxLayout):
    def __init__(self, seed_phrase, name, address, password, **kwargs):
        super(WalletInfoContent, self).__init__()
        self.seed_phrase = seed_phrase
        self.wallet_address = address
        self.wallet_password = password
        self.wallet_name = name
        


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
            background_color=get_color_from_hex("#0d021b"),
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
        try:
            if self.price_text:
                mu_coin_amt = re.findall(r'[0-9]+' + mu_coin, self.price_text)[0]
                if mu_coin_amt:
                    self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(mu_coin_amt.split(mu_coin)[0])/1000000)),3)) + self.ids.drop_item.current_item.replace('u','') 
                    return self.ids.deposit.text
                else:
                    self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(self.ids.price.text.split("udvpn")[0])/1000000)),3)) + self.ids.drop_item.current_item.replace('u','')
                    return self.ids.deposit.text
            else:
                self.ids.deposit.text = "0.0dvpn"
                return self.ids.deposit.text
        except IndexError as e:
            print(str(e))
            if self.ids.price.text:
                self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(self.ids.price.text.split("udvpn")[0])/1000000)),3)) + CoinsList.ibc_mu_coins[0].replace('u','')
                return self.ids.deposit.text
            else:
                self.ids.deposit.text = "0.0dvpn"
                return self.ids.deposit.text
        
        

    def return_deposit_text(self):
        return (self.ids.deposit.text, self.naddress)
    
class IconListItem(OneLineIconListItem):
    icon = StringProperty()

   
class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class NodeRV(RecycleView):    
    pass


class RecycleViewRow(MDCard):
    text = StringProperty()    
    dialog = None
    
    def get_city_of_node(self, naddress):   
        APIURL   = "https://api.sentinel.mathnodes.com"

        endpoint = "/nodes/" + naddress.lstrip().rstrip()
        print(APIURL + endpoint)
        r = requests.get(APIURL + endpoint)
        remote_url = r.json()['result']['node']['remote_url']
        r = requests.get(remote_url + "/status", verify=False)
        print(remote_url)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        NodeInfoJSON = r.json()
        NodeInfoDict = {}
        
        NodeInfoDict['connected_peers'] = NodeInfoJSON['result']['peers']
        NodeInfoDict['max_peers']       = NodeInfoJSON['result']['qos']['max_peers']
        NodeInfoDict['version']         = NodeInfoJSON['result']['version']
        NodeInfoDict['city']            = NodeInfoJSON['result']['location']['city']




        if not self.dialog:
            self.dialog = MDDialog(
                md_bg_color=get_color_from_hex("#0d021b"),
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
                    title="Address:",
                    type="custom",
                    content_cls=subscribe_dialog,
                    md_bg_color=get_color_from_hex("#0d021b"),
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
        deposit = self.reparse_coin_deposit(sub_node[0])
        self.dialog.dismiss()
        self.dialog = None
        self.dialog = MDDialog(title="Subscribing...\n\n%s\n %s" %( deposit, sub_node[1]),md_bg_color=get_color_from_hex("#0d021b"))
        self.dialog.open()
        yield 2.0

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)        
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        
        returncode = HandleWalletFunctions.subscribe(HandleWalletFunctions, KEYNAME, sub_node[1], deposit)
        
        if returncode[0]:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Successful!",
                md_bg_color=get_color_from_hex("#0d021b"),
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
            title="Error: %s" % returncode[1],
            md_bg_color=get_color_from_hex("#0d021b"),
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
        for ibc_coin in IBCCOINS:
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
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW
        Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).SubResult = None
        Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).on_tab_switch(None,None,None,"Subscriptions")
    
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            return
 
        
    
class RecycleViewSubRow(MDCard):
    text = StringProperty()
    dialog = None
    
    
    def get_data_used(self, allocated, consumed):
        try:         
            allocated = float(allocated.replace('GB',''))
            
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
            self.ids.consumed_data.text = str(round(float(float(consumed/allocated)*100),2)) + "%"
            return float(float(consumed/allocated)*100)
        except Exception as e:
            print(str(e))
            return float(50)
        
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(title=title_text,md_bg_color=get_color_from_hex("#0d021b"))
        self.dialog.open()
    def remove_loading_widget(self):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            return
    @delayable
    def connect_to_node(self, ID, naddress, moniker):
        self.add_loading_popup("Connecting...")
        
        yield 1.8
        
        connected = HandleWalletFunctions.connect(HandleWalletFunctions, ID, naddress)
        
        if connected:
            self.remove_loading_widget()
            self.dialog = MDDialog(
                title="Connected!",
                md_bg_color=get_color_from_hex("#0d021b"),
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
                md_bg_color=get_color_from_hex("#0d021b"),
                buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=partial(self.call_ip_get, False, "")
                        ),])
            self.dialog.open()
            
    def call_ip_get(self,result, moniker,  *kwargs):
        if result:
            Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).CONNECTED = True
            Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).set_protected_icon(True, moniker)
        else:
            Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).CONNECTED = False
            
        Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).get_ip_address(None)
        self.remove_loading_widget()
            
            

# In case I go for word wrapping bigger textfield.
'''
class MySeedBox(MDTextFieldRect):

    def insert_text(self, substring, from_undo=False):

        line_length = 65
        seq = ' '.join(substring.split())
        
        if len(seq) > line_length:
            seq = '\n'.join([seq[i:i+line_length] for i in range(0, len(seq), line_length)])

        return super(MySeedtBox, self).insert_text(seq, from_undo=from_undo)
'''
