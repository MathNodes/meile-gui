from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen


from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.uix.list import ImageLeftWidget

from kivymd.uix.datatables import MDDataTable

# meil uix from tests
from uix.expansionpanel import MDExpansionPanelRoundIcon, MDExpansionPanelTwoLineSmall

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
            md_bg_color: get_color_from_hex("#212221")

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

            AnchorLayout:
                orientation: "horizontal"
                md_bg_color: get_color_from_hex("#131313")
                id: servers_datatable

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


        self.data_tables = MDDataTable(
            use_pagination=True,
            check=False,
            column_data=[
                ("Moniker", dp(45)),
                ("Location", dp(20)),
                ("Speed", dp(50)),
                ("Status", dp(20)),
                ("Price", dp(40)),
                ("Protocol", dp(20)),
                ("Type", dp(20)),
            ],
            sorted_on="Moniker",
            sorted_order="ASC",
            elevation=2,
            rows_num=10
        )

        row_data = []
        for _ in range(0, 150):
            upload = random.uniform(100, 900)
            download = random.uniform(100, 900)
            bandwith = "speedometer-medium"
            if upload + download > 1200:
                bandwith = "speedometer"
            elif upload + download < 400:
                bandwith = "speedometer-slow"

            healthcheck = random.choice([True, False])

            row_data.append(
                (
                    ''.join(random.choices(string.printable[:-6], k=random.randint(5, 15))),  # Moniker
                    random.choice(countries),
                    (bandwith, [1, 1, 1, 1] ,f"[size=12][color=#00FF00]up[/color] {round(upload, 2)}mb/s[color=#f44336]down[/color] {round(download, 2)}mb/s[/size]"),
                    ("shield-plus", [39 / 256, 174 / 256, 96 / 256, 1], "Health") if healthcheck is True else ("emoticon-sick", [1, 0, 0, 1], "Sick"),
                    f"[size=12]{random.randint(1, 100)}dvpn, {random.randint(1, 100)}atom, {random.randint(1, 100)}osmo, {random.randint(1, 100)}srct, {random.randint(1, 100)}dec[/size]",
                    random.choice(["Wireguard", "V2RAY"]),
                    random.choice(["Residential", "Datacenter", "Unknown"])
                )
            )

        self.data_tables.row_data = row_data

        self.data_tables.bind(on_row_press=self.on_row_press)
        self.ids.servers_datatable.add_widget(self.data_tables)

    def on_row_press(self, instance_table, instance_row):
        '''Called when a table row is clicked.'''

        print(instance_table, instance_row)

    def on_check_press(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''

        print(instance_table, current_row)

    # Sorting Methods:
    # since the https://github.com/kivymd/KivyMD/pull/914 request, the
    # sorting method requires you to sort out the indexes of each data value
    # for the support of selections.
    #
    # The most common method to do this is with the use of the builtin function
    # zip and enumerate, see the example below for more info.
    #
    # The result given by these funcitons must be a list in the format of
    # [Indexes, Sorted_Row_Data]

    def sort_on_signal(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][2]))

    def sort_on_schedule(self, data):
        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: sum(
                    [
                        int(l[1][-2].split(":")[0]) * 60,
                        int(l[1][-2].split(":")[1]),
                    ]
                ),
            )
        )

    def sort_on_team(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][-1]))

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
