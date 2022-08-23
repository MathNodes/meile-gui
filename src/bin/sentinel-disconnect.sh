#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("bash ${HOME}/.meile-gui/bin/run_expect_disconnect.sh " & quoted form of item 1 of argv & " " & quoted form of item 2 of argv) without altering line endings with administrator privileges        
    end run

EOF

