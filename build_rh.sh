#!/bin/bash
#
# Redhat build script

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <version>"
	exit
fi

new_version="$1"
build_version=`date +%s%3N`

sed -i "s/VERSION = \".*\"/VERSION = \"$new_version\"/" src/typedef/konstants.py
sed -i "s/BUILD = \".*\"/BUILD = \"$build_version\"/" src/typedef/konstants.py

# Linux 
pyinstaller --onefile --collect-all bip_utils --collect-all mospy --collect-all sentinel_protobuf --collect-all sentinel_sdk --collect-all stripe --collect-all kivy_garden --add-data src/fiat/stripe_pay/dist/pyarmor_runtime_002918:pyarmor_runtime_002918 --add-data src/fonts:../fonts --add-data src/awoc/datum/:datum --add-data src/utils/fonts/:../utils/fonts --add-data src/utils/coinimg/:../utils/coinimg --add-data src/imgs/:../imgs --add-data src/kv/:../kv --add-data src/conf/config/:config  --add-data src/bin/:../bin src/main/meile_gui.py

version=$(echo "$1" | sed -E 's/^v([0-9]+\.[0-9]+\.[0-9]+)$/\1/')

if [[ -z "$version" ]]; then
    echo "Invalid version format. Please use the format 'vX.Y.Z'."
    exit 1
fi

mkdir -p dist/meile-gui-$version
mv dist/meile_gui dist/meile-gui-$version/meile-gui

cd dist
tar cvzf meile-gui-$version.tar.gz meile-gui-$version
cd ..
cp dist/meile-gui-$version.tar.gz $HOME/rpmbuild/SOURCES

spec_file="$HOME/rpmbuild/SPECS/meile-gui.spec"
if [[ -f "$spec_file" ]]; then
    sed -i "s/^Version:.*$/Version:        $version/" "$spec_file"
    echo "Spec file updated with version $version."
else
    echo "Spec file not found: $spec_file"
    exit 1
fi

rpmbuild -bb $spec_file

