#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <version>"
	exit
fi

new_version="$1"
build_version=`date +%s%3N`

sed -i "s/VERSION = \".*\"/VERSION = \"$new_version\"/" src/typedef/konstants.py
sed -i "s/BUILD = \".*\"/BUILD = \"$build_version\"/" src/typedef/konstants.py

# Linux 
pyinstaller --onefile --collect-all bip_utils --collect-all mospy_wallet --collect-all sentinel_protobuf --collect-all sentinel_sdk --collect-all stripe --collect-all kivy_garden  --add-data src/fonts:../fonts --add-data src/awoc/datum/:datum --add-data src/utils/fonts/:../utils/fonts --add-data src/utils/coinimg/:../utils/coinimg --add-data src/imgs/:../imgs --add-data src/kv/:../kv --add-data src/conf/config/:config  --add-data src/bin/:../bin src/main/meile_gui.py
