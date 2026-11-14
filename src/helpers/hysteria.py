'''Turn a Hysteria2 client config into a shareable hysteria2:// URI.

The scheme is the one documented at
https://v2.hysteria.network/docs/developers/URI-Scheme/ and understood by the
Hysteria2 clients, so the string - and the QR code drawn from it - can be
imported on a phone.

    hysteria2://[auth@]hostname[:port]/?[key=value]&... [#name]
'''

from urllib.parse import quote


def _section(config, key):
    '''The ``config[key]`` mapping, or an empty dict when it is not one.'''
    value = config.get(key)
    return value if isinstance(value, dict) else {}


def generate_hysteria_uri(config_path, name=None):
    '''Return the ``hysteria2://`` URI for the client config at ``config_path``.

    ``name`` ends up in the fragment of the URI (clients show it as the name
    of the server).  ``None`` is returned when the file carries no server
    address, so a caller can tell "nothing to share" from an URI.
    '''
    import yaml

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}

    if not isinstance(config, dict):
        return None

    server = str(config.get('server') or '').strip()
    if not server:
        return None

    tls  = _section(config, 'tls')
    obfs = _section(config, 'obfs')

    params = []
    if tls.get('insecure'):
        params.append('insecure=1')
    if tls.get('pinSHA256'):
        params.append('pinSHA256=%s' % quote(str(tls['pinSHA256']), safe=''))
    if tls.get('sni'):
        params.append('sni=%s' % quote(str(tls['sni']), safe=''))
    if obfs.get('type'):
        params.append('obfs=%s' % quote(str(obfs['type']), safe=''))
        password = _section(obfs, 'salamander').get('password')
        if password:
            params.append('obfs-password=%s' % quote(str(password), safe=''))

    # The auth lives in the userinfo component, the address in the host one.
    uri = 'hysteria2://'
    auth = str(config.get('auth') or '')
    if auth:
        uri = '%s%s@' % (uri, quote(auth, safe=''))
    uri = '%s%s/' % (uri, server)
    if params:
        uri = '%s?%s' % (uri, '&'.join(params))
    if name:
        uri = '%s#%s' % (uri, quote(str(name), safe=''))
    return uri
