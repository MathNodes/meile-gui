#!/opt/homebrew/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <version>"
	exit
fi

new_version="$1"
build_version=`date +%s%3`

sed -i '' "s/VERSION = \".*\"/VERSION = \"$new_version\"/" src/typedef/konstants.py
sed -i '' "s/BUILD = \".*\"/BUILD = \"$build_version\"/" src/typedef/konstants.py

rm -rf build dist/meile-gui dist/meile-gui.app

pyinstaller --windowed --icon icon.icns --onedir --osx-bundle-identifier 'com.mathnodes.meile' --codesign-identity "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" --collect-all bip_utils --collect-all mospy --collect-all sentinel_protobuf --collect-all sentinel_sdk --collect-all stripe --collect-all kivy_garden --add-data src/fonts:fonts --add-data src/awoc/data/:data --add-data src/utils/fonts/:utils/fonts --add-data src/utils/coinimg/:utils/coinimg --add-data src/imgs/:imgs --add-data src/kv/:kv --add-data src/conf/config/:config --add-data src/bin/:bin src/main/meile-gui.py
