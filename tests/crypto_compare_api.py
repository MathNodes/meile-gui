import requests

HEADERS = {'authorization' : "Apikey 3b90195e03e476c2e10af5b911787397650d0f89424e24d2ff2b33256056c350"}
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/price?fsym=DVPN&tsyms=USD&extraParams=Meile"
r = requests.get(CRYPTOCOMPARE_API, headers=HEADERS)

r.json()['USD']