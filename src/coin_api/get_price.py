from adapters import HTTPRequests
from typedef.konstants import IBCTokens
import coin_api.scrtxxs as scrtxxs
import random

from utils.nowcurrencies import remember_icon_url

class GetPriceAPI():
    #DEC_AscenDEX = "https://ascendex.com/api/pro/v1/spot/ticker?symbol=DEC/USDT"
    CoinStats    = "https://openapiv1.coinstats.app/coins/%s"

    
    def get_usd(self, coin):
        k = 0
        coin_price = 0.0
        coin_icon  = None
        for key,value in IBCTokens.CSAPPMAP.items():
            if coin.lower() == key: 
                try:
                    N = random.randint(0,len(scrtxxs.COINSTATS_API_KEYS)-1)
                    API_KEY = scrtxxs.COINSTATS_API_KEYS[N]
                    headers = {
                        "accept": "application/json",
                        "X-API-KEY": f"{API_KEY}"
                    }
                    Request = HTTPRequests.MakeRequest(headers=headers)
                    http = Request.hadapter()
                    k += 1
                    r = http.get(self.CoinStats % value)
                    if r.status_code == 401 and k < 6:
                        continue
                    elif k < 6:
                        data = r.json()
                        print(data)
                        coin_price = data['price']
                        coin_icon  = data.get('icon')
                        # Remember the icon so it can be reused as the QR
                        # code logo (e.g. for NOWPayments).
                        remember_icon_url(coin, coin_icon)
                        break
                    else:
                        coin_price = 1.00
                        break
                except Exception as e:
                    print(f"BLAH: {str(e)}")
                    return {'success' : False, 'price' : 0.0, 'icon' : None}

        return {'success' : True, 'price' : coin_price, 'icon' : coin_icon}