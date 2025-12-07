import os
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Derives a 32-byte key from a password using PBKDF2-HMAC-SHA256.

    Args:
        password (str): The user's password.
        salt (bytes): The salt used for derivation. If None, a new salt is generated.

    Returns:
        tuple: (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )

    key = kdf.derive(password.encode())
    return key, salt
