import platform
import re
import psutil
from os import path, chdir
from subprocess import Popen, TimeoutExpired, PIPE
from conf.meile_config import MeileGuiConfig


class ChangeDNS:
    def __init__(self, dns: str = "1.1.1.1"):
        self.dns = dns

    def change_dns(self):
        MeileConfig = MeileGuiConfig()
        pltfrm = platform.system()

        if pltfrm == "Linux":
            resolv_file = path.join(MeileConfig.BASEDIR, "dns")
            dns_file = open(resolv_file, "w")

            dns_file.write(f"nameserver {self.dns}")
            dns_file.flush()
            dns_file.close()

            cmd = (
                "pkexec bash -c 'cat %s | resolvconf -a wg99 && resolvconf -u'"
                % resolv_file
            )

            try:
                proc = Popen(cmd, shell=True)
                proc.wait(timeout=60)
            except TimeoutExpired as e:
                print(str(e))

            proc_out, proc_err = proc.communicate()

        elif pltfrm == "Darwin":
            # sudo /usr/sbin/networksetup -listnetworkserviceorder
            # sudo /usr/sbin/networksetup -setdnsservers Wi-Fi 1.1.1.1

            # I don't know if we need some privileged permission pkexec(?)
            osx_interface = "^\([*0-9)]+\)"
            cmd = "/usr/sbin/networksetup -listnetworkserviceorder"
            try:
                proc = Popen(cmd, shell=True, stdout=PIPE)
                proc.wait(timeout=60)
                proc_out, proc_err = proc.communicate()

                parts = proc_out.decode("utf-8").split("\n")
                for p in parts:
                    if re.search(osx_interface, p) != None:  # Founded a interface
                        interface = re.sub(osx_interface, "", p).strip()
                        if p.startswith("(*)") is False:
                            # print(f"{interface} is enabled")
                            cmd = f"/usr/sbin/networksetup -setdnsservers {interface} {self.dns}"
                            try:
                                proc = Popen(cmd, shell=True)
                                proc.wait(timeout=60)
                            except TimeoutExpired as e:
                                print(f"Exception on interface: {interface}, {e}")
            except TimeoutExpired as e:
                print(str(e))

        elif pltfrm == "Windows":
            gsudo = path.join(MeileConfig.BASEBINDIR, "gsudo.exe")

            """
            cmd = "netsh interface ip show config"
            proc = Popen(cmd, shell=True, stdout=PIPE)
            proc.wait(timeout=60)
            proc_out, proc_err = proc.communicate()
            """

            for interface in psutil.net_if_addrs().keys():
                # Filter interface, tun(nnel) or w(ire)g(uard)99
                if "tun" in interface.lower() or "wg99" in interface.lower():
                    cmd = [
                        gsudo,
                        f'netsh interface ipv4 set dns name="{interface}" static {self.dns}',
                    ]
                    chdir(MeileConfig.BASEBINDIR)
                    try:
                        proc = Popen(cmd, shell=True)
                        proc.wait(timeout=60)
                    except TimeoutExpired as e:
                        print(str(e))
                    proc_out, proc_err = proc.communicate()
                    chdir(MeileConfig.BASEDIR)
