"""
AES-256 암호화 모듈.
key 와 iv 값을 기반으로 암호화를 수행
"""
import base64
from Crypto.Cipher import AES
from django.conf import settings


def _pad(s): return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)


def _cipher(key, iv):
    return AES.new(key=key, mode=AES.MODE_CBC, IV=iv)


def encrypt(data, key, iv):
    return _cipher(key, iv).encrypt(_pad(data))


def decrypt(data, key, iv):
    return _cipher(key, iv).decrypt(data)


"""
초기화
"""
key = settings.AES_KEY
iv = settings.AES_SECRET.encode()
aes_key = "{: <32}".format(key).encode("utf-8")


"""
외부 노출 함수
"""
def aes_encrypt(data):
    encrypted_data = _cipher(aes_key, iv).encrypt(_pad(data))
    return base64.b64encode(encrypted_data)


def aes_decrypt(data):
    decoded_data = base64.b64decode(data)
    decrypted_data = _cipher(aes_key, iv).decrypt(decoded_data)
    return decrypted_data


# key = b"BYOUwqYyMgWfEIjSHhmVHBoJgobVUJbR"
# iv = b"I6V8HN5DMUPM4AES"
# data = "text plane"
#
# key = "{: <32}".format(key).encode("utf-8")
#
# encrypted_data = encrypt(data, key, iv)
#
# print(base64.b64encode(encrypted_data))
# print("\n")
