from geography.continents import OurWorld
from kivy.properties import BooleanProperty, StringProperty
from ui.interfaces import Tab, LatencyContent
from typedef.win import WindowNames, ICANHAZURL
from cli.sentinel import  NodeTreeData
from cli.sentinel import NodesInfoKeys, FinalSubsKeys
from cli.sentinel import disconnect as Disconnect
import main.main as Meile
from ui.widgets import WalletInfoContent
from utils.qr import QRCode
from cli.wallet import HandleWalletFunctions
from conf.meile_config import MeileGuiConfig
from typedef.win import CoinsList
from cli.warp import WarpHandler


from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock, mainthread
from kivyoav.delayed import delayable
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.behaviors import HoverBehavior
from kivymd.theming import ThemableBehavior
from kivy.core.window import Window




from save_thread_result import ThreadWithResult
import requests
from functools import partial
from os import path,geteuid
import sys
import copy 
import re
from time import sleep

class WalletRestore(Screen):
    screemanager = ObjectProperty()
    
    dialog = None
    def restore_wallet_from_seed_phrase(self):
        if not self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text and not self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_name_warning.opacity = 1
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_password_warning.opacity = 1
            return
        elif not self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_password_warning.opacity = 1
            return
        elif not self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_name_warning.opacity = 1
            return 
        elif len(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text) < 8:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_password_warning.opacity = 1
            return
        else:
            if not self.dialog:
                if not self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text:
                    seed_text = "Creating a new wallet..."
                else: 
                    seed_text = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text
                self.dialog = MDDialog(
                    md_bg_color=get_color_from_hex("#0d021b"),
                    text="Seed: %s\n\nName: %s\nPassword: %s" %
                     (
                     seed_text,
                     self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text,
                     self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text
                     ),
                    
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=Meile.app.theme_cls.primary_color,
                            on_release=self.cancel,
                        ),
                        MDRaisedButton(
                            text="RESTORE",
                            theme_text_color="Custom",
                            text_color=(1,1,1,1),
                            on_release= self.wallet_restore
                        ),
                    ],
                )
                self.dialog.open()
            
    def set_previous_screen(self):
        self.switch_window(None)
            
    def switch_window(self, inst):
        try: 
            self.dialog.dismiss()
            self.dialog = None
        except AttributeError:
            pass
        
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

       
    def cancel(self):
        self.dialog.dismiss()
        
    def wallet_restore(self, inst):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        try:
            self.dialog.dismiss()
        except Exception as e:
            print(str(e))
            
        seed_phrase  = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text
        wallet_name = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text
        keyring_passphrase = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text
        if seed_phrase:
            Wallet = HandleWalletFunctions.create(HandleWalletFunctions,
                                                  wallet_name.lstrip().rstrip(),
                                                  keyring_passphrase.lstrip().rstrip(),
                                                  seed_phrase.lstrip().rstrip())
        else:
            Wallet = HandleWalletFunctions.create(HandleWalletFunctions, 
                                                  wallet_name.lstrip().rstrip(), 
                                                  keyring_passphrase.lstrip().rstrip(), 
                                                  None)
            
        FILE = open(MeileGuiConfig.CONFFILE,'w')

        CONFIG.set('wallet', 'keyname', wallet_name)
        CONFIG.set('wallet', 'address', Wallet['address'])
        CONFIG.set('wallet', 'password', keyring_passphrase)
        
        CONFIG.write(FILE)
        FILE.close()
        WalletInfo = WalletInfoContent(Wallet['seed'], wallet_name, Wallet['address'], keyring_passphrase)
        self.dialog = MDDialog(
                type="custom",
                content_cls=WalletInfo,
                md_bg_color=get_color_from_hex("#0d021b"),

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
    dialog = None
    UUID = None
    def __init__(self, **kwargs):
        super(PreLoadWindow, self).__init__()
        
        self.NodeTree = NodeTreeData(None)
        
        self.GenerateUUID()
        self.CreateWarpConfig()
        
        # Schedule the functions to be called every n seconds
        Clock.schedule_once(partial(self.NodeTree.get_nodes, "13s"), 3)
        Clock.schedule_interval(self.update_status_text, 0.6)
        
    def CreateWarpConfig(self):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        
        if 'warp' in CONFIG:
            return 
        else:
            CONFIG['warp'] = {}
            CONFIG['warp']['registered'] = str(0)
        with open(MeileGuiConfig.CONFFILE,'w') as FILE:
            CONFIG.write(FILE)
        FILE.close()
        
    def GenerateUUID(self):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        self.UUID = CONFIG['wallet'].get('uuid')
        
        if not self.UUID:
            import uuid
            FILE = open(MeileGuiConfig.CONFFILE,'w')
            self.UUID = uuid.uuid4()
            CONFIG.set('wallet', 'uuid', "%s" % self.UUID)
            CONFIG.write(FILE)
            FILE.close()
            
    def get_logo(self):
        Config = MeileGuiConfig()
        return Config.resource_path("../imgs/logo_hd.png")

    @mainthread        
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(
            title=title_text,
            md_bg_color=get_color_from_hex("#0d021b"),
            buttons=[
                MDFlatButton(
                    text="OKAY",
                    theme_text_color="Custom",
                    text_color=Meile.app.theme_cls.primary_color,
                    on_release=self.quit_meile,
                ),
                ]
        )
        self.dialog.open()
        
   
    @delayable
    def update_status_text(self, dt):
        go_button = self.manager.get_screen(WindowNames.PRELOAD).ids.go_button
        #if geteuid() != 0:
        #    self.add_loading_popup("Please start Meile-GUI as root. i.e., sudo -E env PATH=$PATH ./meile-gui or similarly")

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
    CONNECTED = None
    warpd = False
    NodeTree = None
    SubResult = None
    MeileConfig = None
    ConnectedNode = None
    menu = None
    SortOptions = ['None', "Moniker", "Price"]
    Sort = SortOptions[0]
    
    def __init__(self, node_tree, **kwargs):
        #Builder.load_file("./src/kivy/meile.kv")
        super(MainWindow, self).__init__()
        
        self.NodeTree = node_tree
        
        Clock.schedule_once(self.get_config,1)     
        Clock.schedule_once(self.build, 2)
        sort_icons = ["sort-variant", "sort-alphabetical-ascending", "sort-numeric-ascending"]
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": f"{k}",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i,k in zip(self.SortOptions, sort_icons)
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.drop_item,
            background_color=get_color_from_hex("#0d021b"),
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        
    def set_item(self, text_item):
        self.ids.drop_item.set_item(text_item)
        self.Sort = text_item
        self.menu.dismiss()
        
    def set_warp_icon(self):
        MeileConfig = MeileGuiConfig()
        return MeileConfig.resource_path("../imgs/warp.png")
     
    def set_protected_icon(self, setbool, moniker):
        MeileConfig = MeileGuiConfig()
        if setbool:
            self.ids.protected.opacity = 1
            self.ids.connected_node.text = moniker
        else:
            self.ids.protected.opacity = 0
            self.ids.connected_node.text = moniker
        return MeileConfig.resource_path("../imgs/protected.png")

    def get_config(self, dt):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        self.address = CONFIG['wallet'].get("address")  

    def build(self, dt):
        OurWorld.CONTINENTS.remove(OurWorld.CONTINENTS[1])
        OurWorld.CONTINENTS.append("Subscriptions")
        #OurWorld.CONTINENTS.append("Search")
        
        for name_tab in OurWorld.CONTINENTS:
            tab = Tab(tab_label_text=name_tab)
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.add_widget(tab)
        
        self.get_ip_address(None    )
        
        self.on_tab_switch(
            None,
            None,
            None,
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.ids.layout.children[-1].text
        )
        
    @mainthread
    def display_warp_success(self):
        
        self.dialog = MDDialog(
            text="You are now using DoH (DNS-over-HTTPS) and your DNS traffic is encrypted from prying eyes.",
            md_bg_color=get_color_from_hex("#0d021b"),
            buttons=[
                MDRaisedButton(
                    text="Okay",
                    theme_text_color="Custom",
                    text_color=(1,1,1,1),
                    on_release=self.remove_loading_widget
                ),
            ],
        )
        self.dialog.open()
        
    @delayable    
    def start_warp(self):
        MeileConfig = MeileGuiConfig()
        WARP = WarpHandler()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        self.add_loading_popup("Staring WARP service...")
        yield 2.3
        if not self.warpd:
            if WARP.start_warp_daemon():
                
                sleep(4)
                self.warpd = True
            
    
            if int(CONFIG['warp'].get('registered')) == 0:
                print("Registering WARP...")
                CONFIG.set('warp','registered', '1')
                with open(MeileGuiConfig.CONFFILE, 'w') as FILE:
                    CONFIG.write(FILE)
                FILE.close()
                if WARP.register_warp():
                    sleep(6)
                    print("Running WARP...")
                    if WARP.run_warp():
                        print("SUCCESS")
                        sleep(3)
                        self.remove_loading_widget(None)
                        self.display_warp_success()
                        
            else:
                print("Running WARP...")
                if WARP.run_warp():
                    sleep(3)
                    print("WARP: Success!")
                    self.remove_loading_widget(None)
                    self.display_warp_success()
            
        else:
            #self.remove_loading_widget(None)
            self.dialog = MDDialog(
                text="You are already using WARP.",
                md_bg_color=get_color_from_hex("#0d021b"),
                buttons=[
                    MDRaisedButton(
                        text="OKAY",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=self.remove_loading_widget
                    ),
                ],
            )
            self.dialog.open()
            
    def get_logo(self):
        self.MeileConfig = MeileGuiConfig()
        return self.MeileConfig.resource_path("../imgs/logo.png")
        
    def get_ip_address(self, dt):
        if self.dialog:
            self.dialog.dismiss()
            
        self.old_ip = self.ip
        try: 
            req = requests.get(ICANHAZURL)
            self.ip = req.text
        
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.new_ip.text = self.ip
            return True
            #self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.old_ip.text = "Old IP: " + self.old_ip
        except Exception as e:
            print(str(e))
            return False
        
    def disconnect_from_node(self):
        try:
            if self.CONNECTED == None:
                returncode, self.CONNECTED = Disconnect()
                print("Disconnect RTNCODE: %s" % returncode)
                self.get_ip_address(None)
                self.set_protected_icon(False, "")
            elif self.CONNECTED == False:
                return
            else:
                returncode, self.CONNECTED = Disconnect()
                print("Disconnect RTNCODE: %s" % returncode)
                self.get_ip_address(None)
                self.set_protected_icon(False, "")
        except Exception as e:
            print(str(e))
            self.dialog = None
            self.dialog = MDDialog(
            text="Error disconnecting from node",
            md_bg_color=get_color_from_hex("#0d021b"),
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
        self.get_config(None)
        if not self.address:
            self.dialog = MDDialog(
                text="Wallet Restore/Create",
                md_bg_color=get_color_from_hex("#0d021b"),
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
        
    def build_help_screen_interface(self):
        Meile.app.root.add_widget(HelpScreen(name=WindowNames.HELP))
        Meile.app.root.transition = SlideTransition(direction = "left")
        Meile.app.root.current = WindowNames.HELP
       
    def wallet_restore(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        self.switch_window(WindowNames.WALLET_RESTORE)
        
    
    def wallet_create(self, inst):
        pass
        
    
    def add_sub_rv_data(self, node, flagloc):
        
        if node[FinalSubsKeys[1]] == "Offline":
           self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
                {
                    "viewclass"      : "RecycleViewSubRow",
                    "moniker_text"   : node[FinalSubsKeys[1]].lstrip().rstrip(),
                    "sub_id_text"    : node[FinalSubsKeys[0]].lstrip().rstrip(),
                    "price_text"     : node[FinalSubsKeys[4]].lstrip().rstrip(),
                    "country_text"   : "Offline",
                    "address_text"   : node[FinalSubsKeys[2]].lstrip().rstrip(),
                    "allocated_text" : node[FinalSubsKeys[6]].lstrip().rstrip(),
                    "consumed_text"  : node[FinalSubsKeys[7]].lstrip().rstrip(),
                    "source_image"   : self.MeileConfig.resource_path(flagloc),
                    "md_bg_color"    : "#50507c"
                },
            )
         
        else:
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
                {
                    "viewclass"      : "RecycleViewSubRow",
                    "moniker_text"   : node[FinalSubsKeys[1]].lstrip().rstrip(),
                    "sub_id_text"    : node[FinalSubsKeys[0]].lstrip().rstrip(),
                    "price_text"     : node[FinalSubsKeys[4]].lstrip().rstrip(),
                    "country_text"   : node[FinalSubsKeys[5]].lstrip().rstrip(),
                    "address_text"   : node[FinalSubsKeys[2]].lstrip().rstrip(),
                    "allocated_text" : node[FinalSubsKeys[6]].lstrip().rstrip(),
                    "consumed_text"  : node[FinalSubsKeys[7]].lstrip().rstrip(),
                    "source_image"   : self.MeileConfig.resource_path(flagloc),
                    "md_bg_color"    : "#0d021b"
                    
                },
            )
        
    def add_country_rv_data(self, NodeCountries):
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
            {
                "viewclass"      : "RecycleViewCountryRow",
                "num_text"       : str(NodeCountries['number']) + " Nodes",
                "country_text"   : NodeCountries['country'],
                "source_image"   : self.MeileConfig.resource_path(NodeCountries['flagloc'])
            },
        )
            
    @mainthread
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(title=title_text,md_bg_color=get_color_from_hex("#0d021b"))
        self.dialog.open()
        
    @mainthread
    def remove_loading_widget(self, dt):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            pass
        
    @mainthread
    def sub_address_error(self):
        self.dialog = MDDialog(
            text="Error Loading Subscriptions... No wallet found",
            md_bg_color=get_color_from_hex("#0d021b"),
            buttons=[
                MDRaisedButton(
                    text="Okay",
                    theme_text_color="Custom",
                    text_color=(1,1,1,1),
                    on_release=self.remove_loading_widget
                ),
            ],
        )
        self.dialog.open()
    
    
    def refresh_nodes_and_subs(self):
        lc = LatencyContent()
        self.dialog = MDDialog(
                    title="Latency:",
                    type="custom",
                    content_cls=lc,
                    md_bg_color=get_color_from_hex("#0d021b"),
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=Meile.app.theme_cls.primary_color,
                            on_release=self.remove_loading_widget
                        ),
                        MDRaisedButton(
                            text="REFRESH",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex("#000000"),
                            on_release=partial(self.Refresh, lc)
                        ),
                    ],
                )
        self.dialog.open()
        
    @delayable
    def Refresh(self, latency, *kwargs):
        self.remove_loading_widget(None)
        
        self.add_loading_popup("Reloading Nodes & Subscriptions...")
        yield 0.5
        try: 
            self.NodeTree.NodeTree = None
            thread = ThreadWithResult(target=self.NodeTree.get_nodes, args=(latency.return_latency(),)) 
            #Clock.schedule_once(self.NodeTree.get_nodes, 0.2)
            thread.start()
            thread.join()
        except Exception as e:
            print(str(e))
            pass
        self.SubResult = None
        self.remove_loading_widget(None)
        self.ids.android_tabs.switch_tab("Subscriptions")
        #self.on_tab_switch(None, None, None, "Subscriptions")
        
    def GetSubscriptions(self):
        try: 
            thread = ThreadWithResult(target=self.NodeTree.get_subscriptions, args=(self.address,))
            thread.start()
            thread.join()    
            self.SubResult = thread.result
        except Exception as e:
            print(str(e))
            return None
    
    
    
    @delayable
    def subs_callback(self, dt):
        floc = "../imgs/"
        yield 0.314
        if not self.SubResult:
            self.GetSubscriptions()
        
        for sub in self.SubResult:
            if sub[FinalSubsKeys[5]] == "Czechia":
                sub[FinalSubsKeys[5]] = "Czech Republic"
            try: 
                iso2 = OurWorld.our_world.get_country_ISO2(sub[FinalSubsKeys[5]].lstrip().rstrip()).lower()
            except:
                iso2 = "sc"
            flagloc = floc + iso2 + ".png"
            self.add_sub_rv_data(sub, flagloc)
        self.remove_loading_widget(None)


    @mainthread
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        #from src.cli.sentinel import ConNodes, NodesDictList
        print("instance_tabs: %s, instance_tab: %s, instance_tabs_label: %s, tab_text: %s" % (instance_tabs, instance_tab, instance_tabs_label, tab_text))
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data = []
        if not tab_text:
            tab_text = OurWorld.CONTINENTS[0]
            
        # Subscriptions
        #print(self.NodeTree.NodeTree.show())
        if tab_text == OurWorld.CONTINENTS[6]:
            self.get_config(None)
            self.add_loading_popup("Loading...")
            if self.address:
                
                Clock.schedule_once(self.subs_callback, 1)
                #Subscriptions = get_subscriptions(NodesDictList, address)
                return 
            else:
                self.remove_loading_widget(None)
                self.sub_address_error()
                return

        # use lambda in future
        if tab_text == OurWorld.CONTINENTS[0]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[0]):
                self.add_country_rv_data(self.build_node_data(ncountry))
            
        elif tab_text == OurWorld.CONTINENTS[1]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[1]):
                self.add_country_rv_data(self.build_node_data(ncountry))
            
        elif tab_text == OurWorld.CONTINENTS[2]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[2]):
                self.add_country_rv_data(self.build_node_data(ncountry))

        elif tab_text == OurWorld.CONTINENTS[3]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[3]):
                self.add_country_rv_data(self.build_node_data(ncountry))

        elif tab_text == OurWorld.CONTINENTS[4]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[4]):
                self.add_country_rv_data(self.build_node_data(ncountry))            

        elif tab_text == OurWorld.CONTINENTS[5]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[5]):
                self.add_country_rv_data(self.build_node_data(ncountry))            
        # Search Criteria
        else:
            pass      
    
    def build_node_data(self, ncountry):
        floc = "../imgs/"
        NodeCountries = {}
        
        iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag.lstrip().rstrip()).lower()
        flagloc = floc + iso2 + ".png"
        
        NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag)) 
        NodeCountries['country'] = ncountry.tag
        NodeCountries['flagloc'] = flagloc
        
        return NodeCountries
    
    def switch_window(self, window):
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = window
        
class WalletScreen(Screen):
    text = StringProperty()
    ADDRESS = None
    MeileConfig = None
    dialog = None
    def __init__(self, ADDRESS,  **kwargs):
        super(WalletScreen, self).__init__()
        self.ADDRESS = ADDRESS
        print("WalletScreen, ADDRESS: %s" % self.ADDRESS)
        self.wallet_address = self.ADDRESS
        
        Clock.schedule_once(self.build)
        
        
    def build(self, dt):
        Wallet = HandleWalletFunctions()
        self.SetBalances(Wallet.get_balance(self.ADDRESS))
    
    def open_fiat_interface(self):
        pass
    
    def return_coin_logo(self, coin):
        self.MeileConfig = MeileGuiConfig() 

        predir = "../imgs/"
        logoDict = {} 
        for c in CoinsList.coins:
            logoDict[c] = predir + c + ".png"
        
        for c in CoinsList.coins:
            if c == coin:
                return self.MeileConfig.resource_path(logoDict[c])
        
    def get_qr_code_address(self):
        CONFIG = MeileGuiConfig()
        conf = CONFIG.read_configuration(MeileGuiConfig.CONFFILE)
        self.ADDRESS = conf['wallet'].get("address")  
        QRcode = QRCode()
        if not path.isfile(path.join(CONFIG.IMGDIR, "dvpn.png")):
            QRcode.generate_qr_code(self.ADDRESS)
            
        return path.join(CONFIG.IMGDIR, "dvpn.png")
    
    def SetBalances(self, CoinDict):
        if CoinDict:
            self.dec_text = str(CoinDict['dec']) + " dec"
            self.scrt_text = str(CoinDict['scrt']) + " scrt"
            self.atom_text = str(CoinDict['atom']) + " atom" 
            self.osmo_text = str(CoinDict['osmo']) + " osmo"
            self.dvpn_text = str(CoinDict['dvpn']) + " dvpn"
        else:
            self.dec_text = str("0.0") + " dec"
            self.scrt_text = str("0.0") + " scrt"
            self.atom_text = str("0.0") + " atom" 
            self.osmo_text = str("0.0") + " osmo"
            self.dvpn_text = str("0.0") + " dvpn"
            self.dialog = MDDialog(
                text="Error Loading Wallet Balance. Please try again later.",
                md_bg_color=get_color_from_hex("#0d021b"),
                buttons=[
                    MDRaisedButton(
                        text="OKay",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=self.closeDialog
                    ),
                ],
            )
            self.dialog.open()
               
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except:
            print("Dialog is NONE")
            return

    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

class NodeScreen(Screen):
    NodeTree = None
    Country = None
    MeileConfig = None
    def __init__(self, node_tree, country, sort, **kwargs):
        super(NodeScreen, self).__init__()
        
        self.NodeTree = node_tree
        
        
        floc = "../imgs/"
        CountryNodes = self.NodeTree.NodeTree.children(country)
        
        if sort == Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).SortOptions[1]:
            self.SortNodesByMoniker(CountryNodes)
        elif sort == Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).SortOptions[2]:
            self.SortNodesByPrice(CountryNodes)
        else:
            for node_child in CountryNodes:
                node = node_child.data
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                flagloc = floc + iso2 + ".png"
                self.add_rv_data(node, flagloc)
            
    def SortNodesByPrice(self, CountryNodes):
        NodeData = []     
        for node in CountryNodes:
            NodeData.append(node.data)
            
        i=0
        
        OldNodeData = copy.deepcopy(NodeData)
        
        for data in NodeData:
            try: 
                udvpn = re.findall(r'[0-9]+' +"udvpn", data['Price'])[0]
                NodeData[i]['Price'] = udvpn
            except IndexError:
                NodeData[i]['Price'] = "1000000000udvpn"
            i += 1
        NodeDataSorted = sorted(NodeData, key=lambda d: int(d['Price'].split('udvpn')[0]))
        
        
        NewNodeData = []
    
        for ndata in NodeDataSorted:
            for odata in OldNodeData:
                if odata['Address'] == ndata['Address']:
                    ndata['Price'] = odata['Price']                    
                    NewNodeData.append(ndata)
                    
        
        NodeDataSorted = NewNodeData

        self.meta_add_rv_data(NodeDataSorted)
        
    def SortNodesByMoniker(self, CountryNodes):
        NodeData = []     
        for node in CountryNodes:
            NodeData.append(node.data)
            
        NodeDataSorted = sorted(NodeData, key=lambda d: d[NodesInfoKeys[0]])

        self.meta_add_rv_data(NodeDataSorted)
        
    def meta_add_rv_data(self, NodeDataSorted):  
        floc = "../imgs/"
  
        for node in NodeDataSorted:
            iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
            flagloc = floc + iso2 + ".png"
            self.add_rv_data(node, flagloc)

        
    def add_rv_data(self, node, flagloc):
        self.MeileConfig = MeileGuiConfig()

        floc = "../imgs/"
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
                "speed_image"  : self.MeileConfig.resource_path(speedimage),
                "source_image" : self.MeileConfig.resource_path(flagloc)
                
            },
        )   
        
    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

        
class RecycleViewCountryRow(MDCard,ThemableBehavior, HoverBehavior):
    text = StringProperty()    
    
    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex("#200c3a")
        Window.set_system_cursor('hand')
        
    def on_leave(self, *args):
        self.md_bg_color = get_color_from_hex("#0d021b")
        Window.set_system_cursor('arrow')
    
    def show_country_nodes(self, country):
        print(country)
        self.switch_window(country)
        
    def switch_window(self, country):
        NodeTree = NodeTreeData(Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).NodeTree.NodeTree)
        try:
            Meile.app.root.remove_widget(Meile.app.root.get_screen(WindowNames.NODES))
        except Exception as e:
            print(str(e))
            pass
        Meile.app.root.add_widget(NodeScreen(name="nodes",
                                             node_tree=NodeTree,
                                             country=country,
                                             sort=Meile.app.root.get_screen(WindowNames.MAIN_WINDOW).Sort))

        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.NODES
           
        
    
class HelpScreen(Screen):
    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="right")
        Meile.app.root.current = WindowNames.MAIN_WINDOW
