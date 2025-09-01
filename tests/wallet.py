from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivy.uix.image import Image

 
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivyoav.delayed import delayable
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout




Builder.load_string('''
#: import get_color_from_hex kivy.utils.get_color_from_hex

<WalletRestore>:
    name: "walletrestore"
    title: "Blargy"
    wallet_address: "secret1uhwwgwc7x5cm5xdmn99xnucxz296lyua688wjj"
    MDBoxLayout:
        orientation: "vertical"
        MDToolbar:
            id: toolbar
            title: "Wallet"
            md_bg_color: get_color_from_hex("#FFB908")
            height: "100dp"
            type: "top"
    
            MDTextField:
                hint_text: "Address"
                mode: "fill"
                size_hint_x: 1.2
                pos_hint: {"center_x" : .5, "center_y": .5}
                text: root.wallet_address
                readonly: True
                opacity: 1
                theme_text_color: "Custom"
                text_color: get_color_from_hex("#000000")
                normal_color: app.theme_cls.accent_color
            

    ClickableTextFieldRoundSeed:
        id: seed
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Seed Phrase"
        pos_hint: {"center_x": .5, "center_y": .80}
 
    MDLabel:
        text: "Leave blank if creating a new wallet"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#4a4545")
        pos_hint: {"x": .47, "center_y": .74}
        font_size: "12dp"
     
     
    ClickableTextFieldRoundName:
        id: name
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Wallet Name"
        pos_hint: {"center_x": .5, "center_y": .67}
    MDLabel:
        id: wallet_name_warning
        opacity: 0
        text: "You must give the wallet a name"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("f42121")
        pos_hint: {"x": .47, "center_y": .61}
        font_size: "12dp"
        
    ClickableTextFieldRoundPass:
        id: password
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Wallet Password"
        pos_hint: {"center_x": .5, "center_y": .55}
        
    MDLabel:
        id: wallet_password_warning
        opacity: 0
        text: "Cannot be blank"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("f42121")
        pos_hint: {"x": .47, "center_y": .49}
        font_size: "12dp"
    
        
    MDRaisedButton:
        id: restore_wallet_button
        text: "Restore"
        pos_hint: {"center_x": .5, "center_y": .4}
        on_press: root.restore_wallet_from_seed_phrase()
        
<ClickableTextFieldRoundSeed>:
    size_hint_y: None
    height: seed_phrase.height

    MDTextField:
        id: seed_phrase
        hint_text: root.hint_text
        text: root.text
        password: False
        icon_left: "key-variant"
        mode: "rectangle"

    MDIconButton:
        icon: "eye-off"
        pos_hint: {"center_y": .5}
        pos: seed_phrase.width - self.width + dp(8), 0
        theme_text_color: "Hint"
        on_release:
            self.icon = "eye" if self.icon == "eye-off" else "eye-off"
            seed_phrase.password = False if seed_phrase.password is True else True


<ClickableTextFieldRoundName>:
    size_hint_y: None
    height: wallet_name.height

    MDTextField:
        id: wallet_name
        hint_text: root.hint_text
        text: root.text
        password: False
        icon_left: "key-variant"
        mode: "rectangle"

    MDIconButton:
        icon: "eye-off"
        pos_hint: {"center_y": .5}
        pos: wallet_name.width - self.width + dp(8), 0
        theme_text_color: "Hint"
        on_release:
            self.icon = "eye" if self.icon == "eye-off" else "eye-off"
            wallet_name.password = False if wallet_name.password is True else True
            
<ClickableTextFieldRoundPass>:
    size_hint_y: None
    height: wallet_password.height

    MDTextField:
        id: wallet_password
        hint_text: root.hint_text
        text: root.text
        password: False
        icon_left: "key-variant"
        mode: "rectangle"

    MDIconButton:
        icon: "eye-off"
        pos_hint: {"center_y": .5}
        pos: wallet_password.width - self.width + dp(8), 0
        theme_text_color: "Hint"
        on_release:
            self.icon = "eye" if self.icon == "eye-off" else "eye-off"
            wallet_password.password = False if wallet_password.password is True else True

<WalletInfoContent>
    orientation: "vertical"
    spacing: "4dp"
    size_hint_y: None
    height: "260dp"
    seed_phrase: ""
    wallet_address: ""
    wallet_password: ""
    wallet_name: ""

    MDTextField:
        multiline: True
        hint_text: "Mnemonic Seed"
        text: root.seed_phrase
    MDTextField:
        hint_text: "Wallet"
        mode: "rectangle"
        text: root.wallet_name
    
    MDTextField:
        hint_text: "Address"
        mode: "rectangle"
        text: root.wallet_address
    
    MDTextField:
        hint_text: "Password"
        mode: "rectangle"
        text: root.wallet_password


                    
''')


class WalletInfoContent(BoxLayout):
    def __init__(self, seed_phrase, name, address, password, **kwargs):
        super(WalletInfoContent, self).__init__()
        self.seed_phrase = seed_phrase
        self.wallet_address = address
        self.wallet_password = password
        self.wallet_name = name
        
class WindowManager(ScreenManager):
    pass
class ClickableTextFieldRoundSeed(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    
class ClickableTextFieldRoundName(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    
class ClickableTextFieldRoundPass(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

class WalletRestore(Screen):
    dialog = None
    def __init__(self, **kwargs):
        super(WalletRestore, self).__init__()
        
       
    def restore_wallet_from_seed_phrase(self):
        print(self.manager.get_screen("walletrestore").ids.wallet_name_warning.text)
        print(self.manager.get_screen("walletrestore").ids.wallet_password_warning.text)
        if not self.manager.get_screen("walletrestore").ids.name.ids.wallet_name.text and not self.manager.get_screen("walletrestore").ids.password.ids.wallet_password.text:
            self.manager.get_screen("walletrestore").ids.wallet_name_warning.opacity = 1
            self.manager.get_screen("walletrestore").ids.wallet_password_warning.opacity = 1
            return
        elif not self.manager.get_screen("walletrestore").ids.password.ids.wallet_password.text:
            self.manager.get_screen("walletrestore").ids.wallet_password_warning.opacity = 1
            return
        elif not self.manager.get_screen("walletrestore").ids.name.ids.wallet_name.text:
            self.manager.get_screen("walletrestore").ids.wallet_name_warning.opacity = 1
            return 
        else:
            if not self.dialog:
                WalletInfo = WalletInfoContent(self.manager.get_screen("walletrestore").ids.seed.ids.seed_phrase.text,
                                               self.manager.get_screen("walletrestore").ids.name.ids.wallet_name.text,
                                               "sent1hfkgxzrkhxdxdwjy8d74jhc4dcw5e9zm7vfzh4", 
                                               self.manager.get_screen("walletrestore").ids.password.ids.wallet_password.text)
                self.dialog = MDDialog(
                    type="custom",
                    content_cls=WalletInfo,
                    
                    buttons=[
                        MDFlatButton(
                            text="Cancel",
                            theme_text_color="Custom",
                            text_color=(1,1,1,1),
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
    def cancel(self):
        self.dialog.dismiss()
        
    def wallet_restore(self):
        pass
    
class TestApp(MDApp):
    title = "Blargy"
    
    def build(self):
        
        manager = WindowManager()
        manager.add_widget(WalletRestore(name="walletrestore"))
        
        return manager
    
if __name__ == "__main__":
    app = TestApp()
    app.run()
