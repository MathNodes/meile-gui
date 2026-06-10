import configparser
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from helpers.split_tunnel import parse_split_tunnel


class SplitTunnelConfigTests(unittest.TestCase):
    def test_defaults_to_full_tunnel_when_section_missing(self):
        config = configparser.ConfigParser()

        split_tunnel = parse_split_tunnel(config)

        self.assertFalse(split_tunnel.enabled)
        self.assertEqual(split_tunnel.allowed_ips, ["0.0.0.0/0", "::/0"])

    def test_uses_configured_routes_when_enabled(self):
        config = configparser.ConfigParser()
        config.add_section("split_tunnel")
        config.set("split_tunnel", "enabled", "1")
        config.set("split_tunnel", "routes", "10.20.0.0/16, 192.168.1.5")

        split_tunnel = parse_split_tunnel(config)

        self.assertTrue(split_tunnel.enabled)
        self.assertEqual(split_tunnel.allowed_ips, ["10.20.0.0/16", "192.168.1.5/32"])


if __name__ == "__main__":
    unittest.main()
