from base64 import b64encode
from nacl.public import PrivateKey
 
class WgKey():
    
    def __init__(self):
        self._key = PrivateKey.generate()
        
    @property
    def pubkey(self) -> str:
        return b64encode(bytes(self._key.public_key)).decode("ascii")
    
    @property
    def privkey(self) -> str:
        return b64encode(bytes(self._key)).decode("ascii")