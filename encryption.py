import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class EncryptionTool:
    def __init__(self):
        pass
    
    def _generate_key_from_password(self, password, salt=None):
        """Generate encryption key from password"""
        if salt is None:
            salt = b'cybercloak_salt_2024'  # In production, use random salt
        
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt_data(self, data, password):
        """Encrypt data using AES-256"""
        try:
            key = self._generate_key_from_password(password)
            fernet = Fernet(key)
            
            # Convert data to bytes if it's a string
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            encrypted_data = fernet.encrypt(data_bytes)
            
            # Return base64 encoded string for easy storage
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data, password):
        """Decrypt data using AES-256"""
        try:
            key = self._generate_key_from_password(password)
            fernet = Fernet(key)
            
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            
            # Return as string
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return None
    
    def generate_secure_key(self):
        """Generate a secure random key"""
        return secrets.token_urlsafe(32)
    
    def hash_data(self, data):
        """Create SHA-256 hash of data"""
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
            
        return hashlib.sha256(data_bytes).hexdigest()
    
    def verify_integrity(self, data, hash_value):
        """Verify data integrity using hash"""
        return self.hash_data(data) == hash_value
