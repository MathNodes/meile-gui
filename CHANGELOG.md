CHANGELOG
========================

# v0.9.5-beta.1 (23/08/2022)
* REMOVED: All external dependencies
* NEW: Bundled OS X version with wireguard tools
* NEW: Installs wireguard tools on first run
* NEW: Now a standalone application

# v0.9.4-beta.4 (23/08/2022)
* UPDATE: Made current with linux version
* CHANGE: No longer needed for sudo/root
* CHANGE: Use of applescript to prompt user for fingerprint or password on connect/disconnect


# v0.9.2-alpha.1
* NEW: Filters out nodes with node version less than 0.3.0
* NEW: Mac Silicon M1 build
* FIX: Removed tkinter support in place of smoother gui loading
* FIX: Fixed Subscription crash bug
* CHANGE: Build for Mac M1 requires root for wireguard



# v0.9.1-alpha.1 (04/07/2022)
* NEW: Main app now runs on main thread 
* NEW: Sub threads for other routines
* NEW: Packaged sentinel-cli 0.1.9 in build. No need to install independently
* FIX: Minor fixes and improvements 


# v0.9.0-alpha.1 (02/07/2022)
* Initial Release
