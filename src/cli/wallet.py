from os import path, remove, chdir, getcwd
import wexpect
import json
import requests
import sys
import os

from json.decoder import JSONDecodeError 

from conf.meile_config import MeileGuiConfig
from typedef.konstants import IBCTokens 
from typedef.konstants import ConfParams 
from typedef.konstants import HTTParams 
from adapters import HTTPRequests

MeileConfig  = MeileGuiConfig()
sentinelcli  = path.join(MeileConfig.BASEBINDIR, 'sentinelcli.exe')
sentinelcli  = sentinelcli.replace('\\','/')
gsudo        = path.join(MeileConfig.BASEBINDIR, 'gsudo.exe')

class HandleWalletFunctions():
    
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
        
        SCMD = "%s tx subscription subscribe-to-node --yes --gas-prices 0.3udvpn --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node %s --from '%s' '%s' %s"  % (sentinelcli, ConfParams.KEYRINGDIR, HTTParams.RPC, KEYNAME, NODE, DEPOSIT)    
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
            child = wexpect.spawn(SCMD)
            sys.executable = real_executable
            
            child.expect(".*")
            child.sendline(PASSWORD)
            print(str(child.after))
            ofile.write(str(child.after))
            child.expect(".*")
            child.sendline()
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
            return (False, 1415)
        
        return self.ParseSubscribe(self)
        
        
            
    def ParseSubscribe(self):
        JSONLOADED = False
        with open(ConfParams.SUBSCRIBEINFO, 'r') as sub_file:
                lines = sub_file.readlines()
                k = 0
                for l in lines:
                    if "Error" in l:
                        return(False, l)
                    if k >=1:
                        try:
                            tx_json = json.loads(l)
                            JSONLOADED = True
                            print(tx_json)
                            print("JSON LOADED!")
                            break
                        except JSONDecodeError as e:
                            print("NO JSON LINE")
                            k += 1
                            continue
                    k += 1
                        
                if JSONLOADED:        
                    if tx_json['data']:
                        try: 
                            print(tx_json['logs'][0]['events'][4]['attributes'][0]['value'])
                            sub_id = tx_json['logs'][0]['events'][4]['attributes'][0]['value']
                            if sub_id:
                                #remove(ConfParams.SUBSCRIBEINFO)
                                return (True,0)
                            else:
                                #remove(ConfParams.SUBSCRIBEINFO)
                                return (False,2.71828) 
                        except Exception as e:
                            print(str(e))
                            #remove(ConfParams.SUBSCRIBEINFO)
                            return (False, 3.14159)
                    elif 'insufficient' in tx_json['raw_log']:
                        #remove(ConfParams.SUBSCRIBEINFO)
                        return (False, tx_json['raw_log'])
                else:
                    return(False, 1.1459265357)
    def connect(self, ID, address):

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        connCMD = "%s %s connect --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node %s  --yes --gas-prices 0.3udvpn --from '%s' %s %s" % (gsudo, sentinelcli, ConfParams.KEYRINGDIR, HTTParams.RPC, KEYNAME, ID, address)
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
        
        if path.isfile(ConfParams.WIREGUARD_STATUS):
            CONNECTED = True
        else:
            CONNECTED = False
        chdir(MeileConfig.BASEDIR)
        return CONNECTED

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
    

                
    
        
        