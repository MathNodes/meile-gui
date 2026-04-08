import ipaddress
import logging
from typing import List

from src.conf import SplitTunnelingConfig

logger = logging.getLogger(__name__)

class SplitTunnelingService:
    """
    Manages the application and removal of split tunneling rules.
    This service would interact with the underlying OS network APIs
    to modify routing tables and firewall rules.

    NOTE: The actual OS-specific routing logic (e.g., using `netsh`, `ip route`, `pfctl`)
          is a placeholder and would need concrete implementation based on the target OS.
    """
    def __init__(self, config: SplitTunnelingConfig):
        self._config = config
        self._is_active = False # Tracks if split tunneling rules are currently applied

    @property
    def config(self) -> SplitTunnelingConfig:
        return self._config

    @config.setter
    def config(self, new_config: SplitTunnelingConfig):
        # When config changes, re-apply if active to reflect the new rules
        self._config = new_config
        if self._is_active:
            logger.info("Split tunneling configuration updated. Re-applying rules.")
            self.apply_rules()

    def _parse_ip_rules(self, ip_list: List[str]) -> List[ipaddress.Network]:
        """Parses a list of IP addresses or CIDR subnets into network objects."""
        networks = []
        for ip_str in ip_list:
            try:
                # ipaddress.ip_network handles both single IPs and CIDRs
                networks.append(ipaddress.ip_network(ip_str, strict=False))
            except ValueError:
                logger.warning(f"Invalid IP address or CIDR format in split tunnel config: '{ip_str}'")
        return networks

    def _apply_os_specific_routing(self,
                                   mode: str,
                                   included_networks: List[ipaddress.Network],
                                   excluded_networks: List[ipaddress.Network]):
        """
        [PLACEHOLDER] for OS-specific routing logic.
        This method would interact with `netsh` (Windows), `ip route` (Linux),
        `pfctl`/`route` (macOS) or similar tools/APIs to manipulate network routes.
        """
        logger.info(f"--- Applying Split Tunneling Rules (Mode: {mode}) ---")
        if mode == "whitelist":
            logger.info(f"  Traffic for IPs/subnets {included_networks} to go via VPN.")
            logger.info(f"  All other traffic to bypass VPN.")
            if excluded_networks:
                logger.info(f"  Explicitly excluded/bypassed IPs/subnets: {excluded_networks}.")
            # TODO: Implement OS-specific logic:
            # 1. Set default route to bypass VPN (e.g., via original gateway).
            # 2. Add specific routes for each `included_networks` entry to go via the VPN tunnel interface.
            # 3. Ensure `excluded_networks` entries explicitly bypass VPN (may already be covered by default).

        elif mode == "blacklist":
            logger.info(f"  Traffic for IPs/subnets {excluded_networks} to bypass VPN.")
            logger.info(f"  All other traffic to go via VPN.")
            if included_networks:
                logger.info(f"  Explicitly included/routed via VPN IPs/subnets: {included_networks}.")
            # TODO: Implement OS-specific logic:
            # 1. Set default route to go via VPN tunnel interface.
            # 2. Add specific routes for each `excluded_networks` entry to bypass VPN (e.g., via original gateway).
            # 3. Ensure `included_networks` entries explicitly go via VPN (may already be covered by default).

        else: # "disable"
            logger.info("  Split tunneling is disabled. Reverting all split tunnel specific routes.")
            # TODO: Implement OS-specific logic to revert any split tunneling routes.
            # This typically means ensuring routing is consistent with the VPN's primary connection
            # (e.g., all traffic through VPN if connected, or all direct if VPN is off).

        # Application-level split tunneling is significantly more complex,
        # often requiring OS-specific proxying, network filter drivers, or DPI.
        if self.config.included_apps or self.config.excluded_apps:
            logger.warning("  Application-based split tunneling is not yet implemented and requires OS-specific deep integration.")
        logger.info("--- Split Tunneling Rules Application Placeholder Complete ---")


    def apply_rules(self):
        """Applies the current split tunneling configuration to the system."""
        if self.config.mode == "disable":
            self.disable_rules()
            return

        logger.info(f"Activating split tunneling with mode: {self.config.mode}")

        included_networks = self._parse_ip_rules(self.config.included_ips)
        excluded_networks = self._parse_ip_rules(self.config.excluded_ips)

        # Basic conflict resolution: explicit exclusions take precedence.
        # This simplifies the routing logic by ensuring excluded IPs are removed from included set.
        final_included = [
            net for net in included_networks
            if not any(net.overlaps(ex_net) for ex_net in excluded_networks)
        ]
        final_excluded = excluded_networks # Exclusions are always explicit

        self._apply_os_specific_routing(self.config.mode, final_included, final_excluded)
        self._is_active = True
        logger.info("Split tunneling rules applied successfully (conceptually).")


    def disable_rules(self):
        """Removes all split tunneling-specific rules, reverting to standard VPN routing."""
        if not self._is_active and self.config.mode == "disable":
            logger.info("Split tunneling is already disabled or not active.")
            return

        logger.info("Disabling split tunneling and reverting rules.")
        self._apply_os_specific_routing("disable", [], []) # Call with disable mode to trigger cleanup
        self._is_active = False
        logger.info("Split tunneling rules disabled.")
