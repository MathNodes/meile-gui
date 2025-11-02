import socket
import ipaddress

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



 