import pexpect
from os import path, environ
import requests


import binascii

from cosmpy.aerial.client import LedgerClient, NetworkConfig
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from sentinel_protobuf.sentinel.subscription.v1.msg_pb2 import MsgCancelRequest, MsgCancelResponse
from cosmpy.aerial.tx import Transaction
from cosmpy.aerial.tx_helpers import TxResponse
from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction

USER             = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
KEYRINGDIR       = path.join(path.expanduser('~' + USER), '.meile-gui')
USUBSCRIBEINFO   = path.join(KEYRINGDIR, "unsubscribe.infos")
sentinelcli      = path.join(KEYRINGDIR, 'bin/sentinelcli')

SESSIONS_API_URL = 'https://api.sentinel.mathnodes.com/sentinel/accounts/%s/sessions'

def unsubscribe(keyname, PASSWORD, subId):
        
    ofile =  open(USUBSCRIBEINFO, "wb")    
    if not keyname:
        return (False, 1337)
    
    unsubCMD = "%s keys export --unarmored-hex --unsafe --keyring-backend file --keyring-dir %s %s" % (sentinelcli,  KEYRINGDIR, keyname)
    
    try:
        child = pexpect.spawn(unsubCMD)
        child.logfile = ofile
        
        child.expect(".*")
        child.sendline("y")
        child.expect("Enter*")
        child.sendline(PASSWORD)
        child.expect(pexpect.EOF)
        
        ofile.flush()
        ofile.close()
    except pexpect.exceptions.TIMEOUT:
        return (False,1415)
    
    privkey_hex = ParseUnSubscribe()
    return grpc_unsubscribe(privkey_hex, subId)

def grpc_unsubscribe(privkey, subId):
    tx_success = False
    tx_hash    = "0x0"
    
    cfg = NetworkConfig(
        chain_id="sentinelhub-2",
        url="grpc+http://aimokoivunen.mathnodes.com:9090/",
        fee_minimum_gas_price=0.4,
        fee_denomination="udvpn",
        staking_denomination="udvpn",
        )

    client = LedgerClient(cfg)    
    
    priv_key_bytes = binascii.unhexlify(bytes(privkey.rstrip().lstrip(), encoding="utf8"))
    
    wallet = LocalWallet(PrivateKey(priv_key_bytes), prefix="sent")
    address = wallet.address()
    
    print(f"Address: {address},\nSubscription ID: {subId}")
    print("Checking for active sessions...")
    
    try: 
        session_data = check_active_subscriptions(address)
    except Exception as e:
        print("Error getting sessions")
        return {'hash' : "ERROR Retrieving Sessions", 'success' : tx_success}
    
    if not session_data['session']:
        answer = input("No active sessions... Proceed with unsubscribe [y/n]:")
        
        if answer.upper() == "Y":
        
            tx = Transaction()
            tx.add_message(MsgCancelRequest(frm=str(address), id=subId))
            
            tx = prepare_and_broadcast_basic_transaction(client, tx, wallet)
            tx.wait_to_complete()
            
            tx_hash = tx._tx_hash
            tx_response = tx._response.is_successful()
            
            print("Hash: %s" % str(tx_hash))
            print("Response: %s" % tx_response)
            print("Height: %d" % int(tx._response.height))
            
            if tx_response:
                tx_success = tx_response
        else:
            print("Okay")
            
    else:
        tx_hash = 'STATUS: ' + session_data['data']['status'] + ',' + session_data['data']['status_at']
        
    return {'hash' : tx_hash, 'success' : tx_success}
    
def check_active_subscriptions(address):
    try:
        r = requests.get(SESSIONS_API_URL % address)
        json_data = r.json()
        if len(json_data['sessions']) == 0:
            return {'session' : False, 'data' : None}
        else:
            return {'session' : True, 'data' : { 'status' : json_data['sessions'][0]['status'], 'status_at' : json_data['sessions'][0]['status_at'] } }
        
    except Exception as e:
        print(str(e))
        raise Exception("ERORR: requests or json error")
        return None
        
    
def ParseUnSubscribe():
    with open(USUBSCRIBEINFO, 'r') as usubfile:
        lines = usubfile.readlines()
        lines = [l for l in lines if l != '\n']
        for l in lines:
            l.replace('\n','')
        
        return l
        
        
if __name__ == "__main__":
    tx_data = unsubscribe("Macbook-M1", "blargy101", 1792)
    
    if tx_data['success']:
        print("Unsubscribe successful.")
        print("TX: %s" % str(tx_data['hash']))
        print("https://www.mintscan.io/sentinel/txs/%s" % str(tx_data['hash']).upper())
        
    else: 
        print("Current there is an active session. We cannot unsubscribe to nodes during active sessions - this is a blockchain limitation. Please close this session or wait for it to expire: ~2hrs")
        print(str(tx_data['hash']))
        
        