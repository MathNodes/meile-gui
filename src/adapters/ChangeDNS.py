import platform
import re
import psutil
from os import path, chdir
import tempfile
import shlex
import shutil
import os
import subprocess
from pathlib import Path
from subprocess import Popen, TimeoutExpired, PIPE
from conf.meile_config import MeileGuiConfig


class ChangeDNS:
    def __init__(self, dns: str = "1.1.1.1"):
        self.dns = dns

    def change_dns(self):
        MeileConfig = MeileGuiConfig()
        pltfrm = platform.system()

        if pltfrm == "Linux":

            info = platform.freedesktop_os_release()
            print(info)

            if info.get("ID") == "debian":
                DEBIAN = True
            elif info.get("ID_LIKE") and "debian" in info["ID_LIKE"].split():
                DEBIAN = True
            else:
                DEBIAN = False
            
            if not DEBIAN:
                custom_dns = self.dns
                resolv_file = path.join(MeileConfig.BASEDIR, "dns")
                
                dns_file = open(resolv_file, "w")

                dns_file.write(f"nameserver {custom_dns}")
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
            
            else:
                custom_dns = self.dns
                interfaces = list(psutil.net_if_addrs().keys())
                print("Interface names:", interfaces)
                
                LOOPBACK_NAMES = ['lo', 'lo0', 'Loopback Pseudo-Interface 1']
                non_loopback_interfaces = [iface for iface in interfaces if iface not in LOOPBACK_NAMES]
                
                tmp = None
                try:
                    tmp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, prefix="set_dns_", suffix=".sh")
                    script_path = Path(tmp.name)

                    tmp.write("#!/usr/bin/env bash\n")
                    tmp.write("set -euo pipefail\n\n")

                    dns_quoted = shlex.quote(str(custom_dns))
                    resolver_cmd = None
                    if shutil.which("systemd-resolve"):
                        resolver_cmd = "systemd-resolve"
                        cmd_template = "{resolver_cmd} --set-dns={dns} -i {iface}"
                    elif shutil.which("resolvectl"):
                        resolver_cmd = "resolvectl"
                        cmd_template = "{resolver_cmd} dns {iface} {dns}"
                    else:
                        return   
                    for k, iface in enumerate(non_loopback_interfaces):
                        iface_quoted = shlex.quote(iface)
                        dns_quoted = shlex.quote(str(custom_dns))
                        tmp.write(f"# iface[{k}] = {iface}\n")
                        tmp.write(f"{cmd_template.format(resolver_cmd=resolver_cmd, iface=iface_quoted, dns=dns_quoted)}\n")

                    tmp.flush()
                    tmp.close()

                    os.chmod(script_path, 0o700)

                    subprocess.run(["pkexec", str(script_path)], check=True)

                except subprocess.CalledProcessError as exc:
                    print(f"Command failed: {exc}")
                    return
                #finally:
                #    if tmp is not None:
                #        try:
                #            script_path.unlink(missing_ok=True)
                #        except Exception:
                #            pass

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
