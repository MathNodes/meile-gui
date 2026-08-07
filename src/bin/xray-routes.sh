#!/bin/bash
#
# USE THIS FOR MANUAL INTERVENTION WITH THE XRAY PROTOCOL
# THIS IS TO BRING THE INTERFACE UP


set -e

# --- Config ---

TUN_DEV="utun123"
TUN_ADDR="198.18.0.1"
PROXY_FILE="/Users/${SUDO_USER}/.meile-gui/xray.proxy"

# --- Read the xray server IP from file, stripping whitespace/newlines ---
if [ ! -f "$PROXY_FILE" ]; then
    echo "ERROR: proxy file not found: $PROXY_FILE"
    exit 1
fi

# tr removes CR/LF/spaces/tabs; xargs trims leading/trailing whitespace
XRAY_SERVER=$(tr -d '[:space:]' < "$PROXY_FILE")
if [ -z "$XRAY_SERVER" ]; then
    echo "ERROR: no server IP found in $PROXY_FILE"
    exit 1
fi
echo "xray server: $XRAY_SERVER"

# --- Detect the real default gateway (before we hijack routes) ---
REAL_GW=$(route -n get default 2>/dev/null | awk '/gateway:/ {print $2}')
if [ -z "$REAL_GW" ]; then
    echo "ERROR: could not determine default gateway. Is your network up?"
    exit 1
fi
echo "Real default gateway: $REAL_GW"

# --- Bring up the tun interface ---
ifconfig "$TUN_DEV" "$TUN_ADDR" "$TUN_ADDR" up
sleep 1

# --- Pin the xray server to the real gateway (prevents routing loop) ---
route add -host "$XRAY_SERVER" "$REAL_GW"

# --- Route all IPv4 into the tunnel ---
route add -net 1.0.0.0/8        "$TUN_ADDR"
route add -net 2.0.0.0/7        "$TUN_ADDR"
route add -net 4.0.0.0/6        "$TUN_ADDR"
route add -net 8.0.0.0/5        "$TUN_ADDR"
route add -net 16.0.0.0/4       "$TUN_ADDR"
route add -net 32.0.0.0/3       "$TUN_ADDR"
route add -net 64.0.0.0/2       "$TUN_ADDR"
route add -net 128.0.0.0/1      "$TUN_ADDR"
route add -net 198.18.0.0/15    "$TUN_ADDR"

echo "Routes installed. Testing..."
curl -s https://icanhazip.com