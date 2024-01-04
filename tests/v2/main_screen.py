from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

from kivymd.uix.expansionpanel import MDExpansionPanelOneLine, MDExpansionPanelThreeLine, MDExpansionPanelLabel

from kivymd.uix.behaviors import RoundedRectangularElevationBehavior, CommonElevationBehavior, RectangularRippleBehavior, CircularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.fitimage.fitimage import FitImage

import os
from typing import Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import WidgetException

import kivymd.material_resources as m_res
from kivymd import uix_path
from kivymd.icon_definitions import md_icons
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import (
    IconLeftWidget,
    ImageLeftWidget,
    IRightBodyTouch,
    OneLineAvatarIconListItem,
    ThreeLineAvatarIconListItem,
    TwoLineAvatarIconListItem,
    TwoLineListItem,
)


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

<MDExpansionChevronRight>:
    icon: "chevron-down"
    theme_text_color: "Custom"
    text_color: "white"

    disabled: True
    md_bg_color_disabled: 0, 0, 0, 0

    canvas.before:
        PushMatrix
        Rotate:
            angle: self._angle
            axis: (0, 0, 1)
            origin: self.center
    canvas.after:
        PopMatrix


<MDExpansionPanelRoundIcon>
    size_hint_y: None
    # height: dp(68)
"""

class WindowManager(ScreenManager):
    pass


class Content(MDBoxLayout):
    pass

class MDExpansionChevronRight(IRightBodyTouch, MDIconButton):
    _angle = NumericProperty(0)

class DisplayPic(CommonElevationBehavior, FitImage):
    pass

class MDExpansionPanelTwoLineSmall(TwoLineAvatarIconListItem):
    """
    Two-line panel.

    For more information, see in the
    :class:`~kivymd.uix.list.TwoLineAvatarIconListItem` class documentation.
    """

    _txt_top_pad = NumericProperty("20dp")
    _txt_bot_pad = NumericProperty("6dp")
    _txt_left_pad = NumericProperty("50dp")
    _height = NumericProperty("50dp")
    _num_lines = 2

# https://raw.githubusercontent.com/kivymd/KivyMD/master/kivymd/uix/expansionpanel/expansionpanel.py
class MDExpansionPanelRoundIcon(RelativeLayout):
    content = ObjectProperty()
    icon = StringProperty()
    #TODO: icon size(?)
    opening_transition = StringProperty("out_cubic")
    opening_time = NumericProperty(0.2)
    closing_transition = StringProperty("out_sine")
    closing_time = NumericProperty(0.2)
    panel_cls = ObjectProperty()

    _state = StringProperty("close")
    _anim_playing = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_open")
        self.register_event_type("on_close")

        if self.panel_cls and isinstance(
            self.panel_cls,
            (
                MDExpansionPanelOneLine,
                MDExpansionPanelTwoLineSmall,
                MDExpansionPanelThreeLine,
                MDExpansionPanelLabel,
            ),
        ):
            self.panel_cls.pos_hint = {"top": 1}

            self.panel_cls._no_ripple_effect = True
            self.panel_cls.bind(
                on_release=lambda x: self.check_open_panel(self.panel_cls)
            )
            if not isinstance(self.panel_cls, MDExpansionPanelLabel):
                self.chevron = MDExpansionChevronRight()
                self.panel_cls.add_widget(self.chevron)
                if self.icon:
                    if self.icon in md_icons.keys():
                        self.panel_cls.add_widget(
                            IconLeftWidget(
                                icon=self.icon,
                                pos_hint={"center_y": 0.5},
                            )
                        )
                    else:
                        # self.panel_cls.add_widget(ImageLeftWidget(source=self.icon, pos_hint={"center_y": 0.5}))
                        self.panel_cls.add_widget(DisplayPic(
                            source=self.icon,
                            elevation=dp(3),
                            size_hint=(None, None),
                            size=(dp(30), dp(30)),
                            radius=dp(360),
                            pos_hint={'center_x': .12, 'center_y': .5}
                        ))
                else:
                    self.panel_cls.remove_widget(
                        self.panel_cls.ids._left_container
                    )
                    self.panel_cls._txt_left_pad = 0
            else:
                # if no icon
                self.panel_cls._txt_left_pad = m_res.HORIZ_MARGINS
            self.add_widget(self.panel_cls)
        else:
            raise ValueError(
                "KivyMD: `panel_cls` object must be must be one of the "
                "objects from the list\n"
                "[MDExpansionPanelOneLine, MDExpansionPanelTwoLineSmall, "
                "MDExpansionPanelThreeLine]"
            )

    def on_open(self, *args):
        """Called when a panel is opened."""

    def on_close(self, *args):
        """Called when a panel is closed."""

    def check_open_panel(
        self,
        instance_panel: [
            MDExpansionPanelThreeLine,
            MDExpansionPanelTwoLineSmall,
            MDExpansionPanelThreeLine,
            MDExpansionPanelLabel,
        ],
    ) -> None:
        """
        Called when you click on the panel. Called methods to open or close
        a panel.
        """

        press_current_panel = False
        for panel in self.parent.children:
            if isinstance(panel, MDExpansionPanelRoundIcon):
                if len(panel.children) == 2:
                    if instance_panel is panel.children[1]:
                        press_current_panel = True
                    panel.remove_widget(panel.children[0])
                    if not isinstance(self.panel_cls, MDExpansionPanelLabel):
                        chevron = panel.children[0].children[1].children[0]  # Fix [0/1]
                        self.set_chevron_up(chevron)
                    self.close_panel(panel, press_current_panel)
                    self.dispatch("on_close")
                    break
        if not press_current_panel:
            self.set_chevron_down()

    def set_chevron_down(self) -> None:
        """Sets the chevron down."""

        if not isinstance(self.panel_cls, MDExpansionPanelLabel):
            Animation(_angle=-90, d=self.opening_time).start(self.chevron)
        self.open_panel()
        self.dispatch("on_open")

    def set_chevron_up(self, instance_chevron: MDExpansionChevronRight) -> None:
        """Sets the chevron up."""

        if not isinstance(self.panel_cls, MDExpansionPanelLabel):
            Animation(_angle=0, d=self.closing_time).start(instance_chevron)

    def close_panel(
        self, instance_expansion_panel, press_current_panel: bool
    ) -> None:
        """Method closes the panel."""

        if self._anim_playing:
            return

        if press_current_panel:
            self._anim_playing = True

        self._state = "close"

        anim = Animation(
            height=self.panel_cls.height,
            d=self.closing_time,
            t=self.closing_transition,
        )
        anim.bind(on_complete=self._disable_anim)
        anim.start(instance_expansion_panel)

    def open_panel(self, *args) -> None:
        """Method opens a panel."""

        if self._anim_playing:
            return

        self._anim_playing = True
        self._state = "open"

        anim = Animation(
            height=self.content.height + self.height,
            d=self.opening_time,
            t=self.opening_transition,
        )
        anim.bind(on_complete=self._add_content)
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

    def get_state(self) -> str:
        """Returns the state of panel. Can be `close` or `open` ."""

        return self._state

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(
            widget,
            (
                MDExpansionPanelOneLine,
                MDExpansionPanelTwoLineSmall,
                MDExpansionPanelThreeLine,
                MDExpansionPanelLabel,
            ),
        ):
            self.height = widget.height
        return super().add_widget(widget)

    def _disable_anim(self, *args):
        self._anim_playing = False

    def _add_content(self, *args):
        if self.content:
            try:
                if isinstance(self.panel_cls, MDExpansionPanelLabel):
                    self.content.y = dp(36)
                self.add_widget(self.content)
            except WidgetException:
                pass


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__()
        self.build()

    def build(self):
        import random
        countries = ["France", "Italy", "Brasil", "Egypt", "Belgium", "Deutschland", "Canada"]
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
                    radius = [10, 10, 10, 10],
                    bg_color = get_color_from_hex("#212221"),
                    text = country,
                    text_color = "white",
                    theme_text_color = "Custom",
                    font_style = "Subtitle1",
                    secondary_text = f"{random.randint(1, 100)} servers",
                    secondary_text_color = "white",
                    secondary_theme_text_color = "Custom",
                    secondary_font_style = "Caption",
                )
            )
            self.ids.countries_list.add_widget(item)



Builder.load_string(KV)
class Test(MDApp):
    title = "MainScreen v2"

    def build(self):
        Window.size = (1280,720)

        manager = WindowManager()
        manager.add_widget(MainScreen())
        return manager

if __name__ == "__main__":
    Test().run()