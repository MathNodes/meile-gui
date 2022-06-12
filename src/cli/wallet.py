from os import path, remove
import pexpect

KEYRINGDIR = path.join(path.expanduser('~'), '.meile-gui')
WALLETINFO = path.join(KEYRINGDIR, "infos.txt")
    
class HandleWalletFunctions():
    
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        SCMD = 'sentinelcli keys add ' +  wallet_name +  " -i --keyring-backend file --keyring-dir " +  KEYRINGDIR
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
        