#!/bin/bash

osascript   <<EOF
    do shell script ("${HOME}/.meile-gui/bin/meile-warp/warp-svc") with administrator privileges
 EOF
