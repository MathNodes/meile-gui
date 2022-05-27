from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty, StringProperty

from kivymd.color_definitions import colors
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

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
        height: "160dp"
        
        FitImage:
            source: "./src/imgs/logo.png"
            size_hint: .25, None
            height: "120dp"
            pos_hint: {"left" : 1 }

    
    MDTabs:
        id: android_tabs
        on_tab_switch: app.on_tab_switch(*args)
        size_hint_y: None
        height: "48dp"
        tab_indicator_anim: False
        md_bg_color: 0,0,0,1

    ScrollView:
    
        MDList:
            id: container



<MD3Card>
    
    orientation: "vertical"
    size_hint: .5, None
    height: node_box.height 
    focus_behavior: True
    ripple_behavior: True
    pos_hint: {"center_x": .5, "center_y": .5}


    MDBoxLayout:
        id: node_box
        orientation: "vertical"
        adaptive_height: True
        spacing: "10dp"
        padding: 0, "10dp", "10dp", "10dp"


    MDSeparator:


<Tab>
'''

from kivy.factory import Factory

from kivymd.app import MDApp


class Tab(MDBoxLayout, MDTabsBase):
    pass

class MD3Card(MDCard):
    Moniker = None
    
    def set_moniker(self, name):
        self.Moniker = name
    
    

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
        
        
        self.remove_country_widgets()
        if not tab_text:
            tab_text = CONTINENTS[0]
            
        for node in self.ConNodes:
            if tab_text == CONTINENTS[0]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Africa:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]],
                           secondary_text=node[NodesInfoKeys[3]],
                           tertiary_text=node[NodesInfoKeys[4]]
                       
                    ))
            elif tab_text == CONTINENTS[1]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Anarctica:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]],
                           secondary_text=node[NodesInfoKeys[3]],
                           tertiary_text=node[NodesInfoKeys[4]]
                       
                    ))
            elif tab_text == CONTINENTS[2]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Asia:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]],
                           secondary_text=node[NodesInfoKeys[3]],
                           tertiary_text=node[NodesInfoKeys[4]]
                       
                    ))
                    
            elif tab_text == CONTINENTS[3]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Europe:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]].lstrip().rstrip(),
                           secondary_text=node[NodesInfoKeys[3]].lstrip().rstrip(),
                           tertiary_text=node[NodesInfoKeys[4]].lstrip().rstrip()
                       
                    ))
            elif tab_text == CONTINENTS[4]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in NorthAmerica:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]],
                           secondary_text=node[NodesInfoKeys[3]],
                           tertiary_text=node[NodesInfoKeys[4]]
                       
                    ))
            elif tab_text == CONTINENTS[5]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Oceania:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]],
                           secondary_text=node[NodesInfoKeys[3]],
                           tertiary_text=node[NodesInfoKeys[4]]
                       
                    ))
                    
            else: 
                if node[NodesInfoKeys[4]].lstrip().rstrip() in SouthAmerica:
                    self.screen.ids.container.add_widget(ThreeLineAvatarIconListItem( 
                           text=node[NodesInfoKeys[0]],
                           secondary_text=node[NodesInfoKeys[3]],
                           tertiary_text=node[NodesInfoKeys[4]]
                       
                    ))
           
    def remove_country_widgets(self):
        rows = [i for i in self.screen.ids.container.children]
        for row1 in rows:
            self.screen.ids.container.remove_widget(row1)
            
            
    def on_start(self):
        
        
        self.on_tab_switch(
            None,
            None,
            None,
            self.screen.ids.android_tabs.ids.layout.children[-1].text
        )


Palette().run()