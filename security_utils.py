"""
Utility helpers for symmetric encryption/decryption across the project.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

KEY_FILE = Path(__file__).resolve().parent / "fernet.key"
_FERNET: Optional[Fernet] = None


def _load_or_create_key() -> bytes:
    """
    Load the Fernet key from disk or create one if it does not exist.
    """
    if not KEY_FILE.exists():
        KEY_FILE.write_bytes(Fernet.generate_key())
    return KEY_FILE.read_bytes()


def get_cipher() -> Fernet:
    """
    Return a module-wide Fernet cipher instance.
    """
    global _FERNET
    if _FERNET is None:
        _FERNET = Fernet(_load_or_create_key())
    return _FERNET


def encrypt_text(value: str) -> bytes:
    """
    Encrypt a string value and return the ciphertext as bytes.
    """
    if value is None:
        raise ValueError("value must not be None")
    return get_cipher().encrypt(value.encode("utf-8"))


def decrypt_text(token: bytes) -> str:
    """
    Decrypt ciphertext bytes back into their original string form.
    """
    if token is None:
        raise ValueError("token must not be None")
    return get_cipher().decrypt(token).decode("utf-8")

