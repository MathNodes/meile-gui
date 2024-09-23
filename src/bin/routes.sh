#!/bin/bash
STATE="$1"

if [[ ${STATE} == "up" ]]; then
	${HOME}/.meile-gui/bin/v2ray run -c ${HOME}/.meile-gui/v2ray_config.json &
	sleep 2
	curl --preproxy socks5://localhost:1080 -v https://icanhazip.com
	#sleep 3
	NIC=`route get default | grep "interface" | cut -d ":" -f 2 | tr -d " "`
	${HOME}/.meile-gui/bin/tun2socks  -device utun123 -proxy socks5://127.0.0.1:1080 -interface $NIC &
	sleep 5
	ifconfig utun123 198.18.0.1 198.18.0.1 up
	sleep 1
	route add -net 1.0.0.0/8 198.18.0.1
	route add -net 2.0.0.0/7 198.18.0.1
	route add -net 4.0.0.0/6 198.18.0.1
	route add -net 8.0.0.0/5 198.18.0.1
	route add -net 16.0.0.0/4 198.18.0.1
	route add -net 32.0.0.0/3 198.18.0.1
	route add -net 64.0.0.0/2 198.18.0.1
	route add -net 128.0.0.0/1 198.18.0.1
	route add -net 198.18.0.0/15 198.18.0.1
	#curl -v https://icanhazip.com
else
	route delete -net 1.0.0.0/8 198.18.0.1
	route delete -net 2.0.0.0/7 198.18.0.1
	route delete -net 4.0.0.0/6 198.18.0.1
	route delete -net 8.0.0.0/5 198.18.0.1
	route delete -net 16.0.0.0/4 198.18.0.1
	route delete -net 32.0.0.0/3 198.18.0.1
	route delete -net 64.0.0.0/2 198.18.0.1
	route delete -net 128.0.0.0/1 198.18.0.1
	route delete -net 198.18.0.0/15 198.18.0.1
	ifconfig utun123 198.18.0.1 198.18.0.1 down
	pkill -9 v2ray
	pkill -9 tun2socks
fi
