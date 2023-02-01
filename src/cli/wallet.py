from os import path, remove
import pexpect
import json
import requests
from json.decoder import JSONDecodeError
from time import sleep
import subprocess
from subprocess import PIPE

from src.conf.meile_config import MeileGuiConfig
from src.typedef.konstants import IBCTokens 
from src.typedef.konstants import ConfParams 
from src.typedef.konstants import HTTParams 
from src.adapters import HTTPRequests

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")
sentinelbash = MeileConfig.resource_path("../bin/sentinel.sh")
sentinel_connect_bash = MeileConfig.resource_path("../bin/sentinel-connect.sh")
wgbash = MeileConfig.resource_path("../bin/wg.sh")

class HandleWalletFunctions():
    
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        SCMD = '%s keys add "%s" -i --keyring-backend file --keyring-dir %s' % (sentinelcli, wallet_name, ConfParams.KEYRINGDIR)
        DUPWALLET = False 
        line_numbers = [11, 21]
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
                line_numbers = [13,23]
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
            return (False,1415)
            
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
        cliCMD = "%s connect --home %s --keyring-backend file --keyring-dir %s --chain-id sentinelhub-2 --node %s --gas-prices 0.1udvpn --yes --from '%s' %s %s" % (sentinelcli, ConfParams.BASEDIR, ConfParams.KEYRINGDIR, HTTParams.RPC, KEYNAME, ID, address)
        #connCMD = '%s "%s"' % (sentinelbash, cliCMD)
        connCMD = sentinelbash + ' "%s"' % cliCMD + ' "%s"' % PASSWORD
        print(connCMD)
        #connCMD = [sentinelcli, "connect", "--keyring-backend", "file", "--keyring-dir", KEYRINGDIR, "--chain-id", "sentinelhub-2", "--node",
        #            "https://rpc.mathnodes.com:443", "--gas-prices", "0.1udvpn", "--yes", "--from", "%s" % KEYNAME, ID, address]
    
        try:
            proc1 = subprocess.Popen(connCMD, shell=True)
            proc1.wait(timeout=60)
        except subprocess.TimeoutExpired as e:
            print(str(e))
            pass
        proc_out,proc_err = proc1.communicate()
        
        connectBASH = [sentinel_connect_bash]
        proc2 = subprocess.Popen(connectBASH)
        proc2.wait(timeout=30)
        
        proc_out, proc_err = proc2.communicate()
        
        
        if path.isfile(ConfParams.WIREGUARD_STATUS):
            return True
        else:
            return False

        
        '''
        proc = subprocess.Popen(connCMD, 
                        stdin=subprocess.PIPE, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        proc.stdin.write(b'%b + \n' % bytes(PASSWORD, 'utf-8'))
        proc.stdin.flush()
        proc.stdin.write(b'%b + \n' % bytes(osx_password, 'utf-8'))
        proc.stdin.flush()
        
        stdout,stderr = proc.communicate()
        print(stdout)
        print(stderr)

        
        
        ofile =  open(CONNECTIONINFO, "wb")    


        child = pexpect.spawn(connCMD)
        child.logfile = ofile

        try:
            child.expect(".*")
            child.sendline(PASSWORD)
            child.expect(".*")
            index = child.expect(["Error*", "wg-quick*", pexpect.EOF])
            if index == 0:
                ofile.flush()
                ofile.close()
                return False
            elif index == 1:
                child.sendline(osx_password)
                child.expect(pexpect.EOF)
            else:
                print('Im larry')
        except Exception as e:
            print(str(e))
            ofile.flush()
            ofile.close()
            return False
        
        ofile.flush()
        ofile.close()
        
        
        from python_wireguard import Client, ServerConnection, Key
        
        wg = wgconfig.WGConfig(path.join(BASEDIR, 'wg99.conf'))
        wg.read_file()
        
        private_key = wg.interface['PrivateKey']
        peers_keys = wg.peers.keys()
        for k in peers_keys:
            public_key = k
            
            
        endpoint = wg.peers[public_key]['Endpoint']
        srv_ip,srv_port = endpoint.split(':')    
        local_ip = wg.interface['Address']

        
        client = Client('wg-client', Key(private_key), local_ip)
        
        srv_key = Key(public_key)
        
        
        
        server_conn = ServerConnection(srv_key, srv_ip, srv_port)
        
        client.set_server(server_conn)
        client.connect()
        
        
        
        wg = "wg-quick up %s" % path.join(BASEDIR, "wg99.conf")
        wgCMD = "%s %s" % (sentinelbash, wg)
        #wgCMD = ['wg-quick', 'up', path.join(BASEDIR, "wg99.conf")]
        #wgCMD = [sentinelbash,  'up', path.join(BASEDIR, "wg99.conf")]
        #proc = subprocess.Popen(wgCMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        
        #stdout,stderr = proc.communicate()
        
        #print(stdout)
        #print(stderr)
        
        
        
        ofile = open(WIREGUARDINFO, "wb")
        try:
            
            child = pexpect.spawn(wgCMD)
            child.logfile = ofile
            index = child.expect(["Error*", "wg-quick*", pexpect.EOF])
            if index == 0:
                ofile.flush()
                ofile.close()
                return False
            elif index == 1:
                child.sendline(osx_password)
                child.expect(pexpect.EOF)
            else:
                pass
        except Exception as e:
            print(str(e))
            ofile.flush()
            ofile.close()
            return False 
            
        ofile.flush()
        ofile.close()
        
        if path.isfile(path.join(BASEDIR, "status.json")):
            return True
        else:
            return False
        '''    

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
    

                
    
        