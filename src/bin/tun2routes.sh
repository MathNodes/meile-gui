#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("${HOME}/.meile-gui/bin/routes.sh") without altering line endings with administrator privileges        
    end run

EOF