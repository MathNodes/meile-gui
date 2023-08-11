from adapters import HTTPRequests
import asyncio

class GetPriceAPI():
    DEC_AscenDEX = "https://ascendex.com/api/pro/v1/spot/ticker?symbol=DEC/USDT"
    CoinStats    = "https://api.coinstats.app/public/v1/tickers?exchange=KuCoin&pair=%s-USDT"
    
    async def get_usd(self, coin):
        
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        if coin == "dec":
            URL = self.DEC_AscenDEX
            try: 
                r = http.get(URL)
                print(r.json())
                coin_price = r.json()['data']['high']
            except:
                return {'success' : False, 'price' : 0.0}
        else:
            URL =  self.CoinStats % coin.upper()
            try: 
                r = http.get(URL)
                print(r.json())
                coin_price = r.json()['tickers'][0]['price']
            except:
                return {'success' : False, 'price' : 0.0}


        return {'success' : True, 'price' : coin_price}