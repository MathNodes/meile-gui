import re

tokens = ['1234538udec,666uatom,472829uscrt,382337484udvpn,382829uosmo', '11000000udvpn', ' ','']
UNITTOKEN = {'uscrt' : 'scrt', 'uatom' : 'atom' , 'uosmo' : 'osmo', 'udec' : 'dec', 'udvpn' : 'dvpn'}
SATOSHI  = 1000000

def parse_coin_deposit(tokens):
        UnitAmounts = []
        tokenString = ""
        pattern = r"([0-9]+)"
        
        
        if tokens.isspace() or not tokens:
            return ' '
        
        elif ',' in tokens:
            for deposit in tokens.split(','):
                amt = re.split(pattern,deposit)
                UnitAmounts.append(amt)
        else:
            amt = re.split(pattern,tokens)
            UnitAmounts.append(amt)
            
        for u in UnitAmounts:
            tokenString += str(round(float(float(u[1]) / SATOSHI),4)) + str(UNITTOKEN[u[2]]) + ','
        
        return tokenString[0:-1]
    
    
if __name__ == "__main__":
    for token in tokens:
        print(parse_coin_deposit(token))