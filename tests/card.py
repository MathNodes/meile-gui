from kivy.uix.modalview import ModalView
from kivy.lang import Builder

from kivymd import images_path
from kivymd.app import MDApp
from kivymd.uix.card import MDCard

Builder.load_string(
    '''
<Card>:
    elevation: 10
    radius: [36, ]

    FitImage:
        id: bg_image
        source: "images/bg.png"
        size_hint_y: .35
        pos_hint: {"top": 1}
        radius: 36, 36, 0, 0
''')


class Card(MDCard):
    pass


class Example(MDApp):
    def build(self):
        modal = ModalView(
            size_hint=(0.4, 0.8),
            background=f"{images_path}/transparent.png",
            overlay_color=(0, 0, 0, 0),
        )
        modal.add_widget(Card())
        modal.open()


Example().run()