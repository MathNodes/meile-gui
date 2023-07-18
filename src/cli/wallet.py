from os import path, remove, chdir, getcwd
from time import sleep
import wexpect
import json
import requests
import sys
import os
import psutil
import binascii

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

MeileConfig  = MeileGuiConfig()
sentinelcli  = path.join(MeileConfig.BASEBINDIR, 'sentinelcli.exe')
sentinelcli  = sentinelcli.replace('\\','/')
gsudo        = path.join(MeileConfig.BASEBINDIR, 'gsudo.exe')
v2ray_tun2routes_connect_bash = MeileConfig.resource_path("../bin/routes.sh")

class HandleWalletFunctions():
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', 'https://rpc.mathnodes.com:443')
        
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        #sentinelcli = sentinelcli.replace('\\','\\\\')
        #rsentinelcli = sentinelcli.encode('unicode_escape')
        SCMD = '%s keys add "%s" -i --keyring-backend file --keyring-dir %s' % (sentinelcli, wallet_name, ConfParams.KEYRINGDIR)
        DUPWALLET = False 
        
        ofile =  open(ConfParams.WALLETINFO, "w")    
        
        ''' Process to handle wallet in sentinel-cli '''
        #chdir(MeileConfig.BASEBINDIR)
        real_executable = sys.executable
        try:
            if sys._MEIPASS is not None:
                sys.executable = os.path.join(sys._MEIPASS, "wexpect", "wexpect.exe")
        except AttributeError:
            pass
        child = wexpect.spawn(SCMD)
        sys.executable = real_executable
        
        
        # > Enter your bip39 mnemonic, or hit enter to generate one.
        child.expect(".*")
        
        # Send line to generate new, or send seed_phrase to recover
        if seed_phrase:
            child.sendline(seed_phrase)
        else:
            child.sendline()
        
        
        ofile.write(str(child.after)  + '\n')    
        child.expect(".*")
        child.sendline()
        ofile.write(str(child.after)  + '\n')
        child.expect("Enter .*")
        child.sendline(keyring_passphrase)
        ofile.write(str(child.after)  + '\n')
        try:
            index = child.expect(["Re-enter.", "override.", wexpect.EOF])
            if index == 0:
                child.sendline(keyring_passphrase)
                ofile.write(str(child.after)  + '\n')
                child.expect(wexpect.EOF)
                ofile.write(str(child.before) + '\n')
            elif index ==1:
                child.sendline("N")
                ofile.write(str(child.after)  + '\n')
                print("NO Duplicating Wallet..")
                DUPWALLET = True
                child.expect(wexpect.EOF)
                ofile.write(str(child.before) + '\n')
                ofile.flush()
                ofile.close()
                remove(ConfParams.WALLETINFO)
                return None
            else:
                child.expect(wexpect.EOF)
                ofile.write(str(child.before) + '\n')
                
        except Exception as e:
            child.expect(wexpect.EOF)
            ofile.write(str(child.before) + '\n')
            print("passing: %s" % str(e))
            pass
        
        
        ofile.flush()
        ofile.close()
      
        #chdir(MeileConfig.BASEDIR)
     
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
    
        ofile =  open(ConfParams.SUBSCRIBEINFO, "w")
            
        if not KEYNAME:
            return (False, 1337)
        
        SCMD = "%s tx subscription subscribe-to-node --yes --gas-prices 0.3udvpn --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node %s --from '%s' '%s' %s"  % (sentinelcli, ConfParams.KEYRINGDIR, self.RPC, KEYNAME, NODE, DEPOSIT)    
        try:
            
            ''' 
            This is the needed work-a-round to get wexpect (sentinel-cli wrapper)
            to work with inside Pyinstaller executable on Windows. 
            This code is not necessary for Linux/OS X
            
            https://github.com/raczben/wexpect/issues/12
            https://github.com/raczben/wexpect/wiki/Wexpect-with-pyinstaller
            '''
            real_executable = sys.executable
            try:
                if sys._MEIPASS is not None:
                    sys.executable = os.path.join(sys._MEIPASS, "wexpect", "wexpect.exe")
            except AttributeError:
                pass
            try:
                child = wexpect.spawn(SCMD)
                sys.executable = real_executable
            except Exception as e:
                print("Error Spawning sentinelcli...")
                print(str(e))
                return (False, "Error Spawning sentinelcli")
            
            try: 
                child.expect(".*")
                child.sendline(PASSWORD)
            except Exception as e:
                print("Error expecting value and sending wallet passphrase")
                print(str(e))
                return (False, "Error Expecting initial value/wallet passphrase")
            #print(str(child.after))
            try:
                ofile.write(str(child.after))
            except Exception as e:
                print("Error writing subscribe info to file")
                print(str(e))
                return (False, "Error writing subscribe info to file")
            
            try:
                child.expect(".*")
                child.sendline()
            except Exception as e:
                print("Error expecting second data.")
                print(str(e))
                return (False, "Error expecting second data")
            #print(str(child.before))
            #print(str(child.after))
            try:
                ofile.write(str(child.after))
            except Exception as e:
                print("Error writing child.after 2nd data")
                print(str(e))
                return (False, "Error writing child.after 2nd data")
            
            try:
                child.expect(wexpect.EOF)
            except Exception as e:
                print("Error receiving EOF")
                print(str(e))
                return (False, "Error receiving EOF")
            #print(str(child.before))
            #print(str(child.after))
            try:
                ofile.write(str(child.before))
                ofile.write(str(child.after))
                ofile.flush()
                ofile.close()
            except Exception as e:
                print("ERROR writing final file subscription data")
                print(str(e))
                return (False, "Error writing final file subscription data ")
        except Exception as e:
            print(str(e))
            return (False, 1415)
        
        return self.ParseSubscribe(self)
        
    def unsubscribe(self, subId):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        if not KEYNAME:
            return {'hash' : "0x0", 'success' : False, 'message' : "ERROR Retrieving Keyname"}

        ofile = open(ConfParams.USUBSCRIBEINFO, "w")

        unsubCMD = "%s keys export --unarmored-hex --unsafe --keyring-backend file --keyring-dir %s %s" % (sentinelcli,  ConfParams.KEYRINGDIR, KEYNAME)
        try:
            
            ''' 
            This is the needed work-a-round to get wexpect (sentinel-cli wrapper)
            to work with inside Pyinstaller executable on Windows. 
            This code is not necessary for Linux/OS X
            
            https://github.com/raczben/wexpect/issues/12
            https://github.com/raczben/wexpect/wiki/Wexpect-with-pyinstaller
            '''
            real_executable = sys.executable
            try:
                if sys._MEIPASS is not None:
                    sys.executable = os.path.join(sys._MEIPASS, "wexpect", "wexpect.exe")
            except AttributeError:
                pass
            try:
                child = wexpect.spawn(unsubCMD)
                sys.executable = real_executable
            except Exception as e:
                print("Error Spawning sentinelcli...")
                print(str(e))
                return {'hash' : "0x0", 'success' : False, 'message' : "ERROR: Spawning sentinelcli"}
            try: 
                child.expect(".*")
                child.sendline("y")
                ofile.write(str(child.before))
                ofile.write(str(child.after))
                child.expect("Enter*")
                child.sendline(PASSWORD)
                ofile.write(str(child.before))
                ofile.write(str(child.after))
                child.expect(wexpect.EOF)
                ofile.write(str(child.before))
            except Exception as e:
                ofile.flush()
                ofile.close()
                print("Error sending password and getting privkey...")
                print(str(e))
                return {'hash' : "0x0", 'success' : False, 'message' : "ERROR: Getting privkey"}
            
            ofile.flush()
            ofile.close()
        except Exception as e:
            print(str(e))
            return {'hash' : "0x0", 'success' : False, 'message' : "ERROR: wexpect timeout"}

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
            
    def ParseSubscribe(self):
        SUBJSON = False
        with open(ConfParams.SUBSCRIBEINFO, 'r') as sub_file:
                lines = sub_file.readlines()
                k = 0
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
                
    def connect(self, ID, address, type):

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        connCMD = "%s %s connect --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node %s  --yes --gas-prices 0.3udvpn --from '%s' %s %s" % (gsudo, sentinelcli, ConfParams.KEYRINGDIR, self.RPC, KEYNAME, ID, address)
        print(connCMD)
        ofile =  open(ConfParams.CONNECTIONINFO, "w")    
        chdir(MeileConfig.BASEBINDIR)
        try:
            real_executable = sys.executable
            try:
                if sys._MEIPASS is not None:
                    sys.executable = os.path.join(sys._MEIPASS, "wexpect", "wexpect.exe")
            except AttributeError:
                pass
            child = wexpect.spawn(connCMD)
            sys.executable = real_executable
            
            child.expect(".*")
            ofile.write(str(child.before))
            print(str(child.before))
            child.sendline(PASSWORD)
            ofile.write(str(child.after))
            print(str(child.after))
            child.expect(".*")
            child.sendline('\n')
            print(str(child.before))
            print(str(child.after))
            ofile.write(str(child.after))
            child.expect(wexpect.EOF)
            print(str(child.before))
            print(str(child.after))
            ofile.write(str(child.before))
            ofile.write(str(child.after))
            
            ofile.flush()
            ofile.close()
        except Exception as e:
            print(str(e))
            return False
        
        
        with open(ConfParams.CONNECTIONINFO, "r") as connection_file:
            lines = connection_file.readlines()
            
            for l in lines:
                if "Error" in l:
                    return {"v2ray_pid" : None,  "result": False, "status" : l}
                
        connection_file.close()           
        sleep(5)
        
        if type == "WireGuard":
            if psutil.net_if_addrs().get("wg99"):
                return {"v2ray_pid" : None,  "result": True, "status" : "wg99"}
            
            else:
                return {"v2ray_pid" : None,  "result": False, "status" : "Error bringing up wireguard interface"}
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
                v2raydict = {"v2ray_pid" : V2Ray.v2ray_pid, "result": True, "status" : TUNIFACE}
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
                    
                v2raydict = {"v2ray_pid" : V2Ray.v2ray_pid,  "result": False, "status": "Error connecting to v2ray node: %s" % TUNIFACE}
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
    

                
    
        
        