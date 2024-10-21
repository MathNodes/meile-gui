#!/bin/bash
STATE="$1"

osascript - "$STATE"  <<EOF

    on run argv
    with timeout of 45 seconds
        do shell script ("${HOME}/.meile-gui/bin/run_dnscrypt.sh " & quoted form of item 1 of argv) without altering line endings with administrator privileges        
    end timeout
    end run

EOF