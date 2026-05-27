import socket
import ipaddress
import socket
import time


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


def wait_for_port(host, port, timeout=300, poll=0.2):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with socket.create_connection((host, port), timeout=0.5):
                    return True
            except OSError:
                time.sleep(poll)
        return False

def wait_for_tunnel_iface(iface=None, timeout=300, poll=0.2):
    if not iface:
        raise ValueError("iface must be a non-empty list")

    wanted = set(iface)
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        present = {name for _, name in socket.if_nameindex()}
        found = wanted & present
        if found:
            # if multiple matched, prefer the order the caller gave
            for name in iface:
                if name in found:
                    return name
        time.sleep(poll)

    return None



 