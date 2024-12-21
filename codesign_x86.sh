#!/usr/local/bin/bash

if [[ $# -lt 1 ]]; then
	echo "CodeSign v1.2 by freQniK"
	echo ""
	echo "Usage: $0 <version>"
	echo ""
	echo "where version is in the format of v1.x.x"
	exit
fi

VERSION="$1"

echo "Removing Audio Codecs from App Bundle..."
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/FLAC
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/modplug
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/mpg123
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/Ogg
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/Opus
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/OpusFile
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/Vorbis
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/webp
rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/modplug

sleep 2

	
echo "Removing Infos..."
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/stripe-5.4.0.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/attrs-23.1.0.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/sentinel_protobuf-0.3.1.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/Kivy_Garden-0.1.5.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/cosmpy-0.8.0.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/wheel-0.41.2.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/google_api_core-2.11.1.dist-info
#rm -rf /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/jsonschema-4.17.3.dist-info

sleep 2


echo "Hard signing Meile.app..."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist  --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app

echo "Signing libs..."
mapfile -t libs < <(cat /Users/freqnik/eclipse-workspace/Meile2.0/libs_uniq.txt)
for file in ${libs[@]}
do
	codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" $file
done

#echo "Signing Python..."
#codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --deep   --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/Python

sleep 2
echo "Signing v2ray..."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/v2ray

sleep 2
echo "Signing wireguard-go.."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/wireguard-go

sleep 2
echo "Signing tun2socks..."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/tun2socks

sleep 2
echo "Signing wg..."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/wg

sleep 2
echo "Signing pyarmor..."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist  --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor_runtime_002918/pyarmor_runtime.so
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist  --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor/cli/core/pyarmor_runtime.so
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist  --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor/cli/core/pytransform3.so
sleep 2

echo "Signing meile-gui..."
codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/meile-gui
sleep 2

#echo "Signing files..."
#mapfile -t gfiles < <(find /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/* -type f -maxdepth 7)
#for file in ${gfiles[@]}
#do
#	if [[ "$file" == "/Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/meile-gui" ]]; then
#		continue
#	fi
#	codesign --entitlements /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/entitlements.plist --force --options runtime --timestamp --sign "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" $file
#done

sleep 2
echo "Displaying hardsigning verification..."
sleep 2
codesign --display --verbose /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app
sleep 7

#echo "Press <enter> to create the disk image.."
#read b

echo "Creating disk image..."
#hdiutil create -volname Meile -srcfolder /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile.app -ov -format UDBZ /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile.dmg
create-dmg \
 --volname "Meile" \
  --volicon "icon.icns" \
  --background "meile.app.png" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
 --icon "dist/Meile/Meile.app" 200 190 \
  --app-drop-link 600 185 \
  "Meile-"$VERSION"_x86_64.dmg" \
  "dist/Meile/"
sleep 2

echo "Signing disk image..."
codesign -s "Developer ID Application: Pool Stats LLC (VQYLU43P5V)" --timestamp /Users/freqnik/eclipse-workspace/Meile2.0/"Meile-"$VERSION"_x86_64.dmg"
sleep 2

echo "Press Enter to sumbit the app for notarization..."
read ans
meile_date=`date +%m%d%y`
echo "Submitting App for notarization..."
#xcrun altool --notarize-app --primary-bundle-id "M1-$meile_date" -u "freqnik@mathnodes.com" -p "@keychain:Meile-Intel" -t osx -f /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/"Meile-"$VERSION"_x86_64.dmg"
# altool is deprectated in favor of notarytool
# To use them, specify --keychain-profile "MN-Intel"
xcrun notarytool submit --keychain-profile "MN-Intel"  /Users/freqnik/eclipse-workspace/Meile2.0/"Meile-"$VERSION"_x86_64.dmg" --wait

echo "Press enter once notarization was approved...."
read answer

sleep 2
echo "Stapling the notarization receipt..."
xcrun stapler staple /Users/freqnik/eclipse-workspace/Meile2.0/"Meile-"$VERSION"_x86_64.dmg"
sleep 3

echo "Verification...."
spctl -a -vv -t install /Users/freqnik/eclipse-workspace/Meile2.0/"Meile-"$VERSION"_x86_64.dmg"
