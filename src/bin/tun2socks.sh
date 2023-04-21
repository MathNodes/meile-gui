#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD"  <<EOF

    on run argv
        do shell script ("${HOME}/.meile-gui/bin/tun2socks  -device utun123 -proxy socks5://127.0.0.1:1080 -interface en0") without altering line endings with administrator privileges        
    end run

EOF