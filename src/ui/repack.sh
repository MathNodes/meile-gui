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

# Map codenames to architectures
declare -A ARCH_MAP=(
    ["focal"]="amd64 i386 arm64"
    ["jammy"]="amd64 arm64"
    ["noble"]="amd64 arm64"
    ["plucky"]="amd64 arm64"
)

# Map codenames to descriptions
declare -A DESC_MAP=(
    ["focal"]="Ubuntu 20.04 (Focal Fossa)"
    ["jammy"]="Ubuntu 22.04 (Jammy Jellyfish)"
    ["noble"]="Ubuntu 24.04 (Noble Numbat)"
    ["resolute"]="Ubuntu 26.04 (Resolute Raccoon)"
)

# Function to check if a codename exists in distributions
codename_exists() {
    grep -q "^Codename: $1$" "$DISTRIBUTIONS_FILE" 2>/dev/null
}

# Function to add a new distribution
add_distribution() {
    local codename="$1"
    local archs="${ARCH_MAP[$codename]:-amd64 arm64}"
    local desc="${DESC_MAP[$codename]:-Ubuntu ($codename)}"

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
        # Create an override file for the new codename
        local existing_override_file
        existing_override_file=$(echo "$existing_override" | awk '{print $2}')
        if [ -f "$REPO_DIR/conf/$existing_override_file" ]; then
            cp "$REPO_DIR/conf/$existing_override_file" "$REPO_DIR/conf/override.${codename}"
        fi
        override_line="DebOverride: override.${codename}"
    fi

    echo ""
    echo "Adding new distribution: $codename"
    echo "  Architectures: $archs"
    echo "  Description:   $desc"
    echo "  SignWith:       $sign_key"

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

    echo "  Distribution '$codename' added and exported."
}

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

    # Look up the codename
    CODENAME="${DISTRO_MAP[$UBUNTU_ID]}"

    if [ -z "$CODENAME" ]; then
        echo "ERROR: Unknown distribution identifier: $UBUNTU_ID"
        echo "Please add a mapping for '$UBUNTU_ID' to the DISTRO_MAP in this script."
        continue
    fi

    echo "=========================================="
    echo "Processing: $filename"
    echo "  Version:  $VERSION"
    echo "  Distro:   $UBUNTU_ID -> $CODENAME"
    echo "=========================================="

    # Check if distribution exists, if not add it
    if ! codename_exists "$CODENAME"; then
        echo "  Distribution '$CODENAME' not found in $DISTRIBUTIONS_FILE"
        add_distribution "$CODENAME"
    fi

    EXTRACT_DIR="$WORK_DIR/meile-gui-${CODENAME}"

    # Extract the .deb
    rm -rf "$EXTRACT_DIR"
    dpkg-deb -R "$deb_file" "$EXTRACT_DIR"

    # Update the version in the control file
    sed -i "s/Version: ${VERSION}/Version: ${VERSION}~${CODENAME}/" "$EXTRACT_DIR/DEBIAN/control"

    # Verify the change
    echo "  Updated control file:"
    grep "Version:" "$EXTRACT_DIR/DEBIAN/control" | sed 's/^/    /'

    # Repackage
    OUTPUT_DEB="$WORK_DIR/meile-gui_${VERSION}~${CODENAME}_amd64.deb"
    dpkg-deb -b "$EXTRACT_DIR" "$OUTPUT_DEB"
    echo "  Repacked: $OUTPUT_DEB"

    # Remove old version from repo
    echo "  Removing old version from $CODENAME..."
    EXISTING=$(reprepro -b "$REPO_DIR" list "$CODENAME" "$PACKAGE_NAME" 2>/dev/null || true)
    if [ -n "$EXISTING" ]; then
        echo "    Old: $EXISTING"
        reprepro -b "$REPO_DIR" remove "$CODENAME" "$PACKAGE_NAME"
    else
        echo "    No existing version found."
    fi

    # Add new version to repo
    echo "  Adding new version to $CODENAME..."
    reprepro -b "$REPO_DIR" includedeb "$CODENAME" "$OUTPUT_DEB"
    echo "  Done!"
    echo ""
done

if [ "$FOUND" -eq 0 ]; then
    echo "No matching .deb files found in $DEB_DIR"
    exit 1
fi

# Final verification
echo "=========================================="
echo "Repository status:"
echo "=========================================="
# Dynamically list all codenames from the distributions file
while IFS= read -r codename; do
    reprepro -b "$REPO_DIR" list "$codename" "$PACKAGE_NAME" 2>/dev/null || true
done < <(grep "^Codename:" "$DISTRIBUTIONS_FILE" | awk '{print $2}')

echo ""
echo "Running repo check..."
reprepro -b "$REPO_DIR" check

echo ""
echo "All done! Repository updated successfully."