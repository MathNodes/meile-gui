#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("${HOME}/.meile-gui/bin/v2ray run -c ${HOME}/.sentinelcli/v2ray_config.json ") without altering line endings with administrator privileges        
    end run

EOF