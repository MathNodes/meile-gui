#!/bin/bash

if [[ "${1^^}" == "UP" ]]; then
    DNS_SERVER="127.0.0.1"
else    
    DNS_SERVER="1.1.1.1"
fi
    
for interface in $(resolvectl status | grep "Link" | awk '{print $2}'); do
    resolvectl dns "$interface" $DNS_SERVER
done

resolvectl status


if [[ "${1^^}" == "UP" ]]; then
    echo "Setting up dnscrypt-proxy..."
    /home/${USER}/.meile-gui/bin/dnscrypt-proxy -config /home/${USER}/.meile-gui/dnscrypt-proxy.toml &

else    
    echo "Stopping dnscrypt-proxy..."
    pkill -11 dnscrypt-proxy
fi
    
