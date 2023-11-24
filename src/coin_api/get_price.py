from adapters import HTTPRequests
from typedef.konstants import IBCTokens
import coin_api.scrtxxs as scrtxxs
import random

class GetPriceAPI():
    #DEC_AscenDEX = "https://ascendex.com/api/pro/v1/spot/ticker?symbol=DEC/USDT"
    CoinStats    = "https://openapiv1.coinstats.app/coins/%s"

    
    def get_usd(self, coin):
        N = random.randint(0,len(scrtxxs.COINSTATS_API_KEYS)-1)
        API_KEY = scrtxxs.COINSTATS_API_KEYS[N]
        headers = {
            "accept": "application/json",
            "X-API-KEY": f"{API_KEY}"
        }
        Request = HTTPRequests.MakeRequest(headers=headers)
        http = Request.hadapter()
        
        for key,value in IBCTokens.CSAPPMAP.items():
            if coin.lower() == key: 
                try:
                    r = http.get(self.CoinStats % value)
                    print(r.json())
                    coin_price = r.json()['price']
                except Exception as e:
                    print(str(e))
                    return {'success' : False, 'price' : 0.0}

        return {'success' : True, 'price' : coin_price}