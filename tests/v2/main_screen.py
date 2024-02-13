from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.screenmanager import ScreenManager, Screen


from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.uix.list import ImageLeftWidget, BaseListItem

from kivymd.uix.datatables import MDDataTable
from kivymd.uix.datatables.datatables import TableHeader, TableData

# meil uix from tests
from uix.expansionpanel import MDExpansionPanelRoundIcon, MDExpansionPanelTwoLineSmall
from uix.expansionnode import Node, NodeAccordion, NodeDetails


KV = """
#:import get_color_from_hex kivy.utils.get_color_from_hex

WindowManager:

<Content>
    adaptive_height: True
    orientation: 'vertical'

    OneLineListItem:
        text: "Node1"
        text_color: "white"
        theme_text_color: "Custom"
        font_style: "Overline"
        bg_color: "black"

    OneLineListItem:
        text: "Node 2"
        text_color: "white"
        theme_text_color: "Custom"
        font_style: "Overline"
        bg_color: "black"

    OneLineListItem:
        text: "Node 3"
        text_color: "white"
        theme_text_color: "Custom"
        font_style: "Overline"
        bg_color: "black"


<MainScreen>:
    name: "main"
    MDGridLayout:
        md_bg_color: get_color_from_hex("#121212")
        rows: 2

        MDBoxLayout:
            md_bg_color: get_color_from_hex("#212221")
            size_hint_y: None
            height: 50

            MDLabel:
                padding: 10
                text: "Meile"
                font_style: "H4"
                text_color: "white"
                theme_text_color: "Custom"

        MDGridLayout:
            cols: 2
            # md_bg_color: get_color_from_hex("#212221")

            MDGridLayout:
                rows: 4
                padding: 10
                size_hint_x: None
                width: 250
                md_bg_color: get_color_from_hex("#060606")
                align: "center"

                MDRectangleFlatIconButton:
                    size_hint_y: None

                    text: "Connect"
                    text_color: "black"
                    icon: "lightning-bolt"
                    icon_color: "black"
                    md_bg_color: get_color_from_hex("#FCB70C")
                    line_color: 0, 0, 0, 0
                    font_size: "16sp"
                    size_hint: 1, 0

                MDTextField:
                    icon_left: "magnify"
                    line_color_normal: get_color_from_hex("#FCB70C")
                    line_color_focus: get_color_from_hex("#FCB70C")
                    icon_left_color_normal: get_color_from_hex("#FCB70C")
                    icon_left_color_focus: get_color_from_hex("#FCB70C")
                    text_color_normal: get_color_from_hex("#FCB70C")
                    text_color_focus: get_color_from_hex("#FCB70C")

                MDScrollView:
                    MDList:
                        id: countries_list
                        spacing: 3
                        padding: 10

                MDBoxLayout:
                    orientation: 'horizontal'
                    # padding: [20, 0, 0, 0]
                    size_hint_y: None
                    height: 50
                    spacing: 10

                    canvas:
                        # draw a background of red. This will be the border
                        Color:
                            rgba: get_color_from_hex("#453103")
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size

                        # draw over the above except for 1 pixels around edges, leaving the orange border showing
                        Color:
                            rgba: get_color_from_hex("#212221")
                        RoundedRectangle:
                            pos: self.x+1, self.y+1
                            size: self.width-2, self.height-2

                    MDIconButton:
                        icon: "wallet-outline"
                        theme_text_color: "Custom"
                        text_color: "white"

                    MDIconButton:
                        icon: "book-open-outline"
                        theme_text_color: "Custom"
                        text_color: "white"

                    MDIconButton:
                        icon: "cog-outline"
                        theme_text_color: "Custom"
                        text_color: "white"

                    MDIconButton:
                        icon: "help-circle-outline"
                        theme_text_color: "Custom"
                        text_color: "white"

            # AnchorLayout:
            #     orientation: "horizontal"
            #     md_bg_color: get_color_from_hex("#131313")
            #     id: servers_datatable

            MDGridLayout:
                rows: 2

                MDGridLayout:
                    cols: 7
                    height: 25
                    adaptive_height: True
                    padding: [15, 25, 0, 25]

                    MDLabel:
                        text: "Moniker"
                        bold: True
                        size_hint_x: 2

                    MDLabel:
                        text: "Location"
                        bold: True
                        size_hint_x: 1

                    MDLabel:
                        text: "Speed"
                        bold: True
                        size_hint_x: 2

                    # MDLabel:
                    #     text: "Status"
                    #     bold: True
                    #     size_hint_x: 1

                    # MDLabel:
                    #     text: "Price"
                    #     bold: True
                    #     size_hint_x: 2

                    MDLabel:
                        text: "Protocol"
                        bold: True
                        size_hint_x: 1

                    MDLabel:
                        text: "Type"
                        bold: True
                        size_hint_x: 1

                ScrollView:
                    do_scroll_y: True
                    MDBoxLayout:
                        size_hint_y: None
                        adaptive_height: True

                        orientation: "vertical"
                        padding: [10, 10, 10, 50]
                        spacing: 10
                        id: servers_list
"""

class WindowManager(ScreenManager):
    pass

class Content(MDBoxLayout):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__()
        self.build()

    def build(self):
        import random, string

        countries = [
            "France",
            "Italy",
            "Brasil",
            "Egypt",
            "Belgium",
            "Deutschland",
            "Canada",
        ]
        for _ in range(0, 10):
            country = random.choice(countries)

            # item = TwoLineAvatarListItem(
            #     radius = [10, 10, 10, 10],
            #     bg_color = get_color_from_hex("#212221"),
            #     text = country,
            #     text_color = "white",
            #     theme_text_color = "Custom",
            #     font_style = "Subtitle1",
            #     secondary_text = f"{random.randint(1, 100)} servers",
            #     secondary_text_color = "white",
            #     secondary_theme_text_color = "Custom",
            #     secondary_font_style = "Caption",
            # )
            # item.add_widget(ImageLeftWidget(source=f"../../src/imgs/{country[:2].lower()}.png"))

            item = MDExpansionPanelRoundIcon(
                icon=f"../../src/imgs/{country[:2].lower()}.png",
                icon_size=(25, 25),
                content=Content(),
                panel_cls=MDExpansionPanelTwoLineSmall(
                    radius=[10, 10, 10, 10],
                    bg_color=get_color_from_hex("#212221"),
                    text=country,
                    text_color="white",
                    theme_text_color="Custom",
                    font_style="Subtitle1",
                    secondary_text=f"{random.randint(1, 100)} servers",
                    secondary_text_color="white",
                    secondary_theme_text_color="Custom",
                    secondary_font_style="Caption",
                ),
            )
            self.ids.countries_list.add_widget(item)

        for _ in range(0, 50):
            upload = random.uniform(100, 900)
            download = random.uniform(100, 900)
            item = NodeAccordion(
                node=Node(
                    moniker=''.join(random.choices(string.printable[:-6], k=random.randint(5, 15))),  # Moniker
                    location=random.choice(countries),
                    speed=f"[color=#00FF00]↑[/color] {round(upload, 2)}mb/s [color=#f44336]↓[/color] {round(download, 2)}mb/s",
                    status="Status",
                    protocol=random.choice(["Wireguard", "V2RAY"]),
                    node_type=random.choice(["Residential", "Datacenter", "Unknown"]),
                ),
                content=NodeDetails(
                    health_check=random.choice([True, False]),
                    price=f"{random.randint(1, 100)}[b]dvpn[/b], {random.randint(1, 100)}[b]atom[/b], {random.randint(1, 100)}[b]osmo[/b], {random.randint(1, 100)}[b]srct[/b], {random.randint(1, 100)}[b]dec[/b]",
                )
            )
            self.ids.servers_list.add_widget(item)

Builder.load_string(KV)


class Test(MDApp):
    title = "MainScreen v2"

    def build(self):
        Window.size = (1280, 720)

        # TODO: review this values
        self.theme_cls.theme_style = "Dark" # (?)
        self.theme_cls.primary_palette = "Orange"  # (?)

        manager = WindowManager()
        manager.add_widget(MainScreen())
        return manager


if __name__ == "__main__":
    Test().run()
