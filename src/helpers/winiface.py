import socket
import ifaddr

def get_default_interface():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()

        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                if isinstance(ip.ip, tuple):
                    addr = ip.ip[0]  # IPv6 address
                else:
                    addr = ip.ip
                if addr == local_ip:
                    print(adapter.ips)
                    return adapter.ips, ip.ip
        return None, None
    except Exception as e:
        print("Error determining default interface:", e)
        return None, None