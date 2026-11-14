'''Turn an XRay client config into a shareable URI.

Meile's XRay client (see ``cli.wallet.write_xray_config``) writes its config
into ``~/.meile-gui/v2ray_config.json`` - the file of the V2Ray client - so the
outbound of that file is what the mobile clients have to import:

    vless://<id>@<host>:<port>?<params>#<name>
    vmess://<base64 of the v2rayN JSON>
    trojan://<password>@<host>:<port>?<params>#<name>
    ss://<base64url of "method:password">@<host>:<port>#<name>

TLS certificates are pinned by the client config itself, which none of those
schemes can express; a client importing the URI validates the certificate on
its own (Reality, the usual replacement for a pin, is carried by the
parameters).
'''

import base64
import json
from urllib.parse import quote

# Tags of the XRay client config (cli.wallet.write_xray_config).  The V2Ray
# client tags the same objects "vmess" and "api", which is how the two configs
# sharing one file are told apart.
OUTBOUND_TAG = 'proxy-out'
INBOUND_TAG  = 'api-in'

# XRay transport name -> "type" of the shared URI
_TRANSPORT = {
    'websocket':   'ws',
    'tcp':         'tcp',
    'raw':         'tcp',
    'grpc':        'grpc',
    'httpupgrade': 'httpupgrade',
    'xhttp':       'xhttp',
    'h2':          'h2',
    'http':        'h2',
}

# "type" of the shared URI -> key of the transport settings in streamSettings
# (XRay names the websocket settings "wsSettings", not "websocketSettings").
_SETTINGS = {
    'ws':          'wsSettings',
    'httpupgrade': 'httpupgradeSettings',
    'xhttp':       'xhttpSettings',
    'h2':          'httpSettings',
    'grpc':        'grpcSettings',
    'tcp':         'tcpSettings',
}

# Outbound protocols the mobile clients understand
_SUPPORTED = ('vless', 'vmess', 'trojan', 'shadowsocks', 'shadowsocks-2022')


def _mapping(value):
    '''``value`` when it is a mapping, an empty dict otherwise.'''
    return value if isinstance(value, dict) else {}


def _host(address):
    '''``address`` as it belongs into the authority of an URI.

    IPv6 literals have to be bracketed there (``[::1]:443``), while the vmess
    JSON keeps them bare, so this is only used for URIs.
    '''
    address = str(address)
    if ':' in address and not address.startswith('['):
        return '[%s]' % address
    return address


def is_xray_config(config):
    '''True when the parsed config was written by the XRay client of Meile.

    V2Ray and XRay share ``v2ray_config.json``; the tags of the XRay client
    are the markers the V2Ray client does not use.
    '''
    if not isinstance(config, dict):
        return False
    for outbound in config.get('outbounds') or []:
        if _mapping(outbound).get('tag') == OUTBOUND_TAG:
            return True
    for inbound in config.get('inbounds') or []:
        if _mapping(inbound).get('tag') == INBOUND_TAG:
            return True
    return False


def _outbound(config):
    '''The proxy outbound of the config, ``None`` when it has none.'''
    outbounds = [_mapping(o) for o in config.get('outbounds') or []]
    for outbound in outbounds:
        if outbound.get('tag') == OUTBOUND_TAG:
            return outbound
    return outbounds[0] if outbounds else None


def _server(outbound):
    '''``(address, port, user)`` of the outbound.

    vless/vmess keep host and credentials in ``settings.vnext``, trojan and
    shadowsocks keep both in ``settings.servers``.  ``user`` is empty when the
    config carries none.
    '''
    settings = _mapping(outbound.get('settings'))

    vnext = settings.get('vnext') or []
    if vnext:
        vnext = _mapping(vnext[0])
        users = vnext.get('users') or []
        return (vnext.get('address'), vnext.get('port'),
                _mapping(users[0]) if users else {})

    servers = settings.get('servers') or []
    if servers:
        server = _mapping(servers[0])
        return server.get('address'), server.get('port'), server

    return None, None, {}


def _transport_params(stream):
    '''The ``type`` parameters of ``streamSettings``, in client order.'''
    network   = str(stream.get('network') or 'tcp').lower()
    transport = _TRANSPORT.get(network, network)
    params    = [('type', transport)]

    if transport in ('ws', 'httpupgrade', 'xhttp', 'h2'):
        settings = _mapping(stream.get(_SETTINGS[transport]))
        host = _mapping(settings.get('headers')).get('Host')
        if not host and settings.get('host'):
            # the h2 settings keep the host in a list
            host = settings['host']
            host = host[0] if isinstance(host, list) else host
        if host:
            params.append(('host', str(host)))
        if settings.get('path'):
            params.append(('path', str(settings['path'])))
    elif transport == 'grpc':
        service = _mapping(stream.get(_SETTINGS['grpc'])).get('serviceName')
        if service:
            params.append(('serviceName', str(service)))
    elif transport == 'tcp':
        header = _mapping(_mapping(stream.get(_SETTINGS['tcp'])).get('header'))
        if header.get('type') == 'http':
            params.append(('headerType', 'http'))

    return params


def _security_params(stream):
    '''The TLS / Reality parameters of ``streamSettings``.'''
    security = str(stream.get('security') or 'none').lower()
    params   = [('security', security)]

    if security == 'reality':
        reality = _mapping(stream.get('realitySettings'))
        params.append(('fp', str(reality.get('fingerprint') or 'chrome')))
        if reality.get('serverName'):
            params.append(('sni', str(reality['serverName'])))
        if reality.get('publicKey'):
            params.append(('pbk', str(reality['publicKey'])))
        if reality.get('shortId'):
            params.append(('sid', str(reality['shortId'])))
        if reality.get('spiderX'):
            params.append(('spx', str(reality['spiderX'])))
    elif security == 'tls':
        tls = _mapping(stream.get('tlsSettings'))
        if tls.get('serverName'):
            params.append(('sni', str(tls['serverName'])))
        if tls.get('fingerprint'):
            params.append(('fp', str(tls['fingerprint'])))
        if tls.get('alpn'):
            params.append(('alpn', ','.join(str(a) for a in tls['alpn'])))
        if tls.get('allowInsecure'):
            params.append(('allowInsecure', '1'))

    return params


def _query(params):
    '''``params`` as query string, skipping the empty ones.'''
    return '&'.join('%s=%s' % (key, quote(str(value), safe=''))
                    for key, value in params if value not in (None, ''))


def _fragment(name):
    '''``name`` as fragment of a URI (the name the client shows).'''
    return '#%s' % quote(str(name), safe='') if name else ''


def _vless_uri(address, port, user, stream, name):
    uuid = user.get('id')
    if not uuid:
        return None
    params = [('encryption', 'none')]
    params += _security_params(stream)
    params += _transport_params(stream)
    flow = user.get('flow')
    if flow and flow != 'none':
        params.append(('flow', str(flow)))
    return 'vless://%s@%s:%s?%s%s' % (quote(str(uuid), safe=''), _host(address),
                                      port, _query(params), _fragment(name))


def _vmess_uri(address, port, user, stream, name):
    '''The vmess URI of v2rayN / v2rayNG - a base64 encoded JSON object.'''
    uuid = user.get('id')
    if not uuid:
        return None

    security  = dict(_security_params(stream))
    transport = dict(_transport_params(stream))

    vmess = {
        'v':    '2',
        'ps':   str(name or 'XRay'),
        'add':  str(address),
        'port': str(port),
        'id':   str(uuid),
        'aid':  str(user.get('alterId', 0)),
        'scy':  str(user.get('security') or 'auto'),
        'net':  transport.get('type', 'tcp'),
        'type': transport.get('headerType', 'none'),
        'host': transport.get('host', ''),
        'path': transport.get('path', ''),
        # v2rayN carries Reality as a TLS flavour of its own
        'tls':  '' if security.get('security', 'none') == 'none'
                else security['security'],
        'sni':  security.get('sni', ''),
        'alpn': security.get('alpn', ''),
        'fp':   security.get('fp', ''),
        'pbk':  security.get('pbk', ''),
        'sid':  security.get('sid', ''),
        'spx':  security.get('spx', ''),
    }

    encoded = json.dumps(vmess, separators=(',', ':'))
    return 'vmess://%s' % base64.b64encode(encoded.encode('utf-8')).decode('utf-8')


def _trojan_uri(address, port, user, stream, name):
    password = user.get('password')
    if not password:
        return None
    params = _security_params(stream) + _transport_params(stream)
    return 'trojan://%s@%s:%s?%s%s' % (quote(str(password), safe=''),
                                       _host(address), port, _query(params),
                                       _fragment(name))


def _shadowsocks_uri(address, port, user, name):
    method   = user.get('method')
    password = user.get('password')
    if not method or not password:
        return None
    credentials = '%s:%s' % (method, password)
    # SIP002 keeps the credentials in unpadded base64
    encoded = base64.urlsafe_b64encode(credentials.encode('utf-8'))
    encoded = encoded.decode('utf-8').rstrip('=')
    return 'ss://%s@%s:%s%s' % (encoded, _host(address), port, _fragment(name))


def generate_xray_uri(config_path, name=None):
    '''Return the share URI of the XRay client config at ``config_path``.

    ``name`` names the entry in the client (the fragment of the URI, or the
    ``ps`` field of a vmess one).  ``None`` is returned when the file is not an
    XRay client config or its outbound is one the mobile clients cannot
    import, so a caller can tell "nothing to share" from an URI.
    '''
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (OSError, ValueError) as e:
        print("XRay: %s could not be read: %s" % (config_path, e))
        return None

    if not is_xray_config(config):
        return None

    outbound = _outbound(config)
    if outbound is None:
        return None

    protocol = str(outbound.get('protocol') or '').lower()
    if protocol not in _SUPPORTED:
        print("XRay: %s outbound cannot be shared" % protocol)
        return None

    address, port, user = _server(outbound)
    if not address or not port:
        return None

    stream = _mapping(outbound.get('streamSettings'))

    uri = None
    if protocol == 'vless':
        uri = _vless_uri(address, port, user, stream, name)
    elif protocol == 'vmess':
        uri = _vmess_uri(address, port, user, stream, name)
    elif protocol == 'trojan':
        uri = _trojan_uri(address, port, user, stream, name)
    else:
        uri = _shadowsocks_uri(address, port, user, name)

    if not uri:
        # e.g. a shadowsocks outbound without method/password, which the
        # client config of Meile writes as a vnext entry
        print("XRay: no URI could be built for the %s outbound" % protocol)
    return uri

