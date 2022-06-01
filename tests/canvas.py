from kivy.lang import Builder

import awoc
from kivy.factory import Factory

from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout

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
            source: "../src/imgs/logo.png"
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
        

        
    MDSeparator:


'''
class Tab(MDBoxLayout, MDTabsBase):
    pass


class Palette(MDApp):
    title = "Meile dVPN"
    ConNodes = []
    
    def build(self):
        Builder.load_string(canvas)
        self.screen = Factory.Root()
        
        for name_tab in CONTINENTS:
            tab = Tab(text=name_tab)
            self.screen.ids.android_tabs.add_widget(tab)
        
        
        return self.screen
    
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        return
    
    def on_start(self):
        
        
        self.on_tab_switch(
            None,
            None,
            None,
            self.screen.ids.android_tabs.ids.layout.children[-1].text
        )

Palette().run()