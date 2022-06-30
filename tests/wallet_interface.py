from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard, MDCardSwipe
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.clock import Clock, mainthread
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from os import path

import requests

import qrcode
from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps
from dns.rdataclass import NONE

ADDRESS = "sent1hfkgxzrkhxdxdwjy8d74jhc4dcw5e9zm7vfzh4"
BASEDIR = path.join(path.expanduser('~'), '.meile-gui')
IMGDIR    = path.join(BASEDIR, 'img')
IBCSCRT  = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
IBCATOM  = 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477'
IBCDEC   = 'ibc/B1C0DDB14F25279A2026BC8794E12B259F8BDA546A3C5132CCAEE4431CE36783'
IBCOSMO  = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'
IBCUNKWN = 'ibc/9BCB27203424535B6230D594553F1659C77EC173E36D9CF4759E7186EE747E84'

APIURL   = "https://api.sentinel.mathnodes.com"
SATOSHI = 1000000



KVSTRING = '''

#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Gradient kivy_gradient.Gradient

WindowManager:

    
<MainScreen>:
    canvas.before:
        Rectangle:
            size: self.size
            pos: self.pos
            texture: Gradient.horizontal(get_color_from_hex("#fcb711"), get_color_from_hex("#ffffff"))
    name: "main"
    md_bg_color: get_color_from_hex("#0d021b")
    wallet_name: "Bernoulli Numbers"
    address_qrcode: ""
    sentinel_logo: "../src/imgs/dvpn.png"
    secret_logo: "../src/imgs/scrt.png"
    osmosis_logo: "../src/imgs/osmo.png"
    cosmos_logo: "../src/imgs/atom.png"
    decentr_logo: "../src/imgs/dec.png"
    dec_text: "500 dec"
    scrt_text: " "
    atom_text: " "
    dvpn_text: " "
    osmo_text: " "
    MDBoxLayout:
        
        orientation: "vertical"
        MDToolbar:
            
            id: toolbar
            title: "Sentinel dVPN"
            md_bg_color: get_color_from_hex("#0d021b")
            height: "100dp"
            padding: 10,0,0,10
            spacing: "10dp"
            right_action_items:
                [
                ["lan-disconnect", lambda x: root.blargy(), "Disconnect"],
                ["wallet", lambda x: root.wallet(), "Wallet"],
                ]
            MDLabel:
                text: root.wallet_name
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#FFFFFF")

        MDFloatLayout:
            
            Image:
                source: root.get_qr_code_address()
                pos_hint: {'x': 0, 'top': 1}
                size_hint_y: .5
            
            Image:
                source: root.sentinel_logo
                pos_hint: {'x': -.2, 'top': .9}
            MDLabel:
                text: root.dvpn_text
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                pos_hint: {'x': .35, 'top': .905}

            Image:
                source: root.secret_logo
                pos_hint: {'x': -.2, 'top': .77}
                
            MDLabel:
                text: root.scrt_text
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                pos_hint: {'x': .35, 'top': .7695}
            Image:
                source: root.osmosis_logo
                pos_hint: {'x': -.2, 'top': .63}
                
            MDLabel:
                text: root.osmo_text
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                pos_hint: {'x': .35, 'top': .6295}
            Image:
                source: root.cosmos_logo
                pos_hint: {'x': .25, 'top': .89}
                
            MDLabel:
                text: root.atom_text
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                pos_hint: {'x': .8, 'top': .89}
            Image:
                source: root.decentr_logo
                pos_hint: {'x': .25, 'top': .76}
                
            MDLabel:
                text: root.dec_text
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                pos_hint: {'x': .8, 'top': .76}
'''

class WindowManager(ScreenManager):
    pass
    
class MainScreen(Screen):
    text = StringProperty()
    CoinDict = None
    dialog = None
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        print("Blargy")
        Clock.schedule_once(self.build)
        
    def blargy(self):
        
        self.dialog = MDDialog(
            text="Error disconnecting from node",
            buttons=[
                MDFlatButton(
                    text="Okay",
                    on_release=self.closeMe,
                ),
                ]
            )
        self.dialog.open()
            
    def closeMe(self, dt):
        self.dialog.dismiss()
        
    def build(self, dt):
        self.CoinDict = self.get_balance(ADDRESS)
        self.SetBalances()
        print("BLARGY")
        
        
    def get_qr_code_address(self):
        if not path.isfile(path.join(IMGDIR, "dvpn.png")):
            self.generate_qr_code(ADDRESS)
            
        return path.join(IMGDIR, "dvpn.png")
    
    def SetBalances(self):
        self.dec_text = str(self.CoinDict['dec']) + " dec"
        self.scrt_text = str(self.CoinDict['scrt']) + " scrt"
        self.atom_text = str(self.CoinDict['atom']) + " atom" 
        self.osmo_text = str(self.CoinDict['osmo']) + " osmo"
        self.dvpn_text = str(self.CoinDict['dvpn']) + " dvpn"       
      
    def generate_qr_code(self, ADDRESS):
        DepositCoin    = "dvpn"
        DepositAddress = ADDRESS 
    
        coinLogo = "../src/imgs/dvpn.png"
        logo = Image.open(coinLogo)
        basewidth = 100
         
        # adjust image size
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize))
        
        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        QRcode.add_data(DepositAddress)
        QRcode.make()

        QRimg = QRcode.make_image(fill_color='Black', back_color="white").convert('RGB')
         
        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
               (QRimg.size[1] - logo.size[1]) // 2)
        
        QRimg.paste(logo, pos)
        
        # crop a bit
        border = (0, 4, 0, 30) # left, top, right, bottom
        QRimg = ImageOps.crop(QRimg, border)
        
        
        # Next Process is adding and centering the Deposit address on the image
        # Creating a background a little larger and pasting the QR
        # Image onto it with the text
        if len(DepositAddress) <= 50:
            fontSize = 12
        elif len(DepositAddress) <=75:
            fontSize = 11
        else:
            fontSize = 10
            
        background = Image.new('RGBA', (QRimg.size[0], QRimg.size[1] + 15), (255,255,255,255))
        #robotoFont = ImageFont.truetype(pkg_resources.resource_filename(__name__, os.path.join('fonts', 'Roboto-BoldItalic.ttf')), fontSize)
        robotoFont = ImageFont.truetype('../src/fonts/Roboto-BoldItalic.ttf', fontSize)
    
        draw = ImageDraw.Draw(background)
        w,h  = draw.textsize(DepositAddress)
        draw.text(((QRimg.size[0]+15 - w)/2,QRimg.size[1]-2),DepositAddress, (0,0,0), font=robotoFont)
        
        background.paste(QRimg, (0,0))
        background.save(path.join(IMGDIR, DepositCoin + ".png"))
        
    def get_balance(self, address):
        endpoint = "/bank/balances/" + address
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        try:
            r = requests.get(APIURL + endpoint)
        except:
            return None
            
        
        coinJSON = r.json()
        print(coinJSON)
        for coin in coinJSON['result']:
            if "udvpn" in coin['denom']:
                CoinDict['dvpn'] = round(float(float(coin['amount']) / SATOSHI),4)
            elif IBCSCRT in coin['denom']:
                CoinDict['scrt'] = round(float(float(coin['amount']) / SATOSHI),4)
            elif IBCDEC in coin['denom']:
                CoinDict['dec'] = round(float(float(coin['amount']) / SATOSHI),4)
            elif IBCATOM in coin['denom']:
                CoinDict['atom'] = round(float(float(coin['amount']) / SATOSHI),4)
            elif IBCOSMO in coin['denom']:
                CoinDict['osmo'] = round(float(float(coin['amount']) / SATOSHI),4)
                
        return CoinDict

        
class TestApp(MDApp):
    title = "RecycleView Direct Test"
    
    def build(self):
        kv = Builder.load_string(KVSTRING)
                            
        manager = WindowManager()
        manager.add_widget(MainScreen(name="main"))
        return manager
    
if __name__ == "__main__":
    Test = TestApp()
    
    Test.run()