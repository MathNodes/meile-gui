from kivy.lang import Builder
from kivy.metrics import dp

from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout

from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.tooltip import MDTooltip

from kivy.uix.behaviors import ButtonBehavior

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

from kivy.animation import Animation


KV = """

<Node>:
    cols: 7

    MDLabel:
        padding: [10, 0, 0, 0]
        text: root.moniker
        markup: True
        size_hint_x: 2
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

    MDLabel:
        text: root.location
        markup: True
        size_hint_x: 1
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

    MDLabel:
        text: root.speed
        markup: True
        size_hint_x: 2
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

    # MDLabel:
    #     text: root.status
    #     markup: True
    #     size_hint_x: 1
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

    # MDLabel:
    #     text: root.price
    #     markup: True
    #     size_hint_x: 2
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

    MDLabel:
        text: root.protocol
        markup: True
        size_hint_x: 1
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

    MDLabel:
        text: root.node_type
        markup: True
        size_hint_x: 1
        font_name: "../../src/fonts/arial-unicode-ms.ttf"

<TooltipMDIconButton@MDIconButton+MDTooltip>

<NodeDetails>:
    adaptive_height: True
    orientation: 'horizontal'

    TooltipMDIconButton:
        icon: "shield-plus" if root.health_check is True else 'emoticon-sick'
        icon_color: "green" if root.health_check is True else "red"

        tooltip_text: "Passed Sentinel Health Check" if root.health_check is True else "Failed Sentinel Health Check"
        pos_hint: {"center_x": .5, "center_y": .5}

    MDLabel
        text: root.price
        markup: True


<NodeAccordion>:
    rows: 2
    md_bg_color: get_color_from_hex("#1C1D1B")
    radius: [5, 5, 5, 5]

    height: 50
    adaptive_height: True
"""
Builder.load_string(KV)


class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass


class Node(MDGridLayout):
    moniker = StringProperty()
    location = StringProperty()
    speed = StringProperty()
    status = StringProperty()
    price = StringProperty()
    protocol = StringProperty()
    node_type = StringProperty()


class NodeDetails(MDBoxLayout):
    health_check = BooleanProperty(False)
    price = StringProperty()


class NodeAccordion(ButtonBehavior, MDGridLayout):
    node = ObjectProperty()  # Main node info

    # https://github.com/kivymd/KivyMD/blob/master/kivymd/uix/expansionpanel/expansionpanel.py
    content = ObjectProperty()  # Node details....
    """
    Content of panel. Must be `Kivy` widget.

    :attr:`content` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    opening_transition = StringProperty("out_cubic")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` `'open'`.

    :attr:`opening_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_cubic'`.
    """

    opening_time = NumericProperty(0.2)
    """
    The time taken for the panel to slide to the :attr:`state` `'open'`.

    :attr:`opening_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """

    closing_transition = StringProperty("out_sine")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` 'close'.

    :attr:`closing_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_sine'`.
    """

    closing_time = NumericProperty(0.2)
    """
    The time taken for the panel to slide to the :attr:`state` `'close'`.

    :attr:`closing_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """

    _state = StringProperty("close")
    _anim_playing = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_open")
        self.register_event_type("on_close")

        self.add_widget(self.node)

    def on_release(self):
        if len(self.children) == 1:
            self.add_widget(self.content)
            self.open_panel()
            self.dispatch("on_open")
        else:
            self.remove_widget(self.children[0])
            self.close_panel()
            self.dispatch("on_close")

    def on_open(self, *args):
        """Called when a panel is opened."""

    def on_close(self, *args):
        """Called when a panel is closed."""

    def close_panel(self) -> None:
        """Method closes the panel."""

        if self._anim_playing:
            return

        self._anim_playing = True
        self._state = "close"

        anim = Animation(
            height=self.children[0].height,
            d=self.closing_time,
            t=self.closing_transition,
        )
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

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
        # anim.bind(on_complete=self._add_content)
        anim.bind(on_complete=self._disable_anim)
        anim.start(self)

    def get_state(self) -> str:
        """Returns the state of panel. Can be `close` or `open` ."""

        return self._state

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, NodeDetails):
            self.height = widget.height
        return super().add_widget(widget)

    def _disable_anim(self, *args):
        self._anim_playing = False

    def _add_content(self, *args):
        if self.content:
            self.content.y = dp(36)
            self.add_widget(self.content)