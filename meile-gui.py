from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty, StringProperty

from kivymd.color_definitions import colors
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

from src.cli.sentinel import get_nodes, NodesInfoKeys
from kivymd.uix.list import ThreeLineAvatarIconListItem, ImageLeftWidget
import awoc

our_world = awoc.AWOC()

CONTINENTS   = our_world.get_continents_list()
Africa       = our_world.get_countries_list_of(CONTINENTS[0])
Anarctica    = our_world.get_countries_list_of(CONTINENTS[1])
Asia         = our_world.get_countries_list_of(CONTINENTS[2])
Europe       = our_world.get_countries_list_of(CONTINENTS[3])
NorthAmerica = our_world.get_countries_list_of(CONTINENTS[4])
Oceania      = our_world.get_countries_list_of(CONTINENTS[5])
SouthAmerica = our_world.get_countries_list_of(CONTINENTS[6])


canvas = '''
<Root@MDBoxLayout>
    orientation: 'vertical'

    MDToolbar:
        title: app.title
        md_bg_color: 0,0,0,1
        height: "100dp"
        
        FitImage:
            source: "./src/imgs/logo.png"
            size_hint: None, None
            height: "100dp"
            pos: self.pos

    
    MDTabs:
        id: android_tabs
        on_tab_switch: app.on_tab_switch(*args)
        size_hint_y: None
        height: "48dp"
        tab_indicator_anim: True
        color: 0,0,0,1
        md_bg_color: 0,0,0,1
        
    RecycleView:
        id: rv
        key_viewclass: "viewclass"
        key_size: "height"

        RecycleBoxLayout:
            default_size: None, dp(48)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: "vertical"



<Tab>

<SelectableLabel>:
    # Draw a background to indicate selection
    text1: "GLARGLY"
    text2: "BLARGLY"
    text3: "SHIMARGLY"
    canvas.before:

        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size

<RV>:
    viewclass: 'SelectableLabel'
    RecycleBoxLayout:
        default_size: None, dp(48)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: "vertical"

<MD3Card>
    
    orientation: "vertical"
    height: node_box.height 
    focus_behavior: True
    ripple_behavior: True

    moniker_text:  "BLARGLY"
    moniker2_text: "GLARGLY"
    moniker3_text: "SHLARMLY"
    
    source_image: "TESST"
    
    BoxLayout:
        id: node_box
        size_hint_y: None
        height: "50dp"
    
        canvas:
            Rectangle:
                pos: self.pos
                size: self.size
                
        MDLabel:
            id: label_box
            
            text: root.moniker_text
        MDLabel:
            id: label_box
            
            text: root.moniker2_text
        MDLabel:
            id: label_box
            
            text: root.moniker3_text
        FitImage:
            source: root.source_image
            size_hint: None, None
            height: "30dp"
            width: "50dp"
            pos: self.pos

        
    MDSeparator:


'''

from kivy.factory import Factory

from kivymd.app import MDApp


class Tab(MDBoxLayout, MDTabsBase):
    pass

class MD3Card(MDCard):
    Moniker = None
    
    def set_moniker(self, name):
        self.Moniker = name
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
    
    def populate_rv(self, node):
        self.data.append(
                {           
                    "text1" : node[NodesInfoKeys[0]].lstrip().rstrip(),
                    "text2" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                    "text3" : node[NodesInfoKeys[4]].lstrip().rstrip(),           
                }
            )

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class Palette(MDApp):
    title = "Meile dVPN"
    ConNodes = []
    
    def build(self):
        Builder.load_string(canvas)
        self.screen = Factory.Root()
        
        for name_tab in CONTINENTS:
            tab = Tab(text=name_tab)
            self.screen.ids.android_tabs.add_widget(tab)
        
        self.ConNodes = get_nodes()
        
        return self.screen

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        
        rv = RV()
        floc = "./src/imgs/"
        self.screen.ids.rv.data = []

        if not tab_text:
            tab_text = CONTINENTS[0]
            
        for node in self.ConNodes:
            if tab_text == CONTINENTS[0]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Africa:
                    
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    
            elif tab_text == CONTINENTS[1]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Anarctica:
                    
                       #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    
                    #rv.populate_rv(node)
            elif tab_text == CONTINENTS[2]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Asia:
                    
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    
                    #rv.populate_rv(node)
            elif tab_text == CONTINENTS[3]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Europe:
                    
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    
                    #rv.populate_rv(node)
            elif tab_text == CONTINENTS[4]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in NorthAmerica:
                    
                      #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    
                    #rv.populate_rv(node)
            elif tab_text == CONTINENTS[5]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Oceania:
                    
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    #rv.populate_rv(node)
            else: 
                if node[NodesInfoKeys[4]].lstrip().rstrip() in SouthAmerica:
                    
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.screen.ids.rv.data.append(
                        {
                            "viewclass": "MD3Card",
                            "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                            "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                            "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                            "source_image" : flagloc
                            
                        },
                    )
                    
                    #rv.populate_rv(node)
                  
            
    def on_start(self):
        
        
        self.on_tab_switch(
            None,
            None,
            None,
            self.screen.ids.android_tabs.ids.layout.children[-1].text
        )


Palette().run()