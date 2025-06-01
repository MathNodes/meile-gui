from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import hashlib

from fiat.stripe_pay.dist import scrtsxx

class SecureSeed():
    def xor_password(self, password, xor_key=scrtsxx.XORKEY):
        password_bytes = password.encode()
        xor_key = xor_key * (len(password_bytes) // len(xor_key)) + xor_key[:len(password_bytes) % len(xor_key)]
        return bytes([x ^ y for x, y in zip(password_bytes, xor_key)])
    
    def xor_b64(self, password):
        return base64.b64encode(self.xor_base64(password)).decode()
    
    def blake2_hash(self, data):
        return hashlib.blake2b(data).digest()
    
    def derive_key(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password)
        return key, salt
    
    def encrypt_seed(self, data, password):
        xor_result = self.xor_password(password)
        hashed_password = self.blake2_hash(xor_result)
        
        key, salt = self.derive_key(hashed_password)
        iv = os.urandom(16)  
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()  # 128-bit block size
        padded_data = padder.update(data.encode()) + padder.finalize()
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        combined = salt + iv + encrypted_data
        return base64.b64encode(combined).decode()
    
    def decrypt_seed(self, encrypted_data, password):
        try:
            combined = base64.b64decode(encrypted_data)
        except base64.binascii.Error:
            raise ValueError("Invalid base64-encoded string")
    
        if len(combined) < 32:  
            raise ValueError("Invalid encrypted data")
    
        salt = combined[:16]
        iv = combined[16:32]
        encrypted_data = combined[32:]
    
        xor_result = self.xor_password(password)
        hashed_password = self.blake2_hash(xor_result)
    
        key, _ = self.derive_key(hashed_password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        
        try:
            data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        except ValueError:
            raise ValueError("Invalid padding")
    
        return data.decode()