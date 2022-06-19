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


from functools import partial
from urllib3.exceptions import InsecureRequestWarning
import requests
import re


from src.cli.sentinel import NodesInfoKeys
from src.ui.interfaces import SubscribeContent
from src.typedef.win import CoinsList
from src.conf.meile_config import MeileGuiConfig
from src.cli.wallet import HandleWalletFunctions




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
        try:
            mu_coin_amt = re.findall(r'[0-9]+' + mu_coin, self.price_text)[0]
            if mu_coin_amt:
                self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(mu_coin_amt.split(mu_coin)[0])/1000000)),3)) + self.ids.drop_item.current_item.replace('u','') 
                return self.ids.deposit.text
            else:
                self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(self.ids.price.text.split("udvpn")[0])/1000000)),3)) + self.ids.drop_item.current_item.replace('u','')
                return self.ids.deposit.text
        except IndexError as e:
            print(str(e))
            self.ids.deposit.text = str(round(int(self.ids.slider1.value)*(float(int(self.ids.price.text.split("udvpn")[0])/1000000)),3)) + CoinsList.ibc_mu_coins[0].replace('u','')
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

class MD3Card(MDCard):
    dialog = None
    
    def set_moniker(self, name):
        self.Moniker = name
        
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Subscribe to Node?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.closeDialog,
                    ),
                    MDRaisedButton(
                        text="SUBSCRIBE",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.subscribeME
                    ),
                ],
            )
        self.dialog.open()

    def closeDialog(self, inst):
        self.dialog.dismiss()
        
    def subscribeME(self, inst):
        self.dialog.dismiss()
        print("SUBSCRIBED!")

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
    @delayable
    def subscribe(self, subscribe_dialog, *kwargs):
        sub_node = subscribe_dialog.return_deposit_text()
        deposit = self.reparse_coin_deposit(sub_node[0])
        self.dialog.dismiss()
        self.dialog = None
        self.dialog = MDDialog(title="Subscribing...\n\n%s\n %s" %( deposit, sub_node[1]))
        self.dialog.open()
        yield 2.0

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)        
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        
        returncode = HandleWalletFunctions.subscribe(HandleWalletFunctions, KEYNAME, sub_node[1], deposit)
        
        if returncode[0]:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Successful!",
                buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release=self.closeDialog
                        ),])
            self.dialog.open()

        else:
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Error: %s" % returncode[1],
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
                deposit = deposit.replace(coin, v)
                mu_deposit_amt = int(float(re.findall(r'[0-9]+\.[0-9]+', deposit)[0])*CoinsList.SATOSHI)
                tru_mu_deposit = str(mu_deposit_amt) + v
                return tru_mu_deposit
            except:
                pass
    def closeDialog(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        
   
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
                
            return float(float(consumed/allocated)*100)
        except Exception as e:
            print(str(e))
            return float(50)
      
    

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
