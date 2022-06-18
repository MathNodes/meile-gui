from os import path, remove
import pexpect
import json
from src.conf.meile_config import MeileGuiConfig

KEYRINGDIR = path.join(path.expanduser('~'), '.meile-gui')
WALLETINFO = path.join(KEYRINGDIR, "infos.txt")
SUBSCRIBEINFO = path.join(KEYRINGDIR, "subscribe.infos")

    
class HandleWalletFunctions():
    
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        SCMD = 'sentinelcli keys add "%s" -i --keyring-backend file --keyring-dir %s' % (wallet_name, KEYRINGDIR)
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
                addy_seed = [lines[x] for x in line_numbers]
                WalletDict['address'] = addy_seed[0].split(":")[-1].lstrip().rstrip()
                WalletDict['seed']    = addy_seed[1].lstrip().rstrip().replace('\n', '')
                remove(WALLETINFO)
                return WalletDict
    
        else:
            remove(WALLETINFO)
            return None

    
    
    def subscribe(self, KEYNAME, NODE, DEPOSIT):
        CONFIG = MeileGuiConfig.read_configuration(MeileGuiConfig, MeileGuiConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
    
        ofile =  open(SUBSCRIBEINFO, "wb")    
        
        SCMD = "sentinelcli tx subscription subscribe-to-node --yes --keyring-backend file --keyring-dir %s --gas-prices 0.1udvpn --chain-id sentinelhub-2 --node https://rpc-sentinel.keplr.app:443 --from '%s' '%s' %s"  % (KEYRINGDIR, KEYNAME, NODE, DEPOSIT)    
     
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
                tx_json = json.loads(lines[2])
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
                
    
        