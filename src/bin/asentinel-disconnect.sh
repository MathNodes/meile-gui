#!/bin/bash
set -euo pipefail

AWG_BIN="${HOME}/.meile-gui/bin/awg-quick"
WG_CONF="${HOME}/.meile-gui/wg99.conf"

/usr/bin/osascript <<EOF
do shell script "
    launchctl bootout system/app.meile.amnezia 2>/dev/null ;
    launchctl disable system/app.meile.amnezia ;
    $(printf %q "$AWG_BIN") down $(printf %q "$WG_CONF")
" without altering line endings with administrator privileges
EOF