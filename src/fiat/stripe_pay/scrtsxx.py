SECRET_KEY         = "sk_live_..."
NOWPAYMENTS	   = "apikey..."
WALLET_ADDRESS     = 'sent19xv2hk6sdnndj6jkz48dpzzg08c26kjujyg8d2'
SERVER_ADDRESS     = "https://aimokoivunen.mathnodes.com:5000"
API_ENDPOINT       = "/api/tt"
MAX_SPEND_ENDPOINT = "/api/maxspend"
BTCPAY_ENDPOINT    = "/api/btcpay"
USERNAME           = 'username'
PASSWORD           = 'password'
CCOMPAREAPI        = '...'
CCOMPARE_API_URL   = "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=USD&extraParams=Meile"
# The plan API account is not shipped any more: every install registers its own
# username/password once with this key (POST /register) and keeps them in the
# [network] section of config.ini, then calls the API with a short lived bearer
# token minted from them (see cli/plan_api.py).  A single account - or a single
# token - can therefore be banned server side without locking out the rest of
# the fleet, which the shared static account of PLANUSERNAME/PLANPASSWORD could
# not be.
REGISTRATION_KEY   = 'registrationkey...'
BTCPAYSERVER       = "https://btcpay.foo.bar"
# Store the app creates its invoices in, and the fine-grained API key it does it
# with.  The key must be limited to btcpay.store.cancreateinvoice: the app never
# reads an invoice back (it asks the plan API, which holds a view-only key of
# the same store), so a key recovered from the obfuscated app cannot look up who
# paid what, and it cannot modify, refund or pay anything either.
BTCPAY_STORE_ID    = "storeid..."
BTCPAY_API_KEY     = "apikey..."
BTCPayEmail        = "btcpay@foo.bar"
MEILE_PLAN_API     = "https://api.meile.foo.bar"
MEILE_PLAN_ADD     = "/v1/add"
CARTO_API          = "cartoapikey...."
