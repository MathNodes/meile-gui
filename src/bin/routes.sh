#!/bin/bash

STATE="$1"
GATEWAY=`route -n | grep 'UG[ \t]' | awk '{print $2}'`
PRIMARY_IFACE=`route | grep '^default' | grep -o '[^ ]*$'`

if test -z "$SUDO_USER"
then
    USER=$(getent passwd $PKEXEC_UID | cut -d: -f1)
else
    USER=$SUDO_USER
fi


if [[ ${STATE} = "up" ]]; then

        # save default route iface and gw ip
	echo ${GATEWAY} > /home/${USER}/.meile-gui/gateway
	echo ${PRIMARY_IFACE} > /home/${USER}/.meile-gui/iface

        # start v2ray
        /home/${USER}/.meile-gui/bin/v2ray run -c /home/${USER}/.sentinelcli/v2ray_config.json &
        sleep 3
        
        # get v2ray proxy IP
        PROXY_IP=`curl --preproxy socks5://localhost:1080 https://icanhazip.com`
        echo ${PROXY_IP} > /home/${USER}/.meile-gui/v2ray.proxy
        echo ${PROXY_IP}
        sleep 2
        
        # add tun interface
        TUNID=${RANDOM} 
        TUNIFACE="tun"${TUNID}
        echo ${TUNIFACE} > /home/${USER}/.meile-gui/tuniface
        ip tuntap add mode tun dev ${TUNIFACE}
        ip addr add 10.10.10.10/24 dev ${TUNIFACE}
        ip link set dev ${TUNIFACE} up

        # add default route for tun
        ip route add default via 10.10.10.10 dev ${TUNIFACE} metric 1

        # add normal route for proxy IP
        ip route add ${PROXY_IP} via ${GATEWAY}

        #sysctl net.ipv4.conf.all.rp_filter=0
        #sysctl net.ipv4.conf.${PRIMARY_IFACE}.rp_filter=0
        #sysctl net.ipv4.conf.tun0.rp_filter=2
	#sysctl net.ipv4.conf.tun0.forwarding=1
	#sysctl net.ipv4.conf.${PRIMARY_IFACE}.forwarding=1
	
	# start tun2socks 
        /home/${USER}/.meile-gui/bin/tun2socks -device tun://${TUNIFACE} -proxy socks5://127.0.0.1:1080 -interface ${PRIMARY_IFACE} -mtu 1500 -tcp-sndbuf 1024k -tcp-rcvbuf 1024k -tcp-auto-tuning

        #tun2socks -device tun0 -proxy socks5://127.0.0.1:1080 -interface ${PRIMARY_IFACE} -loglevel debug &
        # sanity check
        sleep 3
	echo "-----------------------_CURLING_---------------------------"
        curl https://icanhazip.com
else

        # get config
	GATEWAY=`cat /home/${USER}/.meile-gui/gateway | cut -d " " -f 1`
	PRIMARY_IFACE=`cat /home/${USER}/.meile-gui/iface | cut -d " " -f 1`
	TUNIFACE=`cat /home/${USER}/.meile-gui/tuniface | cut -d " " -f 1`
        PROXY_IP=`cat /home/${USER}/.meile-gui/v2ray.proxy`
        
        # terminate the v2ray setup
        pkill -11 tun2socks
        pkill -11 v2ray
	sleep 5

        # bring down tun interface
        ip addr del 10.10.10.10/24 dev ${TUNIFACE}
        ip link set dev ${TUNIFACE} down
        ip tuntap del mode tun dev ${TUNIFACE}
        
        # delete routes
        ip route del default
        ip route del default via 10.10.10.10 dev ${TUNIFACE} metric 1
        ip route del ${PROXY_IP} via ${GATEWAY}
        
        # add default route to LAN gateway
        ip route add default via ${GATEWAY} dev ${PRIMARY_IFACE} metric 100

        #sysctl net.ipv4.conf.all.rp_filter=1
        #sysctl net.ipv4.conf.${PRIMARY_IFACE}.rp_filter=1

        # sanity check
	curl https://icanhazip.com
fi
