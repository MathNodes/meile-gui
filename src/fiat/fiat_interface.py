from kivymd.uix.menu import MDDropdownMenu
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty,ObjectProperty

 
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivyoav.delayed import delayable
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.theming import ThemeManager
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineIconListItem, OneLineListItem

from functools import partial
from datetime import datetime
from os import path
import requests
from requests.auth import HTTPBasicAuth
from pycoingecko import CoinGeckoAPI 


import stripe 
from stripe.error import CardError
from fiat.stripe_pay.charge import HotwalletFuncs as HandleWalletFunctions
import fiat.stripe_pay.charge as Charge
from fiat.stripe_pay import scrtsxx


from typedef.win import WindowNames
from ui.interfaces import TXContent
from conf.meile_config import MeileGuiConfig
import main.main as Meile


HotWalletAddress = scrtsxx.WALLET_ADDRESS
class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class FiatInterface(Screen):
    dialog = None
    menu_month = None
    menu_year = None
    menu_dvpn_qty = None
    month = "01"
    year = "2022"
    policy = False
    my_wallet_address = None
    DVPNOptions = [1000,2000,5000,10000]
    idvpn = 0
    CONFIG = None
    clock = None
    def __init__(self, **kwargs):
        super(FiatInterface, self).__init__()
        self.clock = Clock.create_trigger(self.set_dvpn_price, 20)
        self.clock()
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}" if i > 9 else f"%s" % ("0" + str(i)),
                "height": dp(56),
                "on_release": lambda x=f"{i}" if i > 9 else f"%s" % ("0" + str(i)): self.set_month(x),
            } for i in range(1,13)
        ]
        self.menu_month = MDDropdownMenu(
            caller=self.ids.month_list,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_month.bind()
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_year(x),
            } for i in range(2022,2035)
        ]
        self.menu_year = MDDropdownMenu(
            caller=self.ids.year_list,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_year.bind()
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_dvpn_qty(x),
            } for i in self.DVPNOptions
        ]
        self.menu_dvpn_qty = MDDropdownMenu(
            caller=self.ids.dvpn_qty_menu,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_dvpn_qty.bind()
        
        
    
    @delayable
    def pay(self):
        print(len(str(self.ids.ccnum.ids.ccnum.text)))
        if len(self.ids.ccnum.ids.ccnum.text) < 16 or len(self.ids.ccnum.ids.ccnum.text) > 16:
            self.ids.credit_card_number_warning.opacity = 1
        elif len(self.ids.cvvnum.ids.cvvnum.text) > 4 or len(self.ids.cvvnum.ids.cvvnum.text) < 3:
            self.ids.cvv_code_warning.opacity = 1
            
        else:
            if self.get_dvpn_price() > 0:
                if self.policy:
                    self.ProcessingDialog("Checking wallet for sufficient coins....", False,False)
                    yield 2
                    Wallet = HandleWalletFunctions()
                    try:
                        CoinDict = Wallet.get_balance(HotWalletAddress)
                    except Exception as e:
                        self.ProcessingDialog("Error retrieving Wallet Pool Balance. Please try again later.", True, False)
                        print(str(e))
                        return
                    if CoinDict:    
                        if CoinDict['dvpn'] > self.DVPNOptions[self.idvpn]:
                            self.ProcessingDialog("Coins are available. Continue with Charge?",True, True)
                        else:
                            self.ProcessingDialog("There are not enough coins in our wallet pool. Please try your purchase again later. Your credit card has not be charged for this transaction."
                                                  ,True, False)
                    else: 
                        self.ProcessingDialog("Error retrieving Wallet Pool Balance. Please try again later.", True, False)
                        return
                        
                else:
                    self.ProcessingDialog("You did not accept the MathNodes purchasing policy.", True, False) 
                    return
            else:
                self.ProcessingDialog("We could not get an accurate DVPN price at the moment. Please try your order again later.", True, False)
                return 
                
        
    def set_dvpn_price(self, dt):
        self.ids.dvpn_price.text = "DVPN: $" + str(self.get_dvpn_price())
         
    def get_dvpn_price(self):
        try: 
            cg = CoinGeckoAPI()
            cg_price = cg.get_price(ids=['sentinel'], vs_currencies='usd')
            sentinel_price = cg_price['sentinel']['usd']
        except Exception as e:
            print(str(e)) 
            print("Getting price from CryptoCompare...")
            HEADERS = {'authorization' : "Apikey %s" % scrtsxx.CCOMPAREAPI}
            try: 
                r = requests.get(scrtsxx.CCOMPARE_API_URL, headers=HEADERS)
                sentinel_price = r.json()['USD']
            except Exception as e:
                print(str(e))
                return 0
        
        print("Current price of dvpn: %s" % sentinel_price)
        try: 
            self.clock()
        except:
            pass 
        return round(float(sentinel_price)*1.05, 8)
        
        
    def get_my_wallet_address(self):
        self.CONFIG = MeileGuiConfig()
        CONFIGFILE = self.CONFIG.read_configuration(MeileGuiConfig.CONFFILE)
        self.my_wallet_address = CONFIGFILE['wallet'].get("address")
        print("Wallet Address: %s" % self.my_wallet_address)
        return self.my_wallet_address
        
                
            
    def ProcessingDialog(self, status, button, button2):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        if not button:
            self.dialog = MDDialog(title=status,md_bg_color=get_color_from_hex("#0d021b"))
        elif button and not button2:
            self.dialog = MDDialog(
                                title=status,
                                md_bg_color=get_color_from_hex("#0d021b"),
                                
                                buttons=[
                                MDRaisedButton(
                                    text="OKAY",
                                    theme_text_color="Custom",
                                    text_color=get_color_from_hex("#000000"),
                                    on_release=self.closeDialog
                                )]
                                ,)
        else:
            self.dialog = MDDialog(
                                title=status,
                                md_bg_color=get_color_from_hex("#0d021b"),
                                
                                buttons=[
                                MDFlatButton(
                                    text="CANCEL",
                                    theme_text_color="Custom",
                                    text_color=Meile.app.theme_cls.primary_color,
                                    on_release=self.closeDialog
                                ),
                                MDRaisedButton(
                                    text="CONTINUE",
                                    theme_text_color="Custom",
                                    text_color=get_color_from_hex("#000000"),
                                    on_release=partial(self.ProcessPayment,
                                                       self.ids.ccnum.ids.ccnum.text,
                                                       self.month,
                                                       self.year,
                                                       self.ids.cvvnum.ids.cvvnum.text,
                                                       self.my_wallet_address)
                                )]
                                ,)
        self.dialog.open()
        
    
    @delayable
    def ProcessPayment(self, ccnum, ccmonth, ccyear, cvv, wallet_address, inst):
        self.ProcessingDialog("Creating Charge...", False, False)
        CHARGEFILE = open(path.join(self.CONFIG.BASEDIR, 'stripe_payment.log'), 'a+')
        DATEFORMAT = '%Y-%m-%d.%H:%M:%S'
        yield 2
        StripeInstance = Charge.StripePayments()
        #print("Credit Card Number: %s" % ccnum)
        #print("Expiration: %s/%s" %(ccmonth, ccyear))
        #print("CVV: %s" % cvv)
        print("Wallet Address: %s" % wallet_address)
        try:
            token = StripeInstance.generate_card_token(ccnum, ccmonth, ccyear, cvv)
        except CardError as e:
            print(str(e))
            self.ProcessingDialog("Error Processing Payment. Your card has not been charged.", True, False)
            return
        try:
            payment_status = StripeInstance.create_payment_charge(token, str(round((self.get_dvpn_price()*self.DVPNOptions[self.idvpn])+self.GetSurchargeAmount(),2)))
        except Exception as e:
            print(str(e))
            self.ProcessingDialog("Error Processing Payment. Your card has not been charged.", True, False)
            return 
        print("Getting payment for id: %s" % payment_status['id'])
        try:
            CHARGEFILE.write(payment_status['id'] + ',' + datetime.now().strftime(DATEFORMAT) + '\n')
            CHARGEFILE.flush()
            payment_retrieval = stripe.Charge.retrieve(payment_status['id'],)
        except Exception as e:
            print(str(e))
            self.ProcessingDialog("Error retrieving payment information. In the case your card was charged and you did not receive tokens. Please submit a request to support@mathnodes.com", True, False)
            return
        print("Was paid: %s\n%s" % (payment_retrieval['paid'], payment_retrieval['id']))        
        if payment_retrieval['paid']:
            self.ProcessingDialog("Charge Successful. Conducting transfer of tokens to wallet address\n%s...." % wallet_address , False, False)
            yield 2
            STATUS = self.TransferCoins(payment_status['id'], wallet_address,self.DVPNOptions[self.idvpn])
            try: 
                CHARGEFILE.write(STATUS['message'] + ',' + STATUS['tx'] + '\n\n')
                CHARGEFILE.close()
            except Exception as e:
                print("Could not write to status file: %s" % str(e))
                pass
            self.ProcessSuccessfulDialog(STATUS)
            yield 2
        else:
            self.ProcessingDialog("Payment not marked as 'PAID' by Stripe. Cannot continue.", True, False)
            return 
    def ProcessSuccessfulDialog(self, STATUS):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
        tx_dialog = TXContent()
        try:
            tx_dialog.ids.message.text = STATUS['message']
            tx_dialog.ids.txhash.text  = STATUS['tx']
        except Exception as e:
            print(str(e))
            tx_dialog.ids.message.text = 'We apologize. Something went wrong. Please contact support@mathnodes.com for more information.'
            tx_dialog.ids.txhash.text  = 'None'
        if not self.dialog:
            self.dialog = MDDialog(
                    title="STATUS: ",
                    type="custom",
                    content_cls=tx_dialog,
                    md_bg_color=get_color_from_hex("#0d021b"),
                    buttons=[
                        MDRaisedButton(
                            text="OKAY",
                            theme_text_color="Custom",
                            text_color=get_color_from_hex("#000000"),
                            on_release=self.closeDialogReturnToWallet
                        ),
                    ],
                )
            self.dialog.open()
            
    def GetSurchargeAmount(self):
        if self.idvpn in [0,1]:
            self.ids.surcharge.text = "Surcharge: $1.25"
            return float(1.25)
        
        elif self.idvpn in [2]:
            self.ids.surcharge.text = "Surcharge: $1.50"
            return float(1.50)
        
        else:
            self.ids.surcharge.text = "Surcharge: $1.75"
            return float(1.75)
        
    def TransferCoins(self, stripe_id, wallet_address, dvpn_qty):
        SERVER_ADDRESS = scrtsxx.SERVER_ADDRESS
        API            = scrtsxx.API_ENDPOINT
        JSON           = {'id' : '%s' % stripe_id, 'address' : '%s' % wallet_address, 'qty' : '%s' % dvpn_qty }
        STATUS         = {'message' : None}
        USERNAME       = scrtsxx.USERNAME
        PASSWORD       = scrtsxx.PASSWORD
        try:
            print("Sending transfer request....")
            ttr = requests.post(SERVER_ADDRESS + API, json=JSON, auth=HTTPBasicAuth(USERNAME, PASSWORD))
            if ttr.status_code == 200:
                print("Successful Request. Parsing Data....")
                return ttr.json()
        except Exception as e:
            print(str(e))
            STATUS['message'] = str(e)
            return STATUS

    def set_dvpn_qty(self, text_item):
        self.ids.dvpn_qty_menu.set_item(text_item)
        self.menu_dvpn_qty.dismiss()
        
        print("DVPN QTY: %s" % text_item)
        self.idvpn = self.DVPNOptions.index(int(text_item))
        print("Index: %s" % self.idvpn)
        self.ids.charge_amount.text = "Total Charge: $" + str(round((self.get_dvpn_price()*self.get_dvpn_qty())+self.GetSurchargeAmount(),2))
        self.ids.dvpn_qty.text = "QTY: " + str(self.DVPNOptions[self.idvpn]) + " dvpn"
        
        
    def get_dvpn_qty(self):
        return self.DVPNOptions[self.idvpn]
        
    def set_month(self, text_item):
        self.ids.month_list.set_item(text_item)
        self.menu_month.dismiss()
        
        print("Month: %s "  % text_item)
        self.month = text_item
        
    def set_year(self, text_item):
        self.ids.year_list.set_item(text_item)
        self.menu_year.dismiss()
        
        print("Year: %s" % text_item[-2:])
        self.year = text_item[-2:]
        
    def cancel(self):
        try: 
            self.dialog.dismiss()
        except Exception as e:
            print(str(e))
            
    def terms_agreement(self, active):
        print("Active is: %s" % active)
        if active:
            self.policy = True
        else:
            self.policy = False
    def closeDialog(self, inst):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            
    def closeDialogReturnToWallet(self, inst):
        self.closeDialog(None)
        self.set_previous_screen()
    
    def set_previous_screen(self):
        try:
            self.clock.cancel()
        except Exception as e:
            print(str(e))
        Meile.app.root.remove_widget(self)
        Meile.app.root.transistion = SlideTransition(direction="down")
        Meile.app.root.current = WindowNames.WALLET

       
