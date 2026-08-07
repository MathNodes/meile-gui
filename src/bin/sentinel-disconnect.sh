#!/bin/bash
# USE THIS FOR MANUAL INTERVENTION WITH THE WIREGUARD PROTOCOL
# THIS BRINGS THE WIREGUARD INTERFACE DOWN
set -euo pipefail

WG_BIN="${HOME}/.meile-gui/bin/wg-quick"
WG_CONF="${HOME}/.meile-gui/wg99.conf"

/usr/bin/osascript <<EOF
do shell script "
    launchctl bootout system/app.meile.wireguard 2>/dev/null ;
    launchctl disable system/app.meile.wireguard ;
    $(printf %q "$WG_BIN") down $(printf %q "$WG_CONF")
" without altering line endings with administrator privileges
EOF