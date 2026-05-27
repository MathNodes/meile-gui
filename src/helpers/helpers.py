import socket
import ipaddress
import socket
import time
import psutil


def format_byte_size(size, decimals=2, binary_system=True):
    if binary_system:
        units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"]
        largest_unit = "YiB"
        step = 1024
    else:
        units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB"]
        largest_unit = "YB"
        step = 1000
    for unit in units:
        if size < step:
            return ("%." + str(decimals) + "f %s") % (size, unit)
        size /= step
    return ("%." + str(decimals) + "f %s") % (size, largest_unit)


def resolve_address(addr):
    try:
        # Check if addr is already a valid IP
        ip = ipaddress.ip_address(addr)
        return str(ip)  # it's already an IP
    except ValueError:
        # Not an IP, treat as hostname
        return socket.gethostbyname(addr)


def wait_for_port(host, port, timeout=120, poll=0.2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for c in psutil.net_connections(kind="tcp"):
            if c.status == psutil.CONN_LISTEN and c.laddr.port == port:
                # optional: also match host
                if host in ("0.0.0.0", "", c.laddr.ip):
                    return True
        time.sleep(poll)
    return False

def wait_for_tunnel_iface(iface=None, timeout=30, poll=0.2):
    if not iface:
        raise ValueError("iface must be a non-empty list")

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        for tunface in psutil.net_if_addrs().keys():
            for intface in iface:
                if tunface.startswith(intface):
                    return tunface
        time.sleep(poll)

    return None



 