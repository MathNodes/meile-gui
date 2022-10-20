CHANGELOG
========================
# v1.2.0 (20/10/2022)
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
