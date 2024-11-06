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
    BASEBINDIR       = path.join(KEYRINGDIR, "bin")
    WALLETINFO       = path.join(KEYRINGDIR, "infos.txt")
    SUBSCRIBEINFO    = path.join(KEYRINGDIR, "subscribe.infos")
    USUBSCRIBEINFO   = path.join(KEYRINGDIR, "unsubscribe.infos")
    CONNECTIONINFO   = path.join(KEYRINGDIR, "connection.infos")
    CHAINID          = 'sentinelhub-2'
    #CHAINID          = 'testnet'
    GASPRICE         = "0.314159udvpn"
    #GASPRICE         = "0.2tsent"
    GASADJUSTMENT    = 1.25
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
        "grpc.mathnodes.com:443",
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
                              "https://hsinao.com/api/public/card/5591a83b-d076-4278-b1c2-107ed441e21e/query/json",
                              "https://cache.meile.cryptopepper.org/api/public/card/9ced889b-3532-422e-a4c2-e1ee3349342a/query/json"
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
    NOWINVOICE             = "https://api.nowpayments.io/v1/invoice"
    NOWPAYMENT             = "https://api.nowpayments.io/v1/invoice-payment"
    NOWSTATUS              = "https://api.nowpayments.io/v1/payment/%s"
    NOWURL                 = "https://nowpayments.io/payment?iid=%s&paymentId=%s"
    RESOLVERS              = [
                              "adfilter-adl",
                              "adfilter-adl-ipv6",
                              "adfilter-per",
                              "adfilter-per-ipv6",
                              "adfilter-syd",
                              "adfilter-syd-ipv6",
                              "adguard-dns",
                              "adguard-dns-doh",
                              "adguard-dns-family",
                              "adguard-dns-family-doh",
                              "adguard-dns-family-ipv6",
                              "adguard-dns-ipv6",
                              "adguard-dns-unfiltered",
                              "adguard-dns-unfiltered-doh",
                              "adguard-dns-unfiltered-ipv6",
                              "ahadns-doh-la",
                              "ahadns-doh-nl",
                              "alidns-doh",
                              "alidns-doh-ipv6",
                              "ams-ads-doh-nl",
                              "ams-dnscrypt-nl",
                              "ams-dnscrypt-nl-ipv6",
                              "ams-doh-nl",
                              "artikel10-doh-ipv4",
                              "artikel10-doh-ipv6",
                              "bebasdns",
                              "bebasdns-family",
                              "bebasdns-unfiltered-doh",
                              "bortzmeyer",
                              "bortzmeyer-ipv6",
                              "brahma-world",
                              "brahma-world-ipv6",
                              "circl-doh",
                              "circl-doh-ipv6",
                              "cisco",
                              "cisco-doh",
                              "cisco-familyshield",
                              "cisco-familyshield-ipv6",
                              "cisco-ipv6",
                              "cisco-ipv6-doh",
                              "cisco-sandbox",
                              "cleanbrowsing-adult",
                              "cleanbrowsing-family",
                              "cloudflare",
                              "cloudflare-family",
                              "cloudflare-family-ipv6",
                              "cloudflare-ipv6",
                              "cloudflare-security",
                              "cloudflare-security-ipv6",
                              "comodo-02",
                              "controld-block-malware",
                              "controld-block-malware-ad",
                              "controld-block-malware-ad-social",
                              "controld-family-friendly",
                              "controld-uncensored",
                              "controld-unfiltered",
                              "cs-austria",
                              "cs-barcelona",
                              "cs-belgium",
                              "cs-berlin",
                              "cs-brazil",
                              "cs-bulgaria",
                              "cs-ch",
                              "cs-ch2",
                              "cs-czech",
                              "cs-dc",
                              "cs-de",
                              "cs-dk",
                              "cs-dus1",
                              "cs-dus2",
                              "cs-dus3",
                              "cs-dus4",
                              "cs-finland",
                              "cs-fl",
                              "cs-fl2",
                              "cs-fr",
                              "cs-ga",
                              "cs-il",
                              "cs-il2",
                              "cs-india",
                              "cs-ireland",
                              "cs-la",
                              "cs-london",
                              "cs-lv",
                              "cs-madrid",
                              "cs-manchester",
                              "cs-mexico",
                              "cs-milan",
                              "cs-montreal",
                              "cs-nc",
                              "cs-nl",
                              "cs-nl2",
                              "cs-norway",
                              "cs-nv",
                              "cs-nyc1",
                              "cs-nyc2",
                              "cs-ore",
                              "cs-poland",
                              "cs-pt",
                              "cs-ro",
                              "cs-rome",
                              "cs-serbia",
                              "cs-singapore",
                              "cs-sk",
                              "cs-slovakia",
                              "cs-swe",
                              "cs-sydney",
                              "cs-tokyo",
                              "cs-tx",
                              "cs-tx2",
                              "cs-tx3",
                              "cs-vancouver",
                              "dct-nl",
                              "dct-ru",
                              "decloudus-nogoogle-tstipv6",
                              "deffer-dns.au",
                              "digitalprivacy.diy-dnscrypt-ipv4",
                              "digitalprivacy.diy-dnscrypt-ipv6",
                              "dns.digitale-gesellschaft.ch",
                              "dns.digitale-gesellschaft.ch-ipv6",
                              "dns.digitalsize.net",
                              "dns.digitalsize.net-ipv6",
                              "dns.ryan-palmer",
                              "dns.sb",
                              "dns0",
                              "dns0-kids",
                              "dns0-unfiltered",
                              "dnscry.pt-adelaide-ipv4",
                              "dnscry.pt-adelaide-ipv6",
                              "dnscry.pt-allentown-ipv4",
                              "dnscry.pt-allentown-ipv6",
                              "dnscry.pt-amsterdam-ipv4",
                              "dnscry.pt-atlanta-ipv4",
                              "dnscry.pt-atlanta-ipv6",
                              "dnscry.pt-auckland-ipv4",
                              "dnscry.pt-auckland-ipv6",
                              "dnscry.pt-budapest-ipv4",
                              "dnscry.pt-budapest-ipv6",
                              "dnscry.pt-chicago-ipv4",
                              "dnscry.pt-chicago-ipv6",
                              "dnscry.pt-chisinau-ipv4",
                              "dnscry.pt-chisinau-ipv6",
                              "dnscry.pt-coeurdalene-ipv4",
                              "dnscry.pt-coeurdalene-ipv6",
                              "dnscry.pt-coventry-ipv4",
                              "dnscry.pt-coventry-ipv6",
                              "dnscry.pt-dallas-ipv4",
                              "dnscry.pt-dallas-ipv6",
                              "dnscry.pt-denver-ipv4",
                              "dnscry.pt-denver-ipv6",
                              "dnscry.pt-detroit-ipv4",
                              "dnscry.pt-detroit-ipv6",
                              "dnscry.pt-durham-ipv4",
                              "dnscry.pt-durham-ipv6",
                              "dnscry.pt-dusseldorf-ipv4",
                              "dnscry.pt-dusseldorf-ipv6",
                              "dnscry.pt-ebene-ipv4",
                              "dnscry.pt-eygelshoven-ipv4",
                              "dnscry.pt-eygelshoven-ipv6",
                              "dnscry.pt-flint-ipv4",
                              "dnscry.pt-flint-ipv6",
                              "dnscry.pt-frankfurt-ipv4",
                              "dnscry.pt-frankfurt-ipv6",
                              "dnscry.pt-fremont-ipv4",
                              "dnscry.pt-fremont-ipv6",
                              "dnscry.pt-fujairah-ipv4",
                              "dnscry.pt-fujairah-ipv6",
                              "dnscry.pt-geneva-ipv4",
                              "dnscry.pt-geneva-ipv6",
                              "dnscry.pt-helsinki-ipv4",
                              "dnscry.pt-helsinki-ipv6",
                              "dnscry.pt-hongkong-ipv4",
                              "dnscry.pt-hongkong-ipv6",
                              "dnscry.pt-istanbul-ipv4",
                              "dnscry.pt-istanbul-ipv6",
                              "dnscry.pt-jakarta-ipv4",
                              "dnscry.pt-jakarta-ipv6",
                              "dnscry.pt-johannesburg-ipv4",
                              "dnscry.pt-johannesburg-ipv6",
                              "dnscry.pt-kansascity-ipv4",
                              "dnscry.pt-kansascity-ipv6",
                              "dnscry.pt-kharkiv-ipv4",
                              "dnscry.pt-kharkiv-ipv6",
                              "dnscry.pt-kyiv-ipv4",
                              "dnscry.pt-kyiv-ipv6",
                              "dnscry.pt-lagos-ipv4",
                              "dnscry.pt-lagos-ipv6",
                              "dnscry.pt-lasvegas-ipv4",
                              "dnscry.pt-lasvegas-ipv6",
                              "dnscry.pt-libertylake-ipv4",
                              "dnscry.pt-libertylake-ipv6",
                              "dnscry.pt-lima-ipv4",
                              "dnscry.pt-lima-ipv6",
                              "dnscry.pt-london-ipv4",
                              "dnscry.pt-london-ipv6",
                              "dnscry.pt-losangeles-ipv4",
                              "dnscry.pt-losangeles-ipv6",
                              "dnscry.pt-madrid-ipv4",
                              "dnscry.pt-madrid-ipv6",
                              "dnscry.pt-miami-ipv4",
                              "dnscry.pt-miami-ipv6",
                              "dnscry.pt-milan-ipv4",
                              "dnscry.pt-milan-ipv6",
                              "dnscry.pt-montreal-ipv4",
                              "dnscry.pt-montreal-ipv6",
                              "dnscry.pt-mumbai-ipv4",
                              "dnscry.pt-mumbai-ipv6",
                              "dnscry.pt-munich-ipv4",
                              "dnscry.pt-munich-ipv6",
                              "dnscry.pt-naaldwijk-ipv4",
                              "dnscry.pt-naaldwijk-ipv6",
                              "dnscry.pt-newyork-ipv4",
                              "dnscry.pt-newyork-ipv6",
                              "dnscry.pt-nuremberg-ipv4",
                              "dnscry.pt-nuremberg-ipv6",
                              "dnscry.pt-oradea-ipv4",
                              "dnscry.pt-oradea-ipv6",
                              "dnscry.pt-ottoville-ipv4",
                              "dnscry.pt-ottoville-ipv6",
                              "dnscry.pt-paris-ipv4",
                              "dnscry.pt-paris-ipv6",
                              "dnscry.pt-philadelphia-ipv4",
                              "dnscry.pt-philadelphia-ipv6",
                              "dnscry.pt-phoenix-ipv4",
                              "dnscry.pt-phoenix-ipv6",
                              "dnscry.pt-portedwards-ipv4",
                              "dnscry.pt-portedwards-ipv6",
                              "dnscry.pt-portland-ipv4",
                              "dnscry.pt-portland-ipv6",
                              "dnscry.pt-riga-ipv4",
                              "dnscry.pt-riga-ipv6",
                              "dnscry.pt-saltlakecity-ipv4",
                              "dnscry.pt-saltlakecity-ipv6",
                              "dnscry.pt-sandefjord-ipv4",
                              "dnscry.pt-santaclara-ipv4",
                              "dnscry.pt-santaclara-ipv6",
                              "dnscry.pt-seattle-ipv4",
                              "dnscry.pt-seattle-ipv6",
                              "dnscry.pt-singapore-ipv4",
                              "dnscry.pt-singapore-ipv6",
                              "dnscry.pt-singapore02-ipv4",
                              "dnscry.pt-singapore02-ipv6",
                              "dnscry.pt-sofia-ipv4",
                              "dnscry.pt-sofia-ipv6",
                              "dnscry.pt-spokane-ipv4",
                              "dnscry.pt-spokane-ipv6",
                              "dnscry.pt-stockholm-ipv4",
                              "dnscry.pt-stockholm-ipv6",
                              "dnscry.pt-sydney-ipv4",
                              "dnscry.pt-sydney-ipv6",
                              "dnscry.pt-taipeh-ipv4",
                              "dnscry.pt-taipeh-ipv6",
                              "dnscry.pt-tallinn-ipv4",
                              "dnscry.pt-tallinn-ipv6",
                              "dnscry.pt-tampa-ipv4",
                              "dnscry.pt-tampa-ipv6",
                              "dnscry.pt-taos-ipv4",
                              "dnscry.pt-taos-ipv6",
                              "dnscry.pt-tokyo02-ipv4",
                              "dnscry.pt-tokyo02-ipv6",
                              "dnscry.pt-toronto-ipv4",
                              "dnscry.pt-toronto-ipv6",
                              "dnscry.pt-vienna-ipv4",
                              "dnscry.pt-vienna-ipv6",
                              "dnscry.pt-warsaw02-ipv4",
                              "dnscry.pt-warsaw02-ipv6",
                              "dnscrypt.ca-ipv4",
                              "dnscrypt.ca-ipv4-doh",
                              "dnscrypt.pl",
                              "dnscrypt.pl-guardian",
                              "dnscrypt.uk-ipv4",
                              "dnscrypt.uk-ipv6",
                              "dnsforfamily",
                              "dnsforfamily-doh",
                              "dnsforfamily-doh-no-safe-search",
                              "dnsforfamily-no-safe-search",
                              "dnsforfamily-v6",
                              "dnsforge.de",
                              "dnslow.me",
                              "dnspod",
                              "dnswarden-adult-doh",
                              "dnswarden-uncensor-dc-swiss",
                              "doh-cleanbrowsing-adult",
                              "doh-cleanbrowsing-family",
                              "doh-cleanbrowsing-security",
                              "doh-crypto-sx",
                              "doh-crypto-sx-ipv6",
                              "doh-ibksturm",
                              "doh.appliedprivacy.net",
                              "doh.ffmuc.net",
                              "doh.ffmuc.net-2",
                              "doh.ffmuc.net-v6",
                              "doh.ffmuc.net-v6-2",
                              "doh.tiar.app",
                              "doh.tiar.app-doh",
                              "doh.tiarap.org",
                              "doh.tiarap.org-ipv6",
                              "easymosdns-doh",
                              "faelix-ch-ipv4",
                              "faelix-uk-ipv4",
                              "faelix-uk-ipv6",
                              "fdn",
                              "fdn-ipv6",
                              "ffmuc.net",
                              "ffmuc.net-v6",
                              "fluffycat-fr-01",
                              "fluffycat-fr-02",
                              "google",
                              "google-ipv6",
                              "he",
                              "ibksturm",
                              "iij",
                              "jp.tiar.app",
                              "jp.tiar.app-doh",
                              "jp.tiar.app-doh-ipv6",
                              "jp.tiar.app-ipv6",
                              "jp.tiarap.org",
                              "jp.tiarap.org-ipv6",
                              "ksol.io-ns2-dnscrypt-ipv4",
                              "ksol.io-ns2-dnscrypt-ipv6",
                              "libredns",
                              "libredns-noads",
                              "mullvad-adblock-doh",
                              "mullvad-all-doh",
                              "mullvad-base-doh",
                              "mullvad-doh",
                              "mullvad-extend-doh",
                              "mullvad-family-doh",
                              "nextdns",
                              "nextdns-ipv6",
                              "nextdns-ultralow",
                              "nic.cz",
                              "nic.cz-ipv6",
                              "njalla-doh",
                              "plan9dns-fl",
                              "plan9dns-fl-doh",
                              "plan9dns-fl-doh-ipv6",
                              "plan9dns-fl-ipv6",
                              "plan9dns-mx",
                              "plan9dns-mx-doh",
                              "plan9dns-mx-doh-ipv6",
                              "plan9dns-mx-ipv6",
                              "plan9dns-nj",
                              "plan9dns-nj-doh",
                              "plan9dns-nj-doh-ipv6",
                              "plan9dns-nj.ipv6",
                              "pryv8boi",
                              "qihoo360-doh",
                              "quad101",
                              "quad9-dnscrypt-ip4-filter-ecs-pri",
                              "quad9-dnscrypt-ip4-filter-pri",
                              "quad9-dnscrypt-ip4-nofilter-ecs-pri",
                              "quad9-dnscrypt-ip4-nofilter-pri",
                              "quad9-doh-ip4-port443-filter-ecs-pri",
                              "quad9-doh-ip4-port443-filter-pri",
                              "quad9-doh-ip4-port443-nofilter-ecs-pri",
                              "quad9-doh-ip4-port443-nofilter-pri",
                              "quad9-doh-ip4-port5053-filter-ecs-pri",
                              "quad9-doh-ip4-port5053-filter-pri",
                              "quad9-doh-ip4-port5053-nofilter-ecs-pri",
                              "quad9-doh-ip4-port5053-nofilter-pri",
                              "quad9-doh-ip6-port443-filter-ecs-pri",
                              "quad9-doh-ip6-port443-filter-pri",
                              "quad9-doh-ip6-port443-nofilter-ecs-pri",
                              "quad9-doh-ip6-port443-nofilter-pri",
                              "quad9-doh-ip6-port5053-filter-ecs-pri",
                              "quad9-doh-ip6-port5053-filter-pri",
                              "quad9-doh-ip6-port5053-nofilter-ecs-pri",
                              "quad9-doh-ip6-port5053-nofilter-pri",
                              "restena-doh-ipv4",
                              "restena-doh-ipv6",
                              "rethinkdns-doh",
                              "safesurfer",
                              "safesurfer-doh",
                              "saldns01-conoha-ipv4",
                              "saldns02-conoha-ipv4",
                              "saldns03-conoha-ipv4",
                              "sby-doh-limotelu",
                              "sby-limotelu",
                              "scaleway-ams",
                              "scaleway-ams-ipv6",
                              "scaleway-fr",
                              "scaleway-fr-ipv6",
                              "serbica",
                              "sfw.scaleway-fr",
                              "sth-ads-doh-se",
                              "sth-dnscrypt-se",
                              "sth-doh-se",
                              "switch",
                              "switch-ipv6",
                              "tirapan-doh-ipv4",
                              "tirapan-doh-ipv6",
                              "tuna-doh-ipv6",
                              "uncensoreddns-dk-ipv4",
                              "uncensoreddns-dk-ipv6",
                              "uncensoreddns-ipv4",
                              "uncensoreddns-ipv6",
                              "userspace-australia",
                              "userspace-australia-ipv6",
                              "v.dnscrypt.uk-ipv4",
                              "v.dnscrypt.uk-ipv6",
                              "wikimedia",
                              "wikimedia-ipv6",
                              "yandex",
                              "yandex-ipv6",
                              "yandex-safe",
                              "yandex-safe-ipv6",
                            ]
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
    CSAPPMAP     = {'dec' : 'decentr', 'atom' : 'cosmos', 'scrt' : 'secret', 'osmo' : 'osmosis', 'dvpn' : 'sentinel', 'beam' : 'beam', 'firo' : 'zcoin'}
    #mu_coins     = ["tsent", "udvpn", "uscrt", "uosmo", "uatom", "udec"]
class TextStrings():
    dash = "-"
    VERSION = "v2.0.0"
    BUILD   = "1722988800718"
    RootTag = "SENTINEL"
    PassedHealthCheck = "Passed Sentinel Health Check"
    FailedHealthCheck = "Failed Sentinel Health Check"
    
class MeileColors():
    BLACK                    = "#000000"
    MEILE                    = "#fcb711"
    DIALOG_BG_COLOR          = "#121212"
    DIALOG_BG_COLOR2         = "#181818"
    INDICATOR                = "#00DD21"
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
    SPINNER                  = "../imgs/spinner.png"
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

