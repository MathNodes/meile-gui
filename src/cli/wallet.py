import pexpect
import json
import requests
import psutil
import binascii
from time import sleep 
from os import path, remove

from json.decoder import JSONDecodeError 

from conf.meile_config import MeileGuiConfig
from typedef.konstants import IBCTokens 
from typedef.konstants import ConfParams 
from typedef.konstants import HTTParams
from adapters import HTTPRequests
from cli.v2ray import V2RayHandler

from cosmpy.aerial.client import LedgerClient, NetworkConfig
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from sentinel_protobuf.sentinel.subscription.v1.msg_pb2 import MsgCancelRequest, MsgCancelResponse
from cosmpy.aerial.tx import Transaction
from cosmpy.aerial.tx_helpers import TxResponse
from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")
v2ray_tun2routes_connect_bash = MeileConfig.resource_path("../bin/routes.sh")


class HandleWalletFunctions():
    
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        SCMD = '%s keys add "%s" -i --keyring-backend file --keyring-dir %s' % (sentinelcli, wallet_name, ConfParams.KEYRINGDIR)
        DUPWALLET = False 
        ofile =  open(ConfParams.WALLETINFO, "wb")    
        
        ''' Process to handle wallet in sentinel-cli '''
        child = pexpect.spawn(SCMD)
        child.logfile = ofile
        
        # > Enter your bip39 mnemonic, or hit enter to generate one.
        child.expect(".*")
        
        # Send line to generate new, or send seed_phrase to recover
        if seed_phrase:
            child.sendline(seed_phrase)
        else:
            child.sendline()
            
        child.expect(".*")
        child.sendline()
        child.expect("Enter .*")
        child.sendline(keyring_passphrase)
        try:
            index = child.expect(["Re-enter.", "override.", pexpect.EOF])
            if index == 0:
                child.sendline(keyring_passphrase)
                child.expect(pexpect.EOF)
            elif index ==1:
                child.sendline("N")
                print("NO Duplicating Wallet..")
                DUPWALLET = True
                child.expect(pexpect.EOF)
                ofile.flush()
                ofile.closae()
                remove(ConfParams.WALLETINFO)
                return None
            else:
                child.expect(pexpect.EOF)
        except Exception as e:
            child.expect(pexpect.EOF)
            print("passing: %s" % str(e))
            pass
          
        ofile.flush()
        ofile.close()
      
        if not DUPWALLET:
            with open(ConfParams.WALLETINFO, "r") as dvpn_file:
                WalletDict = {}   
                lines = dvpn_file.readlines()
                lines = [l for l in lines if l != '\n']
                for l in lines:
                    if "address:" in l:
                        WalletDict['address'] = l.split(":")[-1].lstrip().rstrip()
                        
                WalletDict['seed'] = lines[-1].lstrip().rstrip()
                dvpn_file.close()
                remove(ConfParams.WALLETINFO)
                return WalletDict
    
        else:
            remove(ConfParams.WALLETINFO)
            return None

    def subscribe(self, KEYNAME, NODE, DEPOSIT):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
    
        ofile =  open(ConfParams.SUBSCRIBEINFO, "wb")
            
        if not KEYNAME:
            return (False, 1337)
        
        SCMD = "%s tx subscription subscribe-to-node --yes --keyring-backend file --keyring-dir %s --gas-prices 0.1udvpn --chain-id sentinelhub-2 --node %s --from '%s' '%s' %s"  % (sentinelcli, ConfParams.KEYRINGDIR, HTTParams.RPC, KEYNAME, NODE, DEPOSIT)    
        try:
            child = pexpect.spawn(SCMD)
            child.logfile = ofile
            
            child.expect(".*")
            child.sendline(PASSWORD)
            child.expect(pexpect.EOF)
            
            ofile.flush()
            ofile.close()
        except pexpect.exceptions.TIMEOUT:
            return (False, 1415)
        
        return self.ParseSubscribe(self)
              
    def ParseSubscribe(self):
        SUBJSON = False
        with open(ConfParams.SUBSCRIBEINFO, 'r') as sub_file:
                lines = sub_file.readlines()
                for l in lines:
                    if "Error" in l:
                        return(False, l)

                for l in lines:
                    try:
                        tx_json = json.loads(l)
                        SUBJSON = True
                    except Exception as e:
                        continue
                if SUBJSON:            
                    if tx_json['data']:
                        try: 
                            sub_id = tx_json['logs'][0]['events'][4]['attributes'][0]['value']
                            if sub_id:
                                #remove(ConfParams.SUBSCRIBEINFO)
                                return (True,0)
                            else:
                                #remove(ConfParams.SUBSCRIBEINFO)
                                return (False,2.71828) 
                        except:
                            #remove(ConfParams.SUBSCRIBEINFO)
                            return (False, 3.14159)
                    elif 'insufficient' in tx_json['raw_log']:
                        #remove(ConfParams.SUBSCRIBEINFO)
                        return (False, tx_json['raw_log'])
                else:
                    return(False, "Error loading JSON")
                
    def unsubscribe(self, subId):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        if not KEYNAME:
            return {'hash' : "0x0", 'success' : False, 'message' : "ERROR Retrieving Keyname"}

        ofile = open(ConfParams.USUBSCRIBEINFO, "wb")

        unsubCMD = "%s keys export --unarmored-hex --unsafe --keyring-backend file --keyring-dir %s %s" % (sentinelcli,  ConfParams.KEYRINGDIR, KEYNAME)

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
            return {'hash' : "0x0", 'success' : False, 'message' : "ERROR: pexpect timeout"}

        privkey_hex = self.ParseUnSubscribe()
        return self.grpc_unsubscribe(privkey_hex, subId)

    def grpc_unsubscribe(self, privkey, subId):
        tx_success = False
        tx_hash    = "0x0"

        cfg = NetworkConfig(
            chain_id=ConfParams.CHAINID,
            url=HTTParams.GRPC,
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
            session_data = self.check_active_subscriptions(address)
        except Exception as e:
            print("Error getting sessions")
            return {'hash' : tx_hash, 'success' : tx_success, 'message' : "ERROR retrieving sessions. Please try again later."}
        try: 
            if not session_data['session']:  
                tx = Transaction()
                tx.add_message(MsgCancelRequest(frm=str(address), id=int(subId)))

                tx = prepare_and_broadcast_basic_transaction(client, tx, wallet)
                tx.wait_to_complete()

                tx_hash     = tx._tx_hash
                tx_response = tx._response.is_successful()
                tx_height   = int(tx._response.height)

                print("Hash: %s" % str(tx_hash))
                print("Response: %s" % tx_response)
                print("Height: %d" % int(tx._response.height))

                if tx_response:
                    tx_success = tx_response
                    message    = "Unsubscribe from Subscription ID: %s, was successful at Height: %d" % (subId, tx_height )

            else:
                message = 'Found active session. Due to blockchain limitations we cannot cancel a subscription while there is a pending session.\n' + 'STATUS: ' + session_data['data']['status'] + ',' + session_data['data']['status_at']
        except:
            message = "Error parsing or retrieving sessions. Please try again later." 

        return {'hash' : tx_hash, 'success' : tx_success, 'message' : message}

    def check_active_subscriptions(self, address):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        endpoint = HTTParams.APIURL + HTTParams.SESSIONS_API_URL % address

        try:
            r = http.get(endpoint)
            json_data = r.json()

            if len(json_data['sessions']) == 0:
                return {'session' : False, 'data' : None}
            else:
                return {'session' : True, 'data' : { 'status' : json_data['sessions'][0]['status'], 'status_at' : json_data['sessions'][0]['status_at'] } }

        except Exception as e:
            print(str(e))
            return None


    def ParseUnSubscribe(self):
        with open(ConfParams.USUBSCRIBEINFO, 'r') as usubfile:
            lines = usubfile.readlines()
            lines = [l for l in lines if l != '\n']
            for l in lines:
                l.replace('\n','')

        usubfile.close()
        remove(ConfParams.USUBSCRIBEINFO)
        return l            
                
    
    def connect(self, ID, address, type):

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        connCMD = "pkexec env PATH=%s %s connect --home %s --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node %s --gas-prices 0.1udvpn --yes --from '%s' %s %s" % (ConfParams.PATH, sentinelcli, ConfParams.BASEDIR, ConfParams.KEYRINGDIR, HTTParams.RPC, KEYNAME, ID, address)
            
        ofile =  open(ConfParams.CONNECTIONINFO, "wb")    
    
        try:
            child = pexpect.spawn(connCMD)
            child.logfile = ofile
    
            child.expect(".*")
            child.sendline(PASSWORD)
            child.expect(pexpect.EOF)
            
            ofile.flush()
            ofile.close()
        except pexpect.exceptions.TIMEOUT:
            return False
            
        if type == "WireGuard":
            if psutil.net_if_addrs().get("wg99"):
                return {"v2ray_pid" : None,  "result": True}
            else:
                return {"v2ray_pid" : None,  "result": False}
        else: 
            TUNIFACE = False
            V2Ray = V2RayHandler(v2ray_tun2routes_connect_bash + " up")
            V2Ray.start_daemon() 
            sleep(15)

            for iface in psutil.net_if_addrs().keys():
                if "tun" in iface:
                    TUNIFACE = True
                    break
                
            if TUNIFACE:
                v2raydict = {"v2ray_pid" : V2Ray.v2ray_pid, "result": True}
                print(v2raydict) 
                return v2raydict
            else:
                try: 
                    V2Ray.v2ray_script = v2ray_tun2routes_connect_bash + " down"
                    V2Ray.kill_daemon()
                    #V2Ray.kill_daemon()
                    #Tun2Socks.kill_daemon()
                except Exception as e: 
                    print(str(e))
                    
                v2raydict = {"v2ray_pid" : V2Ray.v2ray_pid,  "result": False}
                print(v2raydict)
                return v2raydict

    def get_balance(self, address):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        endpoint = HTTParams.BALANCES_ENDPOINT + address
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        
        try:
            r = http.get(HTTParams.APIURL + endpoint)
            coinJSON = r.json()
        except:
            return None
            
        print(coinJSON)
        try:
            for coin in coinJSON['result']:
                if "udvpn" in coin['denom']:
                    CoinDict['dvpn'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCSCRT in coin['denom']:
                    CoinDict['scrt'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCDEC in coin['denom']:
                    CoinDict['dec'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCATOM in coin['denom']:
                    CoinDict['atom'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCOSMO in coin['denom']:
                    CoinDict['osmo'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
        except Exception as e:
            print(str(e))
            return None
        return CoinDict
    

                
    
        