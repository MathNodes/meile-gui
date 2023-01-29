Meile-GUI (may•lah)
========================
[![Github All Releases](https://img.shields.io/github/downloads/mathnodes/meile-gui/total?style=for-the-badge)](https://github.com/MathNodes/meile-gui/releases)
[![GitHub license](https://img.shields.io/github/license/mathnodes/meile-gui?style=for-the-badge)](https://github.com/MathNodes/meile-gui/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/mathnodes/meile-gui?style=for-the-badge)](https://github.com/mathnodes/meile-gui/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/mathnodes/meile-gui?style=for-the-badge)](https://github.com/mathnodes/meile-gui/network)
[![GitHub issues](https://img.shields.io/github/issues/mathnodes/meile-gui?style=for-the-badge)](https://github.com/mathnodes/meile-gui/issues)

[![Downloads](https://static.pepy.tech/personalized-badge/meile-gui?period=total&units=international_system&left_color=black&right_color=orange&left_text=pip)](https://pepy.tech/project/meile-gui)
[![Downloads](https://static.pepy.tech/personalized-badge/meile-gui?period=month&units=international_system&left_color=black&right_color=orange&left_text=pip%20(month))](https://pepy.tech/project/meile-gui)

Meile dVPN GUI for Linux &amp; OS X Powered by the Sentinel Network - a blockchain decentralized VPN. 

# Pre-releases

The new versions come pre-installed with sentinel-cli so there is no requirement to install this separately. There is a also a Mac OS X (M1) port and you can read the readme in that section by switching brances to *osx*

## Mac OS X
Download the latest release [Mac OS X v0.9.3-beta](https://github.com/MathNodes/meile-gui/releases/download/0.9.3-beta/meile-gui-v0.9.3-beta-darwin-M1.zip)

Unzip. Install wireguard-tools
```shell
brew install wireguard-tools
```

Run:
```shell
sudo ./meile-gui
```

### NOTE:
pip install is not currently available for Mac OS X. We are working on bringing this as a separate packages. Also, we are working on bundling wireguard-tools into Meile GUI so we can ease the user's install process. 

## Debian .deb package

The latest version of Meile GUI comes packaged as a Debian archive. Simply download the release: [https://github.com/MathNodes/meile-gui/releases/download/0.9.3-beta/meilegui_0.9.3-beta_amd64.deb](https://github.com/MathNodes/meile-gui/releases/download/0.9.3-beta/meilegui_0.9.3-beta_amd64.deb)

and run:

```shell
sudo apt install ./meilegui_0.9.3-beta_amd64.deb
```

This release will install wireguard tools alongside Meile GUI. To run the application requires root privileges on some machines and we have enforced it within the app.

```shell
sudo meile-gui
```


## Installing via pip

Meile dVPN GUI v0.9.3-beta is now available as a pip packages as well. To install, first install wireguard-tools if you don't already have them

```
sudo apt install wireguard-tools
```

Then install via pip
```shell
pip3 install meile-gui
```

Because meile-gui enforces users to run as root (due to network device permissions of wireguard) we have enforced this in our releases. To run Meile GUI after pip install do the following:

```shell
sudo -E env PATH=$PATH meile-gui
```

This sets the root user's environment to that of the running user (the user that installed the pip packages.)

## Installing from Binary

```shell
sudo apt install wireguard-tools
```

After installing wireguard-tools, download the latest pre-release at the [Release](https://github.com/MathNodes/meile-gui/releases) page and extract:

```shell
tar xvjf meile_gui-v0.9.3-beta-linux-amd64.tar.bz2
```

Run, test, and enjoy. 

Please make comments, suggestions, and issues on the issues page here at GitHub. If you are a GitHub newb, you can join us on our Telegram [MathNodes-Telegram](http://t.me/MathNodes) or our Discord [MathNodes-Discord](https://discord.gg/HQrHXZJHQq) in the Meile channel. 

All suggestions are welcome.

