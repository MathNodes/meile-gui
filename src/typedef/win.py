
class WindowNames():
    WALLET_RESTORE = "walletrestore"
    MAIN_WINDOW    = "main"
    PRELOAD        = "preload"
    NODES          = "nodes"
    WALLET         = "wallet"
    HELP           = "helpscreen"
    FIAT           = "fiatgateway"
    SUBSCRIPTIONS  = "subscriptions"
    SETTINGS       = "settings"
    
    
class CoinsList():
    SATOSHI = 1000000
    #ibc_mu_coins = ["tsent", "dvpn", "scrt", "osmo", "atom", "dec"]
    ibc_mu_coins = ["dvpn", "scrt", "osmo", "atom", "dec"]
    ibc_coins  = { "tsent" : "tsent", "dvpn" : "udvpn", "scrt" : "uscrt", "osmo": "uosmo", "atom" : "uatom", "dec" : "udec"}
    coins = ["atom", "dec", "dvpn", "osmo", "scrt"]