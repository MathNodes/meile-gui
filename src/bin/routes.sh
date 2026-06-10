#!/bin/bash

STATE="$1"
GATEWAY=`route -n | grep 'UG[ \t]' | awk '{print $2}' | tail -1 | tr -d '\n'`
PRIMARY_IFACE=`route | grep '^default' | grep -o '[^ ]*$'`

if test -z "$SUDO_USER"
then
    USER=$(getent passwd $PKEXEC_UID | cut -d: -f1)
else
    USER=$SUDO_USER
fi

SPLIT_ROUTES_FILE="/home/${USER}/.meile-gui/split-routes"

has_split_routes() {
        [[ -s "${SPLIT_ROUTES_FILE}" ]]
}

apply_tunnel_routes() {
        if has_split_routes; then
                while IFS= read -r ROUTE; do
                        [[ -z "${ROUTE}" || "${ROUTE}" =~ ^# ]] && continue
                        echo "ip route add ${ROUTE} via 10.10.10.10 dev ${TUNIFACE} metric 1"
                        ip route add "${ROUTE}" via 10.10.10.10 dev "${TUNIFACE}" metric 1
                done < "${SPLIT_ROUTES_FILE}"
        else
                echo "ip route add default via 10.10.10.10 dev ${TUNIFACE} metric 1"
                ip route add default via 10.10.10.10 dev ${TUNIFACE} metric 1
        fi
}

remove_tunnel_routes() {
        if has_split_routes; then
                while IFS= read -r ROUTE; do
                        [[ -z "${ROUTE}" || "${ROUTE}" =~ ^# ]] && continue
                        echo "ip route del ${ROUTE} via 10.10.10.10 dev ${TUNIFACE} metric 1"
                        ip route del "${ROUTE}" via 10.10.10.10 dev "${TUNIFACE}" metric 1
                done < "${SPLIT_ROUTES_FILE}"
        else
                ip route del default
                ip route del default via 10.10.10.10 dev ${TUNIFACE} metric 1
        fi
}


if [[ ${STATE} = "up" ]]; then

        # save default route iface and gw ip
        echo ${GATEWAY} > /home/${USER}/.meile-gui/gateway
        echo ${PRIMARY_IFACE} > /home/${USER}/.meile-gui/iface

        # start v2ray
        echo "Running xray: /home/${USER}/.meile-gui/bin/v2ray run -c /home/${USER}/.meile-gui/v2ray_config.json &"
        /home/${USER}/.meile-gui/bin/xray run -c /home/${USER}/.meile-gui/v2ray_config.json &
        sleep 3
        
        # get v2ray proxy IP
        PROXY_IP=`cat /home/${USER}/.meile-gui/v2ray.proxy`
        #echo ${PROXY_IP} > /home/${USER}/.meile-gui/v2ray.proxy
        echo ${PROXY_IP}
        sleep 2
        
        # add tun interface
        TUNID=${RANDOM} 
        TUNIFACE="tun"${TUNID}
        echo ${TUNIFACE} > /home/${USER}/.meile-gui/tuniface
        
        echo "Routing Table: "
        ip route show
        
        echo "Adding tun interface..."
        echo "ip tuntap add mode tun dev ${TUNIFACE}"
        ip tuntap add mode tun dev ${TUNIFACE}
        echo "ip addr add 10.10.10.10/24 dev ${TUNIFACE}"
        ip addr add 10.10.10.10/24 dev ${TUNIFACE}
        echo "ip link set dev ${TUNIFACE} up"
        ip link set dev ${TUNIFACE} up

        # add default route for tun
        echo "Adding tunnel routes..."
        apply_tunnel_routes

        # add normal route for proxy IP
        echo "Add normal route for proxy..."
        echo "ip route add ${PROXY_IP} via ${GATEWAY} metric 1"
        ip route add ${PROXY_IP} via ${GATEWAY} metric 1

    	# start tun2socks 
    	echo "Starting tun2socks..."
        /home/${USER}/.meile-gui/bin/tun2socks -device tun://${TUNIFACE} -proxy socks5://127.0.0.1:1080 -interface ${PRIMARY_IFACE} -mtu 1500 -tcp-sndbuf 1024k -tcp-rcvbuf 1024k -tcp-auto-tuning -loglevel silent > /dev/null 2>&1 &

        #tun2socks -device tun0 -proxy socks5://127.0.0.1:1080 -interface ${PRIMARY_IFACE} -loglevel debug &
        # sanity check
        echo "Routing table: "
        ip route show
        
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
        pkill -9 tun2socks
        pkill -9 xray
	    sleep 5

        # delete routes before removing the tun interface
        remove_tunnel_routes
        ip route del ${PROXY_IP} via ${GATEWAY} metric 1

        # bring down tun interface
        ip addr del 10.10.10.10/24 dev ${TUNIFACE}
        ip link set dev ${TUNIFACE} down
        ip tuntap del mode tun dev ${TUNIFACE}
        
        # add default route to LAN gateway & DNS
        if ! has_split_routes; then
                ip route add default via ${GATEWAY} dev ${PRIMARY_IFACE} metric 100
        fi

        # sanity check
	    curl https://icanhazip.com
fi
