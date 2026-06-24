import unittest
from unittest.mock import patch
import platform
import sys
import os

# Add src to path so we can import helpers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from helpers.splittunnel import SplitTunnel

class TestSplitTunnel(unittest.TestCase):
    @patch('platform.system')
    @patch('subprocess.run')
    def test_apply_split_tunneling_windows(self, mock_run, mock_system):
        mock_system.return_value = "Windows"
        
        apps = "C:\\test\\app1.exe, D:\\game\\app2.exe"
        SplitTunnel.apply_split_tunneling(apps, "wg99")
        
        # Check that remove was called first
        mock_run.assert_any_call(
            ["gsudo", "powershell", "-Command", 'Remove-NetFirewallRule -DisplayName "MeileSplitTunnel_*" -ErrorAction SilentlyContinue'],
            check=False
        )
        
        # Check that block all was called
        mock_run.assert_any_call(
            ["gsudo", "powershell", "-Command", 'New-NetFirewallRule -DisplayName "MeileSplitTunnel_BlockAll" -Direction Outbound -Action Block -InterfaceAlias "wg99"'],
            check=False
        )
        
        # Check app 1 allow
        mock_run.assert_any_call(
            ["gsudo", "powershell", "-Command", 'New-NetFirewallRule -DisplayName "MeileSplitTunnel_AllowApp_0" -Direction Outbound -Action Allow -Program "C:\\test\\app1.exe" -InterfaceAlias "wg99"'],
            check=False
        )
        
        # Check app 2 allow
        mock_run.assert_any_call(
            ["gsudo", "powershell", "-Command", 'New-NetFirewallRule -DisplayName "MeileSplitTunnel_AllowApp_1" -Direction Outbound -Action Allow -Program "D:\\game\\app2.exe" -InterfaceAlias "wg99"'],
            check=False
        )

    @patch('platform.system')
    @patch('subprocess.run')
    def test_apply_split_tunneling_non_windows(self, mock_run, mock_system):
        mock_system.return_value = "Linux"
        
        SplitTunnel.apply_split_tunneling("C:\\app.exe", "wg99")
        
        # Should not call subprocess on Linux
        mock_run.assert_not_called()

    @patch('platform.system')
    @patch('subprocess.run')
    def test_remove_split_tunneling(self, mock_run, mock_system):
        mock_system.return_value = "Windows"
        
        SplitTunnel.remove_split_tunneling()
        
        mock_run.assert_called_with(
            ["gsudo", "powershell", "-Command", 'Remove-NetFirewallRule -DisplayName "MeileSplitTunnel_*" -ErrorAction SilentlyContinue'],
            check=False
        )

if __name__ == '__main__':
    unittest.main()
