#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "CodeSign v1.2 by freQniK"
	echo ""
	echo "Usage: $0 <version>"
	echo ""
	echo "where version is in the format of v1.x.x"
	exit
fi

VERSION="$1"

# --- Signing identity ------------------------------------------------------
SIGN_ID="Developer ID Application: Pool Stats LLC (VQYLU43P5V)"

# --- Locations -------------------------------------------------------------
# PyInstaller build that holds dist/Meile/Meile.app.  Override with
# MEILE_BUILD_DIR when building somewhere else.
BUILD_DIR="${MEILE_BUILD_DIR:-}"
if [[ -z "$BUILD_DIR" ]]; then
	if [[ -d "$PWD/dist/Meile" ]]; then
		BUILD_DIR="$PWD"
	else
		BUILD_DIR="/Users/freqnik/eclipse-workspace/Meile2.0"
	fi
fi
APP="$BUILD_DIR/dist/Meile/Meile.app"
SRC_FOLDER="$BUILD_DIR/dist/Meile"
DMG_PATH="$BUILD_DIR/Meile-${VERSION}_arm64.dmg"

# meile-gui checkout: holds icon.icns and assets/banner.png.  The DMG folder
# artwork is generated from that banner, so this has to resolve even when the
# script runs from the PyInstaller build directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI_DIR="${MEILE_GUI_DIR:-}"
for dir in "$GUI_DIR" "$SCRIPT_DIR" "$PWD" "/Users/freqnik/git2/MathNodes/meile-gui"; do
	if [[ -n "$dir" && -f "$dir/assets/banner.png" ]]; then
		GUI_DIR="$dir"
		break
	fi
done
VOLICON="$GUI_DIR/icon.icns"
BANNER="$GUI_DIR/assets/banner.png"
BG_HELPER="$GUI_DIR/make_dmg_background.py"
BG_DIR="$GUI_DIR/assets/dmg"

# --- DMG window geometry (keep in sync with make_dmg_background.py) --------
DMG_W=640
DMG_H=420
DMG_ICON_SIZE=100
DMG_TEXT_SIZE=14
DMG_APP_X=190
DMG_LINK_X=450
DMG_ICON_Y=290


echo "Hard signing Meile.app..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app

sleep 2
echo "Signing hysteria..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/hysteria

sleep 2
echo "Signing xray..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/xray

sleep 2
echo "Signing amneziawg-go.."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/amneziawg-go

sleep 2
echo "Signing wireguard-go.."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/wireguard-go

sleep 2
echo "Signing tun2socks..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/tun2socks

sleep 2
echo "Signing awg..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/awg

sleep 2
echo "Signing wg..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/bin/wg

sleep 2
echo "Signing pyarmor..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor_runtime_002918/pyarmor_runtime.so
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor/cli/core/pyarmor_runtime.so
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/Resources/pyarmor/cli/core/pytransform3.so

sleep 2
echo "Signing meile-gui..."
codesign --force --options runtime --timestamp --sign "$SIGN_ID" /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app/Contents/MacOS/meile-gui

sleep 2
echo "Displaying hardsigning verification..."
sleep 2
codesign --display --verbose /Users/freqnik/eclipse-workspace/Meile2.0/dist/Meile/Meile.app
sleep 7

echo "Creating disk image..."

# --- Folder artwork --------------------------------------------------------
# Finder window artwork is generated from assets/banner.png: the banner is
# painted across the top of the window and a brand-gold arrow is drawn between
# the Meile.app icon (left) and the Applications link (right), so the window
# reads "drag Meile onto Applications".  Needs a python with Pillow - every
# meile venv has one, Kivy depends on it.
PYTHON_BIN=""
for candidate in "${MEILE_PYTHON:-}" "$BUILD_DIR/meile2.0-2/bin/python" \
				 "$BUILD_DIR/meile2.0/bin/python" "$(command -v python3)"; do
	if [[ -n "$candidate" && -x "$candidate" ]] && \
	   "$candidate" -c 'import PIL' >/dev/null 2>&1; then
		PYTHON_BIN="$candidate"
		break
	fi
done
if [[ -z "$PYTHON_BIN" ]]; then
	echo "ERROR: no python with Pillow found, set MEILE_PYTHON=/path/to/python" >&2
	exit 1
fi
echo "Building window background from $BANNER..."
"$PYTHON_BIN" "$BG_HELPER" --banner "$BANNER" --out-dir "$BG_DIR" \
	--width "$DMG_W" --height "$DMG_H" --arrow-y "$DMG_ICON_Y" || exit 1

# Finder only draws the background crisply on a Retina screen when the 1x and
# the 2x image are packed into a single multi-resolution TIFF.
BG_IMAGE="$BG_DIR/background.png"
if command -v tiffutil >/dev/null 2>&1; then
	if tiffutil -cathidpicheck "$BG_DIR/background.png" \
			"$BG_DIR/background@2x.png" -out "$BG_DIR/background.tiff" \
			>/dev/null 2>&1; then
		BG_IMAGE="$BG_DIR/background.tiff"
	fi
fi

# --- Clear stale Meile mountpoints -----------------------------------------
# create-dmg 1.1.0 attaches its scratch image without -mountpoint and its
# "unmount leftover dmg" step detaches whichever device hdiutil happens to
# list first, not the one sitting on MOUNT_DIR.  So a leftover /Volumes/Meile -
# an interrupted run, or another Meile image the user mounted - pushes the
# scratch volume onto "/Volumes/Meile 1" while create-dmg keeps writing to
# "/Volumes/Meile", and the background copy dies with "Read-only file system"
# (or silently bakes the wrong artwork).  Eject our mountpoints up front so the
# scratch image lands where create-dmg expects it.
for vol in /Volumes/Meile /Volumes/Meile\ [0-9]*; do
	[[ -d "$vol" ]] || continue
	echo "Unmounting leftover volume '$vol'..."
	if ! hdiutil detach "$vol" >/dev/null 2>&1; then
		hdiutil detach -force "$vol" >/dev/null 2>&1 || {
			echo "ERROR: '$vol' is still mounted - eject it and retry" >&2
			exit 1
		}
	fi
done

#hdiutil create -volname Meile -srcfolder "$APP" -ov -format UDBZ "$BUILD_DIR/Meile.dmg"
create-dmg \
  --volname "Meile" \
  --volicon "$VOLICON" \
  --background "$BG_IMAGE" \
  --window-pos 200 120 \
  --window-size "$DMG_W" "$DMG_H" \
  --icon-size "$DMG_ICON_SIZE" \
  --text-size "$DMG_TEXT_SIZE" \
  --icon "Meile.app" "$DMG_APP_X" "$DMG_ICON_Y" \
  --hide-extension "Meile.app" \
  --app-drop-link "$DMG_LINK_X" "$DMG_ICON_Y" \
  "$DMG_PATH" \
  "$SRC_FOLDER" || {
	echo "ERROR: create-dmg failed - no disk image at $DMG_PATH" >&2
	exit 1
}
sleep 2

echo "Signing disk image..."
codesign -s "$SIGN_ID" --timestamp "$DMG_PATH"
sleep 2


meile_date=`date +%m%d%y`
echo "Submitting App for notarization..."
#deprecated
#xcrun altool --notarize-app --primary-bundle-id "M1-$meile_date" -u "freqnik@mathnodes.com" -p "@keychain:Meile-M1" -t osx -f /Users/freqnik/eclipse-workspace/Meile2.0/"Meile-"$VERSION".dmg"
xcrun notarytool submit --keychain-profile "MN-M1" "$DMG_PATH" --wait

echo "Press enter once notarization was approved...."
read answer

sleep 2
echo "Stapling the notarization receipt..."
xcrun stapler staple "$DMG_PATH"
sleep 3

echo "Verification...."
spctl -a -vv -t install "$DMG_PATH"
