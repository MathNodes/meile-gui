sentinelcli = "/home/blah/sentinelcli"
sentinelbash = "/home/blah/sentinel-connect.sh"
PASSWORD = "blargy2101"
BASEDIR = "/home/freqnik"
KEYRINGDIR = "/home/freqnik/.meile-gui"
KEYNAME="Zikurat"
ID=31337
address="sent398euhawofhap98ywaiodhwfhld9apw8dfhh"
cliCMD = "{0} connect --home {1} --keyring-backend file --keyring-dir {2} --chain-id sentinelhub-2 --node https://rpc.mathnodes.com:443 --gas-prices 0.1udvpn --yes --from '{3}' {4} {5}" .format(sentinelcli, BASEDIR,  KEYRINGDIR, KEYNAME, ID, address)
connCMD = [sentinelbash, "%s" % cliCMD, '"%s"' % PASSWORD]
print(connCMD)
