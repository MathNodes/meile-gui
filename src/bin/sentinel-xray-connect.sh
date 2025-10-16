#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("launchctl bootstrap system /Library/LaunchDaemons/app.meile.xray.plist && sleep 3 && curl --preproxy socks5://localhost:1080 -s https://icanhazip.com && sleep 1 && launchctl bootstrap system /Library/LaunchDaemons/app.meile.tun2socks.plist && sleep 2 && ${HOME}/.meile-gui/bin/xray-routes.sh ") without altering line endings with administrator privileges        
    end run

EOF