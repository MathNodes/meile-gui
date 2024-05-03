from os import path, environ


class Arch():
    LINUX   = "Linux"
    WINDOWS = "Windows"
    OSX     = "Darwin"
    X86     = "x86_64"
    ARM     = "arm64"
    
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
    #CHAINID          = 'testnet'
    GASPRICE         = "0.2udvpn"
    #GASPRICE         = "0.2tsent"
    GASADJUSTMENT    = 1.15
    GAS              = 500000
    

class HTTParams():
    # Note http://128.199.90.172:26657 is testnet ONLY!
    TIMEOUT                = 5
    APIURL                 = "https://api.sentinel.mathnodes.com"
    
    NODE_API               = ["https://metabase.mathnodes.com/api/public/card/822823f7-9374-435d-b283-2cd3847c1668/query/json",
                              "https://metabase.bluefren.xyz/api/public/card/68fe67a6-6afa-45da-94ff-7e4e8443292f/query/json",
                              "https://metabase.jp.bluefren.xyz/api/public/card/2710bd6b-61bc-4bbd-96f2-9d22fd408627/query/json"]
    
    
    PLAN_API               = "https://api.meile.mathnodes.com:5000"
    #APIURL                 = "http://128.199.90.172:1317"
    SERVER_URL             = "https://aimokoivunen.mathnodes.com"
    RPC                    = "https://rpc.mathnodes.com:443"
    
    RPCS                   = ['https://rpc.mathnodes.com:443', 'https://rpc.dvpn.me:443', 'https://rpc.sentinel.co:443',
                              'https://rpc.sentinelgrowthdao.com:443', 'https://rpc.trinityvalidator.com.com:443',
                              'https://sentinel-rpc.badgerbite.io:443','https://sentinel-rpc2.badgerbite.io:443',
                              'https://rpc.sentinel.quokkastake.io:443', 'https://rpc-sentinel.whispernode.com:443']
    GRPC                   = "http://aimokoivunen.mathnodes.com:9090/"
    #GRPC                   = "grpc+http://128.199.90.172:9090/"
    HEALTH_CHECK           = "https://api.health.sentinel.co/v1/records/%s"
    NODE_SCORE_ENDPOINT    = "/api/nodescores"
    NODE_LOCATION_ENDPOINT = "/api/nodelocations"
    NODE_TYPE_ENDPOINT     = "/api/nodetypes"
    NODE_FORMULA_ENDPOINT  = "/api/nodeformula"
    CACHE_ENDPOINT         = "/api/cachelist"
    API_PING_ENDPOINT      = "/api/ping"
    API_RATING_ENDPOINT    = "/api/rating"
    API_PLANS              = "/v1/plans"
    API_PLANS_SUBS         = "/v1/subscription/%s" # variable is Meile wallet address
    API_PLANS_ADD          = "/v1/add"
    API_PLANS_NODES        = "/v1/nodes/%s" # variable is plan uuid
    SESSIONS_API_URL       = '/sentinel/accounts/%s/sessions'
    BALANCES_ENDPOINT      = "/bank/balances/"
    ICANHAZURL             = "https://icanhazip.com"
    ICANHAZDNS             = "icanhazip.com"
    IFCONFIGDNS            = "ifconfig.co"
    IFCONFIGURL            = "https://ifconfig.co/json"
    IPAPI                  = "http://ip-api.com/json"
    
    
class IBCTokens():
    
    SATOSHI  = 1000000
    
    # IBC Tokens
    IBCSCRT  = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
    IBCATOM  = 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477'
    IBCDEC   = 'ibc/B1C0DDB14F25279A2026BC8794E12B259F8BDA546A3C5132CCAEE4431CE36783'
    IBCOSMO  = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'
    IBCUNKWN = 'ibc/9BCB27203424535B6230D594553F1659C77EC173E36D9CF4759E7186EE747E84'
    
    IBCCOINS     = [{'uscrt' : IBCSCRT}, {'uatom' : IBCATOM}, {'udec' : IBCDEC}, {'uosmo' : IBCOSMO}, {'uknwn' :IBCUNKWN}]
    UNITTOKEN    = {'uscrt' : 'scrt', 'uatom' : 'atom' , 'uosmo' : 'osmo', 'udec' : 'dec', 'udvpn' : 'dvpn', 'tsent' : 'tsent'}
    IBCUNITTOKEN = {'uscrt' : IBCSCRT, 'uatom' : IBCATOM , 'uosmo' : IBCOSMO, 'udec' : IBCDEC, 'udvpn' : 'udvpn', 'tsent' : 'tsent'}
    mu_coins     = ["udvpn", "uscrt", "uosmo", "uatom", "udec"]
    CSAPPMAP     = {'dec' : 'decentr', 'atom' : 'cosmos', 'scrt' : 'secret', 'osmo' : 'osmosis', 'dvpn' : 'sentinel'}
    #mu_coins     = ["tsent", "udvpn", "uscrt", "uosmo", "uatom", "udec"]
class TextStrings():
    dash = "-"
    VERSION = "v1.8.0"
    RootTag = "SENTINEL"
    PassedHealthCheck = "Passed Sentinel Health Check"
    FailedHealthCheck = "Failed Sentinel Health Check"
    
class MeileColors():
    BLACK                    = "#000000"
    MEILE                    = "#fcb711"
    DIALOG_BG_COLOR          = "#121212"
    INACTIVE_DIALOG_BG_COLOR = "#50507c"
    ROW_HOVER                = "#39363c"
    FONT_FACE                = "../fonts/mplus-2c-bold.ttf"
    QR_FONT_FACE             = "../fonts/Roboto-BoldItalic.ttf"
    MAP_MARKER               = "../imgs/location_pin.png"
    LOGO                     = "../imgs/logo.png"
    LOGO_HD                  = "../imgs/logo_hd.png"
    LOGO_TEXT                = "../imgs/logo_text.png"
    HEALTH_ICON              = "shield-plus"
    SICK_ICON                = "emoticon-sick"
    ARCGIS_MAP               = "https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}.png"
    ARCGIS_MAP2              = "https://server.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}.png"
    
class NodeKeys():
    '''v1.8.0
    NodesInfoKeys = ["Moniker","Address","Price","Hourly Price", "Country","Speed","Latency","Peers","Handshake","Type","Version","Status"]
    SubsInfoKeys  = ["ID", "Owner", "Inactive Date", "Status", "Node", "Gigabytes", "Hours", "Deposit", "Plan", "Denom"]
    # [ "ID", "Moniker", "Node", "Gigabytes", "Deposit", "Country", "Allocated", "Consumed", "Type", "Inactive Date", "Hours"]
    FinalSubsKeys = [SubsInfoKeys[0], NodesInfoKeys[0],SubsInfoKeys[4],SubsInfoKeys[5], SubsInfoKeys[7], NodesInfoKeys[4], "Allocated", "Consumed", NodesInfoKeys[9],SubsInfoKeys[2],SubsInfoKeys[6]]
    NodeVersions  = [str(item).zfill(3) for item in range(30,1000)]
    Nodetypes = ['residential', 'business', 'hosting', 'edu']
    '''
    
    NodesInfoKeys = ["Moniker","Address","Price","Hourly Price", "Country","City","Latitude","Longitude","Download","Upload","Peers","Max Peers","Handshake","Type","Version", "ISP Type", "Score", "Votes", "Formula"]
    SubsInfoKeys  = ["ID", "Owner", "Inactive Date", "Status", "Node", "Gigabytes", "Hours", "Deposit", "Plan", "Denom"]
    # [ "ID", "Moniker", "Node", "Gigabytes", "Deposit", "Country", "Allocated", "Consumed", "Type", "Inactive Date", "Hours"]
    FinalSubsKeys = [SubsInfoKeys[0], NodesInfoKeys[0],SubsInfoKeys[4],SubsInfoKeys[5], SubsInfoKeys[7], NodesInfoKeys[4], "Allocated", "Consumed", NodesInfoKeys[13],SubsInfoKeys[2],SubsInfoKeys[6]]
    NodeVersions  = [str(item).zfill(3) for item in range(70,1000)]
    Nodetypes = ['residential', 'business', 'hosting', 'edu']

