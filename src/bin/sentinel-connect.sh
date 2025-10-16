#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("launchctl bootstrap system /Library/LaunchDaemons/app.meile.wireguard.plist") without altering line endings with administrator privileges        
    end run

EOF

