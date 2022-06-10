from src.geography.continents import OurWorld
from src.ui.interfaces import Tab
from src.typedef.win import WindowNames
from src.cli.sentinel import GetSentinelNodes, NodesInfoKeys
import src.main.main as Meile
from src.ui.widgets import MD3Card
from src.cli.wallet import HandleWalletFunctions
 
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivyoav.delayed import delayable
from kivy.properties import ObjectProperty


class WalletRestore(Screen):
    screemanager = ObjectProperty()
    
    dialog = None
    def restore_wallet_from_seed_phrase(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Seed: %s \n\nName: %s \nPassword: %s" %
                
                 (self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text,
                 self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text,
                 self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text
                 ),
                
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        text_color=Meile.app.theme_cls.primary_color,
                        on_release=self.cancel,
                    ),
                    MDRaisedButton(
                        text="Restore",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.wallet_restore
                    ),
                ],
            )
            self.dialog.open()
            
    def set_previous_screen(self, inst):
        if self.screemanager.current != WindowNames.MAIN_WINDOW:
            self.screemanager.transition.direction = "down"
            self.screemanager.current = self.screemanager.previous()
        
    def cancel(self):
        self.dialog.dismiss()
        
    def wallet_restore(self, inst):
        self.dialog.dismiss()
        seed_phrase  = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.seed.ids.seed_phrase.text
        wallet_name = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.name.ids.wallet_name.text
        keyring_passphrase = self.manager.get_screen(WindowNames.WALLET_RESTORE).ids.password.ids.wallet_password.text
        if seed_phrase:
            Wallet = HandleWalletFunctions.create(self, wallet_name, keyring_passphrase, seed_phrase)
        else:
            Wallet = HandleWalletFunctions.create(self, wallet_name, keyring_passphrase, None)
        
        self.dialog = MDDialog(
                text="Wallet created!\n\n Seed: %s\nAddress: %s\nWallet Name: %s\nWallet Password: %s" %
                
                 (Wallet['seed'],
                 Wallet['address'],
                 wallet_name,
                 keyring_passphrase
                 ),
                
                buttons=[
                    MDRaisedButton(
                        text="I saved this",
                        theme_text_color="Custom",
                        text_color=(1,1,1,1),
                        on_release= self.set_previous_screen
                    ),
                ],
            )
        self.dialog.open()
        

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
        go_button = self.manager.get_screen(WindowNames.PRELOAD).ids.go_button


        yield 1.0
        
        if self.j == 2:
            self.manager.get_screen(WindowNames.PRELOAD).status_text = self.StatusMessages[3]
            go_button.opacity = 1
            go_button.disabled = False

            return
            
        if self.k == 3:
            self.k = 0
            self.j += 1
        else:
            self.manager.get_screen(WindowNames.PRELOAD).status_text = self.StatusMessages[self.k]
            self.k += 1
            

        
        
        
 
    def switch_window(self):
        
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = WindowNames.MAIN_WINDOW



class MainWindow(Screen):
    title = "Meile dVPN"
    dialog = None
    def __init__(self, **kwargs):
        #Builder.load_file("./src/kivy/meile.kv")
        super(MainWindow, self).__init__()
        Clock.schedule_once(self.build, 2)

        

    def build(self, dt):
        print("ADDING TABS")
        for name_tab in OurWorld.CONTINENTS:
            tab = Tab(text=name_tab)
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.add_widget(tab)
        
        print("ON START")
        '''
        self.on_tab_switch(
            None,
            None,
            None,
            self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.android_tabs.ids.layout.children[-1].text
        )
        '''
        
        
    def wallet_dialog(self):
        
        # Add a check here to see if they already have a wallet available in
        # the app and proceed to the wallet screen
        # o/w proceed to wallet_create or wallet_restore
        #
        # Eventually, I'd like to add multiple wallet support. 
        # That will be after v1.0
        
        
        self.dialog = MDDialog(
            text="Wallet Restore/Create",
            buttons=[
                MDFlatButton(
                    text="Create",
                    theme_text_color="Custom",
                    text_color=Meile.app.theme_cls.primary_color,
                    on_release=self.wallet_create,
                ),
                MDRaisedButton(
                    text="Restore",
                    theme_text_color="Custom",
                    text_color=(1,1,1,1),
                    on_release= self.wallet_restore
                ),
            ],
        )
        self.dialog.open()
        
    def wallet_restore(self, inst):
        self.dialog.dismiss()
        self.switch_window(WindowNames.WALLET_RESTORE)
        
    
    def wallet_create(self, inst):
        pass
        
    def add_rv_data(self, node, flagloc):
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
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data.append(
            {
                "moniker_text": node[NodesInfoKeys[0]].lstrip().rstrip(),
                "price_text" : node[NodesInfoKeys[3]].lstrip().rstrip(),
                "country_text" : node[NodesInfoKeys[4]].lstrip().rstrip(),
                "address_text" : node[NodesInfoKeys[1]].lstrip().rstrip(),
                "speed_text" : node[NodesInfoKeys[5]].lstrip().rstrip(),
                "speed_image"   : speedimage,
                "source_image" : flagloc
                
            },
        )
        
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tabs_label, tab_text):
        from src.cli.sentinel import ConNodes
        
        floc = "./src/imgs/"
        self.manager.get_screen(WindowNames.MAIN_WINDOW).ids.rv.data = []

        if not tab_text:
            tab_text = OurWorld.CONTINENTS[0]

        for node in ConNodes:
            #print(node)
            if tab_text == OurWorld.CONTINENTS[0]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Africa:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    self.add_rv_data(node, flagloc)
            elif tab_text == OurWorld.CONTINENTS[1]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Anarctica:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == OurWorld.CONTINENTS[2]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Asia:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == OurWorld.CONTINENTS[3]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Europe:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == OurWorld.CONTINENTS[4]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.NorthAmerica:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            elif tab_text == OurWorld.CONTINENTS[5]:
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.Oceania:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
            else: 
                if node[NodesInfoKeys[4]].lstrip().rstrip() in OurWorld.SouthAmerica:
                    
                    iso2 = OurWorld.our_world.get_country_ISO2(node[NodesInfoKeys[4]].lstrip().rstrip()).lower()
                    flagloc = floc + iso2 + ".png"
                    
                    self.add_rv_data(node, flagloc)
                  
            
    def switch_window(self, window):
        Meile.app.root.transition = SlideTransition(direction = "up")
        Meile.app.root.current = window

