# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="meile-gui",
    version="0.13.3.0",
    description="Meile dVPN powered by the Sentinel Network",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="MathNodes",
    author_email="freQniK@mathnodes.com",
    url="https://meile.app",
    license="GNU General Public License (GPL)",
    keywords="vpn, dvpn, sentinel, crypto, gui, privacy, security, decentralized ",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Environment :: X11 Applications",
        "Environment :: MacOS X",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Networking",
        "Topic :: Internet",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "kivymd",
        "pydash",
        "treelib==1.6.1",
        "kivyoav",
        "pexpect",
        "qrcode",
        "save_thread_result",
        "stripe",
        "screeninfo",
        "mapview",
        "psutil",
        "unidecode",
        "dnspython",
        "bip_utils",
        "toml",
        "netifaces",
        "btcpay",

        # "cosmpy",  # Replaced by sentinel-python-sdk + mospy

        # "sentinel_protobuf==0.3.1",
        # The conflict is caused by:
        #     meile-gui 0.13.3.0 depends on sentinel_protobuf==0.3.1
        #     sentinel-sdk 0.0.1 depends on sentinel-protobuf==0.3.3

        "keyrings.cryptfile",
        "mnemonic",
        "bech32",
        "pywgkey",
        "sentinel-sdk",
        "bcrypt",
        "jwcrypto"
    ],
    package_data={
        "conf": ["config/config.ini", "config/dnscrypt-proxy.toml"],
        "bin": ["sentinelcli", "warp-cli", "warp-svc", "tun2socks", "v2ray"],
        "awoc": ["data/world.json"],
        "fonts": ["Roboto-BoldItalic.ttf", "arial-unicode-ms.ttf", "mplus-2c-bold.ttf"],
        "imgs": ["*.png", "tenor.gif", "flags/*.png"],
        "kv": ["meile.kv"],
        "main": ["icon.png"],
        "utils": ["coinimg/dvpn.png", "fonts/Roboto-BoldItalic.ttf"],
    },
    entry_points={
        "console_scripts": ["meile-gui = main.meile_gui:main"],
    },
)
