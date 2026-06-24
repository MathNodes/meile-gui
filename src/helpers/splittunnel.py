import subprocess
import platform
import logging

class SplitTunnel:
    @staticmethod
    def apply_split_tunneling(apps_str, interface_alias="wg99"):
        if platform.system() != "Windows":
            return
            
        # First, remove any existing split tunnel rules
        SplitTunnel.remove_split_tunneling()
        
        if not apps_str:
            return
            
        apps = [app.strip() for app in apps_str.split(',') if app.strip()]
        if not apps:
            return
            
        try:
            # Block all outbound traffic on the VPN interface by default
            subprocess.run(
                ["gsudo", "powershell", "-Command", f'New-NetFirewallRule -DisplayName "MeileSplitTunnel_BlockAll" -Direction Outbound -Action Block -InterfaceAlias "{interface_alias}"'],
                check=False
            )
            
            # Allow specific apps on the VPN interface
            for i, app in enumerate(apps):
                app = app.replace('"', '""')
                cmd = f'New-NetFirewallRule -DisplayName "MeileSplitTunnel_AllowApp_{i}" -Direction Outbound -Action Allow -Program "{app}" -InterfaceAlias "{interface_alias}"'
                subprocess.run(["gsudo", "powershell", "-Command", cmd], check=False)
                
            logging.info(f"Split tunneling applied for {len(apps)} apps on {interface_alias}")
        except Exception as e:
            logging.error(f"Failed to apply split tunneling: {e}")

    @staticmethod
    def remove_split_tunneling():
        if platform.system() != "Windows":
            return
            
        try:
            subprocess.run(
                ["gsudo", "powershell", "-Command", 'Remove-NetFirewallRule -DisplayName "MeileSplitTunnel_*" -ErrorAction SilentlyContinue'],
                check=False
            )
        except Exception:
            pass
