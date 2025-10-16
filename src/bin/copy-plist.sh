#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("cp ${HOME}/.meile-gui/app.meile.wireguard.plist /Library/LaunchDaemons && cp ${HOME}/.meile-gui/app.meile.xray.plist /Library/LaunchDaemons && cp ${HOME}/.meile-gui/app.meile.tun2socks.plist /Library/LaunchDaemons") without altering line endings with administrator privileges        
    end run

EOF