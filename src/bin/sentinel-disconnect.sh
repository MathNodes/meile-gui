#!/bin/bash
CLICMD="$1"

osascript - "$CLICMD" <<EOF

    
    on run argv
    with timeout of 30 seconds
        do shell script ("bash ${HOME}/.meile-gui/bin/wg-quick down ${HOME}/.meile-gui/wg99.conf && rm -rf ${HOME}/.meile-gui/wg99.conf") without altering line endings with administrator privileges        
    end timeout
    end run

EOF

