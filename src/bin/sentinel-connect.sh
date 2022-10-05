#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("${HOME}/.meile-gui/bin/wg-quick up ${HOME}/.sentinelcli/wg99.conf ") without altering line endings with administrator privileges        
    end run

EOF

