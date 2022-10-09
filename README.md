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

The full version 1.x has been released to GitHub. Branches include **main**, **osx**, **fiat**, **osx-fiat**, **pip**. The exception is that we did not include the scrtsxx.py which contains credentials for the FIAT gateway. Please navigate the various branches to understand the different interworkings. 


## Note: 
If you have an older version (<0.9.5-beta.1) of Meile on your system, running the following is mandatory to allow newer versions to work:

```shell
sudo chown -R user:user /home/user/.meile-gui
```
where `user` is your username on your system. 

This just changes the permissions of the meile-gui configuration directory back to a regular user instead of its previous permission as root. 

## Mac OS X
Download the latest release [Mac OS X v1.1.0](https://github.com/MathNodes/meile-gui/releases/download/v1.1.0/meile-gui-v1.1.0_darwin_M1)

Run:
```shell
./meile-gui
```

Or double click on the the icon in Finder. No brew install is required for this version as we have bundled wireguard-tools for the M1 release. MacOS (intel) will be following shortly. 

### NOTE:
pip install is not currently available for Mac OS X. We are working on bringing this as a separate packages. 


## Debian .deb package

The latest version of Meile GUI comes packaged as a Debian archive. Simply download the latest release: [https://github.com/MathNodes/meile-gui/releases/](https://github.com/MathNodes/meile-gui/releases/)

and run:

```shell
sudo apt install -y ./meile-gui-v1.0.1_amd64.deb
```

This release will install wireguard tools (and resolvconf) alongside Meile GUI. To run the application requires root privileges on some machines and we have enforced it within the app.

```shell
meile-gui
```

Or goto your panel menu under Internet and there will be a clickable icon. 

## Debian Virtual Machine (.deb)

Because there were issues loading certain mesa OpenGL drivers in various Debian Virtual Machines, we have included a separate .deb archive that automatically configures the system to handle the Meile dependencies. Please use this version if you are running a Debian flavor in a virutal machine (VM).

[Debian/Ubuntu 20.04 Virtual Machine](https://github.com/MathNodes/meile-gui/releases/download/v1.1.0/meile-gui-v1.1.0_amd64_vm.deb)

## Redhat/CentOS/Fedora (.rpm)

Download the latest RPM for RedHat releases:

[RedHat RPM](https://github.com/MathNodes/meile-gui/releases/download/v1.1.0/meile-gui-1.1.0-1.fc36.x86_64.rpm)

Install the rpm from a terminal:

```shell
sudo rpm -i meile-gui-1.1.0-1.fc36.x86_64.rpm
```

This will install `meile-gui` and all its dependencies. 

## Installing via pip

Meile dVPN GUI v0.9.3-beta is now available as a pip packages as well. To install, first install wireguard-tools and meile dependencies if you don't already have them

```
sudo apt install -y  wireguard-tools openresolv mesa-utils libgl1-mesa-glx xclip
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

## Installing from Binary

```shell
sudo apt install -y wireguard-tools openresolv mesa-utils libgl1-mesa-glx xclip
```

After installing wireguard-tools, download the latest stable release at the [Release](https://github.com/MathNodes/meile-gui/releases) page and extract:

```shell
tar xvjf meile-gui-v1.1.0.tar.bz2
```

Run & enjoy!

Please make comments, suggestions, and issues on the issues page here at GitHub. If you are a GitHub newb, you can join us on our Telegram [MathNodes-Telegram](http://t.me/MathNodes) or our Discord [MathNodes-Discord](https://discord.gg/HQrHXZJHQq) in the Meile channel. 

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

# Donations

Because we are working on a small grant with no VC funding, any additional contributions to our developer team is more than certainly welcomed. It will help fund future releases. 

## DVPN (Sentinel)

`sent12v8ghhg98e2n0chyje3su4uqlsg75sh4lwcyww`

![dvpn](./img/DVPN.png)

## XMR (Monero)

`87qHJPU5dZGWaWzuoC3My5SgoQSuxh4sHSv1FXRZrQ9XZHWnfC33EX1NLv5HujpVhbPbbF9RcXXD94byT18HonAQ75b9dyR`

![xmr](./img/XMR.png)

