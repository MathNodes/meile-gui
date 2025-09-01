from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.textfield import MDTextFieldRect, MDTextField
KV = '''
<MySeedBox>

<ClickableTextFieldRound>:
    size_hint_y: None
    height: text_field.height

    MDTextField:
        id: text_field
        hint_text: root.hint_text
        text: root.text
        password: True
        icon_left: "key-variant"
        mode: "rectangle"

    MDIconButton:
        icon: "eye-off"
        pos_hint: {"center_y": .5}
        pos: text_field.width - self.width + dp(8), 0
        theme_text_color: "Hint"
        on_release:
            self.icon = "eye" if self.icon == "eye-off" else "eye-off"
            text_field.password = False if text_field.password is True else True


MDScreen:

    ClickableTextFieldRound:
        size_hint_x: None
        width: "500dp"
        height: "100dp"
        hint_text: "Seed Phrase"
        pos_hint: {"center_x": .5, "center_y": .85}
    MDRaisedButton:
        id: restore_wallet_button
        text: "Restore"
        pos_hint: {"center_x": .5, "center_y": .5}
        on_press: root.restore_wallet_from_seed_phrase()
'''



class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    # Here specify the required parameters for MDTextFieldRound:
    # [...]


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()