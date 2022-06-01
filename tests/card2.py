from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex


<MD3Card>
    padding: 16
    size_hint: None, None
    size: "200dp", "100dp"

    MDRelativeLayout:
        size_hint: None, None
        size: root.size

        MDIconButton:
            icon: "dots-vertical"
            pos:
                root.width - (self.width + root.padding[0] + dp(4)),                     root.height - (self.height + root.padding[0] + dp(4))

        MDLabel:
            id: label
            text: root.text
            adaptive_size: True
            color: .2, .2, .2, .8


MDScreen:

    MDBoxLayout:
        id: box
        adaptive_size: True
        spacing: "56dp"
        pos_hint: {"center_x": .5, "center_y": .5}
'''


class MD3Card(MDCard, RoundedRectangularElevationBehavior):
    '''Implements a material design v3 card.'''

    text = StringProperty()


class TestCard(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        return Builder.load_string(KV)

    def on_start(self):
        styles = {
            "elevated": "#f6eeee", "filled": "#f4dedc", "outlined": "#f8f5f4"
        }
        for style in styles.keys():
            self.root.ids.box.add_widget(
                MD3Card(
                    line_color=(0.2, 0.2, 0.2, 0.8),
                    text=style.capitalize(),
                    md_bg_color=get_color_from_hex(styles[style]),
                )
            )


TestCard().run()
