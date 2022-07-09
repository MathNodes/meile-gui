from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import  StringProperty
from functools import partial

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

<OSXPasswordDialog>
    name: "osx_password"
    title: "OS X Password"

    MDTextField:
        id: osx
        size_hint_x: None
        width: "300dp"
        height: "300dp"
        text: ""
        hint_text: "OS X  Password"
        pos_hint: {"center_x": .5, "center_y": .80}
        mode: "rectangle"
    

MDFloatLayout:

    MDFlatButton:
        text: "ALERT DIALOG"
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_release: app.show_confirmation_dialog()
'''

class OSXPasswordDialog(BoxLayout):
    def return_password(self):
        print("Self IDS: %s" % self.ids.osx.text)
        return self.ids.osx.text


class Content(BoxLayout):
    pass


class Example(MDApp):
    dialog = None

    def build(self):
        return Builder.load_string(KV)


    def set_osx_password(self, dialog, dt):
        print("PASSWORD IS: %s" % dialog.return_password())
    def show_confirmation_dialog(self):
        from _functools import partial
        if not self.dialog:
            PasswordDialog = OSXPasswordDialog()
            self.dialog = MDDialog(
                title="freQniK Password",
                type="custom",
                content_cls=PasswordDialog,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=partial(self.set_osx_password, PasswordDialog)
                    ),
                ],
            )
        self.dialog.open()


Example().run()