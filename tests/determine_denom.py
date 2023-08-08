UNITTOKEN = {'uscrt' : 'scrt', 'uatom' : 'atom' , 'uosmo' : 'osmo', 'udec' : 'dec', 'udvpn' : 'dvpn'}

DEPOSIT = "5000000udec"

for key in UNITTOKEN.keys():
    if key in DEPOSIT:
        print(key)