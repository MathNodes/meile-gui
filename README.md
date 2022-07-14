Meile-GUI (may•lah)
========================
Meile dVPN GUI for Linux &amp; OS X Powered by the Sentinel Network

# Install
Meile-GUI is now available via pip

```shell
pip3 install meile-gui
```

Run:

```shell
sudo -E env PATH=$PATH meile_gui
```

Enjoy!


# Pre-releases
We have released the first major version of the Meile-gui pre-release, v0.9.1-alpha.1
This version has sentinel-cli preinstalled, so all that is needed is to install wireguard

```shell
sudo apt install wireguard
```

After installing wireguard, download the pre-release at the [Release](https://github.com/MathNodes/meile-gui/releases) page and extract:

```shell
tar xvjf meile-gui-0.9.1-alpha.1-amd64-linux.tar.bz2
```

Run, test, and enjoy. 

Please make comments, suggestions, and issues on the issues page here at GitHub. If you are a GitHub newb, you can join us on our Telegram [MathNodes-Telegram](http://t.me/MathNodes) or our Discord [MathNodes-Discord](https://discord.gg/HQrHXZJHQq) in the Meile channel. 

All suggestions are welcome.

## Install from source
The following is how to install and run Meile-GUI from source on Linux machines

```shell
git clone https://github.com/MathNodes/meile-gui
cd meile-gui
python3 setup.py install
```

**RUN:**
```shell
sudo -E env PATH=$PATH meile_gui
```

