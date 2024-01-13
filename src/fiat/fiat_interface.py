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

import stripe
import time
from stripe.error import CardError
from fiat.stripe_pay.charge import HotwalletFuncs as HandleWalletFunctions
import fiat.stripe_pay.charge as Charge
from fiat.stripe_pay import scrtsxx

from typedef.win import WindowNames
from ui.interfaces import TXContent
from conf.meile_config import MeileGuiConfig
import main.main as Meile
from adapters import HTTPRequests
from coin_api.get_price import GetPriceAPI

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
    DECOptions  = [1000,2000,3000,5000]
    SCRTOptions = [5,10,15,30]
    TokenOptions = ['dvpn', 'dec', 'scrt']
    SelectedCoin = TokenOptions[0]
    CoinOptions = {'dvpn' : DVPNOptions, 'dec' : DECOptions, 'scrt' : SCRTOptions}
    #CoinGeckoAPI = {'scrt' : 'secret', 'dvpn' : 'sentinel', 'dec' : 'decentr'}
    idvpn = 0
    CONFIG = None
    clock = None
    
    def __init__(self, **kwargs):
        super(FiatInterface, self).__init__()
        self.price_api = GetPriceAPI()
        self.price_cache = {}
        self.CoinOptions = self.DynamicCoinOptions()
        self.DVPNOptions = self.CoinOptions['dvpn']
        self.DECOptions  = self.CoinOptions['dec']
        self.SCRTOptions = self.CoinOptions['scrt']
        self.set_token_qty(str(self.DVPNOptions[0]))
        
        
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
            } for i in range(2023,2035)
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
                "on_release": lambda x=f"{i}": self.set_token_qty(x),
            } for i in self.DVPNOptions
        ]
        self.menu_dvpn_qty = MDDropdownMenu(
            caller=self.ids.dvpn_qty_menu,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_dvpn_qty.bind()
        
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_token(x),
            } for i in self.TokenOptions
        ]
        self.menu_token = MDDropdownMenu(
            caller=self.ids.dvpn_qty_menu,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu_token.bind()
        
        self.clock = Clock.create_trigger(partial(self.set_token_price,self.SelectedCoin), 20)
        self.clock()
    
    @delayable
    def pay(self):
        print(len(str(self.ids.ccnum.ids.ccnum.text)))
        if len(self.ids.ccnum.ids.ccnum.text) < 16 or len(self.ids.ccnum.ids.ccnum.text) > 16:
            self.ids.credit_card_number_warning.opacity = 1
        elif len(self.ids.cvvnum.ids.cvvnum.text) > 4 or len(self.ids.cvvnum.ids.cvvnum.text) < 3:
            self.ids.cvv_code_warning.opacity = 1
            
        else:
            if self.get_token_price(self.SelectedCoin) > 0:
                if self.policy:
                    self.ProcessingDialog("Checking wallet for sufficient coins....", False,False)
                    yield 2
                    Wallet = HandleWalletFunctions()
                    try:
                        CoinDict = Wallet.get_balance(HotWalletAddress)
                        print(CoinDict)
                    except Exception as e:
                        self.ProcessingDialog("Error retrieving Wallet Pool Balance. Please try again later.", True, False)
                        print(str(e))
                        return
                    if CoinDict:
                        print("AMT: %s%s" % (CoinDict[self.SelectedCoin], self.SelectedCoin))
                        print("CoinOPtions: %s " % float(self.CoinOptions[self.SelectedCoin][self.idvpn]))
                        if float(CoinDict[self.SelectedCoin]) > float(self.CoinOptions[self.SelectedCoin][self.idvpn]):
                            self.ProcessingDialog("Coins are available. Continue with Charge?",True, True)
                        else:
                            self.ProcessingDialog("There are not enough coins in our wallet pool. Please try your purchase again later. Your credit card has not be charged for this transaction.",True, False)
                    else: 
                        self.ProcessingDialog("Error retrieving Wallet Pool Balance. Please try again later.", True, False)
                        return
                        
                else:
                    self.ProcessingDialog("You did not accept the MathNodes purchasing policy.", True, False) 
                    return
            else:
                self.ProcessingDialog("We could not get an accurate DVPN price at the moment. Please try your order again later.", True, False)
                return 
            
    def DynamicCoinOptions(self):
        MAX_SPEND = 25
        coins = self.TokenOptions
        CoinOptions = {coins[0] : None, coins[1] : None, coins[2] : None}
        
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        
        try:
            r = http.get(scrtsxx.SERVER_ADDRESS + scrtsxx.MAX_SPEND_ENDPOINT)
            MAX_SPEND = r.json()['max_spend']
        except:
            pass
        
        for c in coins:
            self.refresh_price(c, cache=30)
                        
            if self.price_cache[c]["price"] == 0:
                x = 0
                qty = 0
            else:
                x = 1 /self.price_cache[c]["price"]
                qty = int(MAX_SPEND/self.price_cache[c]["price"])

            
            if x < 1:
                factor = 0.1
            elif 1 <= x < 10:
                factor = 1
            elif 10 <= x < 100:
                factor = 10
            elif 100 <= x < 1000:
                factor = 100
            elif 1000 <= x < 10000:
                factor = 1000
            else:
                factor = 10000
            
            mod_qty = qty % factor
            
            qty = qty - mod_qty

            Options = [int(qty/8), int(qty/4), int(qty/2), int(qty)]
            
            if c == coins[0]:
                CoinOptions[coins[0]] = Options
            elif c == coins[1]:
                CoinOptions[coins[1]] = Options
            else:
                CoinOptions[coins[2]] = Options
                
        return CoinOptions
        
    def refresh_price(self, mu_coin: str = "dvpn", cache: int = 30):
        # Need check on cache or trought GetPrice api
        # We don't need to call the price api if the cache is younger that 30s

        if mu_coin not in self.price_cache or time.time() - self.price_cache[mu_coin]["time"] > cache:
            response = self.price_api.get_usd(mu_coin)
            if response['success']:
                self.price_cache[mu_coin] = {
                    "price": float(response['price']),
                    "time": time.time()
                }
            else:
                self.price_cache[mu_coin] = {
                    "price": float(0),
                    "time": time.time()
                }
                    
    def set_token_price(self, token, dt):
        self.ids.dvpn_price.text = "%s: $" % token.upper() + str(self.get_token_price(token))
         
    def get_token_price(self, token):
        try:
            self.refresh_price(token, cache=30)
            token_price = self.price_cache[token]["price"]
            if token_price == 0:
                raise Exception("Error getting price from CoinStats")
        except Exception as e:
            print(str(e)) 
            print("Getting price from CryptoCompare...")
            Request = HTTPRequests.MakeRequest()
            http = Request.hadapter()
            HEADERS = {'authorization' : "Apikey %s" % scrtsxx.CCOMPAREAPI}
            try: 
                r = http.get(scrtsxx.CCOMPARE_API_URL % token.upper(), headers=HEADERS)
                token_price = r.json()['USD']
            except Exception as e:
                print(str(e))
                return 0
        
        print("Current price of %s: %s" % (token.upper(),token_price))
        try: 
            self.clock.cancel()
            self.clock = Clock.create_trigger(partial(self.set_token_price,token), 20)
            self.clock()
        except:
            pass 
        
        self.ids.dvpn_price.text = "%s: $" % token.upper() + str(round(float(token_price)*1.05, 8))
        return round(float(token_price)*1.05, 8)
        
        
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
            self.dialog = MDDialog(title=status,md_bg_color=get_color_from_hex("#121212"))
        elif button and not button2:
            self.dialog = MDDialog(
                                title=status,
                                md_bg_color=get_color_from_hex("#121212"),
                                
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
                                md_bg_color=get_color_from_hex("#121212"),
                                
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
                                                       self.my_wallet_address,
                                                       self.SelectedCoin)
                                )]
                                ,)
        self.dialog.open()
        
    
    @delayable
    def ProcessPayment(self, ccnum, ccmonth, ccyear, cvv, wallet_address, token, inst):
        self.ProcessingDialog("Creating Charge...", False, False)
        CHARGEFILE = open(path.join(self.CONFIG.BASEDIR, 'stripe_payment.log'), 'a+')
        DATEFORMAT = '%Y-%m-%d.%H:%M:%S'
        yield 2
        StripeInstance = Charge.StripePayments()
        #print("Credit Card Number: %s" % ccnum)
        #print("Expiration: %s/%s" %(ccmonth, ccyear))
        #print("CVV: %s" % cvv)
        print("Wallet Address: %s" % wallet_address)
        
        if not ccmonth:
            ccmonth = "01"
            
        if not ccyear:
            ccyear = "23"
        
        try:
            stripe_token = StripeInstance.generate_card_token(ccnum, ccmonth, ccyear, cvv)
        except CardError as e:
            print(str(e))
            self.ProcessingDialog("Error Processing Payment. Your card has not been charged: %s" % str(e), True, False)
            return
        try:
            if token == self.TokenOptions[0]:
                payment_status = StripeInstance.create_payment_charge(stripe_token, str(round((self.get_token_price(token)*self.DVPNOptions[self.idvpn])+self.GetSurchargeAmount(),2)))
            elif token == self.TokenOptions[1]:
                payment_status = StripeInstance.create_payment_charge(stripe_token, str(round((self.get_token_price(token)*self.DECOptions[self.idvpn])+self.GetSurchargeAmount(),2)))
            else:
                payment_status = StripeInstance.create_payment_charge(stripe_token, str(round((self.get_token_price(token)*self.SCRTOptions[self.idvpn])+self.GetSurchargeAmount(),2)))
        except Exception as e:
            print(str(e))
            self.ProcessingDialog("Error Processing Payment. Your card has not been charged: %s" % str(e), True, False)
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
            STATUS = self.TransferCoins(payment_status['id'], wallet_address,token)
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
            if STATUS['tx']:
                tx_dialog.ids.txhash.text  = STATUS['tx']
            else:
                tx_dialog.ids.txhash.text = 'None'
        except Exception as e:
            print(str(e))
            tx_dialog.ids.message.text = 'We apologize. Something went wrong. Please contact support@mathnodes.com for more information.'
            tx_dialog.ids.txhash.text  = 'None'
        if not self.dialog:
            self.dialog = MDDialog(
                    title="STATUS: ",
                    type="custom",
                    content_cls=tx_dialog,
                    md_bg_color=get_color_from_hex("#121212"),
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
            self.ids.surcharge.text = "Surcharge: $2.00"
            return float(2.00)
        
    def TransferCoins(self, stripe_id, wallet_address, token):
        
        if token == self.TokenOptions[0]:
            coin_qty = self.DVPNOptions[self.idvpn]
            
        elif token == self.TokenOptions[1]:
            coin_qty = self.DECOptions[self.idvpn]
            
        else:
            coin_qty = self.SCRTOptions[self.idvpn]
        
        
        SERVER_ADDRESS = scrtsxx.SERVER_ADDRESS
        API            = scrtsxx.API_ENDPOINT
        JSON           = {'id' : stripe_id, 'address' : wallet_address, 'qty' : coin_qty, 'token' : token }
        STATUS         = {'message' : None}
        USERNAME       = scrtsxx.USERNAME
        PASSWORD       = scrtsxx.PASSWORD
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        try:
            print("Sending transfer request....")
            ttr = http.post(SERVER_ADDRESS + API, json=JSON, auth=HTTPBasicAuth(USERNAME, PASSWORD))
            if ttr.status_code == 200:
                print("Successful Request. Parsing Data....")
                return ttr.json()
        except Exception as e:
            print(str(e))
            STATUS['message'] = str(e)
            return STATUS
    
    def set_token(self, text_item):
        self.ids.token.set_item(text_item)
        self.menu_token.dismiss()
        self.menu_dvpn_qty.clear_widgets()
        self.SelectedCoin = text_item
        
        if text_item == self.TokenOptions[0]:
            menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_token_qty(x),
            } for i in self.DVPNOptions
            ]
            self.menu_dvpn_qty = MDDropdownMenu(
                caller=self.ids.dvpn_qty_menu,
                items=menu_items,
                position="center",
                width_mult=4,
            )
            self.menu_dvpn_qty.bind()
            self.set_token_qty(str(self.DVPNOptions[0]))
        
        elif text_item == self.TokenOptions[1]:
            menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_token_qty(x),
            } for i in self.DECOptions
            ]
            self.menu_dvpn_qty = MDDropdownMenu(
                caller=self.ids.dvpn_qty_menu,
                items=menu_items,
                position="center",
                width_mult=4,
            )
            self.menu_dvpn_qty.bind()
            self.ids.dvpn_qty_menu.text = str(self.DECOptions[0])
            self.set_token_qty(str(self.DECOptions[0]))
        else:
            menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_token_qty(x),
            } for i in self.SCRTOptions
            ]
            self.menu_dvpn_qty = MDDropdownMenu(
                caller=self.ids.dvpn_qty_menu,
                items=menu_items,
                position="center",
                width_mult=4,
            )
            self.menu_dvpn_qty.bind()
            self.ids.dvpn_qty_menu.text = str(self.SCRTOptions[0])
            self.set_token_qty(str(self.SCRTOptions[0]))
        self.set_token_price(self.SelectedCoin, None)
            
    def set_token_qty(self, text_item):
        self.ids.dvpn_qty_menu.set_item(text_item)
        try:
            self.menu_dvpn_qty.dismiss()
        except:
            pass
        
        token = self.SelectedCoin
        
        print("%s QTY: %s" % (token.upper(), text_item))
        
        if token == self.TokenOptions[0]:
            self.idvpn = self.DVPNOptions.index(int(text_item))
        elif token == self.TokenOptions[1]:
            self.idvpn = self.DECOptions.index(int(text_item))
        else:
            self.idvpn = self.SCRTOptions.index(int(text_item))
        
        print("Index: %s" % self.idvpn)
        
        self.ids.charge_amount.text = "Total Charge: $" + str(round((self.get_token_price(token)*self.get_token_qty(token))+self.GetSurchargeAmount(),2))
        
        if token == self.TokenOptions[0]:
            self.ids.coin_qty.text = "QTY: " + str(self.DVPNOptions[self.idvpn]) + " " + self.TokenOptions[0]
        elif token == self.TokenOptions[1]:
            self.ids.coin_qty.text = "QTY: " + str(self.DECOptions[self.idvpn]) + " " + self.TokenOptions[1]
        else:
            self.ids.coin_qty.text = "QTY: " + str(self.SCRTOptions[self.idvpn]) + " " + self.TokenOptions[2]
    
    def get_token_qty(self, token):
        if token == self.TokenOptions[0]:
            return self.DVPNOptions[self.idvpn]
        elif token == self.TokenOptions[1]:
            return self.DECOptions[self.idvpn]
        else:
            return self.SCRTOptions[self.idvpn]
             
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

       
