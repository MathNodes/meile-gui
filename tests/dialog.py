from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton,MDTextButton, MDFillRoundFlatButton

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import  StringProperty
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import get_color_from_hex
KV = '''
<Content>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        hint_text: "City"

    MDTextField:
        hint_text: "Street"


MDFloatLayout:

    MDFlatButton:
        text: "ALERT DIALOG"
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_release: app.show_confirmation_dialog()
        
<RatingContent>
    
    spacing: "1dp"
    size_hint_y: None
    height: "100dp"
    price_text: ""
    naddress: " "
    moniker: " "    
    orientation: "vertical"
    MDFloatLayout:
        MDLabel:
            id: node_moniker_text
            text: root.moniker
            font_size: 19
            pos_hint: {"x" : 0.05, "center_y": .9}
             
        MDLabel:
            id: node_addresss_text
            text: root.naddress
            font_size: 10
            pos_hint: {"x" : 0.05, "center_y": .70}
             
        MDSlider:
            id: rating_slider
            min: 1
            max: 10
            value: 9
            pos_hint: {"x" : 0.00, "center_y": .5}
            
<ProcessingSubDialog>
    orientation: "vertical"
    spacing: "1dp"
    size_hint_y: None
    height: "130dp"
    price_text: ""
    naddress: " "
    moniker: " "
    deposit: " "
    MDFloatLayout:
        MDLabel:
            id: moniker
            text: root.moniker
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "20sp"
            text_color: get_color_from_hex("#fcb711")
            pos_hint: {"x" : 0, "top" : 1.35}
        MDLabel:
            id: naddress
            text: root.naddress
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "9sp"
            text_color: get_color_from_hex("#ffffff")
            pos_hint: {"x" : 0, "top" : 1.2}
        MDLabel:
            id: deposit
            text: root.deposit
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "18sp"
            text_color: get_color_from_hex("#fcb711")
            pos_hint: {"x" : 0, "top" : .95}
            
'''


class ProcessingSubDialog(BoxLayout):
    moniker = StringProperty()
    naddress = StringProperty()
    deposit = StringProperty()
    
    def __init__(self, moniker, naddress, deposit):
        super(ProcessingSubDialog, self).__init__()
        self.moniker = moniker
        self.naddress = naddress
        self.deposit = deposit
        
    
class Content(BoxLayout):
    pass
class RatingContent(MDBoxLayout):
    naddress = StringProperty()
    moniker  = StringProperty()

    def __init__(self, moniker, naddress):
        super(RatingContent, self).__init__()
        self.naddress = naddress
        self.moniker  = moniker
        
class Example(MDApp):
    dialog = None

    def build(self):
        return Builder.load_string(KV)

    def show_confirmation_dialog(self):
        if not self.dialog:
            spdialog = ProcessingSubDialog("BALLS IN YOUR MOUTH", "sentnodeahf89aqw8yrihasifhaw7yr87yihbaw", "100dvpn" )
            self.dialog = None
            self.dialog = MDDialog(
                    title="Subscribing...",
                    type="custom",
                    content_cls=spdialog,
                    md_bg_color=get_color_from_hex("#0d021b"),
                )
            self.dialog.open()
    def remove_loading_widget(self, dt):
        try:
            self.dialog.dismiss()
            self.dialog = None
        except Exception as e:
            print(str(e))
            pass

Example().run()