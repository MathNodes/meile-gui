from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import  StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.tooltip import MDTooltip
from kivy.uix.switch import Switch
from kivy_garden.mapview.view import MapView

class Tab(MDBoxLayout, MDTabsBase):
    pass

'''
class SubscribeContent(BoxLayout):
    price_text = StringProperty()
    
    def __init_ (self, price):
        self.price_text = price
'''
class LatencyContent(BoxLayout):
    
    def return_latency(self):
        return self.ids.latency.text
class YellowSwitch(Switch):
    pass
class TooltipMDRaisedButton(MDRaisedButton, MDTooltip):
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

class FullImage(Image):
    pass
class FullImage2(Image):
    pass
