#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("bash $(pwd)/copy-files.sh ") without altering line endings with administrator privileges        
    end run

EOF

