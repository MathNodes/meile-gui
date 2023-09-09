#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "CodeSign v1.1 by freQniK"
	echo ""
	echo "Usage: $0 <version>"
	echo ""
	echo "where version is in the format of v1.x.x"
	exit
fi

VERSION="$1"


echo "Hard signing Meile.app..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app

sleep 2
echo "Signing v2ray..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app/Contents/Resources/bin/v2ray

sleep 2
echo "Signing wireguard-go.."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app/Contents/Resources/bin/wireguard-go

sleep 2
echo "Signing tun2socks..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app/Contents/Resources/bin/tun2socks

sleep 2
echo "Signing wg..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app/Contents/Resources/bin/wg

sleep 2
echo "Signing sentinelcli..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app/Contents/Resources/bin/sentinelcli

sleep 2
echo "Signing meile-gui..."
codesign --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app/Contents/MacOS/meile-gui

sleep 2
echo "Displaying hardsigning verification..."
sleep 2
codesign --display --verbose /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile/Meile.app
sleep 7

echo "Creating disk image..."
#hdiutil create -volname Meile -srcfolder /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile.app -ov -format UDBZ /Users/freqnik/eclipse-workspace/meile-gui/dist/Meile.dmg
create-dmg \
  --volname "Meile" \
  --volicon "icon.icns" \
  --background "meile.app.png" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "dist/Meile/Meile.app" 200 190 \
  --app-drop-link 600 185 \
  "Meile-"$VERSION".dmg" \
  "dist/Meile/"
sleep 2

echo "Signing disk image..."
codesign -s "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" --timestamp /Users/freqnik/eclipse-workspace/meile-gui/"Meile-"$VERSION".dmg"
sleep 2


meile_date=`date +%m%d%y`
echo "Submitting App for notarization..."
xcrun altool --notarize-app --primary-bundle-id "M1-$meile_date" -u "freqnik@mathnodes.com" -p "@keychain:Meile-M1" -t osx -f /Users/freqnik/eclipse-workspace/meile-gui/"Meile-"$VERSION".dmg"

echo "Press enter once notarization was approved...."
read answer

sleep 2
echo "Stapling the notarization receipt..."
xcrun stapler staple /Users/freqnik/eclipse-workspace/meile-gui/"Meile-"$VERSION".dmg"
sleep 3

echo "Verification...."
spctl -a -vv -t install /Users/freqnik/eclipse-workspace/meile-gui/"Meile-"$VERSION".dmg"
