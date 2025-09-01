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
            
<SubTypeDialog>
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
            id: sub_type
            text: "Subscription Type"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "20sp"
            text_color: get_color_from_hex("#fcb711")
            pos_hint: {"x" : 0, "top" : 1.35}
        MDLabel:
            id: bandwidth_text
            text: "Bandwidth (GB)"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            text_color: get_color_from_hex("#ffffff")
            pos_hint: {"x" : 0, "top" : 1}        
        CheckBox:
            group: "sub_type"
            on_active: root.select_sub_type(self, self.active, "gb")
            pos_hint: {"x": 0, "y" : .375}
            size_hint_y: .3
        MDLabel:
            id: hourly_text
            text: "Hourly"
            theme_text_color: "Custom"
            font_style: "Subtitle2"
            font_size: "14sp"
            text_color: get_color_from_hex("#ffffff")
            pos_hint: {"x" : 0, "top" : .8}    
        CheckBox:
            group: "sub_type"
            on_active: root.select_sub_type(self, self.active, "hourly")
            pos_hint: {"x": 0, "y" : .15}
            size_hint_y: .3
'''


class SubTypeDialog(BoxLayout):
    
    def __init__(self):
        super(SubTypeDialog, self).__init__()
        
    def select_sub_type(self,instance, value, type):
        if type == "gb":
            print("You have selected bandwidth")
        else:
            print("You have selected hourly")
            
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
            stypedialog = SubTypeDialog()
            self.dialog = None
            self.dialog = MDDialog(
                    type="custom",
                    content_cls=stypedialog,
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