#!/bin/bash
CLICMD="$1"
PASSWORD="$2"

osascript - "$CLICMD" "$PASSWORD" <<EOF
    on run argv
        set homePath to system attribute "HOME"
        do shell script " \
            launchctl bootstrap system \"/Library/Application Support/Meile/launchd/app.meile.xray.plist\"; \
            sleep 3; \
            curl --preproxy socks5://localhost:1080 -s https://icanhazip.com; \
            sleep 1; \
            launchctl bootstrap system \"/Library/Application Support/Meile/launchd/app.meile.tun2socks.plist\"; \
            sleep 2; \
            " & homePath & "/.meile-gui/bin/v2ray-routes.sh \
        " without altering line endings with administrator privileges
    end run
EOF