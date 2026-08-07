#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD" <<EOF
    on run argv
        do shell script " \
            launchctl bootout system/app.meile.xray 2>/dev/null; \
            launchctl bootout system/app.meile.tun2socks 2>/dev/null; \
            sleep 1; \
            ${HOME}/.meile-gui/bin/routes.sh down v2ray \
        " without altering line endings with administrator privileges
    end run
EOF