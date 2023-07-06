from os import path, environ

class ConfParams():
    USER             = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
    PATH             = environ['PATH']
    KEYRINGDIR       = path.join(path.expanduser('~' + USER), '.meile-gui')
    BASEDIR          = path.join(path.expanduser('~' + USER), '.sentinelcli')
    WALLETINFO       = path.join(KEYRINGDIR, "infos.txt")
    SUBSCRIBEINFO    = path.join(KEYRINGDIR, "subscribe.infos")
    USUBSCRIBEINFO   = path.join(KEYRINGDIR, "unsubscribe.infos")
    CONNECTIONINFO   = path.join(KEYRINGDIR, "connection.infos")
    WIREGUARD_STATUS = path.join(BASEDIR, "status.json")
    CHAINID          = 'sentinelhub-2'
    

class HTTParams():
    TIMEOUT                = 5
    APIURL                 = "https://api.sentinel.mathnodes.com"
    SERVER_URL             = "https://aimokoivunen.mathnodes.com:5000"
    RPC                    = "https://rpc.mathnodes.com:443"
    GRPC                   = "grpc+http://aimokoivunen.mathnodes.com:9090/"
    NODE_SCORE_ENDPOINT    = "/api/nodescores"
    NODE_LOCATION_ENDPOINT = "/api/nodelocations"
    NODE_TYPE_ENDPOINT     = "/api/nodetypes"
    API_PING_ENDPOINT      = "/api/ping"
    API_RATING_ENDPOINT    = "/api/rating"
    SESSIONS_API_URL       = '/sentinel/accounts/%s/sessions'
    BALANCES_ENDPOINT      = "/bank/balances/"
    
    
class IBCTokens():
    
    SATOSHI  = 1000000
    
    # IBC Tokens
    IBCSCRT  = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
    IBCATOM  = 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477'
    IBCDEC   = 'ibc/B1C0DDB14F25279A2026BC8794E12B259F8BDA546A3C5132CCAEE4431CE36783'
    IBCOSMO  = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'
    IBCUNKWN = 'ibc/9BCB27203424535B6230D594553F1659C77EC173E36D9CF4759E7186EE747E84'
    
    IBCCOINS = [{'uscrt' : IBCSCRT}, {'uatom' : IBCATOM}, {'udec' : IBCDEC}, {'uosmo' : IBCOSMO}, {'uknwn' :IBCUNKWN}]
    
    UNITTOKEN = {'uscrt' : 'scrt', 'uatom' : 'atom' , 'uosmo' : 'osmo', 'udec' : 'dec', 'udvpn' : 'dvpn'}

    CoinGeckoIDS = {'scrt' : 'secret', 'atom' : 'cosmos', 'dvpn' : 'sentinel', 'osmo' : 'osmosis', 'dec' : 'decentr'}
    
    
class TextStrings():
    dash = "-"
    VERSION = "v0.13.3.0"
    
class MeileColors():
    DIALOG_BG_COLOR = "#121212"
    FONT_FACE = "../fonts/mplus-2c-bold.ttf"
    MAP_MARKER = "../imgs/location_pin.png"
    
class NodeKeys():
    NodesInfoKeys = ["Moniker","Address","Provider","Price","Country","Speed","Latency","Peers","Handshake","Type","Version","Status"]
    SubsInfoKeys  = ["ID", "Owner", "Plan", "Expiry", "Denom", "Node", "Price", "Deposit", "Free", "Status"]
    FinalSubsKeys = [SubsInfoKeys[0], NodesInfoKeys[0],SubsInfoKeys[5], SubsInfoKeys[6], SubsInfoKeys[7], NodesInfoKeys[4], "Allocated", "Consumed", NodesInfoKeys[9]]
    NodeVersions  = [str(item).zfill(3) for item in range(30,1000)]
    Nodetypes = ['residential', 'business', 'hosting']


