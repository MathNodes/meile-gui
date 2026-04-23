#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("launchctl bootout system /Library/LaunchDaemons/app.meile.wireguard.plist ; launchctl enable /Library/LaunchDaemons/app.meile.wireguard.plist ; launchctl bootstrap system /Library/LaunchDaemons/app.meile.wireguard.plist") without altering line endings with administrator privileges        
    end run

EOF

