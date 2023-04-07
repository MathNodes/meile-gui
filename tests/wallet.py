import wexpect
from os import path, environ
from pathlib import Path
import sys

BASEDIR    = path.join(path.expanduser('~'), '.meile-gui')
BASEBINDIR = path.join(BASEDIR, 'bin')
sentinelcli  = path.abspath(path.join(path.abspath(BASEBINDIR), 'sentinelcli.exe'))


class ConfParams():
    PATH             = environ['PATH']
    KEYRINGDIR       = path.join(path.expanduser('~'), '.meile-gui')
    BASEDIR          = path.join(path.expanduser('~'), '.sentinelcli')
    WALLETINFO       = path.join(KEYRINGDIR, "infos.txt")
    SUBSCRIBEINFO    = path.join(KEYRINGDIR, "subscribe.infos")
    CONNECTIONINFO   = path.join(KEYRINGDIR, "connection.infos")
    WIREGUARD_STATUS = path.join(BASEDIR, "status.json")
  


class HandleWalletFunctions():
    
    def create(self, wallet_name, keyring_passphrase, seed_phrase):
        SCMD = '%s keys add "%s" -i --keyring-backend file --keyring-dir %s' % (sentinelcli, wallet_name, ConfParams.KEYRINGDIR)
        DUPWALLET = False 
        
        ofile =  open(ConfParams.WALLETINFO, "w")    
        
        ''' Process to handle wallet in sentinel-cli '''
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
                line_numbers = [18,38]
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
      
        
     
        if not DUPWALLET:
            with open(ConfParams.WALLETINFO, "r") as dvpn_file:
                WalletDict = {}   
                lines = dvpn_file.readlines()
                lines = [l for l in lines if l != '\n']
                for l in lines:
                    if "address:" in l:
                        WalletDict['address'] = l.split(":")[-1].lstrip().rstrip()
                        
                WalletDict['seed'] = lines[-1].lstrip().rstrip()
                remove(ConfParams.WALLETINFO)
                return WalletDict
    
        else:
            remove(ConfParams.WALLETINFO)
            return None


if __name__ == "__main__": 
    Wallet = HandleWalletFunctions()
    WalletDict = Wallet.create("Blargy", "blargy101", "sad can clay sponsor credit rough pottery mimic pigeon damp wash slide unlock foam path cigar shock palace object hobby midnight peasant fly used")
    print(WalletDict)