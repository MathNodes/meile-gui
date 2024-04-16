from btcpay import BTCPayClient
import pymysql
import pickle
from os import path,environ
from fiat.stripe_pay import scrtsxx
from time import sleep
import sys
from requests.auth import HTTPBasicAuth

class BTCPayDB():
    
    def connDB(self): 
        db = pymysql.connect(host=scrtsxx.HOST,
                             port=scrtsxx.PORT,
                             user=scrtsxx.USERNAME,
                             passwd=scrtsxx.PASSWORD,
                             db=scrtsxx.DB,
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor
                             )
    
        return db
    
    def get_btcpay_client(self, db):
        c = db.cursor()
        
        query = "SELECT btcpay_client FROM btcpay;"
        c.execute(query)
        
        return c.fetchone()['btcpay_client']
        
        
    def get_remote_btcpay_client(self):
        SERVER_ADDRESS = scrtsxx.SERVER_ADDRESS
        API            = scrtsxx.BTCPAY_ENDPOINT
        USERNAME       = scrtsxx.USERNAME
        PASSWORD       = scrtsxx.PASSWORD
        Request = HTTPRequests.MakeRequest()
        
        try:
            btcpayload = http.get(SERVER_ADDRESS + API, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        except:
            print("ERR0R")
            return None
        
        return btcpayload.json()[0]
        
        
    def pickle_btc_client(self, obj):
        
        if path.isfile(path.join(CACHEDIR, BTCPAYOBJ)):
            raise FileExistsError
            return
        with open(path.join(CACHEDIR, BTCPAYOBJ), 'wb') as btcpay_client:
            pickle.dump(obj,btcpay_client)
    
    def unpickle_btc_client(self, obj):
        return pickle.loads(obj)
        
    def store_pickle_btcpay_in_db(self, db):
        if path.isfile(path.join(CACHEDIR, BTCPAYOBJ)):
            with open(path.join(CACHEDIR, BTCPAYOBJ), 'rb') as btcpay_pickle:
                client_data = btcpay_pickle.read()
                
                query = '''INSERT INTO btcpay (btcpay_client) VALUES (%s);'''
                c = db.cursor()
                
                c.execute(query, (client_data,))
                db.commit()
            btcpay_pickle.close()
        else:
            raise FileNotFoundError
        
     