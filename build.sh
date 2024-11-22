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

echo "Setting venv..."
source meile2.0/bin/activate
sleep 3

pyinstaller --windowed --icon icon.icns --onedir --osx-bundle-identifier 'com.mathnodes.meile' --codesign-identity "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" --collect-all pyarmor --collect-all bip_utils --collect-all mospy --collect-all sentinel_protobuf --collect-all sentinel_sdk --collect-all stripe --collect-all kivy_garden --add-data src/fiat/stripe_pay/dist/pyarmor_runtime_002918:pyarmor_runtime_002918 --add-data src/fonts:fonts --add-data src/awoc/data/:data --add-data src/utils/fonts/:utils/fonts --add-data src/utils/coinimg/:utils/coinimg --add-data src/imgs/:imgs --add-data src/kv/:kv --add-data src/conf/config/:config --add-data src/bin/:bin src/main/meile-gui.py


echo "Creating Meile.app..."
rm -rf dist/Meile/Meile.app
cp -R dist/meile-gui.app dist/Meile/Meile.app

echo "Signing pyarmor..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor_runtime_002918/pyarmor_runtime.so
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor/cli/core/pyarmor_runtime.so
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor/cli/core/pytransform3.so

echo "Opening Meile.app..."
open dist/Meile/Meile.app
echo "Press [Enter] once the app loads and you close it..."
read answer

echo "Changing version..."
version=`echo $new_version | sed -e 's/v//g'`
echo $version
plutil -replace CFBundleShortVersionString -string $version dist/Meile/Meile.app/Contents/Info.plist

echo "Done."