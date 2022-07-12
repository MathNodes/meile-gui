CHANGELOG
========================

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
