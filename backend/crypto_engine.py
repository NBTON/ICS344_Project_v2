import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets

def generate_rsa_keypair(key_size=3072):
    """
    Generates a new RSA key pair.

    Args:
        key_size (int): Size of the key in bits. Default is 3072.

    Returns:
        tuple: (private_key_pem, public_key_pem) as bytes.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem

def pem_to_private_key(pem_data):
    """Deserializes a PEM-encoded private key."""
    return serialization.load_pem_private_key(pem_data, password=None)

def pem_to_public_key(pem_data):
    """Deserializes a PEM-encoded public key."""
    return serialization.load_pem_public_key(pem_data)

def rsa_oaep_encrypt(public_key_pem, data):
    """
    Encrypts data using RSA-OAEP.

    Args:
        public_key_pem (bytes): The recipient's public key in PEM format.
        data (bytes): The data to encrypt.

    Returns:
        bytes: The encrypted ciphertext.
    """
    public_key = pem_to_public_key(public_key_pem)

    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def rsa_oaep_decrypt(private_key_pem, ciphertext):
    """
    Decrypts data using RSA-OAEP.

    Args:
        private_key_pem (bytes): The recipient's private key in PEM format.
        ciphertext (bytes): The encrypted data.

    Returns:
        bytes: The decrypted plaintext.
    """
    private_key = pem_to_private_key(private_key_pem)

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

def rsa_pss_sign(private_key_pem, data):
    """
    Signs data using RSA-PSS.

    Args:
        private_key_pem (bytes): The signer's private key in PEM format.
        data (bytes): The data to sign.

    Returns:
        bytes: The signature.
    """
    private_key = pem_to_private_key(private_key_pem)

    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=32
        ),
        hashes.SHA256()
    )
    return signature

def rsa_pss_verify(public_key_pem, data, signature):
    """
    Verifies an RSA-PSS signature.

    Args:
        public_key_pem (bytes): The signer's public key in PEM format.
        data (bytes): The signed data.
        signature (bytes): The signature to verify.

    Returns:
        bool: True if valid, False otherwise.
    """
    public_key = pem_to_public_key(public_key_pem)

    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=32
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def aes_gcm_encrypt(key, plaintext, aad=None):
    """
    Encrypts data using AES-256-GCM.

    Args:
        key (bytes): The 256-bit (32 byte) AES key.
        plaintext (bytes): The data to encrypt.
        aad (bytes): Associated Authenticated Data (optional).

    Returns:
        tuple: (iv, ciphertext, tag) as bytes.
    """
    iv = secrets.token_bytes(12)

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=None)
    encryptor = cipher.encryptor()

    if aad:
        encryptor.authenticate_additional_data(aad)

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return iv, ciphertext, encryptor.tag

def aes_gcm_decrypt(key, iv, ciphertext, tag, aad=None):
    """
    Decrypts data using AES-256-GCM.

    Args:
        key (bytes): The 256-bit (32 byte) AES key.
        iv (bytes): The 96-bit (12 byte) Initialization Vector.
        ciphertext (bytes): The encrypted data.
        tag (bytes): The authentication tag.
        aad (bytes): Associated Authenticated Data (optional).

    Returns:
        bytes: The decrypted plaintext.
    """
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=None)
    decryptor = cipher.decryptor()

    if aad:
        decryptor.authenticate_additional_data(aad)

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext
