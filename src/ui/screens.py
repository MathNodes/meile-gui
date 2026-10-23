from geography.continents import OurWorld
from ui.interfaces import LatencyContent, TooltipMDIconButton, ConnectionDialog, ProtectedLabel, IPAddressTextField, ProtocolTextField, ConnectedNode, QuotaPct,BandwidthBar,BandwidthLabel, MapCenterButton, UploadLabel, DownloadLabel,QRDialogV2RayContent, TimeLabel, QRDialogContent, BTCPayCoinContent
from typedef.win import WindowNames
from cli.sentinel import  NodeTreeData
from typedef.konstants import NodeKeys, TextStrings, MeileColors, HTTParams, IBCTokens, ConfParams, SMSConf
from cli.sentinel import disconnect as Disconnect
import main.main as Meile
from ui.widgets import WalletInfoContent, SeedInfoContent, MDMapCountryButton, RatingContent, NodeRV, NodeRV2, NodeAccordion, NodeRow, NodeDetails, PlanCard, NodeCarousel, SubTypeDialog, SubscribeContent, LoadingSpinner, ShareTypeDialog
from utils.qr import QRCode
from cli.wallet import HandleWalletFunctions
from cli.btcpay import BTCPayDB
from conf.meile_config import MeileGuiConfig
from cli.warp import WarpHandler
from adapters import HTTPRequests, DNSRequests
from fiat import fiat_interface
from cli.v2ray import V2RayHandler
from fiat.stripe_pay.dist import scrtsxx
from adapters.ChangeDNS import ChangeDNS
from adapters.DNSCryptproxy import HandleDNSCryptProxy as dcp
from helpers.helpers import format_byte_size
from helpers.bandwidth import compute_consumed_data, compute_consumed_hours, init_GetConsumedWhileConnected, GetConsumedWhileConnected, GetTotalDataWhileConnected
from helpers.aes import SecureSeed
from helpers.v2ray import generate_v2ray_uri
from helpers.update_checker import UpdateChecker, format_update_message
from ui.update_dialog import UpdateDialog
from coin_api.get_price import GetPriceAPI

from kivy.properties import BooleanProperty, StringProperty, ColorProperty,ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock, mainthread
from kivyoav.delayed import delayable
from kivymd.uix.card import MDCard
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.behaviors import HoverBehavior
#from kivymd.theming import ThemableBehavior
from kivy.core.window import Window
from kivy_garden.mapview import MapMarkerPopup, MapView, MapSource
from kivymd.toast import toast
from kivy.uix.carousel import Carousel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.label.label import MDLabel
from kivy.animation import Animation
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.network.urlrequest import UrlRequest

from requests.auth import HTTPBasicAuth
import sys
import copy
from copy import deepcopy
import re
from urllib.parse import unquote
from time import sleep, time
from functools import partial
from shutil import rmtree
from os import path, chdir, remove
#from save_thread_result import ThreadWithResult
from threading import Thread, Event
from unidecode import unidecode
from datetime import datetime, timedelta
import json
from treelib.exceptions import NodeIDAbsentError
import base64
import subprocess
import traceback
from pathlib import Path

BASE_URL = "https://api.smspool.net"

class WalletRestore(Screen):
    screemanager = ObjectProperty()

    dialog = None

    def __init__(self, **kwargs):
        super(WalletRestore, self).__init__()
        self.build()

    def build(self):
        '''This chooses to display seed phrase box'''
        if Meile.app.manager.get_screen(WindowNames.MAIN_WINDOW).NewWallet:
            self.ids.seed.opacity = 0
            self.ids.seed_hint.opacity = 0
            self.ids.restore_wallet_button.text = "Create"
        else:
            self.ids.seed.opacity = 1
            self.ids.seed_hint.opacity = 1
            self.ids.restore_wallet_button.text = "Restore"

    def restore_wallet_from_seed_phrase(self):
        wallet_password = unidecode(self.ids.password.ids.wallet_password.text)
        wallet_name     = unidecode(self.ids.name.ids.wallet_name.text)
        seed_phrase     = unidecode(self.ids.seed.ids.seed_phrase.text)
        
        '''Add a conditional for seed_phrase.split(" ") and see if len == 12 or 24. Display warning if not'''
        if not wallet_name and not wallet_password:
            self.ids.wallet_name_warning.opacity = 1
            self.ids.wallet_password_warning.opacity = 1
            return
        elif not wallet_password:
            self.ids.wallet_password_warning.opacity = 1
            return
        elif not wallet_name:
            self.ids.wallet_name_warning.opacity = 1
            return
        elif re.match(r"^[A-Za-z0-9 ]*$", wallet_name) is None:
            self.ids.wallet_name_charset_warning.opacity = 1
            return
        elif len(wallet_password) < 8:
            self.ids.wallet_password_warning.opacity = 1
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
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
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
                            text_color=get_color_from_hex(MeileColors.BLACK),
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
        hwf = HandleWalletFunctions()


        try:
            self.dialog.dismiss()
        except Exception as e:
            print(str(e))

        seed_phrase        = unidecode(self.ids.seed.ids.seed_phrase.text)
        wallet_name        = unidecode(self.ids.name.ids.wallet_name.text)
        keyring_passphrase = unidecode(self.ids.password.ids.wallet_password.text)
        if seed_phrase:
            Wallet = hwf.create(wallet_name.lstrip().rstrip(),
                                keyring_passphrase.lstrip().rstrip(),
                                seed_phrase.lstrip().rstrip())
        else:
            Wallet = hwf.create(wallet_name.lstrip().rstrip(),
                                keyring_passphrase.lstrip().rstrip(),
                                None)

        FILE = open(MeileGuiConfig.CONFFILE,'w')

        CONFIG.set('wallet', 'keyname', wallet_name)
        CONFIG.set('wallet', 'address', Wallet['address'])
        CONFIG.set('wallet', 'password', keyring_passphrase.replace('%','%%'))

        CONFIG.write(FILE)
        FILE.close()
        
        ss = SecureSeed()
        encrypted_seed = ss.encrypt_seed(Wallet['seed'], keyring_passphrase)
        with open(path.join(ConfParams.KEYRINGDIR, "seed"), "wb") as f:
            f.write(base64.b64decode(encrypted_seed))
            
        WalletInfo = WalletInfoContent(Wallet['seed'], wallet_name, Wallet['address'], keyring_passphrase)
        self.dialog = MDDialog(
                type="custom",
                content_cls=WalletInfo,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),

                buttons=[
                    MDRaisedButton(
                        text="I saved this",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release=self.switch_window
                    ),
                ],
            )
        self.dialog.open()


class PreLoadWindow(Screen):
    StatusMessages = ["Calculating π...",
                      "Squaring the Circle...",
                      "Solving the Riemann Hypothesis...",
                      "Computing the Monster group M...",
                      "Finding the Galois group of f(x)...",
                      "Solving the Discrete Logarithm Problem...",
                      "Done"]
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
        #self.CreateWarpConfig()
        self.CopyBin()

        chdir(MeileGuiConfig.BASEDIR)

        self.runNodeThread()



    @delayable
    def runNodeThread(self):
        yield 0.6
        thread2 = Thread(target=lambda: self.progress_load())
        thread2.start()
        thread = Thread(target=lambda: self.NodeTree.get_nodes("13s"))
        thread.start()

        self.event = Clock.schedule_interval(partial(self.update_status_text, thread), 1.6)

    @delayable
    def progress_load(self):
        for k in range(1,666):
            yield 0.0375
            self.manager.get_screen(WindowNames.PRELOAD).ids.pb.value += 0.0015


    def CopyBin(self):
        MeileConfig = MeileGuiConfig()
        MeileConfig.copy_bin_dir()

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
        return Config.resource_path(MeileColors.LOGO_HD)

    @delayable
    def update_status_text(self, t, dt):
        yield 1.0

        if not t.is_alive():
            Clock.unschedule(self.event)
            self.manager.get_screen(WindowNames.PRELOAD).status_text = self.StatusMessages[6]
            self.manager.get_screen(WindowNames.PRELOAD).ids.pb.value = 1

            yield 1.0
            self.switch_window()
            
        else:                
            if self.k == 6:
                self.k = 0
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
    MeileConfig = None
    ConnectedNode = None
    menu = None
    MeileLand = None
    SortOptions = ['None', "Moniker", "Price"]
    MenuOptions = ['Refresh', 'Sort', 'DNSCrypt', 'Help', 'Exit']
    Sort = SortOptions[1]
    MeileMap = None
    MeileMapBuilt = False
    NodeSwitch = {"moniker" : None, 
                  "node" : None, 
                  "switch" : False, 
                  'id' : None, 
                  'consumed' : None, 
                  'og_consumed' : None, 
                  'allocated' : None, 
                  'expirary' : None,
                  'deposit': None}
    NewWallet = False
    box_color = ColorProperty('#fcb711')
    clock = None
    PersistentBandwidth = {}
    ConnectedDict = {'v2ray_pid' : None,  'result' : False}
    NodeWidget = None
    Markers = []
    LatLong = []
    SelectedSubscription = {"id" : None,
                            "address" : None,
                            "protocol" : None,
                            "moniker" : None,
                            "allocated" : None,
                            "consumed" : None,
                            "expires" : None,
                            'deposit' : None}
    
    NodeCarouselData = {"moniker" : None,
                        "address" : None,
                        "gb_prices" : None,
                        "hr_prices" : None,
                        "protocol" : None}
    
    SubCaller = False
    PlanID = None
    dnscrypt = False
    PlanConnect = False
    HourlyFirstRun = True
    location_marker = None
    is_running = False
    start_time = 0
    hwf = None


    def __init__(self, node_tree, **kwargs):
        #Builder.load_file("./src/kivy/meile.kv")
        super(MainWindow, self).__init__()

        self.NodeTree = node_tree
        self.MeileLand = OurWorld()
        self.MeileConfig = MeileGuiConfig()

        Clock.schedule_once(self.get_config,1)
        Clock.schedule_once(self.build, 1)
        Clock.schedule_interval(self.update_wallet, 10)
        
        item_height = 50
        max_height = len(self.MenuOptions) * item_height
        
        menu_icons = ["cloud-refresh", "sort", "shield-lock", "help-circle-outline", "exit-to-app"]
        menu_items = [
            {
                "viewclass" : "IconListItem",
                "icon": f"{k}",
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            } for i,k in zip(self.MenuOptions, menu_icons)
        ]
        self.menu = MDDropdownMenu(items=menu_items, 
                                   caller=self.ids.settings_menu,
                                   width_mult=3,
                                   position="center",
                                   max_height=max_height,
                                   md_bg_color=get_color_from_hex(MeileColors.BLACK))
        
    def update_wallet(self, dt):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        
        self.address = CONFIG['wallet'].get('address', None)
    def ping(self):
        CONFIG = self.MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        MNAPI = CONFIG['network'].get('mnapi', HTTParams.SERVER_URL)
        UUID = Meile.app.root.get_screen(WindowNames.PRELOAD).UUID
        try:
            uuid_dict = {'uuid' : "%s" % UUID, 'os' : "l"}
            Request = HTTPRequests.MakeRequest(TIMEOUT=3)
            http = Request.hadapter()
            if MNAPI != HTTParams.SERVER_URL:
                ping = http.post(MNAPI + HTTParams.API_PING_ENDPOINT, json=uuid_dict)
            else:
                ping = http.post(HTTParams.SERVER_URL + HTTParams.API_PING_ENDPOINT, json=uuid_dict)
            if ping.status_code == 200:
                print('ping')
            else:
                print("noping")
        except Exception as e:
            print(str(e))
            pass
            
    
    def connect_routine(self, 
                        node: str = "", 
                        protocol: str = "WireGuard",
                        sub_deposit: str = "0dvpn",
                        units: int = 0,
                        hourly: bool = False,
                        price: dict = {},
                        ):
        
        @delayable
        def connect():
            CONNFILE_OPENED = False            
            self.cd = ConnectionDialog()
            self.set_conn_dialog(self.cd, "")
            yield 0.3
            
            confile = path.join(ConfParams.KEYRINGDIR, "connect.log")
            if path.isfile(confile):
                remove(confile)
                
            with open(confile, 'a'):
                pass
            
            
            self.hwf = HandleWalletFunctions()
            thread = Thread(target=lambda: self.ping())
            thread.start()
            if not self.SubCaller:
                t = Thread(target=lambda: self.hwf.connect(ID, 
                                                      naddress, 
                                                      proto, 
                                                      deposit,
                                                      NodeTree = self.NodeTree, 
                                                      plan=PlanConnect))
                t.start()
            else:
                t = Thread(target=lambda: self.hwf.connect(0, 
                                                      node, 
                                                      protocol, 
                                                      sub_deposit,
                                                      price=price, 
                                                      plan=False, 
                                                      units=units, 
                                                      hourly=hourly))
                t.start()
                self.SubCaller = False
            
            while t.is_alive():
                yield 0.0314
                self.cd.ids.pb.value += 0.00085

                try:
                    if path.isfile(confile) and not CONNFILE_OPENED:
                        conndesc = open(confile, 'r')
                        CONNFILE_OPENED = True
                    elif path.isfile(confile):
                        self.update_conn_status(conndesc.readlines()[-1])
                except IndexError:
                    pass
                    
                
            #conndesc.close()
            self.cd.ids.pb.value = 1
            
            self.ConnectedDict = deepcopy(self.hwf.connected)
            yield 0.420
            try: 
                if self.hwf.connected['result']:
                    print("CONNECTED!!!")
                    self.CONNECTED = True
                    Moniker = self.NodeCarouselData['moniker']
                    self.NodeCarouselDataConnectedNode = deepcopy(self.NodeCarouselData)
                    
                    if hourly:
                        self.setQuotaClock(units, True)
                    else:
                        self.setQuotaClock(units, False)
                        
                    self.setTotalBytesClock()
                    self.remove_loading_widget2()
                    #print("REmove loading Widget")
                    # Here change the Connection button to a "Disconnect" button then display dialogAdd commentMore actions
                    self.set_protected_icon(True, Moniker)
                    self.toggle_time_widget()
                    #if "V2Ray" in [proto, protocol]:
                    connected_content = QRDialogV2RayContent()
                    QRcode = QRCode()
                    if "V2Ray" in [proto, protocol]:
                        uri = generate_v2ray_uri(path.join(ConfParams.KEYRINGDIR,"v2ray_config.json"))
                        connected_content.ids.uri.text = uri
                        connected_content.ids.warning_comment.text = "Scan the QR code or import the URI string into the V2RayNG mobile app. You must do this before you disconnect in Meile. https://dvpn.my/v2ray"
                        connected_content.ids.qr_img.source = QRcode.generate_qr_code(uri, "v2ray")
                    elif "WireGuard" in [proto,protocol]:
                        WG_PATH = path.join(ConfParams.KEYRINGDIR,"wg99.conf")
                        with open(WG_PATH, "r") as f:
                            wg_config = f.read()
                        wg_config = wg_config.replace("127.0.0.1,", "")
                        connected_content.ids.uri.text = wg_config
                        connected_content.ids.warning_comment.text = "Scan the QR code or input the config with the official Wireguard app. You must do this before you disconnect in Meile. https://dvpn.my/wireguard"
                        connected_content.ids.qr_img.source = QRcode.generate_wg_qr_code(WG_PATH, self.NodeCarouselData['moniker'])

                    else:
                        uri = "NULL"
                        connected_content.ids.uri.text = uri
                        connected_content.ids.warning_comment.text = "Hysteria2, XRay, and AmneziaWG quick-connect QR-codes are not available at this time"
                        connected_content.ids.qr_img.source = QRcode.generate_qr_code(uri, "v2ray")
                            
                    self.dialog = MDDialog(
                        title="Connected!",
                        type="custom",
                        content_cls=connected_content,
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                        buttons=[
                                MDRaisedButton(
                                    text="OK",
                                    theme_text_color="Custom",
                                    text_color=get_color_from_hex(MeileColors.BLACK),
                                    on_release=partial(self.call_ip_get,
                                                       True,
                                                       Moniker
                                                       )
                                ),
                            ]
                    )
                    self.dialog.open()
                    
                else:
                    self.remove_loading_widget2()
                    
                    self.dialog = MDDialog(
                        title="Something went wrong. Not connected: ",
                        text=self.hwf.connected['status'] if self.hwf.connected['status'] else "Connection Error",
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                        buttons=[
                                MDFlatButton(
                                    text="OK",
                                    theme_text_color="Custom",
                                    text_color=get_color_from_hex(MeileColors.MEILE),
                                    on_release=partial(self.call_ip_get, False, "")
                                ),])
                    self.dialog.open()
                    
            except (TypeError, KeyError) as e:
                print(str(e))
                self.remove_loading_widget2()
                self.dialog = MDDialog(
                    title="Something went wrong. Not connected: User cancelled",
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                            MDFlatButton(
                                text="OK",
                                theme_text_color="Custom",
                                text_color=get_color_from_hex(MeileColors.MEILE),
                                on_release=partial(self.call_ip_get, False, "")
                            ),])
                self.dialog.open()
        
        if self.ids.connect_button.source == self.return_connect_button("c"):
            #print(self.NodeCarouselData)
            if self.PlanID:
                ID       = self.PlanID
                naddress = self.NodeCarouselData['address']
                self.node_address = deepcopy(naddress)
                proto    = self.NodeCarouselData['protocol']
                deposit  = "dvpn"
                PlanConnect = True
                connect()
                return
            elif self.SubCaller:
                print("Calling for a session subscription")
                proto = None
                connect()
                    
            else:
                self.remove_loading_widget2()
                self.dialog = MDDialog(
                    title="No plan selected. Select a plan before trying to connect.",
                    md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    buttons=[
                            MDFlatButton(
                                text="OK",
                                theme_text_color="Custom",
                                text_color=get_color_from_hex(MeileColors.MEILE),
                                on_release=partial(self.call_ip_get, False, "")
                            ),])
                self.dialog.open()
                return 
            
        else:
            self.disconnect_from_node()
            self.HourlyFirstRun = True
            self.reset_stopwatch()
            try: 
                self.clock.cancel()
            except:
                print("No Clock... Yet")
            self.clock = None
            
            try: 
                self.clockBytes.cancel()
            except:
                print("No Clock Bytes... Yet")
            self.clockBytes = None
        
    def toggle_time_widget(self):
            if not self.is_running:
                self.start_stopwatch()
            else:
                self.stop_stopwatch()
                
    def start_stopwatch(self):
        self.is_running = True
        if self.start_time == 0:
            self.start_time = time()
        Clock.schedule_interval(self.update_time, 1.0)
        
        
    def stop_stopwatch(self):
        self.is_running = False
        Clock.unschedule(self.update_time)
        
    def update_time(self, dt):
        if self.is_running:
            self.elapsed_time = time() - self.start_time
            self.time_widget.text = self.format_time(self.elapsed_time)
        return True
    
    def format_time(self, seconds):
        td = timedelta(seconds=int(seconds))
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"      
                  
    def reset_stopwatch(self):
        self.is_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.time_widget.text = '00:00:00'
        Clock.unschedule(self.update_time)
        
    def qrcode_connection_sharing(self):
        
        share_content = ShareTypeDialog()
        
        self.dialog = MDDialog(
            title="Protocol to Connection Share",
            type="custom",
            content_cls=share_content,
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
        )
        self.dialog.open()
        
            
    def setTotalBytesClock(self):
        self.clockBytes = Clock.create_trigger(self.GetUpDownBytes,10)
        try:
            self.clockBytes()
        except:
            pass
        return True
    
    def GetUpDownBytes(self, dt):
        data_bytes = GetTotalDataWhileConnected()
        print(f"data bytes: {data_bytes}")
        self.upload_widget.text = f"{data_bytes['sent']}↑"
        self.download_widget.text = f"{data_bytes['rcvd']}↓"
        print(self.upload_widget.text)
        print(self.download_widget.text)
        try:
            self.clockBytes()
        except:
            pass
        return True        
       
         
    def setQuotaClock(self,units, hourly):
        if hourly:
            # Need first call to report initial values to update UI, then set clock to reoccur. 
            self.connected_quota(units, 0, hourly, None)
            
            self.clock = Clock.create_trigger(partial(self.connected_quota,
                                                    units,
                                                    0,
                                                    hourly),120)
            self.clock()
            return True
        
        BytesDict = init_GetConsumedWhileConnected()
        print(BytesDict)
        self.UpdateQuotaForNode(units,
                                BytesDict,
                                None)
        
        self.clock = Clock.create_trigger(partial(self.UpdateQuotaForNode,
                                                  units,
                                                  BytesDict),120)

        self.clock()
        
    def connected_quota(self, allocated, consumed, hourly, dt):
              
        if self.CONNECTED:
            #allocated = float(allocated.replace('GB',''))
            if hourly:
                self.allocated        = float(allocated)
                if self.HourlyFirstRun:
                    self.expiration       = datetime.now() + timedelta(hours=self.allocated)
                    self.HourlyFirstRun   = False
                formatted_expiration  = self.expiration.strftime('%Y-%m-%d %H:%M:%S')
                self.consumed         = compute_consumed_hours(self.allocated,formatted_expiration)
                self.quota_pct.text   = str(round(float(float(self.consumed/self.allocated)*100),2)) + "%"
                self.quota.value      = round(float(float(self.consumed/self.allocated)*100),2)
                try: 
                    self.clock()
                except Exception as e:
                    return False 
            else:
                self.allocated = allocated
                self.consumed  = compute_consumed_data(consumed)
                self.quota_pct.text = str(round(float(float(self.consumed/self.allocated)*100),2)) + "%"
                return round(float(float(self.consumed/self.allocated)*100),3)
        else:
            self.quota_pct.text = "0.00%"
            self.quota.value    = 0
            return float(0)
        
    # Used solely for data subscriptions    
    def UpdateQuotaForNode(self,units, BytesDict, dt):
        try:
            consumed = GetConsumedWhileConnected(compute_consumed_data("0GB"),BytesDict)
            self.quota.value = self.connected_quota(units, consumed, False, None)
            print("%s,%sGB - %s%%" % (consumed,
                                    units,
                                    self.quota.value))
        except Exception as e:
            print(str(e))
            print("Error getting bandwidth!")
            
        try: 
            self.clock()
        except Exception as e:
            print("Error running clock()")
            pass
                                      
    def menu_open(self):
        self.menu.open()
    
    def menu_callback(self, selection):
        self.menu.dismiss()
        if selection == self.MenuOptions[0]:
            self.Refresh()
        elif selection == self.MenuOptions[1]:
            pass
        elif selection == self.MenuOptions[2]:
            self.start_dnscrypt()
        elif selection == self.MenuOptions[3]:
            self.build_help_screen_interface()
        elif selection == self.MenuOptions[4]:
            self.disconnect_from_node()
            if self.dnscrypt:
                dnsproxy = dcp()
                
            sys.exit(0)
    
    @delayable
    def start_dnscrypt(self):
        dnsproxy = dcp()
        if not self.dnscrypt:
            self.add_loading_popup("Starting DNSCryptProxy with user selected resolvers...")
            yield 1.3
            t = Thread(target=lambda: dnsproxy.dnscrypt(state=True))
            t.start()
            
            while t.is_alive():
                print(".", end="")
                yield 0.5
                
            self.dnscrypt = True    
            self.remove_loading_widget(None)
            self.display_dnscrypt_success(dnsproxy.dnscrypt_pid)
            self.ids.doh.opacity = 1
                
        else:
            self.add_loading_popup("Terminating DNSCryptProxy...")
            yield 1.3
            
            t = Thread(target=lambda: dnsproxy.dnscrypt(state=False))
            t.start()
            
            while t.is_alive():
                print(".", end="")
                yield 0.5
                
            self.dnscrypt = False
            self.remove_loading_widget(None)
            self.ids.doh.opacity = 0
    
    def build(self, dt):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        
        self.address = CONFIG['wallet'].get('address', None)
        if not self.address:
            self.create_new_wallet()
        # Check to build Map
        self.build_meile_map()

        # Build alphabetical country recyclerview tree data
        self.build_country_tree()
        print("Running: nonblock_get_ip_address()")
        thread = Thread(target=lambda: self.nonblock_get_ip_address(self.get_ip_address, True))
        thread.start() 
        
        if not getattr(self, '_update_checked', False):
            self._update_checked = True
            Thread(target=lambda: self._check_update_background(),daemon=True).start()
            
        
    def create_new_wallet(self):
        hwf = HandleWalletFunctions()
        
        wallet_info = hwf.generate_random_strings()
        wallet_data = hwf.create(wallet_info[0], wallet_info[1])
        
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        
        FILE = open(MeileGuiConfig.CONFFILE,'w')

        CONFIG.set('wallet', 'keyname', wallet_info[0])
        CONFIG.set('wallet', 'address', wallet_data['address'])
        CONFIG.set('wallet', 'password', wallet_info[1].replace('%','%%'))

        CONFIG.write(FILE)
        FILE.close()
        
        ss = SecureSeed()
        encrypted_seed = ss.encrypt_seed(wallet_data['seed'], wallet_info[1])
        with open(path.join(ConfParams.KEYRINGDIR, "seed"), "wb") as f:
            f.write(base64.b64decode(encrypted_seed))

    def build_country_tree(self):

        CountryTree = []
        CountryTreeTags = []
        # Add counry cards
        for ncountry in self.NodeTree.NodeTree.children(TextStrings.RootTag.lower()):
            CountryTree.append(ncountry)
            CountryTreeTags.append(ncountry.tag)

        CTTagsSorted = sorted(CountryTreeTags)
        #print(CTTagsSorted)
        for tag in CTTagsSorted:
            for ctree in CountryTree:
                if tag == ctree.tag:
                    self.add_country_rv_data(self.build_node_data(ctree))


    def build_node_data(self, ncountry):
        from typedef.konstants import MeileColors
        floc = MeileColors.FLOC
        NodeCountries = {}

        try:
            iso2 = OurWorld.our_world.get_country_ISO2(ncountry.tag).lower()
        except:
            iso2 = OurWorld.our_world.get_country_ISO2("Seychelles").lower()
        flagloc = path.join(floc, "flags", f"{iso2}.png")

        NodeCountries['number']  = len(self.NodeTree.NodeTree.children(ncountry.tag))
        NodeCountries['country'] = ncountry.tag
        NodeCountries['flagloc'] = flagloc

        return NodeCountries

    def build_meile_map(self):

        if not self.MeileMapBuilt:
            self.MeileMap = MapView(zoom=2,
                                    background_color=get_color_from_hex(MeileColors.MAP_BG_COLOR))
            source = MapSource(url=MeileColors.CARTO_MAP + f"?key={scrtsxx.CARTO_API}",
                               cache_key="cartodarknew2",
                               tile_size=256,
                               image_ext="png",
                               attribution="© OpenStreetMap © CARTO",
                               min_zoom=1)
            #self.MeileMap.map_source = "osm"
            self.MeileMap.map_source = source

            layout = FloatLayout(size_hint=(1,1))
            bw_label             = BandwidthLabel()
            self.quota           = BandwidthBar()
            self.quota_pct       = QuotaPct()
            self.map_widget_1    = IPAddressTextField()
            self.map_widget_2    = ConnectedNode()
            self.map_widget_3    = ProtectedLabel()
            self.map_widget_4    = ProtocolTextField()
            self.time_widget     = TimeLabel()
            self.upload_widget   = UploadLabel()
            self.download_widget = DownloadLabel()
            recenter             = MapCenterButton()
            
            recenter.on_release = self.recenter_map
            
            self.upload_widget.font_name = self.upload_widget.get_font()
            self.upload_widget.font_size = "30sp"
            self.upload_widget.text = f"0MB↑"
            self.download_widget.font_name = self.upload_widget.get_font()
            self.download_widget.font_size = "30sp"
            self.download_widget.text = f"0MB↓"
            self.MeileMap.bind(lat=self.check_boundaries)
            self.MeileMap.bind(lon=self.check_boundaries)
            
            layout.add_widget(self.MeileMap)
            layout.add_widget(self.map_widget_1)
            layout.add_widget(self.map_widget_2)
            layout.add_widget(self.map_widget_3)
            layout.add_widget(self.map_widget_4)
            layout.add_widget(bw_label)
            layout.add_widget(self.quota)
            layout.add_widget(self.quota_pct)
            layout.add_widget(recenter)
            layout.add_widget(self.upload_widget)
            layout.add_widget(self.download_widget)
            layout.add_widget(self.time_widget)
            

            self.quota.value = 0
            self.quota_pct.text = "0%"

            self.carousel = Carousel(direction='right')
            self.ids.country_map.add_widget(self.carousel)
            self.carousel.add_widget(layout)
            self.AddCountryNodePins(False)
            self.MeileMapBuilt = True
            
    def _check_update_background(self):
        checker = UpdateChecker()
        update_info = checker.check_for_update()

        if update_info is not None:
            Clock.schedule_once(lambda dt: self._show_update_dialog(update_info), 1.0)
            
    def _show_update_dialog(self, update_info):
        message = format_update_message(update_info)
        UpdateDialog(
            message=message,
            download_url=update_info["download_url"]
        ).show()

    def check_boundaries(self, instance, value):
        if self.MeileMap.zoom == 1:
            self.recenter_map()
            
    def add_country_rv_data(self, NodeCountries):
        self.ids.rv.data.append(
            {
                "viewclass"      : "RecycleViewCountryRow",
                "num_text"       : str(NodeCountries['number']) + " Nodes",
                "country_text"   : NodeCountries['country'],
                "source_image"   : self.MeileConfig.resource_path(NodeCountries['flagloc'])
            },
        )

    def refresh_country_recycler(self):
        self.ids.rv.data.clear()
        self.build_country_tree()
        self.ids.rv.refresh_from_data()

    def AddCountryNodePins(self, clear):
        Config = MeileGuiConfig()
        try:

            if clear:
                for m in self.Markers:
                    self.MeileMap.remove_marker(m)
                self.Markers.clear()


            for ncountry in self.NodeTree.NodeTree.children(TextStrings.RootTag.lower()):
                try:
                    loc = self.MeileLand.CountryLatLong[ncountry.tag]
                    marker = MapMarkerPopup(lat=loc[0], lon=loc[1], source=Config.resource_path(MeileColors.MAP_MARKER))
                    marker.add_widget(MDMapCountryButton(text='%s - %s' %(ncountry.tag, len(self.NodeTree.NodeTree.children(ncountry.tag))),
                                                   theme_text_color="Custom",
                                                   md_bg_color=get_color_from_hex(MeileColors.BLACK),
                                                   text_color=(1,1,1,1),
                                                   on_release=partial(self.load_country_nodes, ncountry.tag)
                                                   ))

                    self.Markers.append(marker)
                    self.MeileMap.add_marker(marker)
                except:
                    continue
        except Exception as e:
            print(str(e))
            pass

        #self.get_continent_coordinates(self.MeileLand.CONTINENTS[0])
    
    def get_config(self, dt):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        self.address = CONFIG['wallet'].get("address")
        
    def on_enter_search(self):
        search_string = self.ids.search_box.text
        try: 
            key_string, value_string = search_string.split(',')
        except ValueError:
            toast(text="Please format the search like: key: _, value: _", duration=3.5)
            return 
        try: 
            key_string = key_string.split(':')[-1].lstrip().rstrip()
        except:
            toast(text="key and value must be followed by a :", duration=3.5)
            return
        try: 
            value_string = value_string.split(':')[-1].lstrip().rstrip()
        except:
            toast(text="Value string has improper formatting")
        
        if key_string not in NodeKeys.NodesInfoKeys:
            toast(text="Invalid key", duration=3.5)
            return
        
        print(f"key: {key_string}, value: {value_string}")
        self.NodeTree.search(key=key_string,value=value_string)
        self.refresh_country_recycler()
    
    def restore_results(self):
        self.NodeTree.restore_tree()
        self.refresh_country_recycler()
        self.PlanID = None

    @mainthread
    def display_warp_success(self):

        self.dialog = MDDialog(
            text="You are now using DoH (DNS-over-HTTPS) and your DNS traffic is encrypted from prying eyes.",
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDRaisedButton(
                    text="Okay",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.BLACK),
                    on_release=self.remove_loading_widget
                ),
            ],
        )
        self.dialog.open()
        
    @mainthread
    def display_dnscrypt_success(self, pid):

        self.dialog = MDDialog(
            text=f"You are now using DoH (DNS-over-HTTPS) and your DNS traffic is encrypted from prying eyes. {pid}",
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDRaisedButton(
                    text="Okay",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.BLACK),
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
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                    MDRaisedButton(
                        text="OKAY",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
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
            thread = Thread(target=lambda: self.nonblock_get_ip_address(self.get_ip_address))
            thread.start()
        else:
            print("FAIL")

    def get_logo(self):
        self.MeileConfig = MeileGuiConfig()
        return self.MeileConfig.resource_path(MeileColors.LOGO)

    def get_logo_text(self):
        self.MeileConfig = MeileGuiConfig()
        return self.MeileConfig.resource_path(MeileColors.LOGO_TEXT)


    @mainthread
    def set_ip(self):
        self.map_widget_1.text = self.ip
    
    def nonblock_get_ip_address(self, callback, start: bool = False):
        try:
            resolver = DNSRequests.MakeDNSRequest(domain=HTTParams.IPAPIDNS, timeout=5, lifetime=6.5)
            ifconfig = resolver.DNSRequest()
            if ifconfig:
                print("%s:%s" % (HTTParams.IPAPIDNS, ifconfig))
                Request = HTTPRequests.MakeRequest()
                http = Request.hadapter()
                req = http.get(HTTParams.IPAPI)
                ifJSON = req.json()
                print(ifJSON)
                with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'w') as f:
                    f.write(json.dumps(ifJSON))
                callback(None, start)
                return True
                
            else:
                print("Error resolving ip-api.com... defaulting...")
                with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'w') as f:
                    f.write(json.dumps('{}'))
                return False
        except Exception as e:
            print(str(e))
            with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'w') as f:
                f.write(json.dumps('{}'))
            return False
        
    def get_ip_address(self, dt, startup: bool = False):
        #self.old_ip = self.ip
        try:
            with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'r') as f:
                data = f.read()
                
            ifJSON = json.loads(data)
            if not ifJSON:
                return False
            
            self.ip = str(ifJSON['query'])
            self.set_ip()
            self.LatLong.clear()
            try:
                self.LatLong.append(ifJSON['lat'])
                self.LatLong.append(ifJSON['lon'])
            except:
                print("No Lat/Long")
                try:
                    country = ifJSON['country']
                    loc = self.MeileLand.CountryLatLong[country]
                    self.LatLong.append(loc[0])
                    self.LatLong.append(loc[1])
                except:
                    print("No Country...Defaulting to my dream.")
                    loc = self.MeileLand.CountryLatLong["Seychelles"]
                    self.LatLong.append(loc[0])
                    self.LatLong.append(loc[1])
            if not startup:        
                self.zoom_country_map()
                self.add_location_marker()
            return True
        except Exception as e:
            print(str(e))
            return False
        
    @delayable        
    def change_dns(self):
        MeileConfig = MeileGuiConfig()
        config = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        yield 0.6
        if self.dialog:
            self.dialog.dismiss()
        self.add_loading_popup("DNS Resolver error... Switching to Cloudflare")
        yield 0.314
        
        ChangeDNS(dns=config['network']['dns']).change_dns()
        thread = Thread(target=lambda: self.nonblock_get_ip_address(self.get_ip_address))
        thread.start()
        self.remove_loading_widget(None)
        
    @mainthread
    def disconnect_from_node(self):
        try:
            if self.ConnectedDict['v2ray_pid'] is not None:
                try:
                    returncode, self.CONNECTED = Disconnect(self.NodeCarouselDataConnectedNode['protocol'])
                    print("Disconnect RTNCODE: %s" % returncode)
                    thread = Thread(target=lambda: self.nonblock_get_ip_address(self.get_ip_address))
                    thread.start()
                    self.set_protected_icon(False, "")
                except Exception as e:
                    print(str(e))
                    print("Something went wrong")
                    
            elif self.CONNECTED == None:
                returncode, self.CONNECTED = Disconnect(self.NodeCarouselDataConnectedNode['protocol'])
                print("Disconnect RTNCODE: %s" % returncode)
                thread = Thread(target=lambda: self.nonblock_get_ip_address(self.get_ip_address))
                thread.start()
                self.set_protected_icon(False, "")
                
            elif self.CONNECTED == False:
                print("Disconnected!")
                return True
            
            else:
                returncode, self.CONNECTED = Disconnect(self.NodeCarouselDataConnectedNode['protocol'])
                print("Disconnect RTNCODE: %s" % returncode)
                thread = Thread(target=lambda: self.nonblock_get_ip_address(self.get_ip_address))
                thread.start()
                self.set_protected_icon(False, "")
                
            #self.warp_disconnect(None)
            self.dialog = None
            rating_dialog = RatingContent(self.NodeCarouselData['moniker'], self.NodeCarouselData['address'])
            
            self.dialog = MDDialog(
                title="Node Rating",
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
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
                        text_color=get_color_from_hex(MeileColors.BLACK),
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
                               'allocated' : None,
                               'expirary' : None
                               }
            self.NodeCarouselDataConnectedNode = None
            return True
        except Exception as e:
            print(str(e))
            self.dialog = None
            self.dialog = MDDialog(
            text="Error disconnecting from node",
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
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
            toast(text="Error submitting rating...", duration=3.5)
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
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
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
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release=partial(self.wallet_restore, False)
                    ),
                ],
            )
            self.dialog.open()
        else:
            self.build_wallet_interface()



    @mainthread
    def add_loading_popup(self, title_text):
        self.dialog = None
        self.dialog = MDDialog(title=title_text,md_bg_color=get_color_from_hex(MeileColors.BLACK))
        self.dialog.open()

    @delayable
    def Refresh(self):
        self.remove_loading_widget(None)
        self.AddCountryNodePins(True)
        yield 0.314
        cd = ConnectionDialog()
        self.set_conn_dialog(cd, "Reloading Nodes...")
        yield 0.314
        try:
            self.NodeTree.NodeTree = None
            t = Thread(target=lambda: self.NodeTree.get_nodes("13s"))
            t.start()
            l = 13
            pool = l*100
            inc = float(1/pool)
            while t.is_alive():
                yield 0.0365
                cd.ids.pb.value += inc

            cd.ids.pb.value = 1
        except Exception as e:
            print(str(e))
            pass

        # Clear out Subscriptions
        self.NodeTree.SubResult = []
        # Redraw Map Pins
        self.AddCountryNodePins(False)
        self.refresh_country_recycler()
        self.remove_loading_widget(None)
        
    def recenter_map(self):
        self.MeileMap.zoom = 2
        self.MeileMap.center_on(0, 0)
        
    def get_continent_coordinates(self, c):
        loc = self.MeileLand.ContinentLatLong[c]
        self.MeileMap.zoom = 4
        self.MeileMap.center_on(loc[0], loc[1])

    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)

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


    def clear_node_carousel(self):
        self.NodeCarouselData = {"moniker" : None,
                                "address" : None,
                                "gb_prices" : None,
                                "hr_prices" : None,
                                "protocol" : None}
        
    def build_wallet_interface(self):
        # Clear out any previous Carousel Data
        self.clear_node_carousel()
        CONFIG = self.MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        address = CONFIG['wallet'].get('address', None)
        if not address: 
            print("Prompting to create wallet")
            self.wallet_dialog()
            
        else:
            print("Wallet already exists...")
            Meile.app.root.add_widget(WalletScreen(name=WindowNames.WALLET, ADDRESS=CONFIG['wallet'].get('address', '')))
            Meile.app.root.transition = SlideTransition(direction = "up")
            Meile.app.root.current = WindowNames.WALLET

    def build_help_screen_interface(self):
        # Clear out any previous Carousel Data
        self.clear_node_carousel()
        Meile.app.root.add_widget(HelpScreen(name=WindowNames.HELP))
        Meile.app.root.transition = SlideTransition(direction = "left")
        Meile.app.root.current = WindowNames.HELP

    def build_settings_screen_interface(self):
        # Clear out any previous Carousel Data
        self.clear_node_carousel()
        Meile.app.root.add_widget(SettingsScreen(name=WindowNames.SETTINGS))
        Meile.app.root.transition = SlideTransition(direction = "down")
        Meile.app.root.current = WindowNames.SETTINGS
        
    def build_smspol_screen_interface(self):
        # Clear out any previous Carousel Data
        self.clear_node_carousel()
        Meile.app.root.add_widget(SMSPoolScreen(name=WindowNames.SMS))
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.SMS

    def switch_window(self, window):
        # Clear out any previous Carousel Data
        self.clear_node_carousel()
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = window

    def switch_to_sub_window(self):
        # Clear out any previous Carousel Data
        # Check if we are subscribing from Carousel. If yes, don't clear the data. 
        if not self.SubCaller:
            self.clear_node_carousel()
        try:
            if self.SubCaller:
                if len(self.carousel.slides) >= 3:
                    self.carousel.remove_widget(self.carousel.slides[-1])
                    self.carousel.remove_widget(self.carousel.slides[-1])
            else:        
                self.carousel.remove_widget(self.NodeWidget)
        except Exception as e:
            print(str(e))
        self.NodeWidget = SubscriptionScreen(name=WindowNames.SUBSCRIPTIONS, node_tree=self.NodeTree)
        self.carousel.add_widget(self.NodeWidget)
        self.carousel.load_slide(self.NodeWidget)
    

    def switch_to_plan_window(self):
        # Clear out any previous Carousel Data
        self.clear_node_carousel()
        try:
            while len(self.carousel.slides) > 1:
                self.carousel.remove_widget(self.carousel.slides[-1])
        except Exception as e:
            print(str(e))
        self.NodeWidget = PlanScreen(name=WindowNames.PLAN)
        self.carousel.add_widget(self.NodeWidget)
        self.carousel.load_slide(self.NodeWidget)

    def close_sub_window(self):
        while len(self.carousel.slides) > 1:
            self.carousel.remove_widget(self.carousel.slides[-1])
            
        self.carousel.load_slide(self.carousel.slides[0])

    def zoom_country_map(self):
        try:
            self.MeileMap.zoom = 7
            self.MeileMap.center_on(self.LatLong[0],self.LatLong[1])
        except Exception as e:
            print(str(e))
            pass

    def set_conn_dialog(self, cd, message):
        self.dialog = None
        self.dialog = MDDialog(
                        type="custom",
                        content_cls=cd,
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    )
        # The message used to be the (bold, centered) dialog title.  It now
        # belongs to the small status line of the ConnectionDialog itself.
        cd.set_status(message)
        self.dialog.open()
        
    def update_conn_status(self, status):
        '''Feed the wallet's latest connect.log line to the open dialog: it walks
        the status line under the progress bar and the stage pipeline.'''
        if self.dialog:
            self.dialog.content_cls.set_status(status)
            

    def load_country_nodes(self, country, *kwargs):
        NodeTree = NodeTreeData(self.NodeTree.NodeTree)
        try:
            while len(self.carousel.slides) > 1:
                self.carousel.remove_widget(self.carousel.slides[-1])
        except Exception as e:
            print(str(e))
            pass

        self.NodeWidget = NodeScreen(name="nodes",
                                     node_tree=NodeTree,
                                     country=country,
                                     sort=self.Sort)
        self.carousel.add_widget(self.NodeWidget)
        self.carousel.load_slide(self.NodeWidget)
    
    def call_ip_get(self,result, moniker,  *kwargs):
        if result:
            self.CONNECTED = True
        else:
            self.CONNECTED = False
            self.set_protected_icon(False, " ")
            
        if not self.get_ip_address(None):
            self.remove_loading_widget(None)
            self.change_dns()
            self.close_sub_window()
        else:
            self.remove_loading_widget(None)
            self.close_sub_window()
            
    def add_location_marker(self):
        self.remove_location_marker()
        Config = MeileGuiConfig()
        
        with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'r') as f:
            data = f.read()
            
        ifJSON = json.loads(data)
        if not ifJSON:
            return False
        
        self.location_marker = MapMarkerPopup(lat=self.LatLong[0], lon=self.LatLong[1], source=Config.resource_path(MeileColors.LOC_MARKER))
        self.location_marker.add_widget(MDMapCountryButton(text='%s, %s' %(ifJSON['city'], ifJSON['country']),
                                                   theme_text_color="Custom",
                                                   md_bg_color=get_color_from_hex(MeileColors.BLACK),
                                                   text_color=(1,1,1,1),
                                                   ))
        
        anim = (
            Animation(opacity=0.4, duration=0.8, t='in_out_sine') +
            Animation(opacity=1.0, duration=0.8, t='in_out_sine')
        )
        anim.repeat = True
        anim.start(self.location_marker)
        

        self.Markers.append(self.location_marker)
        self.MeileMap.add_marker(self.location_marker)
    
    def remove_location_marker(self):
        if self.location_marker:
            self.MeileMap.remove_marker(self.location_marker)
            self.Markers.remove(self.Markers[-1])
            
    def set_protected_icon(self, setbool, moniker):
        
        try: 
            if setbool:
                self.map_widget_2.text = moniker
                self.map_widget_3.text = "PROTECTED"
                anim = (
                    Animation(opacity=0.2, duration=0.8, t='in_out_sine') +
                    Animation(opacity=1.0, duration=0.8, t='in_out_sine')
                )
                anim.repeat = True
                anim.start(self.map_widget_3)
                self.map_widget_4.text = self.NodeCarouselData['protocol']
                self.ids.connect_button.source = self.return_connect_button("d")
            else:
                self.map_widget_2.text = moniker
                self.map_widget_3.text = "UNPROTECTED"
                Animation.cancel_all(self.map_widget_3)
                self.map_widget_4.text = ""
                self.ids.connect_button.source = self.return_connect_button("c")
        except Exception as e:
            print(str(e))
            return
            
    @mainthread
    def remove_loading_widget(self, dt):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            pass
    
    def remove_loading_widget2(self):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            pass
    
    
    def return_connect_button(self, text):
        MeileConfig = MeileGuiConfig()
        if text == "c":
            return MeileConfig.resource_path(MeileColors.CONNECT_BUTTON)
        else:
            return MeileConfig.resource_path(MeileColors.DISCONNECT_BUTTON)
        
    def closeDialog(self, inst):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except:
            print("Dialog is NONE")
            return
        
class WalletScreen(Screen):
    text = StringProperty()
    ADDRESS = None
    MeileConfig = None
    dialog = None
    qr_address = StringProperty()
    MenuOptions = ["Refresh", "New Wallet", "View Seed"]

    def __init__(self, ADDRESS,  **kwargs):
        super(WalletScreen, self).__init__()
        self.ADDRESS = ADDRESS
        print("WalletScreen, ADDRESS: %s" % self.ADDRESS)
        self.wallet_address = self.ADDRESS
        
        item_height = 50
        max_height = len(self.MenuOptions) * item_height

        menu_icons = ["refresh-circle", "wallet-plus", "lock-open-variant"]
        menu_items = [
            {
                "viewclass" : "IconListItem",
                "icon": f"{k}",
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            } for i,k in zip(self.MenuOptions, menu_icons)
        ]
        self.menu = MDDropdownMenu(items=menu_items, 
                                   caller=self.ids.wallet_menu,
                                   width_mult=3,
                                   position="center",
                                   max_height=max_height,
                                   md_bg_color=get_color_from_hex(MeileColors.BLACK))
        Clock.schedule_once(self.build)

    def build(self, dt):
        Wallet = HandleWalletFunctions()
        self.SetBalances(Wallet.get_balance(self.ADDRESS))
        
    def copy_to_clipboard(self, text):
        Clipboard.copy(text)
        toast(text="Address copied!", duration=3.5)

    def refresh_wallet(self):
        self.build(None)

    def menu_open(self):
        self.menu.open()
        
    def menu_callback(self, selection):
        self.menu.dismiss()
        if selection == self.MenuOptions[0]:
            self.refresh_wallet()
        elif selection == self.MenuOptions[1]:
            self.open_dialog_new_wallet()
        elif selection == self.MenuOptions[2]:
            self.display_seed()
        '''
        elif selection == self.MenuOptions[2]:
            self.open_fiat_interface()
        '''

        
    def open_dialog_new_wallet(self):
        self.dialog = MDDialog(
            text="Warning, if you continue your current wallet will be deleted",
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDFlatButton(
                    text="CONTINUE",
                    theme_text_color="Custom",
                    text_color=(1,1,1,1),
                    on_release=self.destroy_wallet_open_wallet_dialog
                ),
                MDRaisedButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.BLACK),
                    on_release=self.closeDialog
                ),
            ],
        )
        self.dialog.open()

    def destroy_wallet_open_wallet_dialog(self, _):
        keyring_fpath = path.join(MeileGuiConfig.BASEDIR, "keyring.cfg")
        img_fpath = path.join(MeileGuiConfig.BASEDIR, "img")

        
        if path.exists(img_fpath):
            print(f"Removing: {img_fpath}")
            rmtree(img_fpath)
            
        if path.isfile(keyring_fpath):
            print(f"Removing: {keyring_fpath}")
            remove(keyring_fpath)

        # Remove also the [wallet] section in config.ini
        # So, if the keyring-file is deleted and the use close accidentaly the application
        # We can bypass the case with a wallet reference (in config) without a keyring
        if path.exists(keyring_fpath) is False:
            MeileConfig = MeileGuiConfig()
            CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
            # CONFIG.remove_section('wallet')
            # We had to clear all the data as defaultconf file (can't remove)
            for k in CONFIG["wallet"]:
                if k != "uuid":
                    CONFIG.set("wallet", k, "")
            FILE = open(MeileConfig.CONFFILE, 'w')
            CONFIG.write(FILE)

        self.closeDialog(None) # arg is required (?)

        self.dialog = MDDialog(
            text="Wallet Restore/Create",
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
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
                    text_color=get_color_from_hex(MeileColors.BLACK),
                    on_release=partial(self.wallet_restore, False)
                ),
            ],
        )
        self.dialog.open()

    # duplicate of MainWindow.wallet_restore
    def wallet_restore(self, new_wallet = False, _ = None):
        # Use Main_WIndow NewWallet boolean
        Meile.app.manager.get_screen(WindowNames.MAIN_WINDOW).NewWallet = copy.deepcopy(new_wallet)
        self.closeDialog(None)  # arg is required (?)

        Meile.app.root.remove_widget(self)
        Meile.app.manager.add_widget(WalletRestore(name=WindowNames.WALLET_RESTORE))
        Meile.app.root.transition = SlideTransition(direction = "right")
        Meile.app.root.current = WindowNames.WALLET_RESTORE

    def open_fiat_interface(self):
        Meile.app.root.add_widget(fiat_interface.FiatInterface(name=WindowNames.FIAT))
        Meile.app.root.transistion = SlideTransition(direction="right")
        Meile.app.root.current = WindowNames.FIAT
        
    def display_seed(self):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        keyring_passphrase = CONFIG['wallet'].get('password', '')
        
        ss = SecureSeed()
        
        if path.isfile(path.join(ConfParams.KEYRINGDIR, "seed")):
            with open(path.join(ConfParams.KEYRINGDIR, "seed"), "rb") as f:
                encrypted_seed= base64.b64encode(f.read()).decode()
            
            seedphrase = ss.decrypt_seed(encrypted_seed, keyring_passphrase)
        else:
            seedphrase = "NULL"
            
        SeedInfo = SeedInfoContent(seedphrase)
        self.dialog = MDDialog(
                type="custom",
                content_cls=SeedInfo,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),

                buttons=[
                    MDRaisedButton(
                        text="CLOSE",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release=self.closeDialog
                    ),
                ],
            )
        self.dialog.open()

    def return_coin_logo(self, coin):
        self.MeileConfig = MeileGuiConfig()
        from typedef.konstants import MeileColors

        predir = MeileColors.FLOC
        logoDict = {}
        for c in IBCTokens.ibc_coins:
            logoDict[c] = predir + c + ".png"

        for c in IBCTokens.ibc_coins:
            if c == coin:
                return self.MeileConfig.resource_path(logoDict[c])
            
    def get_swap_image(self, service):
        if service == "Exolix":
            return self.MeileConfig.resource_path(MeileColors.EXOLIX)
        else:
            return self.MeileConfig.resource_path(MeileColors.SIMPLE_SWAP)
        

    def get_qr_code_address(self):
        CONFIG = MeileGuiConfig()
        conf = CONFIG.read_configuration(MeileGuiConfig.CONFFILE)
        self.ADDRESS = conf['wallet'].get("address")
        QRcode = QRCode()
        if not path.isfile(path.join(MeileGuiConfig.BASEDIR, "img", f"{self.ADDRESS}.png")):
            print("Generating QR Code....")
            QRcode.generate_qr_code(self.ADDRESS, "dvpn")
        
        img_path = path.join(MeileGuiConfig.BASEDIR, "img", f"{self.ADDRESS}.png")
        print(img_path)
        return path.join(MeileGuiConfig.BASEDIR, "img", f"{self.ADDRESS}.png")

    def SetBalances(self, CoinDict):
        if CoinDict:
            self.dec_text  = str(CoinDict['dec']) + " dec"
            self.scrt_text = str(CoinDict['scrt']) + " scrt"
            self.atom_text = str(CoinDict['atom']) + " atom"
            self.osmo_text = str(CoinDict['osmo']) + " osmo"
            self.dvpn_text = str(CoinDict['dvpn']) + " p2p"
            self.nam_text  = str(CoinDict['nam'])  + " nam"
            #self.dvpn_text = str(CoinDict['tsent']) + " tsent"
            data = [ 
                { "logo" : self.return_coin_logo("p2p"), "text" : self.dvpn_text },
                { "logo" : self.return_coin_logo("scrt"), "text" : self.scrt_text },
                { "logo" : self.return_coin_logo("atom"), "text" : self.atom_text },
                { "logo" : self.return_coin_logo("osmo"), "text" : self.osmo_text },
                { "logo" : self.return_coin_logo("nam"),  "text" : self.nam_text }
                ]

            recycle_view = self.ids.rv
            recycle_view.data = [{'logo': item['logo'], 'text': item['text']} for item in data]
        else:
            self.dec_text  = str("0.0") + " dec"
            self.scrt_text = str("0.0") + " scrt"
            self.atom_text = str("0.0") + " atom"
            self.osmo_text = str("0.0") + " osmo"
            self.dvpn_text = str("0.0") + " p2p"
            self.nam_text = str("0.0") + " nam"
            #self.dvpn_text = str("0.0") + " tsent"
            
            
            self.dialog = MDDialog(
                text="Error Loading Wallet Balance. Please try again later.",
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                    MDRaisedButton(
                        text="OKay",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.BLACK),
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

# deprecated
class SubscriptionScreen(MDBoxLayout):

    def __init__(self, node_tree,  **kwargs):
        super(SubscriptionScreen, self).__init__()
        self.NodeTree = node_tree

        self.get_config(None)
        
        self.cd = ConnectionDialog()
        self.set_conn_dialog(self.cd, "Loading Subscriptions...")

        if self.address:
            self.subs_callback(None)
            return
        else:
            self.remove_loading_widget(None)
            self.sub_address_error()
            return

    @delayable
    def subs_callback(self, dt):
        yield 0.314
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)

        if len(self.NodeTree.SubResult) == 0:
            try:
                t = Thread(target=lambda: self.NodeTree.get_subscriptions(self.address))
                t.start()
                print("Running Thread...")
                l = 13
                pool = l*100
                inc = float(1/pool)
                while t.is_alive():
                    yield 0.0165
                    self.cd.ids.pb.value += inc
                self.cd.ids.pb.value = 1
                mw.NodeTree.SubResult = deepcopy(self.NodeTree.SubResult)
            except Exception as e:
                print(str(e))
                return None
        try:
            for sub in mw.NodeTree.SubResult:
                self.add_sub_rv_data(sub)
        except TypeError:
            print("Connection Error")
                
        self.remove_loading_widget(None)
               
        # Auto-connect from NodeCarousel if sub found
        if mw.SubCaller: 
            for sub in mw.NodeTree.SubResult:
                if mw.NodeCarouselData['address'] == sub[NodeKeys.FinalSubsKeys[2]]:
                    mw.SelectedSubscription['id']        = sub[NodeKeys.FinalSubsKeys[0]]
                    mw.SelectedSubscription['address']   = sub[NodeKeys.FinalSubsKeys[2]]
                    mw.SelectedSubscription['protocol']  = sub[NodeKeys.FinalSubsKeys[8]]
                    mw.SelectedSubscription['moniker']   = sub[NodeKeys.FinalSubsKeys[1]]
                    mw.SelectedSubscription['allocated'] = sub[NodeKeys.FinalSubsKeys[6]]
                    mw.SelectedSubscription['consumed']  = sub[NodeKeys.FinalSubsKeys[7]]
                    mw.SelectedSubscription['expires']   = sub[NodeKeys.FinalSubsKeys[9]]
                    mw.SelectedSubscription['deposit']   = sub[NodeKeys.FinalSubsKeys[4]]
             
            mw.clear_node_carousel()
            mw.SubCaller = False
            mw.connect_routine()

    def add_sub_rv_data(self, node):
        nscore = "NULL"
        votes = 0
        formula = "NULL"


        price = node[NodeKeys.FinalSubsKeys[4]]
        match = re.match(r"([0-9]+)([a-z]+)", price, re.I)
        if match:
            amount, coin = match.groups()
            amount = round(float(float(amount) / IBCTokens.SATOSHI),4)
            coin = coin.lstrip("u") # Remove u
            price_text = f"{amount}{coin}"
        else:
            price_text = node[NodeKeys.FinalSubsKeys[4]]
            
        if node[NodeKeys.FinalSubsKeys[9]]:
            expirary_date = node[NodeKeys.FinalSubsKeys[9]].split('.')[0]
            expirary_date = datetime.strptime(expirary_date, '%Y-%m-%d %H:%M:%S').strftime('%b %d %Y, %I:%M %p')
        else:
            expirary_date = "Null"

        #May use Insignia later
        '''
            IconButton  = "alpha-r-circle"
            NodeTypeText = "Unknown"
        '''
              
        node_data = self.NodeTree.NodeTree.get_node(node[NodeKeys.FinalSubsKeys[2]])
        if node_data:
            NodeTypeText = node_data.data['ISP Type'] if node_data.data['ISP Type'] else "Unknown" 
            nscore = node_data.data['Score']
            votes = node_data.data['Votes']
            formula = node_data.data['Formula']
        else:
            NodeTypeText = "Unknown"
            nscore = "NULL"
            votes = "NULL"
            formula = "NULL"
            

        item = NodeAccordion(
            node=NodeRow(
                moniker=node[NodeKeys.FinalSubsKeys[1]],
                location=node[NodeKeys.FinalSubsKeys[5]],
                protocol=node[NodeKeys.FinalSubsKeys[8]],
                node_type=NodeTypeText,
                expires=expirary_date,
            ),
            content=NodeDetails(
                sub_id=node[NodeKeys.FinalSubsKeys[0]],
                allocated=node[NodeKeys.FinalSubsKeys[6]],
                consumed=node[NodeKeys.FinalSubsKeys[7]],
                deposit=price_text,
                score=str(nscore),
                votes=str(votes),
                formula=str(formula),
                node_address=node[NodeKeys.FinalSubsKeys[2]],
            )
        )
        self.ids.rv.add_widget(item)

    def get_config(self, dt):
        self.MeileConfig = MeileGuiConfig()
        CONFIG = self.MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        self.address = CONFIG['wallet'].get("address")

    @mainthread
    def set_conn_dialog(self, cd, message):
        self.dialog = None
        self.dialog = MDDialog(
                        type="custom",
                        content_cls=cd,
                        md_bg_color=get_color_from_hex(MeileColors.BLACK),
                    )
        # See MainWindow.set_conn_dialog: the message lives in the dialog's own
        # status line, not in the dialog title.
        cd.set_status(message)
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
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDRaisedButton(
                    text="Okay",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.BLACK),
                    on_release=self.remove_loading_widget
                ),
            ],
        )
        self.dialog.open()

    def set_previous_screen(self):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        mw.carousel.remove_widget(mw.NodeWidget)
        mw.carousel.load_previous()

'''
Main widget of country cards in carousel.
Contains: widgets.RecyclerViewRow, RecyclerViewCountryRow
'''
class NodeScreen(MDBoxLayout):
    NodeTree = None
    Country = None
    MeileConfig = None
    def __init__(self, node_tree, country, sort, **kwargs):
        super(NodeScreen, self).__init__()

        self.NodeTree = node_tree
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        
        # Clear out any previous Carousel Data
        mw.NodeCarouselData = {"moniker" : None,
                                "address" : None,
                                "gb_prices" : None,
                                "hr_prices" : None,
                                "protocol" : None}
        
        

        try:
            CountryNodes = self.NodeTree.NodeTree.children(country)
        except NodeIDAbsentError as e:
            print(str(e))
            return

        if sort == mw.SortOptions[1]:
            self.SortNodesByMoniker(CountryNodes)
        elif sort == mw.SortOptions[2]:
            self.SortNodesByPrice(CountryNodes)
        else:
            for node_child in CountryNodes:
                node = node_child.data
                self.add_rv_data(node)

    def SortNodesByPrice(self, CountryNodes):
        NodeData = []
        for node in CountryNodes:
            NodeData.append(node.data)

        i=0

        OldNodeData = copy.deepcopy(NodeData)

        for data in NodeData:
            try:
                udvpn = re.findall(r'[0-9]+\.[0-9]+' +"dvpn", data['Price'])[0]
                NodeData[i]['Price'] = udvpn
            except IndexError:
                NodeData[i]['Price'] = "10000dvpn"
            i += 1
        NodeDataSorted = sorted(NodeData, key=lambda d: float(d['Price'].split('dvpn')[0]))


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

        NodeDataSorted = sorted(NodeData, key=lambda d: d[NodeKeys.NodesInfoKeys[0]].lower())

        self.meta_add_rv_data(NodeDataSorted)

    def meta_add_rv_data(self, NodeDataSorted):

        for node in NodeDataSorted:
            self.add_rv_data(node)

    def add_rv_data(self, node):
        
        downRate = format_byte_size(int(node[NodeKeys.NodesInfoKeys[8]])) 
        upRate   = format_byte_size(int(node[NodeKeys.NodesInfoKeys[9]]))
        
        speedText = f"{downRate}[color=#00FF00]↓[/color], {upRate}[color=#f44336]↑[/color]"
        if "0B" in downRate or "0B" in upRate:
            speedText = "    " + speedText
        
        # Keeping as I may use the insignia's later
        '''
            IconButton  = "alpha-r-circle"
            ToolTipText = "Residential"
        '''

        self.ids.rv.data.append(
            {
                "viewclass"          : "RecycleViewRow",
                "moniker_text"       : node[NodeKeys.NodesInfoKeys[0]],
                "country_text"       : node[NodeKeys.NodesInfoKeys[5]],
                "protocol_text"      : node[NodeKeys.NodesInfoKeys[13]],
                "speed_text"         : speedText,
                "isp_type_text"      : node[NodeKeys.NodesInfoKeys[15]] if node[NodeKeys.NodesInfoKeys[15]] else "Unknown", 
                "node_data"          : node
            },
        )

    def set_previous_screen(self):
        mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        try:
            while len(mw.carousel.slides) > 1:
                mw.carousel.remove_widget(mw.carousel.slides[-1])
        except Exception as e:
            print(str(e))
            pass
                
        mw.carousel.load_slide(mw.carousel.slides[0])

class PlanScreen(MDBoxLayout):
    instructions = StringProperty("Tick a plan to filter the node list to its nodes")
    status_text  = StringProperty("Loading plans...")

    def __init__(self, **kwargs):
        # `name` is handed over by the carousel but is not a BoxLayout
        # property, so the kwargs are intentionally not forwarded.
        super(PlanScreen, self).__init__()
        self.PlanData       = []
        self.TotalCountries = []
        self.TotalNodes     = []
        self.cards          = []
        self.user_enrolled_plans = []

        self.mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        self.p2p_price = 0
        self.load_failed = False

        Clock.schedule_once(self.pre_build, 1)

    def pre_build(self, *args):
        self.status_text = "Loading plans..."
        try:
            t = Thread(target=lambda: self.build(), daemon=True)
            t.start()
            print("Running Thread...")

        except Exception as e:
            print(str(e))
            self.status_text = str(e)
            return None

    def build(self):
        '''
        Load the plans on a worker thread and always finish the screen, even
        when the plan API is unreachable, so the spinner never runs forever.
        '''
        try:
            self._load_plans()
        except Exception as e:
            print(f"PlanScreen.build: {str(e)}")
            self.load_failed = True
            self.status_text = "Could not load plans"
        finally:
            Clock.schedule_once(self.finished)

    def _load_plans(self):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        wallet = CONFIG['wallet'].get('address', None)
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()

        req = http.get(HTTParams.PLAN_API + HTTParams.API_PLANS, auth=HTTPBasicAuth(scrtsxx.PLANUSERNAME, scrtsxx.PLANPASSWORD))
        plan_data = req.json() if req.ok and req.status_code != 404 else []
        print(plan_data)

        # Prevent plan parsing when wallet is not initialized
        self.user_enrolled_plans = []
        if wallet not in [None, ""]:
            req2 = http.get(HTTParams.PLAN_API + HTTParams.API_PLANS_SUBS % wallet, auth=HTTPBasicAuth(scrtsxx.PLANUSERNAME, scrtsxx.PLANPASSWORD))

            # If the request failed please don't .json() or will raised a exception
            self.user_enrolled_plans = req2.json() if req2.ok and req2.status_code != 404 else []

        for pd in plan_data:
            req3 = http.get(HTTParams.PLAN_API + HTTParams.API_PLANS_NODES % pd['uuid'], auth=HTTPBasicAuth(scrtsxx.PLANUSERNAME, scrtsxx.PLANPASSWORD))
            plan_nodes = req3.json() if req3.ok and req3.status_code != 404 else []
            no_of_nodes = 0
            countries = []
            no_of_countries = 0
            for node in plan_nodes:
                node_data = self.mw.NodeTree.NodeTree.get_node(node)
                if node_data:
                    no_of_nodes += 1
                try: 
                    if node_data.data['Country'] in countries:
                        continue
                    else:
                        no_of_countries += 1
                        countries.append(node_data.data['Country'])
                except AttributeError as e:
                    print(f"{node}: {str(e)}")
                    continue
            
            self.PlanData.append(pd)
            self.TotalCountries.append(no_of_countries)
            self.TotalNodes.append(no_of_nodes)
            
        price_api = GetPriceAPI()
        try:
            self.p2p_price = price_api.get_usd("p2p")['price']
        except Exception as e:
            # A failing price API must not leave the screen spinning forever
            print(f"PlanScreen.build: {str(e)}")
            self.p2p_price = 0

        
    @staticmethod
    def _sub_field(plan, keys, default=''):
        '''
        Read one field of a `/v1/subscription/<wallet>` record.

        The payload of the plan API is not versioned, so every known spelling
        of a field is tried in order (canonical name first) and the first one
        that carries a value is returned.
        '''
        for key in keys:
            value = plan.get(key)
            if value not in (None, ''):
                return value
        return default

    def build_plans(self, data, plans, no_of_nodes, no_of_countries):
        plan = None
        for p in plans:
            plan_uuid = self._sub_field(p, ('uuid', 'plan_uuid'))
            if plan_uuid and plan_uuid == data['uuid']:
                plan = p
                break


        # In the future cost should be both in dvpn and euro (fuck usd)
        # Can use coin_api to get dvpn price and translate cost

        plancost = data['plan_price'] / IBCTokens.SATOSHI
        plancost_usd = round(float(plancost * self.p2p_price), 2)
        plan_name = data['plan_name']
        print(f"Plan Name: {plan_name}")
        premium = 'premium' in plan_name.lower()

        sub_id       = str(self._sub_field(plan, ('subscription_id', 'sub_id', 'id'))) if plan else ""
        expires      = str(self._sub_field(plan, ('expires', 'expiry', 'expires_at'))) if plan else ""
        amount_denom = str(self._sub_field(plan, ('amt_denom', 'amount_denom', 'denom'))) if plan else ""
        try:
            amount_paid = "%.2f" % float(self._sub_field(
                plan, ('amt_paid', 'amount_paid', 'amount'), default=0)) if plan else ""
        except (TypeError, ValueError):
            amount_paid = ""

        card = PlanCard(
            plan_name,
            str(no_of_nodes),
            str(no_of_countries),
            ("%d" % plancost) if float(plancost).is_integer() else ("%.2f" % plancost),
            data['logo'],
            data['uuid'],
            sub_id,
            str(data['plan_id']),
            denom=(data.get('plan_denom') or 'p2p').replace('udvpn', 'p2p').replace('dvpn', 'p2p'),
            usd_price=plancost_usd,
            expires=expires,
            amount_paid=amount_paid,
            amount_denom=amount_denom,
            icon="crown" if premium else "shield-check",
            accent=MeileColors.MEILE if premium else MeileColors.UPLOAD,
            plan_screen=self,
        )

        self.cards.append(card)
        self.ids.plans_box.add_widget(card)

    def toggle_plan(self, card, active):
        '''
        Called by the checkbox of a card. Only one plan can filter the node
        list at a time, so every other card is unchecked without touching the
        node list (`notify_map=False`), the selected card does the filtering.
        '''
        if active:
            for other in self.cards:
                if other is not card:
                    other.apply_selection(False, notify_map=False)
        card.apply_selection(active)

    def set_previous_screen(self):
        #mw = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        self.mw.carousel.remove_widget(self.mw.NodeWidget)
        self.mw.carousel.load_previous()
        
    def get_plan_image(self, plan_type):
        MeileConfig = MeileGuiConfig()
        if plan_type == "b":
            return MeileConfig.resource_path(MeileColors.BASIC_PLAN)
        else:
            return MeileConfig.resource_path(MeileColors.PREMIUM_PLAN)

                
    def finished(self, *args):
        # Nothing left to load, stop the spinner and report the plan count
        spinner = self.ids.get('spinner')
        if spinner is not None and spinner.parent is not None:
            spinner.parent.remove_widget(spinner)

        # A rebuild must replace the cards instead of stacking a second set
        plans_box = self.ids.get('plans_box')
        if plans_box is not None:
            plans_box.clear_widgets()
        self.cards = []

        for pd, nodes, countries in zip(self.PlanData, self.TotalNodes, self.TotalCountries):
            self.build_plans( pd, self.user_enrolled_plans, nodes, countries)

        if plans_box is not None:
            # A single plan uses the full width instead of one narrow column
            plans_box.cols = 2 if len(self.cards) > 1 else 1

        if len(self.cards) == 0:
            # keep the error of a failed build instead of overwriting it
            if not self.load_failed:
                self.status_text = "No plans available right now"
        else:
            self.load_failed = False
            self.status_text = "%d plans available" % len(self.cards)
'''
This is the card class of the country cards on the left panel
'''
class RecycleViewCountryRow(MDCard, HoverBehavior):
    text = StringProperty()

    def on_enter(self, *args):
        self.md_bg_color = get_color_from_hex(MeileColors.ROW_HOVER)
        Window.set_system_cursor('hand')

    def on_leave(self, *args):
        self.md_bg_color = get_color_from_hex(MeileColors.DIALOG_BG_COLOR)
        Window.set_system_cursor('arrow')

    def switch_window(self, country):
        print(country)
        mw       = Meile.app.root.get_screen(WindowNames.MAIN_WINDOW)
        NodeTree = NodeTreeData(mw.NodeTree.NodeTree)


        try:
            mw.carousel.remove_widget(mw.NodeWidget)
        except Exception as e:
            print(str(e))
            pass

        mw.NodeWidget = NodeScreen(name="nodes",
                                   node_tree=NodeTree,
                                   country=country,
                                   sort=mw.Sort)
        print(mw.NodeWidget)
        mw.carousel.add_widget(mw.NodeWidget)
        mw.carousel.load_slide(mw.NodeWidget)

class HelpScreen(Screen):

    def GetMeileVersion(self, spec: str = "V"):
        if spec == "V":
            return TextStrings.VERSION
        else:
            return str(TextStrings.BUILD)

    def set_previous_screen(self):

        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="right")
        Meile.app.root.current = WindowNames.MAIN_WINDOW

    def open_sentinel(self):
        import webbrowser
        
        webbrowser.open('https://sentinel.co')

class SettingsScreen(Screen):
    MeileConfig = MeileGuiConfig()
    SettingsNetworkMenu = ["grpc", "api", "mnapi", "cache", "dns", "resolver1", "resolver2", "resolver3"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        params = HTTParams()
        cparams = ConfParams()
        
        config = self.MeileConfig.read_configuration(self.MeileConfig.CONFFILE)
        # Load default values
        #self.RPC       = config['network'].get('rpc', '')
        self.GRPC      = config['network'].get('grpc', '')
        self.API       = config['network'].get('api', '')
        self.MNAPI     = config['network'].get('mnapi', '')
        self.CACHE     = config['network'].get('cache', '')
        self.RESOLVER1 = config['network'].get('resolver1', '')
        self.RESOLVER2 = config['network'].get('resolver2', '')
        self.RESOLVER3 = config['network'].get('resolver3', '')
        self.GB        = config['subscription'].get('gb', '5')
        self.FRAGMENT  = config['network'].get('fragment', '0')
        self.DNS       = config['network'].get('dns', '1.1.1.1')
        self.CONFIGDNS = config['network'].get('dns', '1.1.1.1')
        self.RINGSESSIONS = config['network'].get('ringsessions', '0')
        
        self.MeileConfig = MeileGuiConfig()

        # I've tried to write a single code with the iteration of 'what' [grpc, rpc]
        # But doesn't work because the code at runtime will pass the loop value and not a copy one
        
        self.grpc_menu = MDDropdownMenu(
            caller=self.ids.grpc_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i['Name']} ({i['Country']})",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "grpc"),
                } for i in params.GRPCS
            ],
            position="center",
            width_mult=5,
        )
        self.grpc_menu.bind()

        self.api_menu = MDDropdownMenu(
            caller=self.ids.api_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i['Name']} ({i['Country']})",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "api"),
                } for i in params.APIS_URL
            ],
            position="center",
            width_mult=5,
        )
        self.api_menu.bind()

        self.mnapi_menu = MDDropdownMenu(
            caller=self.ids.mnapi_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "mnapi"),
                } for i in params.MNAPIS
            ],
            position="center",
            width_mult=7,
        )
        self.mnapi_menu.bind()
        
        self.cache_menu = MDDropdownMenu(
            caller=self.ids.cache_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "cache"),
                } for i in params.NODE_APIS
            ],
            position="center",
            width_mult=10,
        )
        self.cache_menu.bind()
        
        self.dns_menu = MDDropdownMenu(
            caller=self.ids.dns_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i['Country']}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "dns"),
                } for i in params.DNSSERVERS
            ],
            position="center",
            width_mult=5,
        )
        self.dns_menu.bind()
        
        self.gb_menu = MDDropdownMenu(
            caller=self.ids.gb_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "gb"),
                } for i in cparams.DEFAULT_SUBS
            ],
            position="center",
            width_mult=5,
        )
        self.gb_menu.bind()
        
        self.resolver1_menu = MDDropdownMenu(
            caller=self.ids.resolver1_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "resolver1"),
                } for i in params.RESOLVERS
            ],
            position="center",
            width_mult=5,
        )
        self.resolver1_menu.bind()
        
        self.resolver2_menu = MDDropdownMenu(
            caller=self.ids.resolver2_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "resolver2"),
                } for i in params.RESOLVERS
            ],
            position="center",
            width_mult=5,
        )
        self.resolver2_menu.bind()
        
        self.resolver3_menu = MDDropdownMenu(
            caller=self.ids.resolver3_drop_item,
            items=[
                {
                    "viewclass": "IconListItem",
                    "icon": "server-security",
                    "text": f"{i}",
                    "height": dp(56),
                    "on_release": lambda x=f"{i}": self.set_item(x, "resolver3"),
                } for i in params.RESOLVERS
            ],
            position="center",
            width_mult=5,
        )
        self.resolver3_menu.bind()

    def get_config(self, what: str = "rpc"):
        config = self.MeileConfig.read_configuration(self.MeileConfig.CONFFILE)
        if what in self.SettingsNetworkMenu:
            getattr(self.ids, f"{what}_drop_item").set_item(config['network'][what])
            return config['network'][what]
        elif what == "fragment":
            return bool(int(config['network'].get(what, "0")))
        elif what == "ringsessions":
            return bool(int(config['network'].get(what, "0")))
        else:
            getattr(self.ids, f"{what}_drop_item").set_item(config['subscription'][what])
            return config['subscription'][what]
            

    def set_item(self, text_item, what: str = "rpc"):
        if what in [self.SettingsNetworkMenu[0], self.SettingsNetworkMenu[1]]:
            text_item = json.loads(text_item.replace("'",'"'))
            getattr(self.ids, f"{what.lower()}_drop_item").set_item(text_item['Name'])
            setattr(self, what.upper(), text_item['url'])
            getattr(self, f"{what.lower()}_menu").dismiss()
        elif what == self.SettingsNetworkMenu[4]:
            text_item = json.loads(text_item.replace("'",'"'))
            getattr(self.ids, f"{what.lower()}_drop_item").set_item(text_item['Country'])
            setattr(self, what.upper(), text_item['ip'])
            getattr(self, f"{what.lower()}_menu").dismiss()
        else:
            getattr(self.ids, f"{what.lower()}_drop_item").set_item(text_item)
            setattr(self, what.upper(), text_item)
            getattr(self, f"{what.lower()}_menu").dismiss()

    def build(self):
        return self.screen

    def SaveOptions(self):
        config = self.MeileConfig.read_configuration(self.MeileConfig.CONFFILE)
        for what in self.SettingsNetworkMenu:
            '''
            if what == "grpc":
                config.set('network', what, getattr(self, what.upper()))
            '''
            config.set('network', what, getattr(self, what.upper()))
            if what == "dns":
                if self.CONFIGDNS != getattr(self, what.upper()):
                    dns = ChangeDNS(dns=getattr(self, what.upper()))
                    dns.change_dns()
        
        what = "gb"
        config.set('subscription', what, str(getattr(self, what.upper())))
        
        what = "fragment"
        config.set('network', what, '1' if self.ids.fragment.active else '0')
        
        what = "ringsessions"
        config.set('network', what, '1' if self.ids.ring_sessions.active else '0')
        
        with open(self.MeileConfig.CONFFILE, 'w', encoding="utf-8") as f:
            config.write(f)
            
        
        # Write the DNSCrypt-proxy configuration file
        import toml
        cparams = ConfParams()
        meile_config = self.MeileConfig.read_configuration(self.MeileConfig.CONFFILE)
        dnscrypt_confile = path.join(cparams.KEYRINGDIR, 'dnscrypt-proxy.toml')
        with open(dnscrypt_confile, 'r') as file:
            config = toml.load(file)
        config['server_names'] = [meile_config['network'].get('resolver1', 'cs-ch'),
                                  meile_config['network'].get('resolver2', 'uncensoreddns-ipv4'),
                                  meile_config['network'].get('resolver3', 'doh-ibksturm')]

        with open(dnscrypt_confile, 'w') as file:
            toml.dump(config, file)

        self.set_previous_screen()
        
    def on_checkbox_active(self, checkbox_instance, value):
        if value:  
            print("Ring Sessions is CHECKED")
        else:
            print("Ring Sessions is UNCHECKED")

    def set_previous_screen(self):
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="up")
        Meile.app.root.current = WindowNames.MAIN_WINDOW
        
        
class SMSCountryRow(MDCard, HoverBehavior):
    '''One country entry of the searchable RecycleView on SMSPoolScreen.'''
    country_text  = StringProperty("")
    flag_source   = StringProperty("")
    country_index = NumericProperty(-1)
    is_selected   = BooleanProperty(False)
    hovered       = BooleanProperty(False)

    def select(self, *args):
        try:
            screen = Meile.app.root.get_screen(WindowNames.SMS)
            screen.select_country(self.country_index)
        except Exception as e:
            print("SMSCountryRow.select: %s" % str(e))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.select()
        return super().on_touch_down(touch)

    def on_enter(self, *args):
        self.hovered = True
        Window.set_system_cursor('hand')

    def on_leave(self, *args):
        self.hovered = False
        Window.set_system_cursor('arrow')


class SMSServiceRow(MDCard, HoverBehavior):
    '''One service entry of the searchable RecycleView on SMSPoolScreen.

    The row carries the service name (not an index) so a re-render of the
    filtered list can never make a click land on the wrong service.
    '''

    service_text = StringProperty("")
    is_selected  = BooleanProperty(False)
    hovered      = BooleanProperty(False)

    def select(self, *args):
        try:
            screen = Meile.app.root.get_screen(WindowNames.SMS)
            screen.select_service(self.service_text)
        except Exception as e:
            print("SMSServiceRow.select: %s" % str(e))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.select()
        return super().on_touch_down(touch)

    def on_enter(self, *args):
        self.hovered = True
        Window.set_system_cursor('hand')

    def on_leave(self, *args):
        self.hovered = False
        Window.set_system_cursor('arrow')


class SMSPoolScreen(Screen):
    '''SMS Pool ("Virtual Number Terminal").

    Two services are combined here:

      * SMSPool (https://api.smspool.net) buys and tracks the virtual numbers.
      * The Meile plan-rest API keeps the user's USD SMS balance ledger
        (see meile-plan-rest/meile_plan_api.py) so every top-up (Pirate Chain),
        purchase debit and cancel/refund is accounted for server side.
    '''

    # Static copy of the PRICE QUOTE card (see <SMSPoolScreen> in meile.kv).
    QUOTE_IDLE_HINT = ("Pick a country and a service - the cost and the "
                       "provider's success rate show up here.")
    QUOTE_RATE_HINT = ("Success rate: how often this provider has actually "
                       "delivered an SMS for the selected service and country.")
    # Rate light colours (same green/red as the ACTIVE ORDER status dot).
    RATE_GOOD = "#3ecc6d"
    RATE_FAIR = "#e0a33a"
    RATE_POOR = "#c0392b"
    PLACEHOLDER = "#8d8d8d"

    # Face of the "Pay with BTCPay" button of the top-up card (see
    # <ImageTooltipButton> in meile.kv).  Resolved at start up because the
    # artwork sits next to the executable in a frozen build and inside src/
    # when the application runs from a checkout (see _asset).
    btcpay_icon = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # SMSPool credentials (kept in the git-ignored secrets module)
        self.API_KEY = getattr(scrtsxx, "SMSPOOL_API_KEY", "") or ""

        self.uuid             = None
        self.balance          = 0.0
        self.markup           = float(SMSConf.MARKUP_PERCENT)
        self.topup_amount     = float(SMSConf.TOPUP_PRESETS[1])

        self.countries        = []          # list of normalised country dicts
        self.selected_index   = -1
        self.selected_country = None
        self.country_filter   = ""

        self.services         = {}          # name -> SMSPool service id
        self.selected_service = None        # name of the picked service
        self.service_filter   = ""
        self._other_service   = SMSConf.OTHER_SERVICE_LABEL
        self.current_order    = None

        # Price quote for the current country + service selection (see
        # request_quote / _on_quote and the PRICE QUOTE card in meile.kv).
        self.quote            = None        # last /request/price answer
        self.quote_event      = None        # debounce handle
        self.quote_seq        = 0           # drops superseded answers

        self.sms_check_event  = None
        self.countdown_event  = None
        self.order_deadline   = None
        self._order_expiration = None       # unix ts reported by /purchase/sms

        self._pending_service = None
        self._pending_price   = 0.0

        # Pirate Chain (ARRR) top-up state
        self.stop_event        = Event()
        self.topup_dialog      = None
        self.topup_content     = None
        self.topup_poll_event  = None
        self.topup_started     = False
        self.topup_crediting   = False
        self.topup_arrr        = 0.0
        self.zaddress          = None
        self.zaddress_balance  = 0.0

        # BTCPay top-up state (BTC Lightning, Monero, Litecoin MWEB, Zcash,
        # Dash - see open_btcpay_dialog and SMSConf.BTCPAY_COINS).  The invoice
        # is created for the picked coin and then polled from a worker thread
        # (btcpay_stop ends that thread), so the two top-up rails never share
        # state with the ARRR one above.
        self.btcpay_icon        = ""        # resolved in _startup (kv binding)
        self.btcpay_client      = None      # btcpay.BTCPayClient of the store
        self.btcpay_coin_dialog = None      # coin picker dialog
        self.btcpay_dialog      = None      # invoice / QR dialog
        self.btcpay_content     = None
        self.btcpay_coin        = None      # picked SMSConf.BTCPAY_COINS entry
        self.btcpay_code        = ""        # method id the invoice answered with
        self.btcpay_invoice_id  = ""
        self.btcpay_address     = ""
        self.btcpay_amount      = None
        self.btcpay_started     = False
        self.btcpay_crediting   = False
        self.btcpay_stop        = Event()

        Clock.schedule_once(lambda dt: self._startup(), 0.3)

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------
    def _plan_auth(self):
        return HTTPBasicAuth(scrtsxx.PLANUSERNAME, scrtsxx.PLANPASSWORD)

    def _get_uuid(self):
        try:
            return Meile.app.root.get_screen(WindowNames.PRELOAD).UUID
        except Exception:
            MeileConfig = MeileGuiConfig()
            CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
            return CONFIG['wallet'].get('uuid')

    def _sync_uuid_label(self):
        '''Mirror the wallet UUID into the header box (see <SMSPoolScreen>).'''
        try:
            self.ids.uuid_label.text = str(self.uuid) if self.uuid else "-"
        except Exception:
            pass

    @staticmethod
    def _parse(result):
        if isinstance(result, (dict, list)):
            return result
        try:
            return json.loads(result)
        except Exception:
            return None

    def _asset(self, relative):
        '''Absolute path of a bundled asset (image, font, ...).

        MeileGuiConfig.resource_path() points into the frozen bundle
        (sys._MEIPASS) once the application is packaged and at src/conf while
        it runs from a checkout, so a development run falls back to the src
        directory this module lives in - the same fallback _flag_source uses.
        '''
        resolved = MeileGuiConfig().resource_path(relative)
        if path.exists(resolved):
            return resolved
        absolute = path.join(path.dirname(path.dirname(path.abspath(__file__))),
                             relative)
        return absolute if path.exists(absolute) else resolved

    @staticmethod
    def _price_from_payload(data):
        '''(price, success_rate) carried by a /request/price answer.

        Documented 200 body: {"pool": 7, "high_price": "0.24", "price": "0.24",
        "success_rate": 100}.  Both values are also what the documented 400
        "missing parameter" reply omits, so either may come back as None.
        '''
        price = None
        rate  = None
        if isinstance(data, dict):
            for key in ("price", "cost", "cost_price"):
                if data.get(key) is not None:
                    try:
                        price = float(data[key])
                        break
                    except Exception:
                        pass
            for key in ("success_rate", "successrate", "rate"):
                if data.get(key) is not None:
                    try:
                        rate = float(str(data[key]).strip().rstrip("%"))
                        break
                    except Exception:
                        pass
        return price, rate

    @staticmethod
    def _error_message(data):
        '''Readable text of a documented SMSPool error payload.

        SMSPool answers with {"success": 0, "errors": [{"message": ...,
        "param": ...}]} - or a plain "message" on the order endpoints.
        '''
        if not isinstance(data, dict):
            return ""
        errors = data.get("errors")
        if isinstance(errors, list):
            for item in errors:
                if isinstance(item, dict) and item.get("message"):
                    return str(item["message"])
                if isinstance(item, str) and item:
                    return item
        elif isinstance(errors, str) and errors:
            return errors
        return str(data.get("message") or "")

    def _debug(self, text):
        try:
            self.ids.debug_label.text = str(text)
        except Exception:
            pass

    def _toast(self, text):
        try:
            toast(str(text))
        except Exception:
            pass

    def _set_status(self, text, ok=None):
        try:
            self.ids.order_status.text = text
        except Exception:
            pass
        # Recolour the little status dot (see <StatusDot> in meile.kv).
        try:
            if ok is True:
                self.ids.status_dot.dot_color = "#3ecc6d"
            elif ok is False:
                self.ids.status_dot.dot_color = "#c0392b"
            else:
                self.ids.status_dot.dot_color = MeileColors.MEILE
        except Exception:
            pass

    # ---------- SMSPool (api.smspool.net) ----------
    def _sppost(self, path, form, on_success, on_error=None):
        if on_error is None:
            on_error = self._on_sms_error
        body = "&".join("%s=%s" % (k, v) for k, v in form.items())
        UrlRequest(
            BASE_URL + path,
            on_success=on_success,
            on_failure=on_error,
            on_error=on_error,
            req_headers={"Content-Type": "application/x-www-form-urlencoded"},
            req_body=body,
            method='POST',
            timeout=20,
        )

    def _on_sms_error(self, request, error):
        self._set_status("SMSPool error: %s" % str(error)[:120], ok=False)
        self._debug("SMSPool ERR: %s" % str(error))

    # ---------- Meile plan-rest API ----------
    def _plan_call(self, method, path, payload, on_success, on_error=None):
        if on_error is None:
            on_error = self._on_plan_error
        headers = {
            "Content-Type" : "application/json",
            "Authorization": "Basic " + base64.b64encode(
                ("%s:%s" % (scrtsxx.PLANUSERNAME, scrtsxx.PLANPASSWORD)).encode()
            ).decode(),
        }
        kwargs = {
            "on_success" : on_success,
            "on_failure" : on_error,
            "on_error"   : on_error,
            "req_headers": headers,
            "timeout"    : 20,
        }
        if method == "POST":
            kwargs["req_body"] = json.dumps(payload or {})
            kwargs["method"] = "POST"
        UrlRequest(HTTParams.PLAN_API + path, **kwargs)

    def _on_plan_error(self, request, error):
        self._set_status("Plan API error: %s" % str(error)[:120], ok=False)
        self._debug("Plan API ERR: %s" % str(error))

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------
    def _startup(self):
        self.uuid = self._get_uuid()
        self._sync_uuid_label()
        self._render_quote()        # PRICE QUOTE card starts in its idle state
        # Artwork of the "Pay with BTCPay" button (kv binds root.btcpay_icon).
        self.btcpay_icon = self._asset(SMSConf.BTCPAY_ICON)
        if self.uuid:
            self.fetch_balance()
        else:
            self._set_status("No wallet UUID - balances unavailable", ok=False)
        self.load_countries()
        self.load_services()
        self._update_topup_button()

    # ------------------------------------------------------------------
    # Balance ledger (Meile plan-rest API)
    # ------------------------------------------------------------------
    def refresh_balance(self, *args):
        self.fetch_balance()

    def fetch_balance(self):
        if not self.uuid:
            return
        self._plan_call("GET", HTTParams.API_SMS_BALANCE % self.uuid, None,
                        self._on_balance_ok, on_error=self._on_balance_failure)

    def create_account(self):
        self._plan_call("POST", HTTParams.API_SMS_ACCOUNT, {"uuid": self.uuid},
                        self._on_balance_ok)

    def _on_balance_failure(self, request, error):
        status = getattr(request, "resp_status", None)
        if status == 404:
            # No ledger yet for this wallet: create it on the fly.
            self.create_account()
        else:
            self._set_status("Balance error (HTTP %s)" % str(status), ok=False)
            self._debug("Balance failure: %s" % str(error)[:200])

    def _on_balance_ok(self, request, result):
        data = self._parse(result)
        if not isinstance(data, dict) or data.get("balance") is None:
            self._debug("Balance response: %s" % str(result)[:200])
            if isinstance(data, dict) and data.get("error"):
                self.create_account()
            return
        self._apply_balance_payload(data)

    def _apply_balance_payload(self, data):
        '''Apply a Meile plan-rest balance payload (balance + markup).

        Used by both the periodic balance fetch and the top-up credit so the
        server side markup always wins over SMSConf.MARKUP_PERCENT.
        '''
        if data.get("markup") is not None:
            try:
                self.markup = float(data["markup"])
            except Exception:
                pass
        try:
            self._apply_balance(float(data.get("balance", 0.0)))
        except Exception:
            pass

    def _apply_balance(self, bal):
        self.balance = bal
        try:
            self.ids.balance_label.text = "$%.2f" % bal
        except Exception:
            pass
        try:
            self.ids.balance_big.text = "$%.2f" % bal
        except Exception:
            pass
        # Keep the affordability line of the PRICE QUOTE card in step with the
        # ledger (a fresh wallet top-up can turn "top up $x" into "balance $y").
        if self.quote:
            self._render_quote()

    # ------------------------------------------------------------------
    # Top-up with Pirate Chain (ARRR)
    # ------------------------------------------------------------------
    def set_topup_amount(self, text):
        try:
            self.topup_amount = float(text)
        except Exception:
            self.topup_amount = 0.0
        self._update_topup_button()

    def set_topup(self, amount):
        try:
            self.ids.topup_amount_input.text = str(amount)
        except Exception:
            pass
        self.topup_amount = float(amount)
        self._update_topup_button()

    def _update_topup_button(self):
        try:
            self.ids.topup_btn.text = "TOP UP $%.2f" % float(self.topup_amount or 0.0)
        except Exception:
            pass

    def start_topup(self):
        if not self.uuid:
            self._set_status("No wallet UUID - cannot top up", ok=False)
            return
        if self.topup_started or self.btcpay_started:
            return
        amount = float(self.topup_amount or 0.0)
        if amount < float(SMSConf.MIN_TOPUP_USD):
            self._set_status("Minimum top-up is $%.2f" % float(SMSConf.MIN_TOPUP_USD), ok=False)
            return
        self.topup_started   = True
        self.topup_crediting = False
        self._set_status("Creating %s invoice..." % SMSConf.TOPUP_COIN.upper(), ok=None)
        endpoint = "/v1/pirate/newaddress" if SMSConf.TOPUP_COIN == "arrr" else "/v1/pivx/newaddress"
        self._plan_call("GET", endpoint, None, self._on_topup_address,
                        on_error=self._on_topup_address_error)

    def _on_topup_address_error(self, request, error):
        self.topup_started = False
        self._set_status("Could not create invoice", ok=False)
        self._debug("newaddress ERR: %s" % str(error)[:200])

    def _on_topup_address(self, request, result):
        data    = self._parse(result) or {}
        address = data.get("result") if isinstance(data, dict) else None
        if not address or address == "NULL":
            self.topup_started = False
            self._set_status("Could not create invoice", ok=False)
            self._debug("newaddress result: %s" % str(result)[:200])
            return
        self.zaddress         = address
        self.zaddress_balance = 0.0
        # Fetching the live price is a blocking HTTP call -> worker thread.
        Thread(target=lambda: self._prepare_topup_dialog(address), daemon=True).start()

    def _prepare_topup_dialog(self, address):
        coin = SMSConf.TOPUP_COIN
        try:
            price = float(GetPriceAPI().get_usd(coin)["price"])
        except Exception as e:
            print("SMS top-up price error: %s" % str(e))
            price = 0.0
        if price <= 0:
            Clock.schedule_once(lambda dt: self._topup_abort(
                "Could not fetch %s price" % coin.upper()))
            return
        coin_amount = round((float(self.topup_amount) * ConfParams.BTCPAYADJ) / price, 2)
        if coin_amount <= 0:
            coin_amount = round(float(self.topup_amount) / price, 8)
        Clock.schedule_once(
            lambda dt: self._show_topup_dialog(address, coin_amount, coin), 0)

    def _topup_abort(self, message):
        self.topup_started   = False
        self.topup_crediting = False
        self._set_status(message, ok=False)

    def _show_topup_dialog(self, address, coin_amount, coin):
        self.stop_event.clear()
        self.topup_arrr = coin_amount

        content = QRDialogContent()
        content.ids.zaddress_field.text = address
        content.ids.price_field.text    = "%s %s" % (coin_amount, coin)
        QRcode = QRCode()
        if coin == "arrr":
            coin_uri = "pirate:%s?amount=%s" % (address, coin_amount)
        else:
            coin_uri = "%s:%s?amount=%s" % (coin, address, coin_amount)
        content.ids.qr_img.source = QRcode.generate_qr_code(coin_uri, coin)
        self.topup_content = content

        if self.topup_dialog:
            try:
                self.topup_dialog.dismiss()
            except Exception:
                pass
            self.topup_dialog = None
        self.topup_dialog = MDDialog(
            title="Waiting for %s invoice to be paid..." % coin.upper(),
            type="custom",
            content_cls=content,
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.MEILE),
                    on_release=self.cancel_topup
                ),
            ]
        )
        self.topup_dialog.open()
        self._set_status("Waiting for %s payment..." % coin.upper(), ok=None)
        if self.topup_poll_event:
            self.topup_poll_event.cancel()
        self.topup_poll_event = Clock.schedule_interval(self._check_topup, 6)

    def _check_topup(self, dt):
        if not self.topup_started or not self.zaddress:
            return False
        endpoint = "/v1/pirate/getbalance" if SMSConf.TOPUP_COIN == "arrr" else "/v1/pivx/getbalance"
        self._plan_call("POST", endpoint,
                        {"address": self.zaddress, "conf": 0},
                        self._on_topup_balance)
        return True

    def _on_topup_balance(self, request, result):
        data = self._parse(result) or {}
        try:
            balance = float(data.get("result", 0.0))
        except Exception:
            balance = 0.0
        self.zaddress_balance = balance
        try:
            if self.topup_content:
                self.topup_content.ids.status.text = "Received %s of %s %s" % (
                    balance, self.topup_arrr, SMSConf.TOPUP_COIN.upper())
        except Exception:
            pass
        if balance >= self.topup_arrr and self.topup_arrr > 0 and not self.topup_crediting:
            self.topup_crediting = True
            self._credit_topup()

    def _credit_topup(self):
        self._set_status("Payment detected - crediting balance...", ok=None)
        self._plan_call("POST", HTTParams.API_SMS_TOPUP, {
            "uuid"   : self.uuid,
            "amount" : float(self.topup_amount),
            "denom"  : "USD",
            "coin"   : SMSConf.TOPUP_COIN,
            "address": self.zaddress,
        }, self._on_topup_credited)

    def _on_topup_credited(self, request, result):
        data = self._parse(result) or {}
        if isinstance(data, dict) and data.get("balance") is not None:
            self._apply_balance_payload(data)
        self._close_topup_dialog()
        self.topup_started   = False
        self.topup_crediting = False
        self._set_status("Top-up complete: $%.2f added" % float(self.topup_amount), ok=True)
        self._toast("SMS balance topped up")

    def _close_topup_dialog(self):
        if self.topup_poll_event:
            self.topup_poll_event.cancel()
            self.topup_poll_event = None
        self.stop_event.set()
        if self.topup_dialog:
            try:
                self.topup_dialog.dismiss()
            except Exception:
                pass
            self.topup_dialog = None
        self.topup_content = None

    def cancel_topup(self, *args):
        self._close_topup_dialog()
        self.topup_started   = False
        self.topup_crediting = False
        self._set_status("Top-up cancelled", ok=None)

    # ------------------------------------------------------------------
    # Top-up with BTCPay (BTC Lightning, Monero, Litecoin MWEB, Zcash, Dash)
    # ------------------------------------------------------------------
    def _btcpay_coins(self):
        '''SMSConf.BTCPAY_COINS with the logo of every coin resolved on disk.

        The ``icon`` name is kept because utils.qr looks a bundled logo up by
        name, ``icon_path`` is the absolute file the picker dialog paints.
        '''
        coins = []
        for entry in SMSConf.BTCPAY_COINS:
            coin = dict(entry)
            coin["icon_path"] = self._asset(MeileColors.COIN_IMGS + "%s.png" % coin["icon"])
            coins.append(coin)
        return coins

    @staticmethod
    def _btcpay_code(value):
        '''Normalise a BTCPay payment method id ("btc_ln" -> "BTC-LN").'''
        return str(value or "").strip().upper().replace("_", "-")

    def _btcpay_coin(self, code):
        '''The SMSConf.BTCPAY_COINS entry of a crypto code (or None).'''
        wanted = self._btcpay_code(code)
        for coin in self._btcpay_coins():
            if self._btcpay_code(coin["code"]) == wanted:
                return coin
        return None

    @classmethod
    def _btcpay_lookup(cls, mapping, code):
        '''Case insensitive lookup of ``code`` in a BTCPay invoice dict.

        The keys of the legacy dictionaries (``addresses``, ``paymentCodes``,
        ``paymentSubtotals``, ...) are the payment method ids of the store, so
        a recent store names its Lightning entry "BTC-LightningNetwork" where
        SMSConf.BTCPAY_COINS says "BTC-LN" (see SMSConf.BTCPAY_METHOD_ALIASES).
        '''
        if not isinstance(mapping, dict):
            return None
        wanted = cls._btcpay_code(code)
        for key, value in mapping.items():
            found = cls._btcpay_code(key)
            if found == wanted or SMSConf.BTCPAY_METHOD_ALIASES.get(found) == wanted:
                return value
        return None

    @classmethod
    def _btcpay_bare_address(cls, value):
        '''Bare address (or BOLT11 invoice) carried by a BTCPay answer.

        ``addresses`` maps a payment method to its address / bolt11 string,
        while ``paymentCodes`` and ``paymentUrls`` carry whole wallet URIs
        ("monero:8AT...?amount=1.23") and payment links, so the scheme and the
        query string are stripped off here.
        '''
        if isinstance(value, dict):
            for key in ("BIP21", "bip21", "BOLT11", "bolt11", "address",
                        "uri", "URL", "url"):
                if value.get(key):
                    return cls._btcpay_bare_address(value[key])
            return ""
        text = str(value or "").strip()
        if ":" in text:
            text = text.split(":", 1)[1]
            if text.startswith("//"):
                text = text[2:]
        return text.split("?", 1)[0].strip()

    @classmethod
    def _btcpay_uri_amount(cls, value):
        '''Amount BTCPay itself put into a wallet URI (or None).

        The ``paymentCodes`` / ``paymentUrls`` of an invoice are meant to be
        opened by a wallet, so their ``amount`` / ``tx_amount`` is in whole
        coins - unlike the legacy ``paymentTotals`` / ``paymentSubtotals``,
        which the BitPay format reports in the smallest unit of the chain
        (satoshi, piconero, ...), where "14900" would mean 0.00014900 BTC.
        The amount of the URI is only read when the invoice has no legacy
        amount at all (see ``_btcpay_whole_coins``).
        '''
        if isinstance(value, dict):
            for key in ("BIP21", "bip21", "BOLT11", "bolt11", "uri", "URL", "url"):
                found = cls._btcpay_uri_amount(value.get(key))
                if found is not None:
                    return found
            return None
        text = str(value or "")
        if "?" not in text:
            return None
        for pair in text.split("?", 1)[1].split("&"):
            name, _, raw = pair.partition("=")
            if name.strip().lower() not in ("amount", "tx_amount", "txamount"):
                continue
            try:
                return float(unquote(raw))
            except (TypeError, ValueError):
                return None
        return None

    @classmethod
    def _btcpay_whole_coins(cls, amount, coin):
        '''Whole coins instead of a whole number of the smallest unit.

        The legacy dictionaries of a BitPay compatible invoice report every
        amount in the smallest unit of its chain - "paymentTotals": {"XMR":
        33806464744} is 0.033806464744 XMR while "BTC-LN": 24228 is 0.00024228
        BTC - and the size of that unit differs per coin: 8 decimals for the
        BTC family (satoshi, litoshi, zatoshi, duff) but 12 for Monero
        (piconero), so it is read from SMSConf.BTCPAY_COINS["units"].

        An integral amount is such a smallest-unit amount and is divided by the
        units of the coin; a wallet URI amount or a "paymentMethods" amount of
        the newer API already has decimals (whole coins) and is returned
        untouched, as is an amount of a coin without a "units" entry.
        '''
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return amount
        units = float(coin.get("units") or 0)
        if units > 1 and value >= 1 and value.is_integer():
            return value / units
        return amount

    @classmethod
    def _btcpay_method_ids(cls, method):
        '''Every id a ``paymentMethods`` entry of an invoice can be found by.

        The method of a recent store is named by the API ("BTC-LightningNetwork")
        while SMSConf.BTCPAY_COINS uses the id of the legacy dictionaries
        ("BTC-LN"), so every known alias is added to the ids of the entry.
        '''
        ids = []
        for key in ("cryptoCode", "paymentMethod", "paymentMethodId", "code"):
            if method.get(key):
                ids.append(cls._btcpay_code(method[key]))
        crypto = cls._btcpay_code(method.get("cryptoCode"))
        sub    = cls._btcpay_code(method.get("paymentMethod")
                                  or method.get("paymentMethodId"))
        if crypto and sub and not sub.startswith(crypto):
            ids.append("%s-%s" % (crypto, sub))
        for raw in list(ids):
            alias = SMSConf.BTCPAY_METHOD_ALIASES.get(raw)
            if alias and alias not in ids:
                ids.append(alias)
        return ids

    def open_btcpay_dialog(self):
        '''Pick the coin the BTCPay invoice of the entered amount is paid in.'''
        if not self.uuid:
            self._set_status("No wallet UUID - cannot top up", ok=False)
            return
        if self.btcpay_started:
            return
        if self.topup_started:
            self._set_status("A Pirate Chain top-up is already running", ok=False)
            return
        amount = float(self.topup_amount or 0.0)
        if amount < float(SMSConf.MIN_TOPUP_USD):
            self._set_status("Minimum top-up is $%.2f" % float(SMSConf.MIN_TOPUP_USD), ok=False)
            return
        coins = self._btcpay_coins()
        if not coins:
            self._set_status("No BTCPay coins configured", ok=False)
            return
        content = BTCPayCoinContent()
        for coin in coins:
            content.add_coin(coin, self.start_btcpay)
        self._close_btcpay_dialog()
        self.btcpay_coin_dialog = MDDialog(
            title="Pay $%.2f with BTCPay" % amount,
            type="custom",
            content_cls=content,
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.MEILE),
                    on_release=self.cancel_btcpay
                ),
            ]
        )
        self.btcpay_coin_dialog.open()
        self._set_status("Pick the coin to pay $%.2f in" % amount, ok=None)

    def start_btcpay(self, code):
        '''Create the BTCPay invoice for the coin the user picked.'''
        coin = self._btcpay_coin(code)
        if not coin or self.btcpay_started:
            return
        self._close_btcpay_dialog()
        self.btcpay_started    = True
        self.btcpay_crediting  = False
        self.btcpay_coin       = coin
        self.btcpay_code       = coin["code"]
        self.btcpay_invoice_id = ""
        self.btcpay_address    = ""
        self.btcpay_amount     = None
        self.btcpay_stop.clear()
        self._set_status("Creating BTCPay invoice...", ok=None)
        # Creating the invoice is a blocking HTTP call -> worker thread.
        Thread(target=self._btcpay_create_invoice, args=(coin,),
               daemon=True).start()

    def _btcpay_create_invoice(self, coin):
        '''Ask BTCPay for a USD invoice (blocking HTTP, worker thread).

        An invoice is quoted in USD and answers with one payment method per
        coin the store has enabled, so it is created once and the address of
        the picked coin is read out of the answer (see
        _btcpay_payment_method).  The merchant token of the pickled client is
        filled in by btcpay.BTCPayClient, it does not select a coin.
        '''
        try:
            btcpay  = BTCPayDB()
            pickled = btcpay.get_remote_btcpay_client()
            if not pickled:
                raise RuntimeError("no pickled BTCPay client data")
            self.btcpay_client = btcpay.unpickle_btc_client(pickled)
            email = getattr(scrtsxx, "BTCPayEmail", "") or ""
            invoice = self.btcpay_client.create_invoice({
                "price"            : float(self.topup_amount),
                "currency"         : "USD",
                "merchantName"     : "Meile dVPN",
                "itemDesc"         : "Meile SMS balance top-up",
                "notificationEmail": email,
                "transactionSpeed" : "high",
                "buyer"            : {"name"  : str(self.uuid),
                                      "email" : email,
                                      "notify": True}
            })
        except Exception as e:
            print("BTCPay invoice error: %s" % str(e))
            self._debug("BTCPay invoice ERR: %s" % str(e)[:200])
            Clock.schedule_once(lambda dt: self._btcpay_abort(
                "Could not create BTCPay invoice"), 0)
            return
        print("BTCPay invoice: %s" % str(invoice))
        Clock.schedule_once(lambda dt: self._btcpay_invoice_ready(coin, invoice), 0)

    @classmethod
    def _btcpay_available(cls, invoice):
        '''Ids of every payment method an invoice answers with (for messages).'''
        if not isinstance(invoice, dict):
            return ""
        ids = []
        for key in ("addresses", "paymentCodes", "paymentUrls", "paymentSubtotals"):
            value = invoice.get(key)
            if isinstance(value, dict):
                ids.extend(cls._btcpay_code(k) for k in value.keys())
        methods = invoice.get("paymentMethods")
        if isinstance(methods, list):
            for method in methods:
                if isinstance(method, dict):
                    ids.extend(cls._btcpay_method_ids(method))
        unique = []
        for item in ids:
            if item and item not in unique:
                unique.append(item)
        return ", ".join(unique)

    def _btcpay_payment_method(self, invoice, coin):
        '''Address, amount and real method id of ``coin`` inside an invoice.

        A legacy ("BitPay compatible") invoice answers with one entry per
        payment method enabled on the store::

            "addresses"       : {"BTC-LN": "lnbc1...", "XMR": "8AT..."}
            "paymentCodes"    : {"XMR": {"BIP21": "monero:8AT...?amount=1.2"}}
            "paymentUrls"     : {"XMR": {"BIP21": "monero:...", "BIP72": "..."}}
            "paymentTotals"   : {"XMR": 1234000000000}

        while the newer API answers with a ``paymentMethods`` list of
        {"cryptoCode": "XMR", "paymentMethod": "XMR", "destination": "8AT...",
        "amount": "1.234", "paymentLink": "..."} entries - both shapes are read
        here.  When a store does not expose the id of the coin method (BTCPay
        names the Lightning method "BTC-LN" and the MWEB method "LTC-MWEB", a
        store can also be limited to the plain coin) the bare crypto code is
        tried as a fallback so the invoice stays payable, and the ``code`` that
        actually matched is the one the dialog shows.

        The address is the bare address (or BOLT11 string) of the method while
        the amount is in whole coins.  ``paymentTotals`` (what the invoice asks
        for, network fee included) is the first choice because that is the
        number the store itself shows, then the amount BTCPay put into the
        wallet URI and finally the "amount" of the newer paymentMethods list;
        every one of them goes through ``_btcpay_whole_coins`` because the
        legacy fields are smallest-unit amounts.
        '''
        if not isinstance(invoice, dict):
            return None
        wanted = [self._btcpay_code(coin["code"])]
        base   = wanted[0].split("-")[0]
        if base and base != wanted[0]:
            wanted.append(base)

        addresses = invoice.get("addresses")
        codes     = invoice.get("paymentCodes")
        urls      = invoice.get("paymentUrls")
        totals    = invoice.get("paymentTotals") or invoice.get("paymentSubtotals")
        methods   = invoice.get("paymentMethods")

        for code in wanted:
            source  = self._btcpay_lookup(codes, code) or self._btcpay_lookup(urls, code)
            address = self._btcpay_bare_address(
                self._btcpay_lookup(addresses, code) or source)
            # An integral legacy amount is a smallest-unit amount of this chain
            # (33806464744 XMR -> 0.033806464744 XMR, 24228 BTC-LN satoshis ->
            # 0.00024228), see _btcpay_whole_coins.
            amount  = self._btcpay_whole_coins(
                self._btcpay_lookup(totals, code), coin)
            if amount in (None, ""):
                amount = self._btcpay_whole_coins(
                    self._btcpay_uri_amount(source), coin)
            if isinstance(methods, list):
                for method in methods:
                    if not isinstance(method, dict):
                        continue
                    if code not in self._btcpay_method_ids(method):
                        continue
                    if not address:
                        address = self._btcpay_bare_address(
                            method.get("destination") or method.get("address"))
                    if amount in (None, ""):
                        # "amount" / "due" are decimal strings in this API.
                        try:
                            amount = float(method.get("amount")
                                           or method.get("due"))
                        except (TypeError, ValueError):
                            amount = None
                        amount = self._btcpay_whole_coins(amount, coin)
                    break
            if address:
                return {"code": code, "address": address, "amount": amount}
        return None

    @staticmethod
    def _btcpay_amount_text(amount, coin=None):
        '''Readable crypto amount ("0.00123456") or "".

        BTCPay reports the amount of a payment method as a float, so it is
        printed with as many digits as the smallest unit of ``coin`` needs - 8
        for the BTC family, 12 for Monero, whose amounts would be cut off by a
        fixed "%.8f" (0.033806464744 XMR must not become 0.03380646) - and
        trailing zeroes are dropped.
        '''
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return ""
        digits = 8
        units  = int((coin or {}).get("units") or 0)
        if units > 1:
            digits = len(str(units)) - 1
        return (("%." + str(digits) + "f") % value).rstrip("0").rstrip(".")

    @classmethod
    def _btcpay_uri(cls, coin, address, amount):
        '''Wallet URI of ``address`` (see SMSConf.BTCPAY_COINS).

        A BOLT11 invoice carries its amount itself, Monero wallets read the
        amount from ``tx_amount`` while every BIP21 wallet expects ``amount``.
        '''
        address = str(address or "").strip()
        if not address:
            return ""
        scheme = coin.get("uri") or ""
        if scheme == "lightning":
            if address.lower().startswith("lightning:"):
                return address
            return "lightning:" + address
        text = cls._btcpay_amount_text(amount, coin)
        if scheme and text and coin.get("amount_key"):
            return "%s:%s?%s=%s" % (scheme, address, coin["amount_key"], text)
        return ("%s:%s" % (scheme, address)) if scheme else address

    def _btcpay_invoice_ready(self, coin, invoice):
        '''Show the QR code of the invoice and start watching it (main thread).'''
        if not self.btcpay_started:
            return
        payment = self._btcpay_payment_method(invoice, coin)
        if not payment:
            self._debug("BTCPay %s invoice: %s" % (coin["code"], str(invoice)[:400]))
            self._btcpay_abort("BTCPay invoice has no %s method (has: %s)" % (
                coin["code"], self._btcpay_available(invoice) or "none"))
            return
        self.btcpay_invoice_id = str(invoice.get("id") or "")
        self.btcpay_address    = payment["address"]
        self.btcpay_amount     = payment["amount"]
        # The store reports the method it really used ("BTC-LN", "XMR", ...).
        self.btcpay_code       = payment["code"]
        uri = self._btcpay_uri(coin, self.btcpay_address, self.btcpay_amount)
        self._debug("BTCPay %s invoice %s" % (self.btcpay_code, self.btcpay_invoice_id))
        self._show_btcpay_dialog(coin, uri)
        Thread(target=self._btcpay_watch, args=(self.btcpay_invoice_id,),
               daemon=True).start()

    def _show_btcpay_dialog(self, coin, uri):
        '''QR dialog of the created invoice (same layout as the ARRR top-up).'''
        amount  = self._btcpay_amount_text(self.btcpay_amount, coin)
        content = QRDialogContent()
        content.ids.zaddress_field.text = self.btcpay_address
        content.ids.price_field.text    = ("%s %s" % (amount, self.btcpay_code)
                                           if amount else self.btcpay_code)
        content.ids.status.text         = "Waiting for the %s payment..." % coin["label"]
        # A QR that cannot be drawn must say so instead of leaving an empty
        # white box in the dialog: the address (the wallet URI for Monero and
        # the BIP21 chains) is in the field below either way.
        qr_path = ""
        try:
            qr_path = QRCode().generate_payment_qr_code(
                uri, logo_path=coin["icon_path"])
        except Exception as e:
            print("BTCPay QR error: %s" % str(e))
            traceback.print_exc()
        if qr_path and path.exists(qr_path):
            content.ids.qr_img.source = qr_path
        else:
            print("BTCPay QR missing for %s (%s)" % (self.btcpay_code, qr_path))
            content.ids.status.text = ("Could not draw the QR code - pay the "
                                       "address below")
        self.btcpay_content = content

        if self.btcpay_dialog:
            try:
                self.btcpay_dialog.dismiss()
            except Exception:
                pass
            self.btcpay_dialog = None
        self.btcpay_dialog = MDDialog(
            title="Waiting for BTCPay invoice to be paid...",
            type="custom",
            content_cls=content,
            md_bg_color=get_color_from_hex(MeileColors.BLACK),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=get_color_from_hex(MeileColors.MEILE),
                    on_release=self.cancel_btcpay
                ),
            ]
        )
        self.btcpay_dialog.open()
        self._set_status("Waiting for BTCPay %s payment..." % self.btcpay_code, ok=None)

    def _btcpay_watch(self, invoice_id):
        '''Poll the BTCPay invoice until it is paid (worker thread).

        The invoice carries its own payment state, so no price lookup or
        address balance check is needed (unlike the ARRR top-up) - the
        btcpay-stop event ends the loop when the user cancels the dialog.
        '''
        while not self.btcpay_stop.is_set():
            if self.btcpay_stop.wait(float(SMSConf.BTCPAY_POLL)):
                break
            try:
                invoice = self.btcpay_client.get_invoice(invoice_id)
            except Exception as e:
                print("BTCPay invoice check error: %s" % str(e))
                continue
            status = str((invoice or {}).get("status", "")).lower()
            print("BTCPay invoice %s status: %s" % (invoice_id, status))
            Clock.schedule_once(lambda dt: self._btcpay_show_status(invoice), 0)
            if status in SMSConf.BTCPAY_PAID:
                Clock.schedule_once(lambda dt: self._btcpay_credit(), 0)
                return
            if status in SMSConf.BTCPAY_DEAD:
                Clock.schedule_once(lambda dt: self._btcpay_abort(
                    "BTCPay invoice %s" % status), 0)
                return

    def _btcpay_show_status(self, invoice):
        '''Mirror the invoice status into the open dialog (main thread).'''
        status = str((invoice or {}).get("status", "")).upper()
        if not status or not self.btcpay_content:
            return
        try:
            self.btcpay_content.ids.status.text = "BTCPay invoice: %s" % status
        except Exception:
            pass

    def _btcpay_credit(self):
        '''Invoice paid - credit the USD amount on the Meile ledger.'''
        if self.btcpay_crediting:
            return
        self.btcpay_crediting = True
        self._set_status("Payment detected - crediting balance...", ok=None)
        self._plan_call("POST", HTTParams.API_SMS_TOPUP, {
            "uuid"   : self.uuid,
            "amount" : float(self.topup_amount),
            "denom"  : "USD",
            "coin"   : self.btcpay_code,
            "address": self.btcpay_address,
        }, self._on_btcpay_credited)

    def _on_btcpay_credited(self, request, result):
        '''Credit answer of the ledger - refresh the balance card.'''
        data = self._parse(result) or {}
        if isinstance(data, dict) and data.get("balance") is not None:
            self._apply_balance_payload(data)
        else:
            self._debug("BTCPay credit response: %s" % str(result)[:200])
            self.fetch_balance()
        self._close_btcpay_dialog()
        self.btcpay_started   = False
        self.btcpay_crediting = False
        self._set_status("Top-up complete: $%.2f added" % float(self.topup_amount), ok=True)
        self._toast("SMS balance topped up")

    def _close_btcpay_dialog(self):
        '''Stop the invoice poller and close both BTCPay dialogs.'''
        self.btcpay_stop.set()
        for attr in ("btcpay_dialog", "btcpay_coin_dialog"):
            dialog = getattr(self, attr, None)
            if not dialog:
                continue
            try:
                dialog.dismiss()
            except Exception:
                pass
            setattr(self, attr, None)
        self.btcpay_content = None

    def cancel_btcpay(self, *args):
        self._close_btcpay_dialog()
        self.btcpay_started    = False
        self.btcpay_crediting  = False
        self.btcpay_invoice_id = ""
        self._set_status("Top-up cancelled", ok=None)

    def _btcpay_abort(self, message):
        '''Give up on the current invoice (creation or polling failure).'''
        self._close_btcpay_dialog()
        self.btcpay_started   = False
        self.btcpay_crediting = False
        self._set_status(message, ok=False)

    # ------------------------------------------------------------------
    # Countries (searchable list with flags)
    # ------------------------------------------------------------------
    def load_countries(self):
        self._sppost("/country/retrieve_all", {}, self._on_countries)

    def _on_countries(self, request, result):
        data = self._parse(result)
        if not isinstance(data, list):
            self._debug("Country load error: %s" % str(result)[:200])
            return
        self.countries = []
        for country in data:
            if not isinstance(country, dict):
                continue
            cid  = country.get("ID", country.get("id"))
            name = country.get("name") or country.get("country")
            if cid is None or not name:
                continue
            self.countries.append({"id": cid, "name": str(name), "raw": country})
        self.countries.sort(key=lambda c: c["name"].lower())
        for index, country in enumerate(self.countries):
            country["index"] = index
        self._render_countries(self._filtered_countries())
        self._debug("Loaded %d countries" % len(self.countries))

    def _filtered_countries(self):
        if not self.country_filter:
            return self.countries
        return [c for c in self.countries if self.country_filter in c["name"].lower()]

    def filter_countries(self, text):
        self.country_filter = (text or "").strip().lower()
        self._render_countries(self._filtered_countries())

    def _render_countries(self, matches):
        data = []
        for country in matches[:500]:
            data.append({
                "country_text" : country["name"],
                "flag_source"  : self._flag_source(country["raw"]),
                "country_index": country["index"],
                "is_selected"  : country["index"] == self.selected_index,
            })
        try:
            rv = self.ids.country_rv
            rv.data = data
            rv.refresh_from_data()
        except Exception as e:
            print("SMSPoolScreen._render_countries: %s" % str(e))

    def select_country(self, index):
        try:
            index = int(index)
        except Exception:
            return
        if index < 0 or index >= len(self.countries):
            return
        self.selected_index   = index
        self.selected_country = self.countries[index]
        try:
            self.ids.selected_country_label.text = self.selected_country["name"]
            self.ids.selected_flag.source = self._flag_source(self.selected_country["raw"])
        except Exception:
            pass
        # Re-render so the highlight follows the selection.
        self._render_countries(self._filtered_countries())
        # Country picked: quote it as soon as a service is known too.
        self.request_quote()

    @staticmethod
    def _country_iso2(raw):
        if not isinstance(raw, dict):
            return ""
        for key in ("short_name", "country_code", "code", "iso", "iso2",
                    "alpha2", "iso_code"):
            value = raw.get(key)
            if value:
                value = str(value).strip().lower()
                if len(value) == 2:
                    return value
        name = raw.get("name") or raw.get("country")
        if name:
            try:
                return OurWorld.our_world.get_country_ISO2(str(name)).lower()
            except Exception:
                pass
        return ""

    def _flag_source(self, raw):
        MeileConfig = MeileGuiConfig()
        from typedef.konstants import MeileColors
        iso2 = self._country_iso2(raw)
        if not iso2:
            return ""
        relative = MeileConfig.resource_path(path.join(MeileColors.FLOC, "flags", "%s.png" % iso2))
        if path.exists(relative):
            return relative
        absolute = path.join(path.dirname(path.dirname(path.abspath(__file__))),
                             "imgs", "flags", "%s.png" % iso2)
        if path.exists(absolute):
            return absolute
        return relative

    # ------------------------------------------------------------------
    # Services (searchable list + "Not Listed / Other" fallback)
    # ------------------------------------------------------------------
    def load_services(self):
        self._sppost("/service/retrieve_all", {}, self._on_services)

    def _on_services(self, request, result):
        data = self._parse(result)
        if not isinstance(data, list):
            self._debug("Service load error: %s" % str(result)[:200])
            return
        self.services = {}
        for service in data:
            if not isinstance(service, dict):
                continue
            sid  = service.get("ID", service.get("id"))
            name = service.get("name")
            if sid is None or not name:
                continue
            self.services[str(name)] = sid
        self._other_service = self._find_other_service()
        if self.selected_service not in self.services:
            # Preselect a real service so PURCHASE works straight away (the
            # behaviour the old Spinner had with its first entry).
            normal = sorted(n for n in self.services if n != self._other_service)
            self.selected_service = normal[0] if normal else self._other_service
        self._sync_selected_service()
        self._debug("Loaded %d services" % len(self.services))

    def _find_other_service(self):
        '''Name of SMSPool's catch-all service ("Not Listed / Other / Any").

        SMSPool ships that service with a real id, so the option is fully
        purchasable.  Should SMSPool ever rename or drop it, the configured
        label is added with no id instead: the option stays visible and
        purchase() reports the problem rather than silently doing nothing.
        '''
        for name in sorted(self.services):
            normalised = " ".join(str(name).strip().lower().split())
            if normalised in SMSConf.OTHER_SERVICE_NAMES:
                return name
            if normalised.startswith("not listed"):
                return name
        label = SMSConf.OTHER_SERVICE_LABEL
        if label not in self.services:
            self.services[label] = None
        return label

    def _filtered_services(self):
        names = sorted(n for n in self.services if n != self._other_service)
        if self.service_filter:
            names = [n for n in names if self.service_filter in n.lower()]
        # The catch-all entry is always part of the list; when a search finds
        # nothing it becomes the only row, so an unlisted service never
        # dead-ends in an empty list.
        if self._other_service and (not self.service_filter or not names):
            names.append(self._other_service)
        return names

    def filter_services(self, text):
        self.service_filter = (text or "").strip().lower()
        self._render_services(self._filtered_services())

    def _render_services(self, matches):
        data = []
        for name in matches:
            data.append({
                "service_text": name,
                "is_selected" : name == self.selected_service,
            })
        try:
            rv = self.ids.service_rv
            rv.data = data
            rv.refresh_from_data()
        except Exception as e:
            print("SMSPoolScreen._render_services: %s" % str(e))

    def select_service(self, name):
        name = str(name or "")
        if name not in self.services:
            return
        self.selected_service = name
        self._sync_selected_service()

    def _sync_selected_service(self):
        try:
            self.ids.selected_service_label.text = (self.selected_service
                                                    or "No service selected")
        except Exception:
            pass
        # Re-render so the highlight follows the selection.
        self._render_services(self._filtered_services())
        # Service picked: refresh the price/success-rate quote for it.
        self.request_quote()

    # ------------------------------------------------------------------
    # Price quote (country + service -> cost & success rate)
    # ------------------------------------------------------------------
    def request_quote(self, *args):
        '''Ask SMSPool what a number costs for the current selection.

        POST /request/price (SMSPool docs, "Retrieve specific price & Success
        Rate") answers with the pool price *and* the historic success rate of
        that provider for the picked country/service - both are shown in the
        PRICE QUOTE card.  The call is debounced so clicking through the lists
        only fires once the user settles, and every new selection invalidates
        answers still in flight (see quote_seq / _on_quote).
        '''
        self.quote_seq += 1
        if self.quote_event:
            self.quote_event.cancel()
            self.quote_event = None
        if self.selected_country is None or self.service_id() is None:
            self.quote = None
            self._render_quote()
            return
        if not self.API_KEY.strip():
            self.quote = None
            self._render_quote(error="SMSPool key missing in secrets")
            return
        # Drop the previous combination's numbers right away: they no longer
        # describe what the user has picked.
        self.quote = None
        self._render_quote(loading=True)
        self.quote_event = Clock.schedule_once(
            lambda dt: self._fetch_quote(self.quote_seq),
            float(SMSConf.QUOTE_DEBOUNCE))

    def _fetch_quote(self, token=None):
        self.quote_event = None
        if token is None:
            token = self.quote_seq
        if token != self.quote_seq:
            return                      # a newer selection won the race
        country = self.selected_country
        sid     = self.service_id()
        if country is None or sid is None:
            return
        self._render_quote(loading=True)
        self._sppost("/request/price", {
            "key"    : self.API_KEY.strip(),
            "country": str(country["id"]),
            "service": str(sid),
        }, lambda request, result: self._on_quote(token, request, result))

    def _on_quote(self, token, request, result):
        '''Paint the answer, unless a newer selection already replaced it.'''
        if token != self.quote_seq:
            return
        data = self._parse(result) or {}
        price, rate = self._price_from_payload(data)
        if price is None or price <= 0:
            message = self._error_message(data) or "No pool for this combination"
            self.quote = None
            self._render_quote(error=message)
            self._debug("quote response: %s" % str(result)[:200])
            return
        self._store_quote(price, rate)

    def _store_quote(self, price, rate):
        '''Remember a provider price (SMSPool cost) and show it with markup.'''
        price = float(price)
        self.quote = {
            "price"       : price,
            "total"       : round(price * (1.0 + float(self.markup or 0.0) / 100.0), 6),
            "success_rate": rate,
            "country"     : self.selected_country["name"] if self.selected_country else "",
            "service"     : self.selected_service or "",
        }
        self._render_quote()

    def _rate_style(self, rate):
        '''(text, word, colour) for a provider success rate in percent.'''
        if rate is None:
            return "n/a", "", self.PLACEHOLDER
        rate = max(0.0, min(100.0, float(rate)))
        if rate >= float(SMSConf.SUCCESS_GOOD):
            return "%.0f%%" % rate, "Excellent", self.RATE_GOOD
        if rate >= float(SMSConf.SUCCESS_FAIR):
            return "%.0f%%" % rate, "Fair", self.RATE_FAIR
        return "%.0f%%" % rate, "Poor", self.RATE_POOR

    def _render_quote(self, loading=False, error=""):
        '''Paint the PRICE QUOTE card from self.quote / the given state.

        Four states: idle (nothing picked yet), loading, error and ready - the
        latter carries the cost to purchase *plus* the provider's success rate.
        '''
        quote  = self.quote or {}
        total  = quote.get("total")
        price  = quote.get("price")
        markup = float(self.markup or 0.0)
        rate_colour  = self.PLACEHOLDER
        detail_colour = self.PLACEHOLDER

        if loading:
            total_text  = "..."
            rate_text   = "..."
            rate_word   = "checking"
            detail_text = "Asking the provider for a price..."
            hint_text   = self.QUOTE_RATE_HINT
        elif error:
            total_text    = "---"
            rate_text     = "---"
            rate_word     = ""
            detail_text   = str(error)
            rate_colour   = self.RATE_POOR
            detail_colour = self.RATE_POOR
            hint_text     = self.QUOTE_IDLE_HINT
        elif total is None or price is None:
            total_text  = "---"
            rate_text   = "---"
            rate_word   = ""
            detail_text = "Provider cost + Meile markup"
            hint_text   = self.QUOTE_IDLE_HINT
        else:
            total_text  = "$%.2f" % total
            rate_text, rate_word, rate_colour = self._rate_style(quote.get("success_rate"))
            detail_text = "Provider $%.2f" % (total)
            hint_text   = self.QUOTE_RATE_HINT
            # Only compare against the wallet once a balance is actually known.
            if self.uuid:
                if self.balance >= total:
                    detail_text += " - balance $%.2f" % self.balance
                else:
                    detail_text  += " - top up $%.2f" % (total - self.balance)
                    detail_colour = self.RATE_POOR

        try:
            self.ids.quote_total_label.text = total_text
        except Exception:
            pass
        try:
            label = self.ids.quote_rate_label
            label.text  = rate_text
            label.color = get_color_from_hex(rate_colour)
        except Exception:
            pass
        try:
            label = self.ids.quote_rate_note
            label.text  = rate_word
            label.color = get_color_from_hex(rate_colour)
        except Exception:
            pass
        try:
            self.ids.quote_rate_dot.dot_color = rate_colour
        except Exception:
            pass
        try:
            label = self.ids.quote_detail_label
            label.text  = detail_text
            label.color = get_color_from_hex(detail_colour)
        except Exception:
            pass
        try:
            self.ids.quote_hint_label.text = hint_text
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Price / purchase
    # ------------------------------------------------------------------
    def service_id(self):
        '''Id of the service currently selected in the list (or None).'''
        if not self.selected_service:
            return None
        return self.services.get(self.selected_service)

    def purchase(self):
        if not self.API_KEY.strip():
            self._set_status("SMSPool key missing in secrets", ok=False)
            return
        if self.selected_country is None:
            self._set_status("Select a country first", ok=False)
            return
        if not self.selected_service:
            self._set_status("Select a service", ok=False)
            return
        sid = self.service_id()
        if sid is None:
            self._set_status("Not listed on SMSPool - contact support", ok=False)
            return
        self._pending_service = self.selected_service
        self._set_status("Fetching price...", ok=None)
        try:
            self.ids.purchase_btn.disabled = True
        except Exception:
            pass
        self._sppost("/request/price", {
            "key"    : self.API_KEY.strip(),
            "country": str(self.selected_country["id"]),
            "service": str(sid),
        }, self._on_price)

    def _on_price(self, request, result):
        try:
            self.ids.purchase_btn.disabled = False
        except Exception:
            pass
        data  = self._parse(result) or {}
        price, rate = self._price_from_payload(data)
        if price is None or price <= 0:
            message = self._error_message(data) or "no pool"
            self._set_status("Price unavailable: %s" % message, ok=False)
            self.quote = None
            self._render_quote(error=message)
            self._debug("price response: %s" % str(result)[:200])
            return
        total = round(price * (1.0 + self.markup / 100.0), 6)
        # The price fetched for the purchase is the freshest quote there is.
        self._store_quote(price, rate)
        if self.balance < total:
            missing = total - self.balance
            self._set_status("Insufficient balance - top up $%.2f" % missing, ok=False)
            self._toast("Insufficient balance (need $%.2f)" % total)
            return
        self._do_purchase(price)

    def _do_purchase(self, price):
        self._pending_price = price
        self._set_status("Ordering number...", ok=None)
        try:
            self.ids.purchase_btn.disabled = True
        except Exception:
            pass
        self._sppost("/purchase/sms", {
            "key"    : self.API_KEY.strip(),
            "country": str(self.selected_country["id"]),
            "service": str(self.service_id()),
        }, self._on_order_success, self._on_order_error)

    def _on_order_error(self, request, error):
        try:
            self.ids.purchase_btn.disabled = False
        except Exception:
            pass
        self._set_status("Order error: %s" % str(error)[:120], ok=False)
        self._debug("Purchase ERR: %s" % str(error))

    def _on_order_success(self, request, result):
        try:
            self.ids.purchase_btn.disabled = False
        except Exception:
            pass
        self._debug("Order response: %s" % str(result)[:300])
        data = self._parse(result)
        if not isinstance(data, dict):
            self._set_status("Invalid order response", ok=False)
            return
        if str(data.get("success")) != "1":
            message = data.get("message") or data.get("errors") or "unknown"
            self._set_status("Order failed: %s" % message, ok=False)
            return

        try:
            cost = float(data.get("cost"))
        except Exception:
            cost = float(self._pending_price or 0.0)

        self.current_order = {
            "id"        : data.get("order_id") or data.get("orderid"),
            "number"    : data.get("number") or data.get("phonenumber"),
            "country"   : self.selected_country["name"],
            "country_id": self.selected_country["id"],
            "service"   : self._pending_service,
            "service_id": self.service_id(),
            "cost"      : cost,
            "refunded"  : False,
        }
        try:
            self.ids.phone_label.text = str(self.current_order["number"])
            self.ids.sms_output.text  = ""
        except Exception:
            pass
        # /purchase/sms reports the real expiry ("expiration" unix ts or
        # "expires_in" seconds). Prefer it over the configured fallback.
        self._order_expiration = None
        expiration = data.get("expiration")
        if expiration:
            try:
                self._order_expiration = float(expiration)
            except Exception:
                self._order_expiration = None
        if self._order_expiration is None:
            try:
                expires_in = float(data.get("expires_in") or 0)
            except Exception:
                expires_in = 0.0
            if expires_in > 0:
                self._order_expiration = time() + expires_in
        self._set_status("Order #%s active" % str(self.current_order["id"]), ok=True)
        # Debit the Meile ledger, then start the countdown/inbox polling.
        self._debit_order(cost)
        self._start_order_tracking()

    def _debit_order(self, cost):
        order = self.current_order
        if not order:
            return
        self._plan_call("POST", HTTParams.API_SMS_PURCHASE, {
            "uuid"      : self.uuid,
            "order_id"  : str(order["id"]),
            "country_id": str(order["country_id"]),
            "country"   : order["country"],
            "service_id": str(order["service_id"]),
            "service"   : str(order["service"]),
            "phone"     : str(order["number"]),
            "cost"      : cost,
        }, self._on_order_debited, on_error=self._on_order_debit_error)

    def _on_order_debited(self, request, result):
        data = self._parse(result) or {}
        if isinstance(data, dict) and data.get("balance") is not None:
            self._apply_balance_payload(data)
        # SMSPool may charge a different price than quoted; remember it so a
        # refund credits back exactly what was taken.
        if isinstance(data, dict) and data.get("charged") is not None:
            try:
                self.current_order["charged"] = float(data["charged"])
            except Exception:
                pass

    def _on_order_debit_error(self, request, error):
        self._debug("Debit failed: %s" % str(error)[:200])
        self._set_status("Balance debit failed - releasing number...", ok=False)
        # Never leave a provider order running that was not paid for.
        if self.current_order and self.current_order.get("id"):
            self._sppost("/sms/cancel", {
                "key"    : self.API_KEY.strip(),
                "orderid": str(self.current_order["id"]),
            }, self._on_rollback_cancel, self._on_rollback_cancel_error)
        else:
            self._reset_order()

    def _on_rollback_cancel(self, request, result):
        self._reset_order()
        self._set_status("Order cancelled (balance debit failed)", ok=False)

    def _on_rollback_cancel_error(self, request, error):
        self._reset_order()
        self._set_status("Debit failed and provider release failed", ok=False)

    # ------------------------------------------------------------------
    # Order tracking (countdown + inbox polling)
    # ------------------------------------------------------------------
    def _start_order_tracking(self):
        self._stop_polling()
        self.order_deadline = self._order_expiration
        if not self.order_deadline or self.order_deadline <= time():
            self.order_deadline = time() + float(SMSConf.ORDER_SECONDS)
        self.countdown_event = Clock.schedule_interval(self._tick_countdown, 1)
        self._tick_countdown(0)
        self.sms_check_event = Clock.schedule_interval(
            self._check_sms, float(SMSConf.POLL_INTERVAL))

    def _stop_polling(self):
        if self.sms_check_event:
            self.sms_check_event.cancel()
            self.sms_check_event = None
        if self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None

    def _tick_countdown(self, dt):
        if not self.order_deadline:
            return False
        remaining = int(self.order_deadline - time())
        if remaining <= 0:
            try:
                self.ids.countdown_label.text = "expired"
            except Exception:
                pass
            self.countdown_event = None
            self._set_status("Number expired - cancel to refund", ok=False)
            return False
        minutes, seconds = divmod(remaining, 60)
        try:
            self.ids.countdown_label.text = "%02d:%02d" % (minutes, seconds)
        except Exception:
            pass
        return True

    def _check_sms(self, dt):
        if not self.current_order or not self.current_order.get("id"):
            self.sms_check_event = None
            return False
        if not self.API_KEY.strip():
            self.sms_check_event = None
            return False
        self._sppost("/sms/check", {
            "key"    : self.API_KEY.strip(),
            "orderid": str(self.current_order["id"]),
        }, self._on_sms_received, self._on_sms_check_error)
        return True

    def _on_sms_check_error(self, request, error):
        self._debug("sms/check error: %s" % str(error)[:150])

    def _on_sms_received(self, request, result):
        data = self._parse(result)
        if not isinstance(data, dict):
            return
        status = str(data.get("status", ""))
        sms    = data.get("sms") or data.get("full_sms")
        if status == "3" and sms:
            existing = ""
            try:
                existing = self.ids.sms_output.text or ""
            except Exception:
                pass
            if sms not in existing:
                try:
                    self.ids.sms_output.text = "[RECEIVED]\n%s\n\n%s" % (sms, existing)
                except Exception:
                    pass
            self._set_status("SMS received", ok=True)
            self._stop_polling()
        elif status in ("2", "5", "6"):
            # Terminal states documented by SMSPool: 2 expired, 5 cancelled,
            # 6 refunded (the provider already credited its own balance back).
            labels = {
                "2": "Number expired - refunding",
                "5": "Order cancelled by provider - refunding",
                "6": "Number released by provider - refunding",
            }
            self._set_status(labels.get(status, "Order closed"), ok=False)
            self._stop_polling()
            self._refund_order()

    # ------------------------------------------------------------------
    # Cancel + refund
    # ------------------------------------------------------------------
    def cancel_order(self):
        if not self.current_order or not self.current_order.get("id"):
            self._set_status("No active order", ok=False)
            return
        if not self.API_KEY.strip():
            self._set_status("SMSPool key missing in secrets", ok=False)
            return
        self._set_status("Cancelling order...", ok=None)
        self._stop_polling()
        self._sppost("/sms/cancel", {
            "key"    : self.API_KEY.strip(),
            "orderid": str(self.current_order["id"]),
        }, self._on_cancel_success, self._on_cancel_error)

    def _on_cancel_success(self, request, result):
        data = self._parse(result)
        if isinstance(data, dict) and str(data.get("success")) == "1":
            try:
                self.ids.sms_output.text = "[CANCELLED]\n\n" + (self.ids.sms_output.text or "")
            except Exception:
                pass
            self._set_status("Order cancelled - refunding balance...", ok=None)
            self._refund_order()
        else:
            message = data.get("message") if isinstance(data, dict) else None
            self._set_status("Cancel failed: %s" % (message or "unknown"), ok=False)

    def _on_cancel_error(self, request, error):
        self._set_status("Cancel error: %s" % str(error)[:120], ok=False)

    def _refund_order(self):
        order = self.current_order
        if not order or not order.get("id") or order.get("refunded"):
            return
        order["refunded"] = True
        payload = {"uuid": self.uuid, "order_id": str(order["id"])}
        if order.get("charged") is not None:
            payload["amount"] = order["charged"]
        self._plan_call("POST", HTTParams.API_SMS_REFUND, payload,
                        self._on_refunded, on_error=self._on_refund_error)

    def _on_refunded(self, request, result):
        data = self._parse(result) or {}
        if isinstance(data, dict) and data.get("balance") is not None:
            self._apply_balance_payload(data)
        if isinstance(data, dict) and data.get("amount") is not None:
            self._toast("Refunded $%s" % str(data["amount"]))
        self._set_status("Order cancelled & refunded", ok=None)
        self._reset_order()

    def _on_refund_error(self, request, error):
        self._debug("Refund failed: %s" % str(error)[:200])
        self._set_status("Cancelled, but refund failed - contact support", ok=False)
        self._reset_order()

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def copy_number(self, *args):
        '''Copy the rented number (ACTIVE ORDER copy icon) to the clipboard.'''
        try:
            number = self.ids.phone_label.text
        except Exception:
            number = ""
        if number and number not in ("---", ""):
            Clipboard.copy(number)
            self._toast("Phone number copied")
        else:
            self._toast("No number to copy")

    def copy_uuid(self, *args):
        '''Copy the wallet UUID shown in the header box to the clipboard.'''
        if not self.uuid:
            self._toast("No wallet UUID to copy")
            return
        try:
            Clipboard.copy(str(self.uuid))
            self._toast("Wallet address copied")
        except Exception as e:
            self._debug("Clipboard error: %s" % str(e)[:120])

    def open_arrr_exchange(self, *args):
        '''Send the user to the exchange where ARRR can be bought.

        The invoice in the top-up dialog is paid in Pirate Chain (ARRR), which
        is not sold on the usual exchanges - so the top-up card offers a
        one click hop to NonKYC (see SMSConf.ARRR_EXCHANGE_URL).
        '''
        import webbrowser

        webbrowser.open(SMSConf.ARRR_EXCHANGE_URL)

    def _reset_order(self):
        self.current_order     = None
        self.order_deadline    = None
        self._order_expiration = None
        self._stop_polling()
        try:
            self.ids.phone_label.text     = "---"
            self.ids.countdown_label.text = "--:--"
        except Exception:
            pass

    def set_previous_screen(self):
        self._stop_polling()
        self._close_topup_dialog()
        if self.quote_event:
            self.quote_event.cancel()
            self.quote_event = None
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.MAIN_WINDOW





