#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("launchctl bootout system /Library/Application Support/Meile/launchd/app.meile.xray.plist ; launchctl disable /Library/Application Support/Meile/launchd/app.meile.xray.plist ;  sleep 1 ; launchctl bootout system /Library/Application Support/Meile/launchd/app.meile.tun2socks.plist ; launchctl disable /Library/Application Support/Meile/launchd/app.meile.tun2socks.plist ; sleep 1 ; ${HOME}/.meile-gui/bin/routes.sh down") without altering line endings with administrator privileges        
    end run

EOF