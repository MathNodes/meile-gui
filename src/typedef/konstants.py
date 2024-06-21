from os import path, environ

MEILE_PLAN_WALLET = "sent1tdgva8fhl9rgawrj2am9sv8prw2h44mc8g3qch"

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
    GASPRICE         = "0.314159udvpn"
    #GASPRICE         = "0.2tsent"
    GASADJUSTMENT    = 1.15
    GAS              = 175000
    FEE              = 31416
    DEFAULT_SUB      = 5
    DEFAULT_SUBS     = [5 * i for i in range(1, 6)]

class HTTParams():
    # Note http://128.199.90.172:26657 is testnet ONLY!
    TIMEOUT                = 5
    APIURL                 = "https://api.sentinel.mathnodes.com"
    APIS_URL = [APIURL] + [
        "https://api.ungovernable.dev",
        "https://api.noncompliant.network",
        "https://api.ro.mathnodes.com",
        "https://lcd-sentinel.whispernode.com:443",
        "https://api.sentinel.quokkastake.io",
        "https://api.dvpn.roomit.xyz",
        "https://sentinel-rest.publicnode.com",
        "https://sentinel-api.validatornode.com",
        "https://api.trinityvalidator.com",
        "https://api.sentinelgrowthdao.com",
    ]
    MNAPI = "https://aimokoivunen.mathnodes.com"
    MNAPIS = [MNAPI] + []
    RPC = "https://rpc.mathnodes.com:443"
    # Note http://128.199.90.172:26657 is testnet ONLY!
    RPCS = [RPC] + [
        "https://rpc.sentinel.co:443",
        "https://rpc.dvpn.me443",
        "https://rpc.noncompliant.network:443",
        "https://rpc.ro.mathnodes.com:443",
        "https://rpc-sentinel.whispernode.com:443",
        "https://rpc.sentinel.chaintools.tech:443",
        "https://rpc.sentinel.quokkastake.io:443",
        "https://rpc.dvpn.roomit.xyz:443",
        "https://sentinel-rpc.badgerbite.io:443",
        "https://sentinel-rpc.publicnode.com:443",
        "https://sentinel-rpc.validatornode.com:443",
        "https://rpc.trinityvalidator.com:443",
        "https://rpc.sentinelgrowthdao.com:443",
        "https://sentinel-rpc.polkachu.com:443",
        "https://rpc-sentinel.busurnode.com:443"
    ]
    GRPC = "grpc.ungovernable.dev:443"
    GRPCS = [GRPC] + [
        "grc.mathnodes.com:443",
        "grpc.dvpn.me:443",
        "grpc.noncompliant.network:443",
        "grpc.ungovernable.dev:443",
        "grpc.bluefren.xyz:443",
        "sentinel.grpc.nodeshub.online:443",
        "sentinel-rpc.publicnode.com:443",
        "sentinel.grpcui.chaintools.host:443",
        "sentinel-mainnet-grpc.autostake.com:443",
        "grpc.dvpn.roomit.xyz:8443",
        "aimokoivunen.mathnodes.com:9090",
    ]
    NODE_API = "https://ungovernable.dev/api/public/card/1643a397-ddbd-48b1-89f7-396d16606eb5/query/json"
    NODE_APIS = [NODE_API] +  [
                              "https://metabase.mathnodes.com/api/public/card/bdff9cda-e0b8-417e-afd0-a8736a329914/query/json",
                              "https://metabase.bluefren.xyz/api/public/card/4a891454-51da-462a-a5df-e85ca17c05d5/query/json",
                              "https://metabase.jp.bluefren.xyz/api/public/card/feed7c25-410a-4e3a-bfe1-8a701defdc38/query/json",
                              "https://metabase.ro.mathnodes.com/api/public/card/6fd7194d-f025-4766-ba3c-3635ba6a6c00/query/json",
                              "https://noncompliant.network/api/public/card/bc75f719-db4a-44b8-9688-f5793742a203/query/json",
                              ]
    
    
    PLAN_API               = "https://api.meile.mathnodes.com:10000"
    #APIURL                 = "http://128.199.90.172:1317"
    SERVER_URL             = "https://aimokoivunen.mathnodes.com"
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
    IPAPIDNS               = "ip-api.com"
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
    VERSION = "v2.0.0-alpha1"
    RootTag = "SENTINEL"
    PassedHealthCheck = "Passed Sentinel Health Check"
    FailedHealthCheck = "Failed Sentinel Health Check"
    
class MeileColors():
    BLACK                    = "#000000"
    MEILE                    = "#fcb711"
    DIALOG_BG_COLOR          = "#121212"
    DIALOG_BG_COLOR2         = "#181818"
    INACTIVE_DIALOG_BG_COLOR = "#50507c"
    ROW_HOVER                = "#39363c"
    FONT_FACE                = "../fonts/mplus-2c-bold.ttf"
    FONT_FACE_ARIAL          = "../fonts/arial-unicode-ms.ttf"
    QR_FONT_FACE             = "../fonts/Roboto-BoldItalic.ttf"
    MAP_MARKER               = "../imgs/location_pin.png"
    LOGO                     = "../imgs/logo.png"
    LOGO_HD                  = "../imgs/logo_hd.png"
    LOGO_TEXT                = "../imgs/logo_text.png"
    SUBSCRIBE_BUTTON         = "../imgs/SubscribeButton.png"
    GETINFO_BUTTON           = "../imgs/GetInfoButton.png"
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

