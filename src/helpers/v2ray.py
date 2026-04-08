import json
import base64
import sys

def generate_v2ray_uri(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Find the vmess outbound
    outbound = None
    for o in config.get('outbounds', []):
        if o.get('protocol') == 'vmess' or o.get('protocol') == 'vless':
            outbound = o
            break

    if not outbound:
        print("No VMess outbound found in config")
        sys.exit(1)

    vnext  = outbound['settings']['vnext'][0]
    user   = vnext['users'][0]
    stream = outbound.get('streamSettings', {})

    network  = stream.get('network', 'tcp')
    security = stream.get('security', 'none')

    vmess = {
        "v":    "2",
        "ps":   "My VPN",           # nickname, change as you like
        "add":  vnext['address'],
        "port": str(vnext['port']),
        "id":   user['id'],
        "aid":  str(user.get('alterId', 0)),
        "scy":  user.get('security', 'auto'),
        "net":  network,
        "type": "none",
        "host": "",
        "path": "",
        "tls":  "tls" if security == "tls" else ""
    }

    # WebSocket settings
    if network == 'ws':
        ws = stream.get('wsSettings', {})
        vmess['path'] = ws.get('path', '')
        vmess['host'] = ws.get('headers', {}).get('Host', '')

    # HTTP/2 settings
    elif network == 'h2':
        h2 = stream.get('httpSettings', {})
        vmess['path'] = h2.get('path', '')
        hosts = h2.get('host', [])
        vmess['host'] = hosts[0] if hosts else ''

    # gRPC settings
    elif network == 'grpc':
        grpc = stream.get('grpcSettings', {})
        vmess['path'] = grpc.get('serviceName', '')
        vmess['type'] = 'gun'

    # TCP with HTTP obfs
    elif network == 'tcp':
        tcp = stream.get('tcpSettings', {})
        header = tcp.get('header', {})
        if header.get('type') == 'http':
            vmess['type'] = 'http'

    # TLS SNI
    tls_settings = stream.get('tlsSettings', {})
    if not vmess['host'] and tls_settings.get('serverName'):
        vmess['host'] = tls_settings['serverName']

    json_str  = json.dumps(vmess, separators=(',', ':'))
    b64       = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    uri       = f"{o.get('protocol')}://{b64}"

    #print("\n✅ VMess URI:\n")
    return uri
