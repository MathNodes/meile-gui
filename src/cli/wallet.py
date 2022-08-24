from os import path, remove, environ
import pexpect
import json
import requests

from json.decoder import JSONDecodeError 

from conf.meile_config import MeileGuiConfig
from cli.sentinel import IBCATOM, IBCDEC, IBCOSMO, IBCSCRT, SATOSHI, APIURL

USER = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
PATH = environ['PATH']
KEYRINGDIR = path.join(path.expanduser('~' + USER), '.meile-gui')
BASEDIR  = path.join(path.expanduser('~' + USER), '.sentinelcli')
WALLETINFO = path.join(KEYRINGDIR, "infos.txt")
SUBSCRIBEINFO = path.join(KEYRINGDIR, "subscribe.infos")
CONNECTIONINFO = path.join(KEYRINGDIR, "connection.infos")

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")

class HandleWalletFunctions():
    
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        SCMD = '%s keys add "%s" -i --keyring-backend file --keyring-dir %s' % (sentinelcli, wallet_name, KEYRINGDIR)
        DUPWALLET = False 
        line_numbers = [11, 21]
        ofile =  open(WALLETINFO, "wb")    
        
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
                line_numbers = [13,23]
            elif index ==1:
                child.sendline("N")
                print("NO Duplicating Wallet..")
                DUPWALLET = True
                child.expect(pexpect.EOF)
                ofile.flush()
                ofile.closae()
                remove(WALLETINFO)
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
            with open(WALLETINFO, "r") as dvpn_file:
                WalletDict = {}   
                lines = dvpn_file.readlines()
                addy_seed = [lines[x] for x in range(line_numbers[0], line_numbers[1] +1)]
                if "address:" in addy_seed[0]:
                    WalletDict['address'] = addy_seed[0].split(":")[-1].lstrip().rstrip()
                else:
                    WalletDict['address'] = addy_seed[1].split(":")[-1].lstrip().rstrip()
                WalletDict['seed'] = lines[-1].lstrip().rstrip().replace('\n', '')
                remove(WALLETINFO)
                return WalletDict
    
        else:
            remove(WALLETINFO)
            return None

    
    
    def subscribe(self, KEYNAME, NODE, DEPOSIT):
        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
    
        ofile =  open(SUBSCRIBEINFO, "wb")    
        
        SCMD = "%s tx subscription subscribe-to-node --yes --keyring-backend file --keyring-dir %s --gas-prices 0.1udvpn --chain-id sentinelhub-2 --node https://rpc.mathnodes.com:443 --from '%s' '%s' %s"  % (sentinelcli, KEYRINGDIR, KEYNAME, NODE, DEPOSIT)    
     
        child = pexpect.spawn(SCMD)
        child.logfile = ofile
        
        child.expect(".*")
        child.sendline(PASSWORD)
        child.expect(pexpect.EOF)
        
        ofile.flush()
        ofile.close()
        
        return self.ParseSubscribe(self)
        
        
            
    def ParseSubscribe(self):
        SUBSCRIBEINFO = path.join(KEYRINGDIR, "subscribe.infos")
        with open(SUBSCRIBEINFO, 'r') as sub_file:
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
                            remove(SUBSCRIBEINFO)
                            return (True,0)
                        else:
                            remove(SUBSCRIBEINFO)
                            return (False,2.71828) 
                    except:
                        remove(SUBSCRIBEINFO)
                        return (False, 3.14159)
                elif 'insufficient' in tx_json['raw_log']:
                    remove(SUBSCRIBEINFO)
                    return (False, tx_json['raw_log'])
    def connect(self, ID, address):

        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        connCMD = "pkexec env PATH=%s %s connect --home %s --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node https://rpc.mathnodes.com:443 --gas-prices 0.1udvpn --yes --from '%s' %s %s" % (PATH, sentinelcli, BASEDIR, KEYRINGDIR, KEYNAME, ID, address)
        
        ofile =  open(CONNECTIONINFO, "wb")    

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
        
        if path.isfile(path.join(BASEDIR, "status.json")):
            CONNECTED = True
        else:
            CONNECTED = False
            
        return CONNECTED

    def get_balance(self, address):
        endpoint = "/bank/balances/" + address
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        try:
            r = requests.get(APIURL + endpoint)
            coinJSON = r.json()
        except:
            return None
            
        print(coinJSON)
        try:
            for coin in coinJSON['result']:
                if "udvpn" in coin['denom']:
                    CoinDict['dvpn'] = round(float(float(coin['amount']) / SATOSHI),4)
                elif IBCSCRT in coin['denom']:
                    CoinDict['scrt'] = round(float(float(coin['amount']) / SATOSHI),4)
                elif IBCDEC in coin['denom']:
                    CoinDict['dec'] = round(float(float(coin['amount']) / SATOSHI),4)
                elif IBCATOM in coin['denom']:
                    CoinDict['atom'] = round(float(float(coin['amount']) / SATOSHI),4)
                elif IBCOSMO in coin['denom']:
                    CoinDict['osmo'] = round(float(float(coin['amount']) / SATOSHI),4)
        except Exception as e:
            print(str(e))
            return None
        return CoinDict
    

                
    
        