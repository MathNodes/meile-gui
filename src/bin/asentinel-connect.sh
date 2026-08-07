#!/bin/bash
# USE THIS FOR MANUAL INTERVENTION WITH THE AMNEZIA WIREGUARD PROTOCOL
# THIS BRINGS THE AMNEZIAWG INTERFACE UP
set -euo pipefail

USER_PLIST="${HOME}/.meile-gui/launchd/app.meile.amnezia.plist"

if [ ! -f "$USER_PLIST" ]; then
    echo "Generated plist not found at $USER_PLIST" >&2
    exit 1
fi

/usr/bin/osascript <<EOF
do shell script "
    mkdir -p '/Library/Application Support/Meile/launchd' ;
    launchctl bootout system /Library/LaunchDaemons/app.meile.amnezia.plist 2>/dev/null ;
    rm -f /Library/LaunchDaemons/app.meile.amnezia.plist ;
    cp $(printf %q "$USER_PLIST") '/Library/Application Support/Meile/launchd/app.meile.amnezia.plist' ;
    chown -R root:wheel '/Library/Application Support/Meile' ;
    chmod 755 '/Library/Application Support/Meile' '/Library/Application Support/Meile/launchd' ;
    chmod 644 '/Library/Application Support/Meile/launchd/app.meile.amnezia.plist' ;
    launchctl enable system/app.meile.amnezia ;
    launchctl bootstrap system '/Library/Application Support/Meile/launchd/app.meile.amnezia.plist'
" without altering line endings with administrator privileges
EOF