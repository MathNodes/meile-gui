from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import  StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivy.uix.switch import Switch
from kivy_garden.mapview.view import MapView
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior, CircularElevationBehavior, RectangularRippleBehavior, CircularRippleBehavior
from kivymd.uix.fitimage.fitimage import FitImage
from kivy.uix.behaviors import ButtonBehavior 
from kivymd.uix.textfield.textfield import MDTextField
from kivymd.uix.label.label import MDLabel
from kivymd.uix.progressbar.progressbar import MDProgressBar

from conf.meile_config import MeileGuiConfig
from typedef.konstants import MeileColors

class ProtectedLabel(MDLabel):
    def get_font(self):
        Config = MeileGuiConfig()
        return Config.resource_path(MeileColors.QR_FONT_FACE)
    
    
class MapCenterButton(MDIconButton, MDTooltip):
    pass

class ToolTipMDIconButton(MDIconButton, MDTooltip):
    pass

class IPAddressTextField(MDTextField):
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

#class DisplayPic(CircularElevationBehavior, ButtonBehavior, FitImage):
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

class ConnectionDialog(MDBoxLayout):
    pass


