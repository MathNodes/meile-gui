from geography.continents import OurWorld
from ui.interfaces import Tab, LatencyContent
from typedef.win import WindowNames, ICANHAZURL
from cli.sentinel import  NodeTreeData
from typedef.konstants import NodeKeys, TextStrings
from cli.sentinel import disconnect as Disconnect
import main.main as Meile
from ui.widgets import WalletInfoContent, MDMapCountryButton, RatingContent
from utils.qr import QRCode
from cli.wallet import HandleWalletFunctions
from conf.meile_config import MeileGuiConfig
from typedef.win import CoinsList
from cli.warp import WarpHandler
from adapters import HTTPRequests

from kivy.properties import BooleanProperty, StringProperty, ColorProperty
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton,MDTextButton, MDFillRoundFlatButton
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
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivy_garden.mapview import MapMarkerPopup, MapView
from kivymd.toast import toast

import requests
import sys
import copy 
import re
from time import sleep
from functools import partial
from os import path,geteuid, chdir
from save_thread_result import ThreadWithResult
from unidecode import unidecode

TIMEOUT = 5

class WalletRestore(Screen):
    screemanager = ObjectProperty()
    
    dialog = None
    
    def __init__(self, **kwargs):
        super(WalletRestore, self).__init__()
        self.build()

    def build(self):
        if Meile.app.manager.get_screen(WindowNames.MAIN_WINDOW).NewWallet:
            self.ids.seed.opacity = 0
            self.ids.seed_hint.opacity = 0
            self.ids.restore_wallet_button.text = "Create"
        else:
            self.ids.seed.opacity = 1
            self.ids.seed_hint.opacity = 1
            self.ids.restore_wallet_button.text = "Restore"
        
    def restore_wallet_from_seed_phrase(self):
        wallet_password = unidecode(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text)
        wallet_name     = unidecode(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text)
        seed_phrase     = unidecode(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text)

        if not wallet_name and not wallet_password:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_name_warning.opacity = 1
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_password_warning.opacity = 1
            return
        elif not wallet_password:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_password_warning.opacity = 1
            return
        elif not wallet_name:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_name_warning.opacity = 1
            return 
        elif len(wallet_password) < 8:
            self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.wallet_password_warning.opacity = 1
            return
        else:
            if not self.dialog:
                if not seed_phrase:
                    seed_text = "Creating a new wallet..."
                    button_text = "CREATE"
                else: 
                    seed_text = seed_phrase
                    button_text = "RESTORE"
                self.dialog = MDDialog(
                    md_bg_color=get_color_from_hex("#0d021b"),
                    text="Seed: %s\n\nName: %s\nPassword: %s" %
                     (
                     seed_text,
                     wallet_name,
                     wallet_password
                     ),
                    
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Custom",
                            text_color=Meile.app.theme_cls.primary_color,
                            on_release=self.cancel,
                        ),
                        MDRaisedButton(
                            text=button_text,
                            theme_text_color="Custom",
                            text_color=(1,1,1,1),
                            on_release=self.wallet_restore
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
        Meile.app.root.remove_widget(self)
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

       
    def cancel(self, inst):
        self.dialog.dismiss()
        
    def wallet_restore(self, inst):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        try:
            self.dialog.dismiss()
        except Exception as e:
            print(str(e))
            
        seed_phrase        = unidecode(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text)
        wallet_name        = unidecode(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text)
        keyring_passphrase = unidecode(self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text)
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
        CONFIG.set('wallet', 'password', keyring_passphrase.replace('%','%%'))
        
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
        chdir(MeileGuiConfig.BASEDIR)
        
        
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
    warpd_disconnected = True
    NodeTree = None
    SubResult = None
    MeileConfig = None
    ConnectedNode = None
    menu = None
    MeileLand = None
    SortOptions = ['None', "Moniker", "Price"]
    Sort = SortOptions[0]
    MeileMap = None
    MeileMapBuilt = False
    NodeSwitch = {"moniker" : None, "node" : None, "switch" : False, 'id' : None, 'consumed' : None, 'og_consumed' : None, 'allocated' : None}
    NewWallet = False
    box_color = ColorProperty('#fcb711')
    clock = None
    PersistentBandwidth = {}


    def __init__(self, node_tree, **kwargs):
        #Builder.load_file("./src/kivy/meile.kv")
        super(MainWindow, self).__init__()
        
        self.NodeTree = node_tree
        self.MeileLand = OurWorld()
        
        Clock.schedule_once(self.get_config,1)     
        Clock.schedule_once(self.build, 1)
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
        
    def build(self, dt):
        OurWorld.CONTINENTS.remove(OurWorld.CONTINENTS[1])
        OurWorld.CONTINENTS.append("Subscriptions")
        #OurWorld.CONTINENTS.append("Search")
        
        for name_tab in OurWorld.CONTINENTS:
            tab = Tab(tab_label_text=name_tab)
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.add_widget(tab)
        
        self.get_ip_address(None)
        
        self.on_tab_switch(
            None,
            None,
            None,
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.ids.layout.children[-1].text
        )
        
    
    def build_meile_map(self):
        if not self.MeileMapBuilt: 
            self.MeileMap = MapView(lat=50.6394, lon=3.057, zoom=3)
            self.MeileMap.map_source = "osm"
            
            self.ids.country_map.add_widget(self.MeileMap)
            self.AddCountryNodePins()
            self.MeileMapBuilt = True
        
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path("../fonts/arial-unicode-ms.ttf")
        
    def AddCountryNodePins(self):
        try:
            for continent in self.MeileLand.CONTINENTS:
                for ncountry in self.NodeTree.NodeTree.children(continent):
                    loc = self.MeileLand.CountryLatLong[ncountry.tag]
                    marker = MapMarkerPopup(lat=loc[0], lon=loc[1])
                    marker.add_widget(MDMapCountryButton(text='%s - %s' %(ncountry.tag, len(self.NodeTree.NodeTree.children(ncountry.tag))),
                                                   theme_text_color="Custom",
                                                   md_bg_color=get_color_from_hex("#0d021b"),
                                                   text_color=(1,1,1,1),
                                                   on_release=partial(self.load_country_nodes, ncountry.tag)
                                                   ))
                    self.MeileMap.add_marker(marker)
        except Exception as e:
            print(str(e))
            pass        
        self.get_continent_coordinates(self.MeileLand.CONTINENTS[0])
                
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
        
        if not self.warpd and self.warpd_disconnected:
            self.add_loading_popup("Starting WARP service...")
            yield 1.3
            if WARP.start_warp_daemon():
                sleep(7)
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
                        self.warpd_disconnected = False
                        
            else:
                print("Running WARP...")
                if WARP.run_warp():
                    sleep(3)
                    print("WARP: Success!")
                    self.remove_loading_widget(None)
                    self.display_warp_success()
                    self.warpd_disconnected = False
                        
        elif self.warpd and self.warpd_disconnected: 
            self.add_loading_popup("Starting WARP service...")
            yield 1.3
            print("Running WARP...")
            if WARP.run_warp():
                sleep(3)
                print("WARP: Success!")
                self.remove_loading_widget(None)
                self.display_warp_success()
                self.warpd_disconnected = False
                        
            
            
        else:
            #self.remove_loading_widget(None)
            self.dialog = MDDialog(
                text="Disconnecting from WARP and using system DNS...",
                md_bg_color=get_color_from_hex("#0d021b"),
                buttons=[
                    MDRaisedButton(
                        text="OKAY",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=self.warp_disconnect
                    ),
                ],
            )
            self.dialog.open()
            
    @mainthread
    def warp_disconnect(self, inst):
        WARP = WarpHandler()
        self.remove_loading_widget(None)
        
        if WARP.warp_disconnect():
            print("SUCCESS")
            self.warpd_disconnected = True
            self.get_ip_address(None)
        else:
            print("FAIL")
            
    def get_logo(self):
        self.MeileConfig = MeileGuiConfig()
        return self.MeileConfig.resource_path("../imgs/logo.png")
        
    def get_ip_address(self, dt):
        if self.dialog:
            self.dialog.dismiss()
            
        self.old_ip = self.ip
        try: 
            Request = HTTPRequests.MakeRequest()
            http = Request.hadapter()
            req = http.get(ICANHAZURL)
            self.ip = req.text
        
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.new_ip.text = self.ip
            return True
            #self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.old_ip.text = "Old IP: " + self.old_ip
        except Exception as e:
            print(str(e))
            return False
    @mainthread    
    def disconnect_from_node(self):
        try:
            if self.CONNECTED == None:
                returncode, self.CONNECTED = Disconnect()
                print("Disconnect RTNCODE: %s" % returncode)
                self.get_ip_address(None)
                self.set_protected_icon(False, "")
            elif self.CONNECTED == False:
                print("Disconnected!")
            else:
                returncode, self.CONNECTED = Disconnect()
                print("Disconnect RTNCODE: %s" % returncode)
                self.get_ip_address(None)
                self.set_protected_icon(False, "")
            
            #self.warp_disconnect(None)
            self.dialog = None
            rating_dialog = RatingContent(self.NodeSwitch['moniker'], self.NodeSwitch['node'])
            self.dialog = MDDialog(
                title="Node Rating",
                md_bg_color=get_color_from_hex("#0d021b"),
                type="custom",
                content_cls=rating_dialog,
                buttons=[
                    MDFlatButton(
                        text="LATER",
                        theme_text_color="Custom",
                        text_color=Meile.app.theme_cls.primary_color,
                        on_release=self.remove_loading_widget,
                    ),
                    MDRaisedButton(
                        text="RATE",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=partial(self.WrapperSubmitRating, rating_dialog),
                    ),
                    ]
                )
            self.dialog.open()
            self.NodeSwitch = {"moniker" : None,
                               "node" : None,
                               "switch" : False,
                               'id' : None,
                               'consumed' : None,
                               'og_consumed' : None,
                               'allocated' : None
                               }
            return True
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
            return False 
                    
    def WrapperSubmitRating(self, rc, dt):
        if rc.SubmitRating(rc.return_rating_value(), rc.naddress) == 0:
            toast(text="Rating Sent!", duration=3.5)
        else:
            toast(text="Error sending rating...", duration=3.5)
        self.remove_loading_widget(None)
            
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
                    MDFlatButton(
                        text="CREATE",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=partial(self.wallet_restore, True)
                        ),
                    
                    MDRaisedButton(
                        text="RESTORE",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release=partial(self.wallet_restore, False)
                    ),
                ],
            )
            self.dialog.open()
        else:
            self.build_wallet_interface()
            
    def wallet_restore(self, NewWallet, inst):
        if NewWallet:
            self.NewWallet = True
        else:
            self.NewWallet = False
            
        self.dialog.dismiss()
        self.dialog = None
        Meile.app.manager.add_widget(WalletRestore(name=WindowNames.WALLET_RESTORE))
        Meile.app.root.transition = SlideTransition(direction = "right")
        Meile.app.root.current = WindowNames.WALLET_RESTORE
            
    def build_wallet_interface(self):
        Meile.app.root.add_widget(WalletScreen(name=WindowNames.WALLET, ADDRESS=self.address))
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.WALLET
        
    def build_help_screen_interface(self):
        Meile.app.root.add_widget(HelpScreen(name=WindowNames.HELP))
        Meile.app.root.transition = SlideTransition(direction = "left")
        Meile.app.root.current = WindowNames.HELP
        
    def add_sub_rv_data(self, node, flagloc):
        
        if node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip() in self.NodeTree.NodeScores:
            nscore = str(self.NodeTree.NodeScores[node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip()][0])
            votes  = str(self.NodeTree.NodeScores[node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip()][1])
        else:
            nscore = "null"
            votes  = "0"
            
        if node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip() in self.NodeTree.NodeLocations:
            city = self.NodeTree.NodeLocations[node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip()]
        else:
            city = " "
            
        if node[NodeKeys.FinalSubsKeys[1]] == "Offline":
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
                 {
                     "viewclass"      : "RecycleViewSubRow",
                     "moniker_text"   : node[NodeKeys.FinalSubsKeys[1]].lstrip().rstrip(),
                     "sub_id_text"    : node[NodeKeys.FinalSubsKeys[0]].lstrip().rstrip(),
                     "price_text"     : node[NodeKeys.FinalSubsKeys[4]].lstrip().rstrip(),
                     "country_text"   : "Offline",
                     "address_text"   : node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip(),
                     "allocated_text" : node[NodeKeys.FinalSubsKeys[6]].lstrip().rstrip(),
                     "consumed_text"  : node[NodeKeys.FinalSubsKeys[7]].lstrip().rstrip(),
                     "source_image"   : self.MeileConfig.resource_path(flagloc),
                     "score"          : nscore,
                     "votes"          : votes,
                     "city"           : city,
                     "md_bg_color"    : "#50507c"
                 },
             )
            print("%s" % node[NodeKeys.FinalSubsKeys[0]].lstrip().rstrip(),end=',')
            sys.stdout.flush()
            
        else:
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
                {
                    "viewclass"      : "RecycleViewSubRow",
                    "moniker_text"   : node[NodeKeys.FinalSubsKeys[1]].lstrip().rstrip(),
                    "sub_id_text"    : node[NodeKeys.FinalSubsKeys[0]].lstrip().rstrip(),
                    "price_text"     : node[NodeKeys.FinalSubsKeys[4]].lstrip().rstrip(),
                    "country_text"   : node[NodeKeys.FinalSubsKeys[5]].lstrip().rstrip(),
                    "address_text"   : node[NodeKeys.FinalSubsKeys[2]].lstrip().rstrip(),
                    "allocated_text" : node[NodeKeys.FinalSubsKeys[6]].lstrip().rstrip(),
                    "consumed_text"  : node[NodeKeys.FinalSubsKeys[7]].lstrip().rstrip(),
                    "source_image"   : self.MeileConfig.resource_path(flagloc),
                    "score"          : nscore,
                    "votes"          : votes,
                    "city"           : city,
                    "md_bg_color"    : "#0d021b"
                    
                },
            )
            print("%s" % node[NodeKeys.FinalSubsKeys[0]].lstrip().rstrip(),end=',')
            sys.stdout.flush()
        
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
            if sub[NodeKeys.FinalSubsKeys[5]] == "Czechia":
                sub[NodeKeys.FinalSubsKeys[5]] = "Czech Republic"
            try: 
                iso2 = OurWorld.our_world.get_country_ISO2(sub[NodeKeys.FinalSubsKeys[5]].lstrip().rstrip()).lower()
            except:
                iso2 = "sc"
            flagloc = floc + iso2 + ".png"
            self.add_sub_rv_data(sub, flagloc)
        self.remove_loading_widget(None)


    @mainthread
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        #from src.cli.sentinel import ConNodes, NodesDictList
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data = []
        if not tab_text:
            tab_text = OurWorld.CONTINENTS[0]
            
        # Check to build Map
        self.build_meile_map()
            
            
        # Subscriptions
        #print(self.NodeTree.NodeTree.show())
        if tab_text == OurWorld.CONTINENTS[6]:
            self.get_config(None)
            self.add_loading_popup("Loading...")
            if self.address:
                
                Clock.schedule_once(self.subs_callback, 1)
                self.ids.country_map.remove_widget(self.MeileMap)
                self.MeileMapBuilt = False
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
                self.get_continent_coordinates(OurWorld.CONTINENTS[0])
        elif tab_text == OurWorld.CONTINENTS[1]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[1]):
                self.add_country_rv_data(self.build_node_data(ncountry))
                self.get_continent_coordinates(OurWorld.CONTINENTS[1])
        elif tab_text == OurWorld.CONTINENTS[2]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[2]):
                self.add_country_rv_data(self.build_node_data(ncountry))
                self.get_continent_coordinates(OurWorld.CONTINENTS[2])
        elif tab_text == OurWorld.CONTINENTS[3]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[3]):
                self.add_country_rv_data(self.build_node_data(ncountry))
                self.get_continent_coordinates(OurWorld.CONTINENTS[3])
        elif tab_text == OurWorld.CONTINENTS[4]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[4]):
                self.add_country_rv_data(self.build_node_data(ncountry))            
                self.get_continent_coordinates(OurWorld.CONTINENTS[4])
        elif tab_text == OurWorld.CONTINENTS[5]:
            for ncountry in self.NodeTree.NodeTree.children(OurWorld.CONTINENTS[5]):
                self.add_country_rv_data(self.build_node_data(ncountry))
                self.get_continent_coordinates(OurWorld.CONTINENTS[5])            
        # Search Criteria
        else:
            pass      
    def get_continent_coordinates(self, c):
        loc = self.MeileLand.ContinentLatLong[c]
        self.MeileMap.center_on(loc[0], loc[1])
            
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
        
        
    def load_country_nodes(self, country, *kwargs):
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
    
    def refresh_wallet(self):
        self.build(None)
    
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
                iso2 = OurWorld.our_world.get_country_ISO2(node[NodeKeys.NodesInfoKeys[4]].lstrip().rstrip()).lower()
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
            
        NodeDataSorted = sorted(NodeData, key=lambda d: d[NodeKeys.NodesInfoKeys[0]])

        self.meta_add_rv_data(NodeDataSorted)
        
    def meta_add_rv_data(self, NodeDataSorted):  
        floc = "../imgs/"
  
        for node in NodeDataSorted:
            iso2 = OurWorld.our_world.get_country_ISO2(node[NodeKeys.NodesInfoKeys[4]].lstrip().rstrip()).lower()
            flagloc = floc + iso2 + ".png"
            self.add_rv_data(node, flagloc)

        
    def add_rv_data(self, node, flagloc):
        self.MeileConfig = MeileGuiConfig()
        speedRate = []
        floc = "../imgs/"
        speed = node[NodeKeys.NodesInfoKeys[5]].lstrip().rstrip().split('+')
        speedAdj = node[NodeKeys.NodesInfoKeys[5]].lstrip().rstrip().split('+')
        
        if "GB" in speedAdj[0]:
            speedRate.append("GB")
        elif "MB" in speedAdj[0]:
            speedRate.append("MB")
        elif "KB" in speedAdj[0]:
            speedRate.append("KB")
        else:
            speedRate.append("B")
        
        if "GB" in speedAdj[1]:
            speedRate.append("GB")       
        elif "MB" in speedAdj[1]:
            speedRate.append("MB")
        elif "KB" in speedAdj[1]:
            speedRate.append("KB")
        else:
            speedRate.append("B")
        
        
        speedAdj[0] = speedAdj[0].replace('GB', '').replace('MB', '').replace('KB', '').replace('B', '')
        speedAdj[1] = speedAdj[1].replace('GB', '').replace('MB', '').replace('KB', '').replace('B', '')
        
        if float(speedAdj[0]) < 0:
                speedAdj[0] = 0
                
        if float(speedAdj[1]) < 0:
                speedAdj[1] = 0
                
        # Values are reversed in nodeTree
        if "0B" in str(str(speedAdj[1]) + speedRate[1]) or "0B" in str(str(speedAdj[0]) + speedRate[0]):
            speedText = "    " + str(speedAdj[1]) + speedRate[1] + "↓" + "," + str(speedAdj[0]) + speedRate[0] + "↑"
        else: 
            speedText = str(speedAdj[1]) + speedRate[1] + "↓" + "," + str(speedAdj[0]) + speedRate[0] + "↑"
            
        if "GB" in speed[0]:
            speed[0] = float(speed[0].replace("GB", '')) * 1024
        elif "MB" in speed[0]:
            speed[0] = float(speed[0].replace("MB", ''))
        elif "KB" in speed[0]:
            speed[0] = float(float(speed[0].replace("KB", '')) / 1024 )
        else:
            speed[0] = 10
        
        if speed[0] < 0:
            speed[0] = 0
        
        if "GB" in speed[1]:
            speed[1] = float(speed[1].replace("GB", '')) * 1024    
        elif "MB" in speed[1]:
            speed[1] = float(speed[1].replace("MB", ''))
        elif "KB" in speed[1]:
            speed[1] = float(float(speed[1].replace("KB", '')) / 1024 )
        else:
            speed[1] = 10
        
        if speed[1] < 0:
            speed[1] = 0
        
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
            
            
        if node[NodeKeys.NodesInfoKeys[1]].lstrip().rstrip() in self.NodeTree.NodeScores:
            nscore = str(self.NodeTree.NodeScores[node[NodeKeys.NodesInfoKeys[1]].lstrip().rstrip()][0])
            votes  = str(self.NodeTree.NodeScores[node[NodeKeys.NodesInfoKeys[1]].lstrip().rstrip()][1])
        else:
            nscore = "null"
            votes  = "0"
            
        if node[NodeKeys.NodesInfoKeys[1]].lstrip().rstrip() in self.NodeTree.NodeLocations:
            city = self.NodeTree.NodeLocations[node[NodeKeys.NodesInfoKeys[1]].lstrip().rstrip()]
        else:
            city = " "
            
        self.ids.rv.data.append(
            {
                "viewclass"    : "RecycleViewRow",
                "moniker_text" : node[NodeKeys.NodesInfoKeys[0]].lstrip().rstrip(),
                "price_text"   : node[NodeKeys.NodesInfoKeys[3]].lstrip().rstrip(),
                "country_text" : node[NodeKeys.NodesInfoKeys[4]].lstrip().rstrip(),
                "address_text" : node[NodeKeys.NodesInfoKeys[1]].lstrip().rstrip(),
                "speed_text"   : speedText,
                "node_score"   : nscore,
                "votes"        : votes,
                "city"         : city,
                "speed_image"  : self.MeileConfig.resource_path(speedimage),
                "source_image" : self.MeileConfig.resource_path(flagloc)
                
            },
        )   
        
    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

        
class RecycleViewCountryRow(MDCard,RectangularElevationBehavior,ThemableBehavior, HoverBehavior):
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
    
    def GetMeileVersion(self):
        return TextStrings.VERSION
    
    def set_previous_screen(self):
        
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="right")
        Meile.app.root.current = WindowNames.MAIN_WINDOW
