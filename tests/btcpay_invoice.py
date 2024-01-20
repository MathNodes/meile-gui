from btcpay import BTCPayClient
import pymysql
import pickle
from os import path,environ
import scrtsxx
from time import sleep
import sys


USER             = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
PATH             = environ['PATH']
CACHEDIR         = path.join(path.expanduser('~' + USER), 'CacheServer')
BTCPAYOBJ        = "btcpay_client.obj"
    
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
        
        
if __name__ == '__main__':
    BTCPay = BTCPayDB()
    db = BTCPay.connDB()
    
    pickled_client_data = BTCPay.get_btcpay_client(db)
    print(pickled_client_data)
    
    if pickled_client_data:
        client = BTCPay.unpickle_btc_client(pickled_client_data)
        
    elif path.isfile(path.join(CACHEDIR, BTCPAYOBJ)):
        with open(path.join(CACHEDIR, BTCPAYOBJ), 'rb') as btcobj_fd:
            client_data = btcobj_fd.read()
            client = BTCPay.unpickle_btc_client(client_data)
        btcobj_fd.close()
        try:
            BTCPay.store_pickle_btcpay_in_db(db)
        except Exception as e:
            print(str(e))
            print("Could not store in DB")
            sys.exit(1)      
    else:
        client = BTCPayClient.create_client(host=scrtsxx.BTCPAYSERVER, code=scrtsxx.BTCPayToken)
        try:
            BTCPay.pickle_btc_client(client)
        except FileExistsError:
            print("BTCPay pickled client data file already exists")
            sys.exit(1)
        
        try:
            BTCPay.store_pickle_btcpay_in_db(db)
        except FileNotFoundError:
            print("Error storing the pickeled BTCPay client data")
            sys.exit(1)
        
    buyer = {"name" : "sent1tdgva8fhl9rgawrj2am9sv8prw2h44mc8g3qch", "email" : "freqnik@mathnodes.com", "notify" : True}
    
    new_invoice = client.create_invoice({"price": 2,
                                          "currency": "USD",
                                          "token" : "XMR",
                                          "merchantName" : "Meile dVPN",
                                          "itemDesc" : "Meile Residential Node Subscription Plan",
                                          "notificationEmail" : scrtsxx.BTCPayEmail,
                                          "trasnactionSpeed" : "high",
                                          "buyer" : buyer})
    
    
    print(new_invoice)
    print(new_invoice['url'])
    btcpay_tx_id = new_invoice['id']
    
    
    fetched_invoice = client.get_invoice(btcpay_tx_id)
    
    while fetched_invoice['status'] != "confirmed":
        fetched_invoice = client.get_invoice(btcpay_tx_id)
        print("invoice not yet confirmed....")
        sleep(10)
        
    print("invoice paid!")
        
        
    