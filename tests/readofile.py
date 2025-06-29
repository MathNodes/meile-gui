import os
ofilestr = '''
Enter keyring passphrase:balhfashlfaj

gas estimate: 104648
code: 0
codespace: ""
data: ""
events: []
gas_used: "0"
gas_wanted: "0"
height: "0"
info: ""
logs: []
raw_log: '[]'
timestamp: ""
tx: null
txhash: 17A782264B94C963402765CEA6747AF6F3DA0819E564F271109E76EF7259818F'''

ofile = open('blah.txt' ,'a+')

ofile.write(ofilestr)
ofile.flush()
ofile.close()
with open('blah.txt' ,'r+') as rfile:
    last_line = rfile.readlines()[-1]
    if 'txhash' in last_line:
        tx = last_line.split(':')[-1].rstrip().lstrip()
        print(tx)
        
rfile.close()