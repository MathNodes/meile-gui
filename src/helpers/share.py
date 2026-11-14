'''The string and the QR code used to share a running connection.

Both the "Connected!" dialog of the main screen and the standalone
"Connection Sharing" dialog of the QR button are filled from here, so the two
places cannot drift apart.
'''

import json
from os import path

from typedef.konstants import ConfParams

from helpers.hysteria import generate_hysteria_uri
from helpers.v2ray import generate_v2ray_uri
from helpers.wireguard import is_amnezia_config
from helpers.xray import generate_xray_uri, is_xray_config
from utils.qr import QRCode

WIREGUARD = "WireGuard"
AMNEZIAWG = "AmneziaWG"
V2RAY     = "V2Ray"
XRAY      = "XRay"
HYSTERIA2 = "Hysteria2"

# Short codes of the radio buttons of <ShareTypeDialog> in meile.kv.
SHORTCUTS = {"wg": WIREGUARD, "awg": AMNEZIAWG, "v2": V2RAY, "xr": XRAY,
             "hy2": HYSTERIA2}

_NAMES = {name.lower(): name for name in SHORTCUTS.values()}

WG_CONF_PATH       = path.join(ConfParams.KEYRINGDIR, "wg99.conf")
V2RAY_CONF_PATH    = path.join(ConfParams.KEYRINGDIR, "v2ray_config.json")
HYSTERIA_CONF_PATH = path.join(ConfParams.KEYRINGDIR, "hysteria.yml")

WIREGUARD_WARNING = (
    'Scan the QR code or input the config with the official WireGuard app. '
    'You must do this before you disconnect in Meile. '
    'https://dvpn.my/wireguard'
)
AMNEZIAWG_WARNING = (
    'Scan the QR code or import the config string into the AmneziaWG app. '
    'You must do this before you disconnect in Meile. '
    'https://dvpn.my/amnezia'
)
V2RAY_WARNING = (
    'Scan the QR code or import the URI string into the V2RayNG mobile app. '
    'You must do this before you disconnect in Meile. '
    'https://dvpn.my/v2ray'
)
XRAY_WARNING = (
    'Scan the QR code or import the URI string into an XRay client '
    '(v2rayNG, NekoBox, ...). You must do this before you disconnect in Meile. '
    'https://dvpn.my/xray'
)
HYSTERIA2_WARNING = (
    'Scan the QR code or import the hysteria2:// URI into a Hysteria2 client. '
    'You must do this before you disconnect in Meile. '
    'https://dvpn.my/hysteria'
)
NOT_AVAILABLE_WARNING = (
    'Quick-connect sharing is only available for WireGuard, AmneziaWG, '
    'V2Ray, XRay and Hysteria2.'
)


def _canonical(protocol):
    '''The protocol name behind a radio button code or a loose spelling.'''
    if not protocol:
        return None
    protocol = str(protocol).strip()
    if protocol in SHORTCUTS:
        return SHORTCUTS[protocol]
    return _NAMES.get(protocol.lower(), protocol)


def _wireguard_config(amnezia):
    '''wg99.conf when it belongs to the requested protocol, else ``None``.

    WireGuard and AmneziaWG share the same file, so the junk parameters tell
    which of the two protocols is actually connected.
    '''
    try:
        with open(WG_CONF_PATH, 'r') as f:
            config = f.read()
    except OSError as e:
        print("Share: %s could not be read: %s" % (WG_CONF_PATH, e))
        return None
    config = config.replace("127.0.0.1,", "")
    if is_amnezia_config(config) != amnezia:
        return None
    return config


def _hysteria_uri(moniker):
    '''hysteria2:// URI of the running Hysteria2 connection, else ``None``.'''
    if not path.isfile(HYSTERIA_CONF_PATH):
        return None
    try:
        return generate_hysteria_uri(HYSTERIA_CONF_PATH, moniker)
    except Exception as e:
        # A config the YAML parser chokes on must not cost the dialog.
        print("Share: hysteria2 URI could not be built: %s" % e)
        return None


def _proxy_config():
    '''The parsed v2ray_config.json, ``None`` when it cannot be read.

    V2Ray and XRay both write this file, so a caller has to know whose config
    it is (is_xray_config of helpers.xray) before reading anything out of it.
    '''
    try:
        with open(V2RAY_CONF_PATH, 'r') as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print("Share: %s could not be read: %s" % (V2RAY_CONF_PATH, e))
        return None


def _v2ray_uri():
    '''URI of the running V2Ray connection, else ``None``.'''
    config = _proxy_config()
    if not config or is_xray_config(config):
        return None
    try:
        return generate_v2ray_uri(V2RAY_CONF_PATH)
    except (Exception, SystemExit) as e:
        # generate_v2ray_uri exits when the file has no vless/vmess outbound;
        # a config the dialog cannot read must not close the application.
        print("Share: v2ray URI could not be built: %s" % e)
        return None


def _xray_uri(moniker):
    '''URI of the running XRay connection, else ``None``.'''
    if not path.isfile(V2RAY_CONF_PATH):
        return None
    try:
        return generate_xray_uri(V2RAY_CONF_PATH, moniker)
    except Exception as e:
        print("Share: xray URI could not be built: %s" % e)
        return None


def share_details(protocol, moniker=None):
    '''Return ``(string, qr_image_path, warning)`` for ``protocol``.

    ``string`` is the config or URI shown in the dialog, ``qr_image_path`` a
    freshly rendered QR code for it and ``warning`` the hint printed below.
    ``protocol`` is a protocol name (NodeKeys.ProtocolTypes) or one of the
    short codes of the sharing radio buttons; ``moniker`` names the node in
    the QR code / URI when one is known.
    '''
    protocol = _canonical(protocol)
    Qr = QRCode()

    if protocol in (WIREGUARD, AMNEZIAWG):
        amnezia = protocol == AMNEZIAWG
        warning = AMNEZIAWG_WARNING if amnezia else WIREGUARD_WARNING
        config  = _wireguard_config(amnezia)
        if config is None:
            return ("Connect with %s in Meile first." % protocol,
                    Qr.generate_qr_code("NULL", "wireguard"),
                    warning)
        return (config,
                Qr.generate_wg_qr_code(WG_CONF_PATH, moniker or protocol),
                warning)

    if protocol == V2RAY:
        uri = _v2ray_uri()
        if not uri:
            return ("Connect with V2Ray in Meile first.",
                    Qr.generate_qr_code("NULL", "v2ray"),
                    V2RAY_WARNING)
        return (uri, Qr.generate_qr_code(uri, "v2ray"), V2RAY_WARNING)

    if protocol == XRAY:
        uri = _xray_uri(moniker)
        if not uri:
            return ("Connect with XRay in Meile first.",
                    Qr.generate_qr_code("NULL", "v2ray"),
                    XRAY_WARNING)
        return (uri, Qr.generate_qr_code(uri, "v2ray"), XRAY_WARNING)

    if protocol == HYSTERIA2:
        uri = _hysteria_uri(moniker)
        if not uri:
            return ("Connect with Hysteria2 in Meile first.",
                    Qr.generate_qr_code("NULL", "v2ray"),
                    HYSTERIA2_WARNING)
        return (uri, Qr.generate_qr_code(uri, "v2ray"), HYSTERIA2_WARNING)

    return ("Quick-connect QR codes are not available for %s."
            % (protocol or "this protocol"),
            Qr.generate_qr_code("NULL", "v2ray"),
            NOT_AVAILABLE_WARNING)
