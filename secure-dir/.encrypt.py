#!/bin/python3

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# ===== Hàm mã hóa AES =====
def aes_encrypt(key: bytes, plaintext: str) -> bytes:
    # Sinh IV ngẫu nhiên (16 byte)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return (ciphertext+iv).hex()

# ===== Hàm giải mã AES =====
def aes_decrypt(key: bytes, ciphertext: str) -> str:
    iv = bytes.fromhex(ciphertext)[-16:]
    cip_text = bytes.fromhex(ciphertext)[:-16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(cip_text), AES.block_size)
    return plaintext.decode()


key = b'\xf3%\xc3{a\x9fj\xd5B\xdf\x80f\xc1r\xb2\xd5'  # AES-128 (16 byte)
