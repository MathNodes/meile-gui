import re

from base64 import b64encode
from nacl.public import PrivateKey

# AmneziaWG writes its junk parameters into the [Interface] section of the
# very same wg99.conf a plain WireGuard connection uses (see
# HandleWalletFunctions.write_wireguard_config), Jc being the first of them.
_AMNEZIA_KEY = re.compile(r'^\s*Jc\s*=', re.MULTILINE)


def is_amnezia_config(config_text: str) -> bool:
    '''True when ``config_text`` is an AmneziaWG rather than a WireGuard config.'''
    return bool(_AMNEZIA_KEY.search(config_text or ''))


class WgKey():
    
    def __init__(self):
        self._key = PrivateKey.generate()
        
    @property
    def pubkey(self) -> str:
        return b64encode(bytes(self._key.public_key)).decode("ascii")
    
    @property
    def privkey(self) -> str:
        return b64encode(bytes(self._key)).decode("ascii")
