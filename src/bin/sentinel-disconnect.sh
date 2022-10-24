#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    
    on run argv
    with timeout of 30 seconds
        do shell script ("bash ${HOME}/.meile-gui/bin/wg-quick down ${HOME}/.sentinelcli/wg99.conf ") without altering line endings with administrator privileges        
    end timeout
    end run

EOF

