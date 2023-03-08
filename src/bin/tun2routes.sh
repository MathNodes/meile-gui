#!/bin/bash
STATE="$1"
PASSWORD="$2"

osascript - "$STATE" "$PASSWORD"  <<EOF

    on run argv
    with timeout of 45 seconds
        do shell script ("${HOME}/.meile-gui/bin/routes.sh " & quoted form of item 1 of argv) without altering line endings with administrator privileges        
    end timeout
    end run

EOF
