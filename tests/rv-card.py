from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.properties import ListProperty, StringProperty

from kivymd.color_definitions import colors
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard


demo = '''
<Root@MDBoxLayout>
    orientation: 'vertical'

    MDToolbar:
        title: app.title

    MDTabs:
        id: android_tabs
        on_tab_switch: app.on_tab_switch(*args)
        size_hint_y: None
        height: "48dp"
        tab_indicator_anim: False

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


<ItemColor>
    size_hint_y: None
    height: "42dp"

    MDLabel:
        text: root.text
        halign: "center"



<MD3Card>
    
    orientation: "vertical"
    height: node_box.height 
    focus_behavior: True
    ripple_behavior: True

    moniker_text: "BLARGLY"
    moniker2_text: "GLARGLY"
    source_image: "CUNTS"
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
        

        
    MDSeparator:


<Tab>
'''

from kivy.factory import Factory

from kivymd.app import MDApp


class Tab(MDBoxLayout, MDTabsBase):
    pass


class ItemColor(MDBoxLayout):
    text = StringProperty()
    color = ListProperty()


class MD3Card(MDCard):
    moniker_text = StringProperty()
    
class Palette(MDApp):
    title = "Colors definitions"

    def build(self):
        Builder.load_string(demo)
        self.screen = Factory.Root()

        for name_tab in colors.keys():
            tab = Tab(text=name_tab)
            self.screen.ids.android_tabs.add_widget(tab)
        return self.screen

    def on_tab_switch(
        self, instance_tabs, instance_tab, instance_tabs_label, tab_text
    ):
        self.screen.ids.rv.data = []
        if not tab_text:
            tab_text = 'Red'
        old_value_color = "SHITMYFfuck"
        for value_color in colors[tab_text]:
            from kivymd.uix.card import MDCard
            self.screen.ids.rv.data.append(
                {
                    "viewclass": "MD3Card",
                    "md_bg_color": get_color_from_hex(colors[tab_text][value_color]),
                    "moniker_text": value_color,
                    "moniker2_text" : old_value_color,
                    "source_image" : "./src/cli/at.png"
                    
                },
            )
            old_value_color = value_color

    def on_start(self):
        self.on_tab_switch(
            None,
            None,
            None,
            self.screen.ids.android_tabs.ids.layout.children[-1].text,
        )


Palette().run()
