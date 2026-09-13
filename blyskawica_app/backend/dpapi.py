"""
[Moduł: Bezpieczeństwo DPAPI i Tożsamość Maszyny (dpapi.py)]
Zapewnia szyfrowanie Windows Data Protection API (DPAPI) dla wrażliwych danych
pamięci i tożsamości Błyskawicy oraz generowanie unikalnego odcisku sprzętowego.
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from typing import Dict

logger = logging.getLogger("DPAPI")


def get_user_fingerprint() -> Dict[str, str]:
    """Generuje unikalny odcisk maszyny i środowiska użytkownika."""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
    return {
        "mac": mac,
        "pc_name": os.environ.get('COMPUTERNAME', 'Unknown-PC'),
        "username": os.environ.get('USERNAME', 'Unknown-User'),
        "os": "Windows 11" if sys.platform == "win32" else sys.platform
    }


if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def encrypt_dpapi(data: bytes) -> bytes:
        """Szyfruje dane binarne za pomocą DPAPI (klucz maszynowo-użytkownikowy Windows)."""
        try:
            p_data_in = DATA_BLOB(len(data), ctypes.create_string_buffer(data))
            p_data_out = DATA_BLOB()
            success = ctypes.windll.crypt32.CryptProtectData(
                ctypes.byref(p_data_in),
                None,
                None,
                None,
                None,
                0,
                ctypes.byref(p_data_out)
            )
            if not success:
                raise OSError("CryptProtectData failed")
            result = ctypes.string_at(p_data_out.pbData, p_data_out.cbData)
            ctypes.windll.kernel32.LocalFree(p_data_out.pbData)
            return result
        except Exception as e:
            logger.error(f"DPAPI Encryption error: {e}")
            return data

    def decrypt_dpapi(data: bytes) -> bytes:
        """Odszyfrowuje dane binarne przy użyciu DPAPI."""
        try:
            p_data_in = DATA_BLOB(len(data), ctypes.create_string_buffer(data))
            p_data_out = DATA_BLOB()
            success = ctypes.windll.crypt32.CryptUnprotectData(
                ctypes.byref(p_data_in),
                None,
                None,
                None,
                None,
                0,
                ctypes.byref(p_data_out)
            )
            if not success:
                raise OSError("CryptUnprotectData failed")
            result = ctypes.string_at(p_data_out.pbData, p_data_out.cbData)
            ctypes.windll.kernel32.LocalFree(p_data_out.pbData)
            return result
        except Exception as e:
            logger.debug(f"DPAPI Decryption error: {e}")
            return data
else:
    def encrypt_dpapi(data: bytes) -> bytes:
        """Fallback szyfrowania dla środowisk bez Windows DPAPI."""
        return data

    def decrypt_dpapi(data: bytes) -> bytes:
        """Fallback deszyfrowania dla środowisk bez Windows DPAPI."""
        return data
