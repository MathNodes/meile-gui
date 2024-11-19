from btcpay import BTCPayClient
import pickle
from os import path,environ
from time import sleep
import sys
from requests.auth import HTTPBasicAuth

from adapters import HTTPRequests
from fiat.stripe_pay.dist import scrtsxx
from conf.meile_config import MeileGuiConfig
class BTCPayDB():
    
    def connDB(self): 
        '''
        db = pymysql.connect(host=scrtsxx.HOST,
                             port=scrtsxx.PORT,
                             user=scrtsxx.USERNAME,
                             passwd=scrtsxx.PASSWORD,
                             db=scrtsxx.DB,
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor
                             )
    
        return db
        '''
        return None
    
    '''
    def get_btcpay_client(self, db):
        c = db.cursor()
        
        query = "SELECT btcpay_client FROM btcpay;"
        c.execute(query)
        
        return c.fetchone()['btcpay_client']
        
    '''    
    def get_remote_btcpay_client(self):
        MeileConfig = MeileGuiConfig()
        CONFIG = MeileConfig.read_configuration(MeileGuiConfig.CONFFILE)
        MNAPI = CONFIG['network'].get('mnapi', HTTParams.SERVER_URL)
        SERVER_ADDRESS = scrtsxx.SERVER_ADDRESS if "aimokoivunen" in scrtsxx.SERVER_ADDRESS else MNAPI
        API            = scrtsxx.BTCPAY_ENDPOINT
        USERNAME       = scrtsxx.USERNAME
        PASSWORD       = scrtsxx.PASSWORD
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        try:
            btcpayload = http.get(SERVER_ADDRESS + API, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        except:
            print("ERR0R")
            return None
        
        return btcpayload.content
        
        
    def pickle_btc_client(self, obj):
        
        if path.isfile(path.join(CACHEDIR, BTCPAYOBJ)):
            raise FileExistsError
            return
        with open(path.join(CACHEDIR, BTCPAYOBJ), 'wb') as btcpay_client:
            pickle.dump(obj,btcpay_client)
    
    def unpickle_btc_client(self, obj):
        return pickle.loads(obj)
