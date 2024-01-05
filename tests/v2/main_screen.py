from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen


from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.uix.list import ImageLeftWidget

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
                    size_hint_y: None
                    height: 50

                    MDIconButton:
                        icon: "wallet"
                        theme_text_color: "Custom"
                        text_color: "white"

                    MDIconButton:
                        icon: "cog"
                        theme_text_color: "Custom"
                        text_color: "white"

                    MDIconButton:
                        icon: "help-circle"
                        theme_text_color: "Custom"
                        text_color: "white"



            MDFloatLayout:
                orientation: "horizontal"
                md_bg_color: get_color_from_hex("#131313")


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
        import random

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


Builder.load_string(KV)


class Test(MDApp):
    title = "MainScreen v2"

    def build(self):
        Window.size = (1280, 720)

        manager = WindowManager()
        manager.add_widget(MainScreen())
        return manager


if __name__ == "__main__":
    Test().run()
