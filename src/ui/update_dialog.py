import webbrowser

from typedef.konstants import TextStrings, MeileColors

from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.utils import get_color_from_hex

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_string("""
<UpdateDialogContent>:
    orientation: "vertical"
    spacing: dp(12)
    padding: [dp(16), dp(8), dp(16), dp(8)]
    size_hint_y: None
    height: self.minimum_height
    adaptive_height: True

    MDLabel:
        id: update_message_label
        text: root.message_text
        markup: True
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 0.87
        font_size: sp(14)
        size_hint_y: None
        height: self.texture_size[1]
        on_ref_press: root.open_link(args[1])
""")

class UpdateDialogContent(MDBoxLayout):
    message_text = StringProperty("")

    def open_link(self, ref_name):
        if ref_name == "download":
            webbrowser.open(TextStrings.DOWNLOAD_URL)

class UpdateDialog:

    def __init__(self, message: str, download_url: str = TextStrings.DOWNLOAD_URL):
        self.message = message
        self.download_url = download_url
        self.dialog = None

    def show(self):
        if self.dialog is None:
            content = UpdateDialogContent(message_text=self.message)

            self.dialog = MDDialog(
                title="[color=#3CDAB7]Update Available[/color]",
                type="custom",
                content_cls=content,
                md_bg_color=get_color_from_hex(MeileColors.BLACK),
                buttons=[
                    MDFlatButton(
                        text="LATER",
                        theme_text_color="Custom",
                        text_color=get_color_from_hex(MeileColors.MEILE),
                        on_release=lambda *_: self.dismiss(),
                    ),
                    MDRaisedButton(
                        text="DOWNLOAD",
                        md_bg_color=get_color_from_hex(MeileColors.MEILE),
                        text_color=get_color_from_hex(MeileColors.BLACK),
                        on_release=lambda *_: self.open_download(),
                    ),
                ],
            )

        self.dialog.open()

    def dismiss(self):
        if self.dialog:
            self.dialog.dismiss()

    def open_download(self):
        webbrowser.open(self.download_url)
        self.dismiss()