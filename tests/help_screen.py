from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivymd.theming import ThemeManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

Builder.load_string('''
#: import get_color_from_hex kivy.utils.get_color_from_hex

<HelpScreen>:
    MDBoxLayout:
        orientation: "vertical"
        MDLabel:
            font_name: "Roboto-Bold"
            text: "HELP SCREEN"
            font_size: "30sp"
            size_hint_y: .1
            width: dp(500)
            pos_hint: { "right": 1.4, "top": 1.5}
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#fcb711")
        ScrollView:
            effect_cls: "ScrollEffect"
            scroll_type: ['bars']
            MDGridLayout:
                rows: 10
                cols: 1
                size_hint_y:None
                size_hint_x: 1
                height: self.minimum_height
                spacing: "10dp"
                MDLabel:
                    font_name: "Roboto-BoldItalic"
                    text: "What is a mnemonic/seed phrase?"
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    halign: "center"
                MDLabel:
                    font_name: "DejaVuSans"
                    text: "A mnemonic/seed phrase is a set of pre-defined dictionary words that form a unique set. This uniuqqe set is used to generate a wallet with a unique address, similar to how bank accounts have a unique number. i.e., no two bank accounts have the same account number. This address can be used to send and receive currency just like your bank account."
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    pos_hint_x: .9
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#fcb711")
                    font_size: "12dp"
                    
                MDLabel:
                    font_name: "Roboto-BoldItalic"
                    text: "What is a address"
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    halign: "center"
                MDLabel:
                    font_name: "DejaVuSans"
                    text: "An address is a unique identifier that links your funds to the blockcahin. This is a pseudonymous identifier meaning it links your digital identity on the blockchain without storing any personal identifiers of an individual. Addresses are used to send and receive funds in the native currency of the acting network. "
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    pos_hint_x: .9
                    halign: "center" 
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#fcb711")
                    font_size: "12dp"
                MDLabel:
                    font_name: "Roboto-BoldItalic"
                    text: "How do I receive funds to be able to subscribe and use Meile dVPN?"
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    halign: "center"
                MDLabel:
                    font_name: "DejaVuSans"
                    text: "There are two primary ways to receive tokens to purchase dVPN (the currency) subscriptions and utilize the network. 1.) You get the DVPN token on a exchange and send it to your wallet address. Current exchanges are KuCoin, HotBit, Polarity and Osmosis. Once you purchase the tokens on the exchange, you need to withdraw them to your address listed in the wallet section of this app. The tokens should appear within minutes after a withdrawal and you can begin purchasing and subscribing to Sentinel dVPN nodes through Meile. 2.) You can purchase the currency used for Meile dVPN right in our app via the 'Top-Up' button within the wallet. These funds will be handled by our servers and the payment processing is handled by stripe. Once you succesfully complete a purchase, your funds should appear in your wallet within minutes of a successful purchase through our app. This is the easiest method to using Meile dVPN."
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    pos_hint_x: .9
                    halign: "center" 
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#fcb711")
                    font_size: "12dp"
                MDLabel:
                    font_name: "Roboto-BoldItalic"
                    text: "What is MathNodes privacy policy?"
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    halign: "center"
                MDLabel:
                    font_name: "DejaVuSans"
                    text: "MathNodes uses Stripe to process payments in order to receive funds to use the dVPN. You will see that we do not even need the name of the individual. Once a payment is processed through Stripe, Mathnodes stores only the payment_id received from stripe, the address of your wallet, and the amount of tokens sent (1,000). We have to keep records some information in case there is a dispute and we need to query the orders and verify if tokens were sent to the reciept's address. We do not store your name, your credit card details, or any other information beside what we have mentioned. "
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    pos_hint_x: .9
                    halign: "center" 
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#fcb711")
                    font_size: "12dp"
                MDLabel:
                    font_name: "Roboto-BoldItalic"
                    text: "Why is a dVPN better than a tradiation VPN?"
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    halign: "center"
                MDLabel:
                    font_name: "DejaVuSans"
                    text: "A traditional VPN, like Nord, Norton, Cryptostorm, or Proton is a centralized set of servers that a user connects through to access the internet. Most VPNs are required to keep a degree of logging information about users. Centralized VPNs can terminate a user's plan or restrict access to the internet based on private, public, or governmental policy. A dVPN such as the one Meile offers, uses blockchain technologies via the Sentinel Network to ensure a decentralized structure. This means that the servers you connect through are ran by a community of volunteers rather than a central authority. As such, no logging takes places, users don't have the ability to throttle or restrict traffic and no censorship is possible through the use of a dVPN."
                    size_hint_y: None
                    height: self.texture_size[1]
                    size_hint_x: 1
                    pos_hint_x: .9
                    halign: "center" 
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#fcb711")
                    font_size: "12dp"
                
                    
                
<MyScrollViewWidget>:


''')

class HelpScreen(Screen):
    def SetText(self):
        text = 'Total=' + str(17*21)
        self.manager.get_screen('strategy').labelText = text

class MyScrollViewWidget(MDGridLayout):
    pass
class TestApp(MDApp):
    def build(self):
        # Create the screen manager
        screenManager = ScreenManager()        
        theme = ThemeManager()
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Dark" 
        self.theme_cls.disabled_primary_color = "Amber"
        self.theme_cls.opposite_disabled_primary_color = "Amber"
        screenManager.add_widget(MainScreen(name='main'))
        return screenManager

if __name__ == '__main__':
    app = TestApp()
    app.run()