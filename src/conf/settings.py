from typing import List, Literal, Optional
import os
import json

class SplitTunnelingConfig:
    """
    Configuration for split tunneling.

    mode:
        - "disable": Split tunneling is disabled.
        - "whitelist": Only traffic to specified IPs/subnets goes through the VPN.
                       All other traffic bypasses the VPN.
        - "blacklist": Traffic to specified IPs/subnets bypasses the VPN.
                       All other traffic goes through the VPN.
    included_ips: List of IP addresses or CIDR subnets that should be routed via VPN.
                  In 'whitelist' mode, these are the *only* IPs routed via VPN.
                  In 'blacklist' mode, these are *forced* to be routed via VPN even if
                  they overlap with blacklisted apps/other criteria.
    excluded_ips: List of IP addresses or CIDR subnets that should bypass the VPN.
                  In 'blacklist' mode, these are the *only* IPs bypassing VPN.
                  In 'whitelist' mode, these are *forced* to bypass VPN.
    included_apps: (Future) List of application names whose traffic should be
                   routed through the VPN. OS-specific implementation required.
    excluded_apps: (Future) List of application names whose traffic should
                   bypass the VPN. OS-specific implementation required.
    """
    mode: Literal["disable", "whitelist", "blacklist"] = "disable"
    included_ips: List[str] = []  # e.g., ["192.168.1.0/24", "10.0.0.5"]
    excluded_ips: List[str] = []  # e.g., ["172.16.0.0/16", "8.8.8.8"]
    included_apps: List[str] = [] # e.g., ["firefox", "thunderbird"]
    excluded_apps: List[str] = [] # e.g., ["steam", "spotify"]

    def __init__(self,
                 mode: Literal["disable", "whitelist", "blacklist"] = "disable",
                 included_ips: Optional[List[str]] = None,
                 excluded_ips: Optional[List[str]] = None,
                 included_apps: Optional[List[str]] = None,
                 excluded_apps: Optional[List[str]] = None):
        self.mode = mode
        self.included_ips = included_ips if included_ips is not None else []
        self.excluded_ips = excluded_ips if excluded_ips is not None else []
        self.included_apps = included_apps if included_apps is not None else []
        self.excluded_apps = excluded_apps if excluded_apps is not None else []

    def to_dict(self):
        return {
            "mode": self.mode,
            "included_ips": self.included_ips,
            "excluded_ips": self.excluded_ips,
            "included_apps": self.included_apps,
            "excluded_apps": self.excluded_apps,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            mode=data.get("mode", "disable"),
            included_ips=data.get("included_ips"),
            excluded_ips=data.get("excluded_ips"),
            included_apps=data.get("included_apps"),
            excluded_apps=data.get("excluded_apps"),
        )

class AppConfig:
    """
    Main application configuration containing all settings.
    """
    _instance = None
    _config_file_path: Optional[str] = None

    def __new__(cls, config_file_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file_path: Optional[str] = None):
        if self._initialized:
            return

        self._config_file_path = config_file_path or os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
            'config.json'
        )
        self.split_tunneling = SplitTunnelingConfig()
        # Other potential configurations would go here

        self._load_config()
        self._initialized = True

    def _load_config(self):
        """Loads the application configuration from a file."""
        if self._config_file_path and os.path.exists(self._config_file_path):
            try:
                with open(self._config_file_path, 'r') as f:
                    data = json.load(f)
                    if "split_tunneling" in data:
                        self.split_tunneling = SplitTunnelingConfig.from_dict(data["split_tunneling"])
            except json.JSONDecodeError as e:
                print(f"Warning: Error parsing configuration file {self._config_file_path}: {e}. Using default settings.")
            except IOError as e:
                print(f"Warning: Error loading configuration from {self._config_file_path}: {e}. Using default settings.")

    def save_config(self):
        """Saves the current application configuration to a file."""
        if not self._config_file_path:
            raise ValueError("Configuration file path not set.")
        try:
            with open(self._config_file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
        except IOError as e:
            print(f"Error saving configuration to {self._config_file_path}: {e}")

    def to_dict(self):
        return {
            "split_tunneling": self.split_tunneling.to_dict()
        }

# Initialize a global configuration instance
current_app_config = AppConfig()
