import pytest
import os
from backend.crypto_engine import (
    generate_rsa_keypair,
    rsa_oaep_encrypt,
    rsa_oaep_decrypt,
    rsa_pss_sign,
    rsa_pss_verify,
    aes_gcm_encrypt,
    aes_gcm_decrypt
)

def test_rsa_keypair_generation():
    private_pem, public_pem = generate_rsa_keypair(key_size=2048) # Using 2048 for faster tests
    assert private_pem.startswith(b"-----BEGIN PRIVATE KEY-----")
    assert public_pem.startswith(b"-----BEGIN PUBLIC KEY-----")

def test_rsa_oaep_encryption_decryption():
    private_pem, public_pem = generate_rsa_keypair(key_size=2048)
    message = b"Secret Message"

    ciphertext = rsa_oaep_encrypt(public_pem, message)
    assert ciphertext != message

    decrypted = rsa_oaep_decrypt(private_pem, ciphertext)
    assert decrypted == message

def test_rsa_pss_signing_verification():
    private_pem, public_pem = generate_rsa_keypair(key_size=2048)
    message = b"Signed Message"

    signature = rsa_pss_sign(private_pem, message)
    assert len(signature) > 0

    is_valid = rsa_pss_verify(public_pem, message, signature)
    assert is_valid is True

    is_valid_tampered = rsa_pss_verify(public_pem, b"Tampered Message", signature)
    assert is_valid_tampered is False

def test_aes_gcm_encryption_decryption():
    key = os.urandom(32)
    plaintext = b"Confidential Data"
    aad = b"Metadata"

    iv, ciphertext, tag = aes_gcm_encrypt(key, plaintext, aad)

    assert len(iv) == 12
    assert len(tag) == 16
    assert ciphertext != plaintext

    decrypted = aes_gcm_decrypt(key, iv, ciphertext, tag, aad)
    assert decrypted == plaintext

def test_aes_gcm_tampering():
    key = os.urandom(32)
    plaintext = b"Confidential Data"

    iv, ciphertext, tag = aes_gcm_encrypt(key, plaintext)

    # Tamper with ciphertext
    tampered_ciphertext = bytearray(ciphertext)
    tampered_ciphertext[0] ^= 0xFF

    with pytest.raises(Exception):
        aes_gcm_decrypt(key, iv, bytes(tampered_ciphertext), tag)

    # Tamper with tag
    tampered_tag = bytearray(tag)
    tampered_tag[0] ^= 0xFF

    with pytest.raises(Exception):
        aes_gcm_decrypt(key, iv, ciphertext, bytes(tampered_tag))
