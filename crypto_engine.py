#<Math-crypto>
import base64
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    """Создает криптографический ключ на основе текста и соли"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=400_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

def encrypt_data(data: str, fernet: Fernet) -> str:
    """Шифрует строку"""
    if not data: return ""
    return fernet.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data(encrypted_str: str, fernet: Fernet) -> str:
    """Расшифровывает строку"""
    if not encrypted_str: return ""
    return fernet.decrypt(encrypted_str.encode('utf-8')).decode('utf-8')

def generate_strong_password(length: int) -> str:
    """Генерирует стойкий случайный пароль заданной длины (минимум 10)"""
    if length < 10:
        length = 10
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c in string.ascii_lowercase for c in password)
                and any(c in string.ascii_uppercase for c in password)
                and any(c in string.digits for c in password)
                and any(c in "!@#$%^&*()_+-=" for c in password)):
            return password