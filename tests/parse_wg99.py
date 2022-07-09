import wgconfig
from os import path
BASEDIR  = path.join(path.expanduser('~'), '.sentinelcli')

wg = wgconfig.WGConfig(path.join(BASEDIR, 'wg99.conf'))
wg.read_file()

private_key = wg.interface['PrivateKey']
peers_keys = wg.peers.keys()
for k in peers_keys:
    public_key = k
    
    
endpoint = wg.peers[public_key]['Endpoint']
srv_ip,srv_port = endpoint.split(':')    
local_ip = wg.interface['Address']

print(private_key)
print(public_key)
print(srv_ip)
print(srv_port)
print(local_ip[0])