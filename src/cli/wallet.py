from os import path, remove
import pexpect
import json
import requests

from json.decoder import JSONDecodeError 

from conf.meile_config import MeileGuiConfig
from typedef.konstants import IBCTokens 
from typedef.konstants import ConfParams 
from typedef.konstants import HTTParams
from adapters import HTTPRequests

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")

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
        with open(ConfParams.SUBSCRIBEINFO, 'r') as sub_file:
                lines = sub_file.readlines()
                try:
                    tx_json = json.loads(lines[2])
                except JSONDecodeError as e:
                    try: 
                        tx_json = json.loads(lines[3])
                    except JSONDecodeError as e2:
                        return(False, 1.1459265357)
                        
                if tx_json['data']:
                    try: 
                        sub_id = tx_json['logs'][0]['events'][4]['attributes'][0]['value']
                        if sub_id:
                            remove(ConfParams.SUBSCRIBEINFO)
                            return (True,0)
                        else:
                            remove(ConfParams.SUBSCRIBEINFO)
                            return (False,2.71828) 
                    except:
                        remove(ConfParams.SUBSCRIBEINFO)
                        return (False, 3.14159)
                elif 'insufficient' in tx_json['raw_log']:
                    remove(ConfParams.SUBSCRIBEINFO)
                    return (False, tx_json['raw_log'])
    def connect(self, ID, address):

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
        
        if path.isfile(ConfParams.WIREGUARD_STATUS):
            CONNECTED = True
        else:
            CONNECTED = False
            
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
    

                
    
        