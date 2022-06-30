from src.geography.continents import OurWorld
from kivy.properties import BooleanProperty, StringProperty
from src.ui.interfaces import Tab
from src.typedef.win import WindowNames, ICANHAZURL
from src.cli.sentinel import  NodeTreeData
from src.cli.sentinel import NodesInfoKeys, FinalSubsKeys
from src.cli.sentinel import disconnect as Disconnect
import src.main.main as Meile
from src.ui.widgets import  NodeRV
from src.utils.qr import QRCode
from src.cli.wallet import HandleWalletFunctions
from src.conf.meile_config import MeileGuiConfig

from kivy.uix.popup import Popup
from kivymd.uix.spinner import MDSpinner  
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock, mainthread
from kivyoav.delayed import delayable
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard
from functools import partial

import asyncio
from save_thread_result import ThreadWithResult
import requests
import collections


from os import path

class WalletRestore(Screen):
    screemanager = ObjectProperty()
    
    dialog = None
    def restore_wallet_from_seed_phrase(self):
        
        
        if not self.dialog:
            self.dialog = MDDialog(
                text="Seed: %s \n\nName: %s \nPassword: %s" %
                
                 (self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text,
                 self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text,
                 self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text
                 ),
                
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        text_color=Meile.app.theme_cls.primary_color,
                        on_release=self.cancel,
                    ),
                    MDRaisedButton(
                        text="Restore",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.wallet_restore
                    ),
                ],
            )
            self.dialog.open()
            

            
    def switch_window(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

       
    def cancel(self):
        self.dialog.dismiss()
        
    def wallet_restore(self, inst):
        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)

        self.dialog.dismiss()
        seed_phrase  = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text
        wallet_name = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text
        keyring_passphrase = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text
        if seed_phrase:
            Wallet = HandleWalletFunctions.create(HandleWalletFunctions, wallet_name, keyring_passphrase, seed_phrase)
        else:
            Wallet = HandleWalletFunctions.create(HandleWalletFunctions, wallet_name, keyring_passphrase, None)
            
        FILE = open(MeileGuiConfig.CONFFILE,'w')

        CONFIG.set('wallet', 'keyname', wallet_name)
        CONFIG.set('wallet', 'address', Wallet['address'])
        CONFIG.set('wallet', 'password', keyring_passphrase)
        
        CONFIG.write(FILE)
        FILE.close()
        
        self.dialog = MDDialog(
                text="Wallet created!\n\n Seed: %s\nAddress: %s\nWallet Name: %s\nWallet Password: %s" %
                
                 (Wallet['seed'],
                 Wallet['address'],
                 wallet_name,
                 keyring_passphrase
                 ),
                
                buttons=[
                    MDRaisedButton(
                        text="I saved this",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=self.switch_window
                    ),
                ],
            )
        self.dialog.open()
        

class PreLoadWindow(Screen):   
    StatusMessages = ["Calculating π...", "Squaring the Circle...", "Solving the Riemann Hypothesis...", "Done"]
    title = "Meile dVPN"
    k = 0
    j = 0
    go_button = ObjectProperty()
    NodeTree = None
    def __init__(self, **kwargs):
        super(PreLoadWindow, self).__init__()
        
        self.NodeTree = NodeTreeData(None)
        
        # Schedule the functions to be called every n seconds
        Clock.schedule_once(self.NodeTree.get_nodes, 6)
        Clock.schedule_interval(self.update_status_text, 1)
        
        
        
        

    @delayable
    def update_status_text(self, dt):
        go_button = self.manager.get_screen(WindowNames.PRELOAD).ids.go_button


        yield 1.0
        
        if self.j == 2:
            self.manager.get_screen(WindowNames.PRELOAD).status_text = self.StatusMessages[3]
            go_button.opacity = 1
            go_button.disabled = False

            return
            
        if self.k == 3:
            self.k = 0
            self.j += 1
        else:
            self.manager.get_screen(WindowNames.PRELOAD).status_text = self.StatusMessages[self.k]
            self.k += 1
            

        
        
        
 
    def switch_window(self):
        Meile.app.root.add_widget(MainWindow(name=WindowNames.MAIN_WINDOW, node_tree=self.NodeTree))
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.MAIN_WINDOW



class MainWindow(Screen):
    title = "Meile dVPN"
    dialog = None
    Subscriptions = []
    address = None
    old_ip = ""
    ip = ""
    CONNECTED = False
    NodeTree = None
    SubResult = None
    
    def __init__(self, node_tree, **kwargs):
        #Builder.load_file("./src/kivy/meile.kv")
        super(MainWindow, self).__init__()
        
        self.NodeTree = node_tree
        
        Clock.schedule_once(self.build, 2)
        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        self.address = CONFIG['wallet'].get("address")

        

    def build(self, dt):
        OurWorld.CONTINENTS.remove(OurWorld.CONTINENTS[1])
        OurWorld.CONTINENTS.append("Subscriptions")
        #OurWorld.CONTINENTS.append("Search")
        
        for name_tab in OurWorld.CONTINENTS:
            tab = Tab(text=name_tab)
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.add_widget(tab)
        
        self.get_ip_address()
        
        self.on_tab_switch(
            None,
            None,
            None,
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.ids.layout.children[-1].text
        )
        
    def get_ip_address(self):
        if self.dialog:
            self.dialog.dismiss()
            
        self.old_ip = self.ip
        req = requests.get(ICANHAZURL)
        self.ip = req.text
    
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.new_ip.text = "IP: " + self.ip
        #self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.old_ip.text = "Old IP: " + self.old_ip
        
    def disconnect_from_node(self):
        try:
            if not self.CONNECTED:
                return
            else:
                returncode, self.CONNECTED = Disconnect()
                if returncode == 0 and not self.CONNECTED:
                    self.get_ip_address()
        except:
            self.dialog = None
            self.dialog = MDDialog(
            text="Error disconnecting from node",
            buttons=[
                MDFlatButton(
                    text="Okay",
                    theme_text_color="Custom",
                    text_color=Meile.app.theme_cls.primary_color,
                    on_release=self.get_ip_address,
                ),
                ]
            )
            self.dialog.open()
            
                    
        
    def wallet_dialog(self):
        
        # Add a check here to see if they already have a wallet available in
        # the app and proceed to the wallet screen
        # o/w proceed to wallet_create or wallet_restore
        #
        # Eventually, I'd like to add multiple wallet support. 
        # That will be after v1.0
        
        if not self.address:
            self.dialog = MDDialog(
                text="Wallet Restore/Create",
                buttons=[
                    MDRaisedButton(
                        text="Restore/Create",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.wallet_restore
                    ),
                ],
            )
            self.dialog.open()
        else:
            self.build_wallet_interface()
            
    def build_wallet_interface(self):
        Meile.app.root.add_widget(WalletScreen(name=WindowNames.WALLET, ADDRESS=self.address))
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.WALLET
        
    def wallet_restore(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        self.switch_window(WindowNames.WALLET_RESTORE)
        
    
    def wallet_create(self, inst):
        pass
        
    
    def add_sub_rv_data(self, node, flagloc):
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
            {
                "viewclass"      : "RecycleViewSubRow",
                "moniker_text"   : node[FinalSubsKeys[1]].lstrip().rstrip(),
                "sub_id_text"    : node[FinalSubsKeys[0]].lstrip().rstrip(),
                "price_text"     : node[FinalSubsKeys[3]].lstrip().rstrip(),
                "country_text"   : node[FinalSubsKeys[5]].lstrip().rstrip(),
                "address_text"   : node[FinalSubsKeys[2]].lstrip().rstrip(),
                "allocated_text" : node[FinalSubsKeys[6]].lstrip().rstrip(),
                "consumed_text"  : node[FinalSubsKeys[7]].lstrip().rstrip(),
                "source_image"   : flagloc
                
            },
        )
        
    def add_country_rv_data(self, NodeCountries):
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
            {
                "viewclass"      : "RecycleViewCountryRow",
                "num_text"       : str(NodeCountries['number']) + " Nodes",
                "country_text"   : NodeCountries['country'],
                "source_image"   : NodeCountries['flagloc']
            },
        )
            
    @mainthread        
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(title=title_text)
        self.dialog.open()
        
    @mainthread
    def remove_loading_widget(self):
        self.dialog.dismiss()
        self.dialog = None

    
    @delayable
    def subs_callback(self, dt):
        #from src.cli.sentinel import NodesDictList
        
        floc = "./src/imgs/"
        yield 0.314
        if not self.SubResult:
            thread = ThreadWithResult(target=self.NodeTree.get_subscriptions, args=(self.address,))
            thread.start()
            thread.join()    
            self.SubResult = thread.result
        #self.Subscriptions = get_subscriptions(NodesDictList, self.address)
        for sub in self.SubResult:
            if sub[FinalSubsKeys[5]] == "Czechia":
                sub[FinalSubsKeys[5]] = "Czech Republic"
            try: 
                iso2 = OurWorld.our_world.get_country_ISO2(sub[FinalSubsKeys[5]].lstrip().rstrip()).lower()
            except:
                iso2 = "sc"
            flagloc = floc + iso2 + ".png"
            self.add_sub_rv_data(sub, flagloc)
        self.remove_loading_widget()

    @mainthread
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        #from src.cli.sentinel import ConNodes, NodesDictList
        
        floc = "./src/imgs/"
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data = []
        if not tab_text:
            tab_text = OurWorld.CONTINENTS[0]
            
        # Subscriptions
        print(self.NodeTree.NodeTree.show())
        if tab_text == OurWorld.CONTINENTS[6]:
            self.add_loading_popup("Loading...")

            if self.address:
            
                Clock.schedule_once(self.subs_callback, 2)
                #Subscriptions = get_subscriptions(NodesDictList, address)
                
                return 
        
        NodeCountries = {}
        
        if tab_text == OurWorld.CONTINENTS[0]:
             
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[0]):
                print("AFRICA")
                print(ncountry.tag)
                iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
                print(iso2)
                flagloc = floc + iso2 + ".png"
                print(flagloc)
                NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
                NodeCountries['country'] = ncountry.tag
                NodeCountries['flagloc'] = flagloc
                
                self.add_country_rv_data(NodeCountries)
            
            '''
            if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Africa:
                
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                self.add_rv_data(node, flagloc)
            '''
        elif tab_text == OurWorld.CONTINENTS[1]:
            print("ASIA")
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[1]):
                print(ncountry.tag)
                iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
                print(iso2)
                flagloc = floc + iso2 + ".png"
                print(flagloc)
                NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
                NodeCountries['country'] = ncountry.tag
                NodeCountries['flagloc'] = flagloc
                
                self.add_country_rv_data(NodeCountries)
            
            '''
            if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Asia:
                
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                
                self.add_rv_data(node, flagloc)
            '''
        elif tab_text == OurWorld.CONTINENTS[2]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[2]):
                iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
                print(iso2)
                flagloc = floc + iso2 + ".png"
                print(flagloc)
                NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
                NodeCountries['country'] = ncountry.tag
                NodeCountries['flagloc'] = flagloc
                
                self.add_country_rv_data(NodeCountries)
            
            '''
            if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Europe:
                
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                
                self.add_rv_data(node, flagloc)
            '''
        elif tab_text == OurWorld.CONTINENTS[3]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[3]):
                iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
                print(iso2)
                flagloc = floc + iso2 + ".png"
                print(flagloc)
                NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
                NodeCountries['country'] = ncountry.tag
                NodeCountries['flagloc'] = flagloc
                
                self.add_country_rv_data(NodeCountries)
            
            '''
            if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.NorthAmerica:
                
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                
                self.add_rv_data(node, flagloc)
            '''
        elif tab_text == OurWorld.CONTINENTS[4]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[4]):
                iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
                print(iso2)
                flagloc = floc + iso2 + ".png"
                print(flagloc)
                NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
                NodeCountries['country'] = ncountry.tag
                NodeCountries['flagloc'] = flagloc
                
                self.add_country_rv_data(NodeCountries)
            
            '''
            if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Oceania:
                
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                
                self.add_rv_data(node, flagloc)
            '''
        elif tab_text == OurWorld.CONTINENTS[5]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[5]):
                iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
                print(iso2)
                flagloc = floc + iso2 + ".png"
                print(flagloc)
                NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
                NodeCountries['country'] = ncountry.tag
                NodeCountries['flagloc'] = flagloc
                
                self.add_country_rv_data(NodeCountries)
            
            ''' 
            if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.SouthAmerica:
                
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                
                self.add_rv_data(node, flagloc)
            '''
            
                
                
        # Search Criteria
        else:
            pass      
    
    def switch_window(self, window):
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = window
        
class WalletScreen(Screen):
    text = StringProperty()
    ADDRESS = None
    def __init__(self, ADDRESS,  **kwargs):
        super(WalletScreen, self).__init__(**kwargs)
        self.ADDRESS = ADDRESS 
        Clock.schedule_once(self.build)
        
        
    def build(self, dt):
        Wallet = HandleWalletFunctions()
        self.SetBalances(Wallet.get_balance(self.ADDRESS))
        
        
    def get_qr_code_address(self):
        CONFIG = MeileGuiConfig()
        QRcode = QRCode()
        if not path.isfile(path.join(CONFIG.IMGDIR, "dvpn.png")):
            QRcode.generate_qr_code(self.ADDRESS)
            
        return path.join(CONFIG.IMGDIR, "dvpn.png")
    
    def SetBalances(self, CoinDict):
        self.dec_text = str(CoinDict['dec']) + " dec"
        self.scrt_text = str(CoinDict['scrt']) + " scrt"
        self.atom_text = str(CoinDict['atom']) + " atom" 
        self.osmo_text = str(CoinDict['osmo']) + " osmo"
        self.dvpn_text = str(CoinDict['dvpn']) + " dvpn"       

    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

class NodeScreen(Screen):
    NodeTree = None
    Country = None
    def __init__(self, node_tree, country, **kwargs):
        super(NodeScreen, self).__init__()
        
        self.NodeTree = node_tree
        floc = "./src/imgs/"

        for node_child in self.NodeTree.NodeTree.children(country):
            node = node_child.data
            iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
            flagloc = floc + iso2 + ".png"
            self.add_rv_data(node, flagloc)
        
        
        
        
    def add_rv_data(self, node, flagloc):
        floc = "./src/imgs/"
        speed = node[NodesInfoKeys[5]].lstrip().rstrip().split('+')
        
        if "MB" in speed[0]:
            speed[0] = float(speed[0].replace("MB", ''))
        elif "KB" in speed[0]:
            speed[0] = float(float(speed[0].replace("KB", '')) / 1024 )
        else:
            speed[0] = 10
            
        if "MB" in speed[1]:
            speed[1] = float(speed[1].replace("MB", ''))
        elif "KB" in speed[1]:
            speed[1] = float(float(speed[1].replace("KB", '')) / 1024 )
        else:
            speed[1] = 10
        
        total = float(speed[0] + speed[1])
        if total >= 200:
            speedimage = floc + "fast.png"
        elif 125 <= total < 200:
            speedimage = floc + "fastavg.png"
        elif 75 <= total < 125:
            speedimage = floc + "avg.png"
        elif 30 <= total < 75:
            speedimage = floc + "slowavg.png"
        else:
            speedimage = floc + "slow.png"
        self.ids.rv.data.append(
            {
                "viewclass"    : "RecycleViewRow",
                "moniker_text" : node[NodesInfoKeys[0]].lstrip().rstrip(),
                "price_text"   : node[NodesInfoKeys[3]].lstrip().rstrip(),
                "country_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                "address_text" : node[NodesInfoKeys[1]].lstrip().rstrip(),
                "speed_text"   : node[NodesInfoKeys[5]].lstrip().rstrip(),
                "speed_image"  : speedimage,
                "source_image" : flagloc
                
            },
        )   
        
    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

        
class RecycleViewCountryRow(MDCard):
    text = StringProperty()
    
    def show_country_nodes(self, country):
        print(country)
        self.switch_window(country)
        
    def switch_window(self, country):
        NodeTree = NodeTreeData(Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).NodeTree.NodeTree)
        Meile.app.root.add_widget(NodeScreen(name="nodes", node_tree=NodeTree, country=country))

        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.NODES
           
        
    
