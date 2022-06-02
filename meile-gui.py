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
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import ThreeLineAvatarIconListItem, ImageLeftWidget
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, SlideTransition
from kivyoav.delayed import delayable

from kivy.clock import Clock



import threading
from src.cli.sentinel import get_nodes, NodesInfoKeys
import awoc
from time import sleep
our_world = awoc.AWOC()

CONTINENTS   = our_world.get_continents_list()
Africa       = our_world.get_countries_list_of(CONTINENTS[0])
Anarctica    = our_world.get_countries_list_of(CONTINENTS[1])
Asia         = our_world.get_countries_list_of(CONTINENTS[2])
Europe       = our_world.get_countries_list_of(CONTINENTS[3])
NorthAmerica = our_world.get_countries_list_of(CONTINENTS[4])
Oceania      = our_world.get_countries_list_of(CONTINENTS[5])
SouthAmerica = our_world.get_countries_list_of(CONTINENTS[6])

ConNodes = []
SentinelValue = False

from kivy.factory import Factory

from kivymd.app import MDApp

#class MainWindow(Screen):
    
#    pass

#class PreLoadWindow(Screen):
#    pass

class WindowManager(ScreenManager):
    pass


class Tab(MDBoxLayout, MDTabsBase):
    pass

class MD3Card(MDCard):
    dialog = None
    
    def set_moniker(self, name):
        self.Moniker = name
        
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Subscribe to Node?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.closeDialog,
                    ),
                    MDRaisedButton(
                        text="SUBSCRIBE",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.subscribeME
                    ),
                ],
            )
        self.dialog.open()

    def closeDialog(self, inst):
        self.dialog.dismiss()
        
    def subscribeME(self, inst):
        self.dialog.dismiss()
        print("SUBSCRIBED!")

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


class MainWindow(Screen):
    title = "Meile dVPN"
    
    def __init__(self, **kwargs):
        #Builder.load_file("./src/kivy/meile.kv")
        super(MainWindow, self).__init__()
        Clock.schedule_once(self.build, 2)

        

    def build(self, dt):
        print("ADDING TABS")
        for name_tab in CONTINENTS:
            tab = Tab(text=name_tab)
            self.manager.get_screen("main").ids.android_tabs.add_widget(tab)
        
        print("ON START")
        '''
        self.on_tab_switch(
            None,
            None,
            None,
            self.manager.get_screen("main").ids.android_tabs.ids.layout.children[-1].text
        )
        '''
    def add_rv_data(self, node, flagloc):
        print("Adding Data...")
        floc = "./src/imgs/"
        speed = node[NodesInfoKeys[5]].lstrip().rstrip().split('+')
        
        if "MB" in speed[0]:
            speed[0] = float(speed[0].replace("MB", ''))
        elif "KB" in speed[0]:
            speed[0] = float(float(speed[0].replace("KB", '')) / 1024 )
        else:
            speed[0] = 10
            
        if "MB" in speed[1]:
            speed[1] = float(speed[1].replace("MB", ''))
        elif "KB" in speed[1]:
            speed[1] = float(float(speed[1].replace("KB", '')) / 1024 )
        else:
            speed[1] = 10
        
        total = float(speed[0] + speed[1])
        if total >= 200:
            speedimage = floc + "fast.png"
        elif 100 <= total < 200:
            speedimage = floc + "fastavg.png"
        elif 50 <= total < 100:
            speedimage = floc + "slowavg.png"
        else:
            speedimage = floc + "slow.png"
        self.manager.get_screen("main").ids.rv.data.append(
            {
                "viewclass": "MD3Card",
                "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                "moniker2_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                "moniker3_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                "moniker4_text" : node[NodesInfoKeys[1]].lstrip().rstrip(),
                "speed_image"   : speedimage,
                "source_image" : flagloc
                
            },
        )
        
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        print("ON TAB SWITCCH")
        print(ConNodes)
        rv = RV()
        floc = "./src/imgs/"
        self.manager.get_screen("main").ids.rv.data = []

        if not tab_text:
            tab_text = CONTINENTS[0]
            
        for node in ConNodes:
            if tab_text == CONTINENTS[0]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Africa:
                    
                    #rv.populate_rv(node)
                    print("ADDING AFRICA")
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    self.add_rv_data(node, flagloc)
        
                    
            elif tab_text == CONTINENTS[1]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Anarctica:
                    print("ADDING ANTARCTICA")
                       #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
                    #rv.populate_rv(node)
            elif tab_text == CONTINENTS[2]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Asia:
                    print("ADDING ASIA")
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == CONTINENTS[3]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Europe:
                    print("ADDING EUROPE")
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == CONTINENTS[4]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in NorthAmerica:
                    print("ADDING NA")
                      #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == CONTINENTS[5]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in Oceania:
                    print("ADDING OCEANIA")
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            else: 
                if node[NodesInfoKeys[4]].lstrip().rstrip() in SouthAmerica:
                    print("ADDING SA")
                    #rv.populate_rv(node)
                    iso2 = our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
                  
            



def GetSentinelNodes(dt):
    print("Getting Nodes...")
    global ConNodes
    ConNodes = get_nodes()
    print("Nodes begotten and not made")
    global SentinelValue
    SentinelValue = True
class PreLoadWindow(Screen):   
    StatusMessages = ["Calculating π...", "Squaring the Circle...", "Solving the Riemann Hypothesis...", "Done"]
    title = "Meile dVPN"
    k = 0
    j = 0
    go_button = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(PreLoadWindow, self).__init__()
        
        # Schedule the functions to be called every n seconds
        Clock.schedule_once(GetSentinelNodes, 6)
        Clock.schedule_interval(self.update_status_text, 1)
        
        
        
        

    @delayable
    def update_status_text(self, dt):
        go_button = self.manager.get_screen('preload').ids.go_button


        yield 1.0
        
        if self.j == 2:
            self.manager.get_screen('preload').status_text = self.StatusMessages[3]
            go_button.opacity = 1
            go_button.disabled = False

            return
            
        if self.k == 3:
            self.k = 0
            self.j += 1
        else:
            self.manager.get_screen('preload').status_text = self.StatusMessages[self.k]
            self.k += 1
            

        
        
        
 
    def switch_window(self):
        app.root.transition = SlideTransition(direction = "up")
        app.root.current = "main"

class MyMainApp(MDApp):
    title = "Meile dVPN"

    def build(self):
        kv = Builder.load_file("./src/kivy/meile.kv")

        manager = WindowManager()
        manager.add_widget(PreLoadWindow(name='preload'))
        manager.add_widget(MainWindow(name='main'))
        return manager
    
   


if __name__ == "__main__":
    app = MyMainApp()
    app.run()
#Palette().run()