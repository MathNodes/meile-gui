import stripe
import requests 
import fiat.stripe_pay.scrtsxx as scrtsxx

stripe.api_key=scrtsxx.SECRET_KEY

IBCSCRT  = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
IBCATOM  = 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477'
IBCDEC   = 'ibc/B1C0DDB14F25279A2026BC8794E12B259F8BDA546A3C5132CCAEE4431CE36783'
IBCOSMO  = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'
IBCUNKWN = 'ibc/9BCB27203424535B6230D594553F1659C77EC173E36D9CF4759E7186EE747E84'

class StripePayments():
    def generate_card_token(self, cardnumber,expmonth,expyear,cvv):
        data= stripe.Token.create(
                card={
                    "number": str(cardnumber),
                    "exp_month": int(expmonth),
                    "exp_year": int(expyear),
                    "cvc": str(cvv),
                })
        card_token = data['id']
    
        return card_token
    
    
    def create_payment_charge(self, tokenid,amount):
    
        payment = stripe.Charge.create(
                    amount= int(float(amount)*100),                  # convert amount to cents
                    currency='usd',
                    description='dVPN Credits',
                    source=tokenid,
                    )
    
        payment_check = payment    # return True for payment
    
        return payment_check


class HotwalletFuncs():
    def get_balance(self, address):
        APIURL = "https://api.sentinel.mathnodes.com"
        SATOSHI = 1000000
        endpoint = "/bank/balances/" + address
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        try:
            r = requests.get(APIURL + endpoint)
            coinJSON = r.json()
        except:
            return None
            
        
        
        #print(coinJSON)
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