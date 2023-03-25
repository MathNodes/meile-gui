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

# Full Version

The full version 1.5.1 has been released to GitHub. Branches include **main**, **osx**, **windows**, **fiat**, **osx-fiat**, **pip**. The exception is that we did not include the scrtsxx.py which contains credentials for the FIAT gateway. Please navigate the various branches to understand the different interworkings. 


## Windows

We finally produced a workable Windows build. The current release is version **1.4.1** and includes the changes as seen in the [CHANGELOG](./CHANGELOG.md)

This release is a pre-relase for now until we have sufficient testing from the dVPN community. Our ongoing efforts will enhance this release with more functionality as time continues. We are a small team, so be patient while we search for new features and solutions.

Download: [Meile for Windows (v1.4.1)](https://github.com/MathNodes/meile-gui/releases/tag/v1.4.1)


## Mac OS X
Download the latest release as a DMG: [Mac OS X v1.5.1](https://github.com/MathNodes/meile-gui/releases/tag/v1.5.1)

The OS X M1/M2 and Intel builds are packaged as a disk image (DMG). To install, simply download the correct DMG for your architecture (Intel or Apple Silicon). Double click on the DMG file and move the Meile app bundle to your desktop or to the Applications folder. 

You may need to press "control" + click to open it as we have not yet been accepted to the Apple Developer program in order to sign our applications and make them ready for the Apple Store. The above method will present a dialog warning you the app was downloaded from the internet. Just approve this and give it a short time and the app will open. 

### NOTE:
pip install is not currently available for Mac OS X. We are working on bringing this as a separate packages. 


## Debian .deb package

The latest version of Meile GUI comes packaged as a Debian archive. Simply download the latest release: [https://github.com/MathNodes/meile-gui/releases/](https://github.com/MathNodes/meile-gui/releases/)

and run apt for your build:

```shell
sudo apt install -y ./meile-gui-v1.5.1_ubuntu22.04_amd64.deb
```

This release will install wireguard tools, resolvconf, curl, and net-tools alongside the Meile GUI. To connect to nodes or disconnect requires "sudo" privileges. You will be prompted by your system dialog to enter your username's password to give authorization to complete the connection. This is due to how Linux handles permissions with regards to network interfaces. 

```shell
meile-gui
```

Or goto your panel menu under Internet and there will be a clickable icon. 

## Debian Virtual Machine (.deb)

Because there were issues loading certain mesa OpenGL drivers in various Debian Virtual Machines, we have included a separate .deb archive that automatically configures the system to handle the Meile dependencies. Please use this version if you are running a Debian flavor in a virutal machine (VM).

[Debian/Ubuntu 20.04 Virtual Machine](https://github.com/MathNodes/meile-gui/releases/download/v1.5.1/meile-gui-v1.5.1_ubuntu2004_amd64_vm.deb)

[Debian/Ubuntu 22.04 Virtual Machine](https://github.com/MathNodes/meile-gui/releases/download/v1.5.1/meile-gui-v1.5.1_ubuntu2204_amd64_vm.deb)

## Redhat/CentOS/Fedora (.rpm)

Download the latest RPM for RedHat releases:

[RedHat RPM (fc36)](https://github.com/MathNodes/meile-gui/releases/download/v1.5.1/meile-gui-v1.5.1-1.fc36.x86_64.rpm)

[RedHat RPM (fc37)](https://github.com/MathNodes/meile-gui/releases/download/v1.5.1/meile-gui-v1.5.1-1.fc37.x86_64.rpm)


Install the rpm from a terminal via *dnf* (**RECOMMENDED**):
```shell
sudo dnf install meile-gui-v1.4.1-1.fc36.x86_64.rpm
```

or via *rpm*:

```shell
sudo rpm -i meile-gui-v1.4.1-1.fc36.x86_64.rpm
```

*dnf* is **recommended** as it will install all dependencies for Meile to function correctly.


## Installing via pip

Meile dVPN GUI v0.11.2 is now available as a pip packages as well. These are pre-releases scheduled to be built into a binary. To install, first install **wireguard-tools** and **Meile** dependencies if you don't already have them

```
sudo apt install -y  wireguard-tools openresolv mesa-utils libgl1-mesa-glx xclip python3-devel curl net-tools
```

Then install via pip
```shell
pip3 install meile-gui
```

Upgrade via pip

```shell
pip3 install meile-gui --upgrade
```

To run Meile GUI after pip install do the following:

```shell
meile-gui
```

### NOTE:

The FIAT gateway is not included in the pip package. This is due to certain credentials needing to remain secret for OPSEC reasons. The pip package will continue to get updated with the FIAT release in bug fixes and feature additions. 

We consider the pip releases to be pre-releases of the compiled binaries. Pip is considered the bleeding edge of Meile releases

## Help

Please make comments, suggestions, and issues on the issues page here at GitHub. If you are a GitHub newb, you can join us in our various open messaging channels:

* Telegram [MathNodes-Telegram](http://t.me/MathNodes)
* Discord [MathNodes-Discord](https://discord.gg/HQrHXZJHQq) in the Meile channel, 
* Session [Session Open Group](http://session.mathnodes.com/mathnodes-dvpn-oxen-dero?public_key=8585d7f3fb44f4f40fb1685a0cf10627dd24467a9379eafbb7ba08e5607e9c21)

Session:
![session](./img/session_qr.png)


All suggestions are welcome.


## Creating a Binary for your distribution:

In order to create a binary for your distribution some packages need to be installed first.

Pyinstaller:
```shell
pip3 install pyinstaller
```

Install a python virtualenv:

```shell
sudo apt install python3-virtualenv
```

Then clone the repo:
```shell
git clone https://github.com/MathNodes/meile-gui
```

Switch to the pip branch as this is the one without FIAT gateway
```
cd meile-gui && git checkout pip
```

Then run a python virtual environment and install meile-gui. This will find all the dependencies for **meile-gui**.

```shell
python3 -m venv meile-gui && \
source meile-gui/bin/activate && \ 
pip install -e .
```

Once meile-gui and it's dependencies have been installed within the python virutal environment, a binary release can be created:

```
bash pyinstaller.cmd
```

That's it. Navigate to the `dist` folder where the binary will be. 

### Windows

For windows, install the necessary pip packages found in `setup.py` and run the following with `pyinstaller`

```shell
pyinstaller meile_gui.spec
```

This will build the binary found in the `dist` directory of the Meile tree. 

# Donations

Because we are working on a small grant with no VC funding, any additional contributions to our developer team is more than certainly welcomed. It will help fund future releases. 

## BTC (Bitcoin)

`bc1qtvc9l3cr9u4qg6uwe6pvv7jufvsnn0xxpdyftl`

![BTC](./img/BTC.png)

## DVPN (Sentinel)

`sent12v8ghhg98e2n0chyje3su4uqlsg75sh4lwcyww`

![dvpn](./img/DVPN.png)

## XMR (Monero)

`87qHJPU5dZGWaWzuoC3My5SgoQSuxh4sHSv1FXRZrQ9XZHWnfC33EX1NLv5HujpVhbPbbF9RcXXD94byT18HonAQ75b9dyR`

![xmr](./img/XMR.png)

## ARRR (Pirate Chain)

`zs1gn457262c52z5xa666k77zafqmke0hd60qvc38dk48w9fx378h4zjs5rrwnl0x8qazj4q3x4svz`

![ARRR](./img/ARRR.png)


