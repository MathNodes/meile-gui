import argparse
import os
import sys
import logging

# Configure basic logging for CLI output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Assume project root is the parent of src
# This is important for module imports if running main.py directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.conf import current_app_config, SplitTunnelingConfig
from src.vpn_service.split_tunnel import SplitTunnelingService

# Global service instance (in a real app, this might be managed by a daemon or passed around)
# The service observes the current_app_config.split_tunneling
split_tunnel_service = SplitTunnelingService(current_app_config.split_tunneling)

def show_split_tunnel_config(args):
    """Displays the current split tunneling configuration."""
    config = current_app_config.split_tunneling
    print("\n--- Split Tunneling Configuration ---")
    print(f"Mode: {config.mode}")
    print(f"Included IPs/Subnets: {config.included_ips}")
    print(f"Excluded IPs/Subnets: {config.excluded_ips}")
    print(f"Included Applications: {config.included_apps} (Note: App-based split tunneling is not fully implemented)")
    print(f"Excluded Applications: {config.excluded_apps} (Note: App-based split tunneling is not fully implemented)")
    print("-----------------------------------")

def set_split_tunnel_mode(args):
    """Sets the split tunneling mode."""
    current_app_config.split_tunneling.mode = args.mode
    current_app_config.save_config()
    print(f"Split tunneling mode set to '{args.mode}'.")
    # Propagate change to service if it's active
    split_tunnel_service.config = current_app_config.split_tunneling

def add_split_tunnel_ip(args):
    """Adds an IP address or subnet to included/excluded lists."""
    target_list = getattr(current_app_config.split_tunneling, args.type)
    changed = False
    for ip in args.ips:
        if ip not in target_list:
            target_list.append(ip)
            changed = True
            print(f"Added '{ip}' to '{args.type}'.")
        else:
            print(f"'{ip}' is already in '{args.type}'.")

    if changed:
        setattr(current_app_config.split_tunneling, args.type, target_list)
        current_app_config.save_config()
        # Propagate change to service if it's active
        split_tunnel_service.config = current_app_config.split_tunneling
    else:
        print("No changes made.")


def remove_split_tunnel_ip(args):
    """Removes an IP address or subnet from included/excluded lists."""
    target_list = getattr(current_app_config.split_tunneling, args.type)
    changed = False
    for ip in args.ips:
        if ip in target_list:
            target_list.remove(ip)
            changed = True
            print(f"Removed '{ip}' from '{args.type}'.")
        else:
            print(f"'{ip}' not found in '{args.type}'.")

    if changed:
        setattr(current_app_config.split_tunneling, args.type, target_list)
        current_app_config.save_config()
        # Propagate change to service if it's active
        split_tunnel_service.config = current_app_config.split_tunneling
    else:
        print("No changes made.")

def apply_split_tunnel_rules(args):
    """Applies the configured split tunneling rules."""
    split_tunnel_service.config = current_app_config.split_tunneling # Ensure service has latest config
    split_tunnel_service.apply_rules()
    print("Split tunneling rules application command sent.")

def disable_split_tunnel_rules(args):
    """Disables split tunneling rules."""
    split_tunnel_service.disable_rules()
    print("Split tunneling rules disable command sent.")

def main():
    parser = argparse.ArgumentParser(
        description="VPN Client CLI - Manage VPN connections and features like Split Tunneling.",
        formatter_class=argparse.RawTextHelpFormatter # For better multi-line help
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Split Tunneling commands ---
    split_parser = subparsers.add_parser('split-tunnel',
                                         help='Manage split tunneling configuration.',
                                         description='''Manage split tunneling configuration.
Split tunneling allows specific traffic to bypass the VPN tunnel,
while other traffic continues to use it.''')
    split_subparsers = split_parser.add_subparsers(dest='subcommand', help='Split Tunneling subcommands')

    # Show config
    split_show = split_subparsers.add_parser('show', help='Show current split tunneling configuration.')
    split_show.set_defaults(func=show_split_tunnel_config)

    # Set mode
    split_mode = split_subparsers.add_parser('mode', help='Set split tunneling mode.')
    split_mode.add_argument('mode', choices=['disable', 'whitelist', 'blacklist'],
                            help='''Split tunneling mode:
  - disable: All traffic either uses VPN or bypasses (based on main VPN setting).
  - whitelist: ONLY traffic to specified IPs/subnets uses the VPN.
  - blacklist: Traffic to specified IPs/subnets BYPASSES the VPN.''')
    split_mode.set_defaults(func=set_split_tunnel_mode)

    # Add IP
    split_add_ip = split_subparsers.add_parser('add-ip', help='Add IP(s)/subnet(s) to include/exclude list.')
    split_add_ip.add_argument('type', choices=['included_ips', 'excluded_ips'],
                              help='Type of list to add to (e.g., included_ips, excluded_ips).')
    split_add_ip.add_argument('ips', nargs='+', help='One or more IP addresses (e.g., 192.168.1.1) or CIDR subnets (e.g., 10.0.0.0/24).')
    split_add_ip.set_defaults(func=add_split_tunnel_ip)

    # Remove IP
    split_remove_ip = split_subparsers.add_parser('remove-ip', help='Remove IP(s)/subnet(s) from include/exclude list.')
    split_remove_ip.add_argument('type', choices=['included_ips', 'excluded_ips'],
                                help='Type of list to remove from.')
    split_remove_ip.add_argument('ips', nargs='+', help='One or more IP addresses or CIDR subnets to remove.')
    split_remove_ip.set_defaults(func=remove_split_tunnel_ip)

    # Apply rules
    split_apply = split_subparsers.add_parser('apply', help='Apply the current split tunneling rules to the system network stack.')
    split_apply.set_defaults(func=apply_split_tunnel_rules)

    # Disable rules
    split_disable = split_subparsers.add_parser('disable-rules', help='Disable active split tunneling rules and revert changes.')
    split_disable.set_defaults(func=disable_split_tunnel_rules)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
