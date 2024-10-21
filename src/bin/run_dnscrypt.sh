#!/bin/bash

if [[ "${1}" == "up" ]]; then
    DNS_SERVER="127.0.0.1"
else    
    DNS_SERVER="1.1.1.1"
fi
    

network_services=()

while IFS= read -r service; do
    network_services+=("$service")
done < <(networksetup -listallnetworkservices | grep -v 'An asterisk')


for service in "${network_services[@]}"; do
    networksetup -setdnsservers "$service" $DNS_SERVER
done


if [[ "${1}" == "up" ]]; then
    echo "Setting up dnscrypt-proxy..."
    ${HOME}/.meile-gui/bin/dnscrypt-proxy -config ${HOME}/.meile-gui/dnscrypt-proxy.toml &

else    
    echo "Stopping dnscrypt-proxy..."
    pkill -11 dnscrypt-proxy
fi
    
