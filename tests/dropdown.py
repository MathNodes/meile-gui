from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty

from kivymd.uix.list import OneLineIconListItem
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

KV = '''
<IconListItem>

    IconLeftWidget:
        icon: "server-security"


<SettingsScreen>
    MDBoxLayout:
        orientation: "vertical"
        MDLabel:
            font_name: "Roboto-Bold"
            text: "SETTINGS"
            font_size: "30sp"
            size_hint_y: .1
            pos_hint: { "center_x": .9, "top": .5}
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#fcb711")    
        MDFloatLayout:
    
            MDLabel:
                font_name: "Roboto-Bold"
                text: "RPC"
                font_size: "15sp"
                size_hint_y: .1
                size_hint_x: .2
                width: dp(500)
                pos_hint: { "x": .05, "top": 1}
                    
            MDDropDownItem:
                id: drop_item
                size_hint_x: .5
                pos_hint: {'x': .5, 'top': 1}
                text: 'https://rpc.mathnodes.com:443'
                on_release: app.menu.open()
            MDRaisedButton:
                text: "SAVE"
                on_release: root.refresh_wallet()
            
'''


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class Test(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_string(KV)
        
        rpcs = ['https://rpc.mathnodes.com:443', 'https://rpc.sentinel.co:443', 'https://sentinel-rpc.badgerbite.io:443',
                'https://sentinel-rpc2.badgerbite.io:443', 'https://rpc.sentinel.quokkastake.io:443', 'https://rpc-sentinel.whispernode.com:443',
                'https://rpc-sentinel-ia.cosmosia.notional.ventures:443']
        
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "git",
                "text": f"{i}",
                "height": dp(56),
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in rpcs
        ]
        self.menu = MDDropdownMenu(
            caller=self.screen.ids.drop_item,
            items=menu_items,
            position="center",
            width_mult=50,
        )
        self.menu.bind()

    def set_item(self, text_item):
        self.screen.ids.drop_item.set_item(text_item)
        self.menu.dismiss()

    def build(self):
        return self.screen


Test().run()