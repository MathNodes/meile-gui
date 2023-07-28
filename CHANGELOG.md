CHANGELOG
========================
# v0.13.3.1 (28/072023)
* NEW: Add dependency asyncio
* UPDATE: Added coin_api GetPriceAPI class
* UPDATE: Make get_usd async
* CHANGE: get_usd in SubscribeContent to use GetPriceAPI class

# v0.13.3.0 (05/07/2023)
* NEW: Unsubscribe functions in HandleWalletFunctions()
* NEW: Check for active or pending sessions before unsub
* NEW: Click subscription card to prompt user to unsubscribe
* NEW: Present status dialog once unsub routines run, detailing height, hash of blockchain msg.
* NEW: Added dependencies cospmy and MathNodes/sentinel-protobuf for blockchain msgs. 
* NEW: Added Mathnodes GRPC endpoint
* UPDATE: New collection of cosmpy and sentinel-protobuf in pyinstaller script
* FIX: Sort by Price. Bug was created when prices switched from udvpn to dvpn. 
* FIX: Get Details by re-adding InsecureWarning import
* FIX: Set SubResult = None on refresh to enable subscription refresh

# v0.13.2.1 (21/04/2023)
* FIX: Not loading new subs. Redraw subs screen
* FIX: Crash on New subscription trying to switch to (null) subs tab.
* UPDATE: Use MainWindow.SubResult

# v0.13.2.0 (20/04/2023)
* FIX: setup.py to include pin marker
* ADD: DNSRequests Adapter
* NEW: Merge Windows commit e11f398 for faster DNS resolver checks on errors

# v0.13.1.0 (19/04/2023)
* NEW: Meile Cache API backed for Node Types (residential, datacenter, etc.)
* NEW: MDIcon Tooltip for node type on node screen

# v0.13.0.0 (12/04/2023)
* NEW: 70% map, 30% country nodes cards
* NEW: Map pin marker to yellow pin
* NEW: Subscription nav bar icon
* NEW: Subscription screen
* CHANGE: Rounded circle flag in front of country label


# v0.12.0.0 (22/03/2023)
* NEW: sentinelcli 0.3.0 
* NEW: v2ray support added
* NEW: v2ray 5.1.0 binary added
* NEW: tun2socks binary for TCP routing to Sentinel v2ray nodes
* NEW: Node type listing in node window and subscription (v2ray/wireguard)
* NEW: routes.sh for handling v2ray node connection
* CHANGE: Cosolidated colors to konstants.py
* CHANGE: Consolidate fonts to konstants.py
* CHANGE: Logic in real-time bandwidth to handle random tunXXX interface
* CHANGE: mc-plus2 font for unicode characters
* UPDATED: Connection logic to handle v2ray nodes
* UPDATED: Disconnect logic to handle v2ray nodes 
* FIX: Real-time bandwidth report when switching between nodes
* FIX: Unicode font problem 
* FIX: IBC Coin listing crash
* FIX: Node version reporting



# v0.11.2.4 (01/02/2023)
* NEW: Toast Message for Rating sent or errored out
* NEW: Version control in Help Screen
* NEW: Mac OS X App Bundle Release
* FIX: Logic in Rating and Location retrieval
* FIX: MapView Cache folder now located in ~/.meile.gui instead of CWD (fixes App Bundle)
* FIX: Wallet logic
* UPDATE: Sentinel-CLI for CosmWasm Sentinel Network Upgrade
* UPDATE: Packager Installer installs App Bundle to Desktop
* UPDATE: Improved HTTPs requests using requests adapter

# v0.11.2.0 (01/12/2022)
* NEW: Unicode Support for Moniker names
* NEW: Rating scores in subscription tab
* NEW: City names in subscription tabs
* UPDATE: Enhanced Subscription dialog with Moniker and better fonts
* UPDATE: Enhanced subscription processing dialog with nicer look
* UPDATE: Fixed freeze on TIMEOUT in API requests (ratings,wallet,etc.)
* UPDATE: Set requests TIMEOUT to 5 seconds
* CHANGE: Housekeeping by adding src/typedef/konstants.py 
* CHANGE: Housekeeping in wallet.py and sentinel.py

# v0.11.1.0 (28/11/2022)
* NEW: Cities for Nodes now available in node selection window
* NEW: Backend server API for node locations

# v0.11.0.0 (26/11/2022)
* NEW: Allows user to rate node after disconnecting
* NEW: Node ratings and vote count are visible in node selection window
* NEW: Backend server API for node ratings

# v0.10.4.2 (26/11/2022)
* FIX: Bug crash on speed text parsing for GB nodes
* FIX: Real-time bandwidth from propagating back to accumlation
* FIX: Spacing under bandwidth meter for nodes with errorneous speed reporting

# v0.10.4.1 (13/11/2022)
* NEW: Arial unicode fonts for bandwidth arrows
* NEW: Persistent real-time bandwidth usage between switching nodes
* FIX: Handling of connected node

# v0.10.4.0 (05/11/2022)
* NEW: Real-time bandwidth usage for current session, snapshot taken every two minutes. 
* NEW: Dependency *psutil* added - needed for bandwidth usage
* CHANGE: IP Address/Node now rectangle TextField instaed of Fill Box
* CHANGE: Bandwidth meter for current session at top
* UPDATE: Aligned Sort label with menu option

# v0.10.3.x (17/10/2022)
* NEW: Clickable Pin map with total node listings
* NEW: Refresh button in wallet screen
* NEW: Copy button for seed phrase on wallet restore/create
* NEW: Visible and draggable scrollbar on nodes
* CHANGE: Removed elevation from node cards as shadow rendering is broken in Kivy 1.1.1 
* CHANGE: Padding on "wallet" in the fiat interface (binary release only)
* CHANGE: Using rpc.mathnodes.com:443 for subs fixing country block of port 4444
* FIX: Connection switch bug that displayed random on in nodes when refreshing leading to confusion 
* FIX: Poor resize of screen with node cards. Resizes fast and clean
* FIX: Offline node consumed/allocated data progress bar and status text
* FIX: Divide by 0 bug and convert 0.00B to float
* FIX: Switch set to off if user cancels connection


# v0.10.2-pip (11/10/2022)
* FIX: Python 3.8 kivy_garden error

# v0.10.1-pip (09/10/2022)
* FIX: Minor bug fixes

# v0.10.0-pip (09/10/2022)
* NEW: Meile Pin map of country nodes
* NEW: Clickable pins
* NEW: Map centers around region tab
* NEW: Dictionary of Country Lat/Long coordinates
* FIX: Fixed KivyMD Warnings about MDCard Behavior


# v1.1.0 (20/09/2022)
* NEW: Cloudflar DoH (DNS-over-HTTPS) WARP integration
* NEW: Hover focus on node listings
* NEW: Sort by Price (dpvn) or Moniker
* NEW: Hover on focus for country listings
* NEW: Switch for Connect/Disconnect in Subscriptions
* CHANGE: Removed Disconnect button in NavBar
* FIX: Minor bugs

# v1.0.1 (01/09/2022)
* NEW: .deb package for virtual machine guest OSes
* FIX: Binary release fix for FIAT Gateway

# v1.0.0 (30/8/2022)
* NEW: Fiat Gateway
* CHANGE: Added CryptoCompare API alongside CoinGecko for additional DVPN price in FIAT gateway
* NEW: Automatic DNS resolve configuration for MacOS and Linux. Resolves to cloudflar if host HNS does not work
* FIX: No wallet subscription crash 
* FIX: Major/Minor bug fixes for stability

# v0.9.5-beta.1 (20/08/2022)
* NEW: Ping
* FIX: pexpect timeout exception handling

# v0.9.4-beta.4 (06/08/2022)
* CHANGE: No longer needed to run as sudo/root. 
* CHANGE: Propmpts user for system password when connecting/disconnecting

# v0.9.4-beta.3 (06/08/2022)
* ENHANCEMENT: Better UX on sub cards with added info

# v0.9.4-beta.2 (03/08/2022)
* NEW: Gnome-menu launcher and icon (ran as sudo) for .deb package
* ENHANCEMENT: Faster load times with option to refresh
* FIX: Subscription button text color
* FIX: Bug that created multiple nodes screen causing confusion

# v0.9.4-beta.1 (30/07/2022)
* NEW: Refresh Icon with Latency Selector
* NEW: TextField with currently connected node name
* FIX: Protected shield icon in pip install
* FIX: Minor bugs

# v0.9.3-beta.6 (28/07/2022)
* FIX: Disconnect Issues on some platforms

# v0.9.3-beta.5 (27/07/2022)
* NEW: Shield Icon in App Bar to Notify User is Connected
* FIX: Image stretching on subscriptions. 

# v0.9.3-beta.4 (24/07/2022)
* FIX: Bug when parsing wallet create/restore output

# v0.9.3-beta.3 (22/07/2022)
* NEW: Extra console debug messages 
* FIX: Wallet Balance retrieval error. Now displays dialog if unable to process wallet balances
* FIX: Crash on null price in Solar DVPN Node 15 

# v0.9.3-beta.2 (20/07/2022)
* FIX: Error parsing JSON line when subscribing on certain machines/os 

# v0.9.3-beta.1 (18/07/2022)
* NEW: 100% DeepPurple / Amber Theme
* FIX: Multiple bug fixes and crashes

# v0.9.2-alpha.1 (11/07/2022)
* NEW: Meile ICON logo in app and window bar
* NEW: Filter out dVPN nodes with version < 0.3.0
* FIX: Check to see if user is sudo/root. Issues on some linux with users not having network device permissions causing a panic when connecting
* FIX: Subscription crash when wallet not loaded
* FIX: Removed duplicate or unnessary imports
* FIX: Other minor improvements
* CHANGE: Removed tkinter support in favor of smaller screen library
* CHANGE: Determine actual user and place config files in ~/.meile-gui


# v0.9.1-alpha.1 (04/07/2022)
* NEW: Main app now runs on main thread 
* NEW: Sub threads for other routines
* NEW: Packaged sentinel-cli 0.1.9 in build. No need to install independently
* FIX: Minor fixes and improvements 


# v0.9.0-alpha.1 (02/07/2022)
* Initial Release
