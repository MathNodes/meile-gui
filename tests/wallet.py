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
<WalletRestore>:
    name: "walletrestore"
    title: "Blargy"
    ActionBar:
        ActionView:
            ActionPrevious:
                title: 'Go Back'
                with_previous: True
                on_release: root.set_previous_screen() 

    ClickableTextFieldRoundSeed:
        id: seed
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Seed Phrase"
        pos_hint: {"center_x": .5, "center_y": .80}
     
    ClickableTextFieldRoundName:
        id: name
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Wallet Name"
        pos_hint: {"center_x": .5, "center_y": .70}
    
    ClickableTextFieldRoundPass:
        id: password
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        hint_text: "Wallet Password"
        pos_hint: {"center_x": .5, "center_y": .60}
    
        
    MDRaisedButton:
        id: restore_wallet_button
        text: "Restore"
        pos_hint: {"center_x": .5, "center_y": .5}
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

                    
''')
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
        if not self.dialog:
            self.dialog = MDDialog(
                text="Seed: %s \n Name: %s \n Password: %s" %
                
                (self.manager.get_screen("walletrestore").ids.seed.ids.seed_phrase.text,
                 self.manager.get_screen("walletrestore").ids.name.ids.wallet_name.text,
                 self.manager.get_screen("walletrestore").ids.password.ids.wallet_password.text
                 ),
                
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
