from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import  StringProperty, NumericProperty, ListProperty, \
    OptionProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from os import path
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivy.uix.switch import Switch
from kivy_garden.mapview.view import MapView
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior, RectangularRippleBehavior, CircularRippleBehavior
from kivymd.uix.fitimage.fitimage import FitImage
from kivy.uix.behaviors import ButtonBehavior 
from kivymd.uix.textfield.textfield import MDTextField
from kivymd.uix.label.label import MDLabel
from kivymd.uix.progressbar.progressbar import MDProgressBar

from conf.meile_config import MeileGuiConfig
from typedef.konstants import ConnectStages, MeileColors

# Geometry of the connection dialog pipeline (ui/kv/meile.kv <ConnectionRing>,
# <ConnectionStage> and <ConnectionDialog>).
CONN_RING_WIDTH      = dp(1)      # idle ring
CONN_RING_ACTIVE     = dp(1.25)   # ring while its stage runs
CONN_RING_SOLID      = dp(1.5)    # ring once the stage is done / failed
CONN_GLOW_INNER_MIN  = dp(1.5)    # inner halo, narrowest pulse
CONN_GLOW_INNER_MAX  = dp(3.5)    # inner halo, widest pulse
CONN_GLOW_OUTER_MIN  = dp(1)
CONN_GLOW_OUTER_MAX  = dp(2.5)
CONN_GLOW_INNER_GAP  = dp(3)      # halo offsets from the ring radius
CONN_GLOW_OUTER_GAP  = dp(7)
CONN_GLOW_ALPHA      = (0.40, 0.10)   # inner halo alpha (bright, dim)
CONN_OUTER_ALPHA     = (0.20, 0.04)   # outer halo alpha (bright, dim)
CONN_LINK_WIDTH      = dp(2)      # connector between two finished stages


def resolve_stage_icon(relative_path):
    '''Absolute path of a connection stage icon (imgs/*.png).

    The app addresses its images with MeileGuiConfig.resource_path(), which is
    right inside a PyInstaller build; in a plain checkout that helper points at
    src/conf instead, so fall back to this module's own directory, which finds the
    same imgs/ folder whatever the working directory happens to be.
    '''
    bundled = MeileGuiConfig().resource_path(relative_path)
    if path.exists(bundled):
        return bundled
    local = path.normpath(path.join(path.dirname(path.abspath(__file__)),
                                    "..", relative_path))
    return local if path.exists(local) else relative_path

class ProtectedLabel(MDLabel):
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
class DownloadLabel(MDLabel):
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
class UploadLabel(MDLabel):
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
class TimeLabel(MDLabel):
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.FONT_FACE)
    
class MapCenterButton(MDIconButton, MDTooltip):
    pass

class ToolTipMDIconButton(MDIconButton, MDTooltip):
    pass

class IPAddressTextField(MDTextField):
    pass

class ProtocolTextField(MDTextField):
    pass

class ConnectedNode(MDTextField):
    pass

class BandwidthLabel(MDLabel):
    pass

class BandwidthBar(MDProgressBar):
    pass

class QuotaPct(MDLabel):
    pass

class LatencyContent(BoxLayout):
    
    def return_latency(self):
        return self.ids.latency.text
class YellowSwitch(Switch):
    pass
class TooltipMDRaisedButton(MDRaisedButton, MDTooltip):
    pass
class TooltipMDFlatButton(MDFlatButton, MDTooltip):
    pass

class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass

class WindowManager(ScreenManager):
    pass

class ClickableTextFieldRoundSeed(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    
class ClickableTextFieldRoundName(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    
class ClickableTextFieldRoundPass(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''
    
class ContinentMap(MapView):
    pass

class DisplayPic(ButtonBehavior, FitImage):
    pass

class ClickableTextFieldRoundCC(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    
'''
class ClickableTextFieldRoundName(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

'''
class ClickableTextFieldRoundCVV(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

class TXContent(BoxLayout):
    pass

class ConnectionRing(MDFloatLayout):
    '''Icon of a ConnectionStage wrapped in its status ring.

    The drawing only: three concentric canvas circles (an inner and an outer
    translucent halo plus the crisp ring) around the icon.  ConnectionStage owns
    the colours and widths, so a stage can be idle, glowing, finished or failed.
    '''

    icon_source  = StringProperty()
    icon_inset   = NumericProperty(dp(7))
    icon_opacity = NumericProperty(1.0)

    # NB: MDFloatLayout's BackgroundColorBehavior already owns `radius` for its
    # own rounded background, hence the ring's own name.
    ring_radius  = NumericProperty(0)
    ring_gap     = NumericProperty(dp(1))      # ring inset from the widget edge
    ring_rgba    = ListProperty([0.227, 0.227, 0.227, 1.0])
    ring_width   = NumericProperty(CONN_RING_WIDTH)
    # Halo widths stay positive (Line rejects 0); alpha is what hides them.  The
    # resting colour is UPLOAD blue (see MeileColors), the "work in progress" hue.
    inner_rgba   = ListProperty([0.184, 0.631, 0.898, 0.0])
    inner_width  = NumericProperty(CONN_GLOW_INNER_MIN)
    outer_rgba   = ListProperty([0.184, 0.631, 0.898, 0.0])
    outer_width  = NumericProperty(CONN_GLOW_OUTER_MIN)

    def on_size(self, *largs):
        self.ring_radius = max(0.0, min(self.width, self.height) / 2.0 - self.ring_gap)


class ConnectionStage(MDBoxLayout):
    '''One step of the connection dialog pipeline: icon, ring and caption.

    ``state`` drives the whole look.  The ``active`` stage pulses an UPLOAD-blue
    glow around its icon *while the step is still running*; ``done`` freezes that
    ring solid green the moment the step succeeds, and ``failed`` shows it solid
    red, so the user can read how far the connection got.
    '''

    caption = StringProperty()
    source  = StringProperty()
    state   = OptionProperty("idle", options=["idle", "active", "done", "failed"])

    # Forwarded to the ConnectionRing in kv (kept here so the state machine has a
    # single owner).  Halos rest at UPLOAD blue; a finished stage switches the
    # crisp ring (and its caption) to the DOWNLOAD green.
    caption_color = ListProperty([0.227, 0.227, 0.227, 1.0])
    icon_opacity  = NumericProperty(0.35)
    ring_rgba     = ListProperty([0.227, 0.227, 0.227, 1.0])
    ring_width    = NumericProperty(CONN_RING_WIDTH)
    inner_rgba    = ListProperty([0.184, 0.631, 0.898, 0.0])
    inner_width   = NumericProperty(CONN_GLOW_INNER_MIN)
    outer_rgba    = ListProperty([0.184, 0.631, 0.898, 0.0])
    outer_width   = NumericProperty(CONN_GLOW_OUTER_MIN)

    def _rgba(self, hex_color, alpha=1.0):
        r, g, b, _ = get_color_from_hex(hex_color)
        return [r, g, b, alpha]

    @property
    def ring_radius(self):
        '''Radius of the drawn ring, in the stage's own coordinates.'''
        return self.ids.ring.ring_radius

    @property
    def ring_center(self):
        '''Centre of the drawn ring, in the stage's own coordinates.'''
        return self.ids.ring.center

    def on_state(self, *largs):
        if self.state == "active":
            # Still running: UPLOAD blue ring with a matching breathing glow.
            self._start_glow()
            self.icon_opacity = 1.0
            self.ring_width = CONN_RING_ACTIVE
            self.ring_rgba = self._rgba(MeileColors.UPLOAD)
            self.caption_color = self._rgba(MeileColors.WHITE, 0.94)
        elif self.state == "done":
            # Succeeded: the ring settles into solid DOWNLOAD green.
            self._stop_glow()
            self.icon_opacity = 1.0
            self.ring_width = CONN_RING_SOLID
            self.ring_rgba = self._rgba(MeileColors.DOWNLOAD)
            self.caption_color = self._rgba(MeileColors.DOWNLOAD, 0.9)
        elif self.state == "failed":
            self._stop_glow()
            self.icon_opacity = 1.0
            self.ring_width = CONN_RING_SOLID
            self.ring_rgba = self._rgba(MeileColors.CONN_STAGE_FAILED)
            self.caption_color = self._rgba(MeileColors.CONN_STAGE_FAILED)
        else:  # idle - this stage has not started yet
            self._stop_glow()
            self.icon_opacity = 0.35
            self.ring_width = CONN_RING_WIDTH
            self.ring_rgba = self._rgba(MeileColors.CONN_STAGE_IDLE)
            self.caption_color = self._rgba(MeileColors.CONN_STAGE_IDLE)

    def _start_glow(self):
        '''Pulse the two halos (UPLOAD blue): a slow in/out breath while the
        stage is still running.  It is stopped the moment the step succeeds and
        the ring turns solid green.'''
        rgb = get_color_from_hex(MeileColors.UPLOAD)[:3]
        inner_bright = rgb + [CONN_GLOW_ALPHA[0]]
        inner_dim    = rgb + [CONN_GLOW_ALPHA[1]]
        outer_bright = rgb + [CONN_OUTER_ALPHA[0]]
        outer_dim    = rgb + [CONN_OUTER_ALPHA[1]]

        self.inner_rgba  = list(inner_dim)
        self.outer_rgba  = list(outer_dim)
        self.inner_width = CONN_GLOW_INNER_MIN
        self.outer_width = CONN_GLOW_OUTER_MIN

        glow = (
            Animation(inner_rgba=inner_bright, inner_width=CONN_GLOW_INNER_MAX,
                      outer_rgba=outer_bright, outer_width=CONN_GLOW_OUTER_MAX,
                      duration=0.85, t="in_out_sine") +
            Animation(inner_rgba=inner_dim, inner_width=CONN_GLOW_INNER_MIN,
                      outer_rgba=outer_dim, outer_width=CONN_GLOW_OUTER_MIN,
                      duration=0.85, t="in_out_sine")
        )
        glow.repeat = True
        glow.start(self)

    def _stop_glow(self):
        Animation.cancel_all(self, "inner_rgba", "inner_width",
                             "outer_rgba", "outer_width")
        self.inner_width = CONN_GLOW_INNER_MIN
        self.outer_width = CONN_GLOW_OUTER_MIN
        self.inner_rgba = [self.inner_rgba[0], self.inner_rgba[1],
                           self.inner_rgba[2], 0.0]
        self.outer_rgba = [self.outer_rgba[0], self.outer_rgba[1],
                           self.outer_rgba[2], 0.0]


class ConnectionDialog(MDBoxLayout):
    '''Connect progress dialog: the pipeline of connection stages, the progress
    bar and the wallet's own status line (which used to be the dialog title).

    ``set_status()`` is the entry point used by ui.screens: the text lands in the
    small line under the progress bar and, when it names a later stage of
    cli.wallet.HandleWalletFunctions.connect(), the stages behind it turn solid
    and a green connector lights up to the new one.
    '''

    status_text  = StringProperty(ConnectStages.DEFAULT_STATUS)
    link_width   = NumericProperty(CONN_LINK_WIDTH)

    # Connector geometry/alpha, drawn in this widget's canvas (kv).  A link is
    # the line between two stage icons, lit once the stage before it finished.
    link1_points = ListProperty([])
    link2_points = ListProperty([])
    link1_rgba   = ListProperty([0.184, 0.898, 0.282, 0.0])
    link2_rgba   = ListProperty([0.184, 0.898, 0.282, 0.0])

    # Kivy dispatches on_kv_post from inside the base __init__, hence these
    # defaults rather than assignments in an __init__ body of our own.
    stage_defs   = ConnectStages.STAGES     # ordered (icon, caption, keywords)
    stages       = ()                       # the three ConnectionStage widgets
    _links_shown = ()                       # per-connector visibility flags
    _stage_index = 0                        # furthest stage reached so far

    def on_kv_post(self, base_widget):
        self.stages = [self.ids.stage_session, self.ids.stage_credentials,
                       self.ids.stage_internet]
        self._links_shown = [False, False]
        self._stage_index = 0
        for stage, (icon, caption, _keywords) in zip(self.stages, self.stage_defs):
            stage.source = resolve_stage_icon(icon)
            stage.caption = caption
        # The connectors follow whatever the layout pass does to the stages.
        self.bind(pos=self._sync_links, size=self._sync_links)
        for stage in self.stages:
            stage.bind(pos=self._sync_links, size=self._sync_links)
            stage.ids.ring.bind(pos=self._sync_links, size=self._sync_links)
        self._apply_status(self.status_text)
        self._sync_links()
        Clock.schedule_once(self._sync_links, 0)
        Clock.schedule_once(self._sync_links, 0.2)

    def set_status(self, text):
        '''Show ``text`` (a connect.log line) and advance the pipeline.'''
        text = (text or "").strip()
        if text:
            self.status_text = text

    def on_status_text(self, *largs):
        self._apply_status(self.status_text)

    def _apply_status(self, text):
        line = (text or "").strip().lower()
        # The wallet only ever moves forward (session -> credentials -> network)
        # and keeps writing unrelated lines in between ("Bringing up ... tunnel",
        # errors), so the farthest stage named by any line so far is the one that
        # is running.
        index = self._stage_index
        for i, (_icon, _caption, keywords) in enumerate(self.stage_defs):
            if keywords and any(k in line for k in keywords):
                index = max(index, i)
        self._stage_index = index
        failed = any(k in line for k in ConnectStages.FAILED_KEYWORDS)
        for i, stage in enumerate(self.stages):
            if i < index:
                stage.state = "done"
            elif i == index:
                stage.state = "failed" if failed else "active"
            else:
                stage.state = "idle"
        # A connector is only drawn once the stage it comes from has finished.
        for i in range(1, len(self.stages)):
            self._set_link(i - 1, self.stages[i - 1].state == "done")
        self._sync_links()

    def _set_link(self, index, show):
        if index >= len(self._links_shown) or self._links_shown[index] == show:
            return
        self._links_shown[index] = show
        name = "link%d_rgba" % (index + 1)
        rgba = get_color_from_hex(MeileColors.DOWNLOAD)[:3] + [1.0 if show else 0.0]
        Animation.cancel_all(self, name)
        if show:
            Animation(**{name: rgba, "duration": 0.35}).start(self)
        else:
            setattr(self, name, rgba)

    def _sync_links(self, *largs):
        '''Point each connector from the right edge of one ring to the left edge
        of the next, both at the height of their shared centre.'''
        if len(self.stages) < 3:
            return
        for i, (left, right) in enumerate(zip(self.stages, self.stages[1:])):
            lx, ly = self._to_dialog(left, left.ring_center)
            rx, ry = self._to_dialog(right, right.ring_center)
            points = [lx + left.ring_radius, ly, rx - right.ring_radius, ry]
            setattr(self, "link%d_points" % (i + 1), points)

    def _to_dialog(self, widget, position):
        '''Map a coordinate of ``widget`` (a stage) into this canvas' space.'''
        wx, wy = widget.to_window(*position)
        dx, dy = self.to_window(0, 0)
        return wx - dx, wy - dy

class QRDialogContent(MDBoxLayout):
    pass

class QRDialogZanoContent(MDBoxLayout):
    pass

class QRDialogV2RayContent(MDBoxLayout):
    pass
