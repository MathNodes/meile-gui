from kivy.properties import BooleanProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.recycleview import RecycleView


from src.cli.sentinel import NodesInfoKeys

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
