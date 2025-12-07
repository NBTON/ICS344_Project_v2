import base64
import json
from backend.crypto_engine import generate_rsa_keypair, aes_gcm_encrypt, aes_gcm_decrypt
from backend.utils import derive_key

class KeyManager:
    @staticmethod
    def generate_user_keys(password: str):
        """
        Generates RSA keypair and encrypts the private key with the password.

        Returns:
            public_key_pem (str)
            encrypted_private_key (str)
        """
        private_pem, public_pem = generate_rsa_keypair()

        # Derive encryption key from password
        key, salt = derive_key(password)

        # Encrypt private key
        iv, ciphertext, tag = aes_gcm_encrypt(key, private_pem)

        # Serialize encrypted data
        encrypted_data = {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8')
        }

        return public_pem.decode('utf-8'), json.dumps(encrypted_data)

    @staticmethod
    def decrypt_private_key(password: str, encrypted_private_key_json: str):
        """
        Decrypts the private key using the password.
        """
        try:
            data = json.loads(encrypted_private_key_json)
            salt = base64.b64decode(data['salt'])
            iv = base64.b64decode(data['iv'])
            ciphertext = base64.b64decode(data['ciphertext'])
            tag = base64.b64decode(data['tag'])

            key, _ = derive_key(password, salt)

            private_pem = aes_gcm_decrypt(key, iv, ciphertext, tag)
            return private_pem
        except Exception as e:
            # print(f"Decryption failed: {e}")
            return None
