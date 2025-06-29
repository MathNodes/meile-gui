#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <version>"
	exit
fi

new_version="$1"
ubuntu_version=`cat /etc/os-release | grep VERSION_ID | cut -d '"' -f 2 | sed -e 's/\.//g'`
build_version=`date +%s%3N`

sed -i "s/VERSION = \".*\"/VERSION = \"$new_version\"/" src/typedef/konstants.py
sed -i "s/BUILD = \".*\"/BUILD = \"$build_version\"/" src/typedef/konstants.py

source meile310/bin/activate

# Linux 
pyinstaller --onefile --collect-all bip_utils --collect-all mospy --collect-all sentinel_protobuf --collect-all sentinel_sdk --collect-all stripe --collect-all kivy_garden --add-data src/fiat/stripe_pay/dist/pyarmor_runtime_002918:pyarmor_runtime_002918 --add-data src/fonts:../fonts --add-data src/awoc/datum/:datum --add-data src/utils/fonts/:../utils/fonts --add-data src/utils/coinimg/:../utils/coinimg --add-data src/imgs/:../imgs --add-data src/kv/:../kv --add-data src/conf/config/:config  --add-data src/bin/:../bin src/main/meile_gui.py

version=$(echo "$1" | sed -E 's/^v([0-9]+\.[0-9]+\.[0-9]+)$/\1/')

if [[ -z "$version" ]]; then
    echo "Invalid version format. Please use the format 'vX.Y.Z'."
    exit 1
fi

rm -rf meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64/
rm -rf meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64_vm/

rm -rf *.deb

mkdir meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64
mkdir meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64_vm

control_file="template/DEBIAN/control"
control_file_vm="template_vm/DEBIAN/control"

if [[ -f "$control_file" ]]; then
    sed -i "s/^Version:.*$/Version: $version/" "$control_file"
    echo "Control file updated with version $version."
else
    echo "Control file not found: $control_file"
    exit 1
fi

if [[ -f "$control_file_vm" ]]; then
    sed -i "s/^Version:.*$/Version: $version/" "$control_file_vm"
    echo "Control file updated with version $version."
else
    echo "Control file not found: $control_file_vm"
    exit 1
fi



cp -R template/* meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64/
cp -R template_vm/* meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64_vm/

cp dist/meile_gui meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64/usr/local/bin/meile-gui
cp dist/meile_gui meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64_vm/usr/local/bin/meile_gui

dpkg-deb --build --root-owner-group meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64
dpkg-deb --build --root-owner-group meile-gui-v"$version"_ubuntu"$ubuntu_version"_amd64_vm
