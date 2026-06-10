import ipaddress
from os import path, remove


FULL_TUNNEL_ROUTES = ("0.0.0.0/0", "::/0")


def split_routes_file():
    try:
        from typedef.konstants import ConfParams
        return path.join(ConfParams.KEYRINGDIR, "split-routes")
    except KeyError:
        return path.join(path.expanduser("~"), ".meile-gui", "split-routes")


class SplitTunnelConfig:
    def __init__(self, enabled=False, routes=None):
        self.enabled = enabled
        self.routes = routes or []

    @property
    def allowed_ips(self):
        if not self.enabled or not self.routes:
            return list(FULL_TUNNEL_ROUTES)
        return self.routes


def parse_split_tunnel(config):
    if not config.has_section("split_tunnel"):
        return SplitTunnelConfig()

    enabled = config.getboolean("split_tunnel", "enabled", fallback=False)
    raw_routes = config.get("split_tunnel", "routes", fallback="")
    routes = []

    for raw_route in raw_routes.replace("\n", ",").split(","):
        route = raw_route.strip()
        if not route:
            continue
        routes.append(str(ipaddress.ip_network(route, strict=False)))

    return SplitTunnelConfig(enabled=enabled, routes=routes)


def write_split_routes(config):
    split_tunnel = parse_split_tunnel(config)
    routes_path = split_routes_file()

    if not split_tunnel.enabled or not split_tunnel.routes:
        if path.isfile(routes_path):
            remove(routes_path)
        return split_tunnel

    with open(routes_path, "w", encoding="utf-8") as routes_file:
        routes_file.write("\n".join(split_tunnel.routes))
        routes_file.write("\n")

    return split_tunnel
