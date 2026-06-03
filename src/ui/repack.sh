#!/bin/bash

# Exit on any error
set -e

REPO_DIR="/var/www/apt-repo"
PACKAGE_NAME="meile-gui"
DISTRIBUTIONS_FILE="$REPO_DIR/conf/distributions"

# Directory where the original .deb files are located
DEB_DIR="$1"

if [ -z "$DEB_DIR" ]; then
    echo "Usage: $0 <deb-directory>"
    echo "Example: $0 ~/sentinel"
    exit 1
fi

# Create a temp working directory
WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

# Map Ubuntu version numbers to codenames
declare -A DISTRO_MAP=(
    ["ubuntu2004"]="focal"
    ["ubuntu2204"]="jammy"
    ["ubuntu2404"]="noble"
    ["ubuntu2604"]="resolute"
)

# Map LMDE codenames to the Ubuntu build they should use
# key = lmde codename, value = ubuntu identifier to pull .deb from
declare -A LMDE_SOURCE_MAP=(
    ["faye"]="ubuntu2004"
    ["gigi"]="ubuntu2204"
)

# Map codenames to architectures
declare -A ARCH_MAP=(
    ["focal"]="amd64 i386 arm64"
    ["jammy"]="amd64 arm64"
    ["noble"]="amd64 arm64"
    ["resolute"]="amd64 arm64"
    ["faye"]="amd64 arm64"
    ["gigi"]="amd64 arm64"
)

# Map codenames to descriptions
declare -A DESC_MAP=(
    ["focal"]="Ubuntu 20.04 (Focal Fossa)"
    ["jammy"]="Ubuntu 22.04 (Jammy Jellyfish)"
    ["noble"]="Ubuntu 24.04 (Noble Numbat)"
    ["resolute"]="Ubuntu 26.04 (Resolute Raccoon)"
    ["faye"]="LMDE 5 (Faye) - Debian Bullseye based"
    ["gigi"]="LMDE 6 (Gigi) - Debian Bookworm based"
)

# Function to check if a codename exists in distributions
codename_exists() {
    grep -q "^Codename: $1$" "$DISTRIBUTIONS_FILE" 2>/dev/null
}

# Function to add a new distribution
add_distribution() {
    local codename="$1"
    local archs="${ARCH_MAP[$codename]:-amd64 arm64}"
    local desc="${DESC_MAP[$codename]:-Unknown ($codename)}"

    # Get SignWith key from an existing entry
    local sign_key
    sign_key=$(grep "^SignWith:" "$DISTRIBUTIONS_FILE" | head -1 | awk '{print $2}')

    # Get Origin and Label from existing entry
    local origin
    local label
    origin=$(grep "^Origin:" "$DISTRIBUTIONS_FILE" | head -1 | awk '{print $2}')
    label=$(grep "^Label:" "$DISTRIBUTIONS_FILE" | head -1 | awk '{print $2}')

    # Check if there's a DebOverride in existing entries
    local override_line=""
    local existing_override
    existing_override=$(grep "^DebOverride:" "$DISTRIBUTIONS_FILE" | head -1 || true)
    if [ -n "$existing_override" ]; then
        local existing_override_file
        existing_override_file=$(echo "$existing_override" | awk '{print $2}')
        if [ -f "$REPO_DIR/conf/$existing_override_file" ]; then
            cp "$REPO_DIR/conf/$existing_override_file" \
                "$REPO_DIR/conf/override.${codename}"
        fi
        override_line="DebOverride: override.${codename}"
    fi

    echo ""
    echo "  Adding new distribution: $codename"
    echo "    Architectures: $archs"
    echo "    Description:   $desc"
    echo "    SignWith:       $sign_key"

    # Append to distributions file
    {
        echo ""
        echo "Origin: ${origin:-YourProjectName}"
        echo "Label: ${label:-YourProjectName}"
        echo "Codename: $codename"
        echo "Architectures: $archs"
        echo "Components: main"
        echo "Description: Packages for $desc"
        echo "SignWith: $sign_key"
        if [ -n "$override_line" ]; then
            echo "$override_line"
        fi
    } >> "$DISTRIBUTIONS_FILE"

    # Export the new distribution
    reprepro -b "$REPO_DIR" export "$codename"

    echo "    Distribution '$codename' added and exported."
}

# Function to repack and add a .deb to a specific codename
repack_and_add() {
    local deb_file="$1"
    local version="$2"
    local codename="$3"
    local label="$4"

    echo "------------------------------------------"
    echo "  [$label] Codename: $codename"
    echo "------------------------------------------"

    # Check if distribution exists, if not add it
    if ! codename_exists "$codename"; then
        echo "  Distribution '$codename' not found in $DISTRIBUTIONS_FILE"
        add_distribution "$codename"
    fi

    local extract_dir="$WORK_DIR/meile-gui-${codename}"

    # Extract the .deb
    rm -rf "$extract_dir"
    dpkg-deb -R "$deb_file" "$extract_dir"

    # Update the version in the control file
    sed -i "s/Version: ${version}/Version: ${version}~${codename}/" \
        "$extract_dir/DEBIAN/control"

    # Verify the change
    echo "  Updated control file:"
    grep "Version:" "$extract_dir/DEBIAN/control" | sed 's/^/    /'

    # Repackage
    local output_deb="$WORK_DIR/meile-gui_${version}~${codename}_amd64.deb"
    dpkg-deb -b "$extract_dir" "$output_deb"
    echo "  Repacked: $output_deb"

    # Remove old version from repo
    echo "  Removing old version from $codename..."
    local existing
    existing=$(reprepro -b "$REPO_DIR" list "$codename" "$PACKAGE_NAME" \
        2>/dev/null || true)
    if [ -n "$existing" ]; then
        echo "    Old: $existing"
        reprepro -b "$REPO_DIR" remove "$codename" "$PACKAGE_NAME"
    else
        echo "    No existing version found."
    fi

    # Add new version to repo
    echo "  Adding new version to $codename..."
    reprepro -b "$REPO_DIR" includedeb "$codename" "$output_deb"
    echo "  Done!"
    echo ""
}

# Collect source .deb paths by ubuntu identifier for LMDE reuse
declare -A SOURCE_DEBS

# Find all matching .deb files
FOUND=0
for deb_file in "$DEB_DIR"/meile-gui-v*_ubuntu*_amd64.deb; do
    if [ ! -f "$deb_file" ]; then
        echo "No matching .deb files found in $DEB_DIR"
        exit 1
    fi

    FOUND=1
    filename=$(basename "$deb_file")

    # Extract version number (e.g., 2.5.4)
    VERSION=$(echo "$filename" | grep -oP 'v\K[0-9]+\.[0-9]+\.[0-9]+')

    # Extract ubuntu identifier (e.g., ubuntu2004)
    UBUNTU_ID=$(echo "$filename" | grep -oP 'ubuntu\d{4}')

    # Look up the Ubuntu codename
    CODENAME="${DISTRO_MAP[$UBUNTU_ID]}"

    if [ -z "$CODENAME" ]; then
        echo "ERROR: Unknown distribution identifier: $UBUNTU_ID"
        echo "Please add a mapping for '$UBUNTU_ID' to the DISTRO_MAP."
        continue
    fi

    # Store the path for LMDE reuse
    SOURCE_DEBS[$UBUNTU_ID]="$deb_file"

    echo "=========================================="
    echo "Processing: $filename"
    echo "  Version:  $VERSION"
    echo "  Ubuntu:   $UBUNTU_ID -> $CODENAME"
    echo "=========================================="

    # Repack and add for Ubuntu
    repack_and_add "$deb_file" "$VERSION" "$CODENAME" "Ubuntu"

done

if [ "$FOUND" -eq 0 ]; then
    echo "No matching .deb files found in $DEB_DIR"
    exit 1
fi

# Now handle LMDE distributions
echo ""
echo "=========================================="
echo "Processing LMDE distributions"
echo "=========================================="

for lmde_codename in "${!LMDE_SOURCE_MAP[@]}"; do
    ubuntu_id="${LMDE_SOURCE_MAP[$lmde_codename]}"
    source_deb="${SOURCE_DEBS[$ubuntu_id]}"

    if [ -z "$source_deb" ] || [ ! -f "$source_deb" ]; then
        echo "WARNING: No source .deb found for LMDE '$lmde_codename'"
        echo "  Expected Ubuntu build: $ubuntu_id"
        echo "  Skipping."
        continue
    fi

    echo ""
    echo "LMDE $lmde_codename <- reusing $ubuntu_id build"
    repack_and_add "$source_deb" "$VERSION" "$lmde_codename" "LMDE"

done

# Final verification
echo "=========================================="
echo "Repository status:"
echo "=========================================="
while IFS= read -r codename; do
    result=$(reprepro -b "$REPO_DIR" list "$codename" "$PACKAGE_NAME" \
        2>/dev/null || true)
    if [ -n "$result" ]; then
        echo "$result"
    fi
done < <(grep "^Codename:" "$DISTRIBUTIONS_FILE" | awk '{print $2}')

echo ""
echo "Running repo check..."
reprepro -b "$REPO_DIR" check

echo ""
echo "All done! Repository updated successfully."