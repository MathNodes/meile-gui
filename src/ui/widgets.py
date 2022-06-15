from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.recycleview import RecycleView

from urllib3.exceptions import InsecureRequestWarning
import requests

from src.cli.sentinel import NodesInfoKeys
from src.ui.interfaces import SubscribeContent


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

class NodeRV(RecycleView):    
    pass
class RecycleViewRow(MDCard):
    text = StringProperty()    
    dialog = None
    
    def get_city_of_node(self, naddress):   
        APIURL   = "https://api.sentinel.mathnodes.com"

        endpoint = "/nodes/" + naddress.lstrip().rstrip()
        print(APIURL + endpoint)
        r = requests.get(APIURL + endpoint)
        remote_url = r.json()['result']['node']['remote_url']
        r = requests.get(remote_url + "/status", verify=False)
        print(remote_url)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        NodeInfoJSON = r.json()
        NodeInfoDict = {}
        
        NodeInfoDict['connected_peers'] = NodeInfoJSON['result']['peers']
        NodeInfoDict['max_peers']       = NodeInfoJSON['result']['qos']['max_peers']
        NodeInfoDict['version']         = NodeInfoJSON['result']['version']
        NodeInfoDict['city']            = NodeInfoJSON['result']['location']['city']




        if not self.dialog:
            self.dialog = MDDialog(
                text='''
City: %s
Connected Peers:  %s  
Max Peers: %s  
Node Version: %s 
                    ''' % (NodeInfoDict['city'], NodeInfoDict['connected_peers'],NodeInfoDict['max_peers'],NodeInfoDict['version']),
  
                buttons=[
                    MDRaisedButton(
                        text="OKAY",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.closeDialog,
                    )
                ],
            )
        self.dialog.open()

    def subscribe_to_node(self, price, naddress, moniker):
        subscribe_dialog = SubscribeContent(price)
        
        if not self.dialog:
            self.dialog = MDDialog(
                title="Address:",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        self.dialog.open()
        
        
    def closeDialog(self, inst):
        self.dialog.dismiss()
        self.dialog = None
        
   
class RecycleViewSubRow(MDCard):
    text = StringProperty()
    dialog = None
    
        
    def get_data_used(self, allocated, consumed):
        try:         
            allocated = float(allocated.replace('GB',''))
            if "MB" in consumed:
                consumed = float(float(consumed.replace('MB', '')) / 1024)
            else:
                consumed  = float(consumed.replace('GB', ''))
                
            return float(float(consumed/allocated)*100)
        except Exception as e:
            print(str(e))
            return float(50)
      
    

# In case I go for word wrapping bigger textfield.
'''
class MySeedBox(MDTextFieldRect):

    def insert_text(self, substring, from_undo=False):

        line_length = 65
        seq = ' '.join(substring.split())
        
        if len(seq) > line_length:
            seq = '\n'.join([seq[i:i+line_length] for i in range(0, len(seq), line_length)])

        return super(MySeedtBox, self).insert_text(seq, from_undo=from_undo)
'''
