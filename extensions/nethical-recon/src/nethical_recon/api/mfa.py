"""Multi-Factor Authentication (MFA) manager for TOTP-based 2FA."""

import io
import secrets
from typing import Any

import pyotp
import qrcode
from PIL import Image


class MFAManager:
    """Manager for Multi-Factor Authentication using TOTP."""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new MFA secret for a user.

        Returns:
            Base32-encoded secret string.
        """
        return pyotp.random_base32()

    @staticmethod
    def verify_token(secret: str, token: str, valid_window: int = 1) -> bool:
        """Verify a TOTP token.

        Args:
            secret: Base32-encoded secret.
            token: 6-digit TOTP token to verify.
            valid_window: Number of time steps to check before/after current (default: 1).

        Returns:
            True if token is valid, False otherwise.
        """
        if not secret or not token:
            return False

        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=valid_window)
        except Exception:
            return False

    @staticmethod
    def generate_qr_code(secret: str, username: str, issuer: str = "Nethical Recon") -> bytes:
        """Generate a QR code for MFA setup.

        Args:
            secret: Base32-encoded secret.
            username: Username for the account.
            issuer: Issuer name (default: "Nethical Recon").

        Returns:
            QR code image as PNG bytes.
        """
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=username, issuer_name=issuer)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return img_bytes.getvalue()

    @staticmethod
    def get_current_token(secret: str) -> str:
        """Get the current TOTP token for testing purposes.

        Args:
            secret: Base32-encoded secret.

        Returns:
            Current 6-digit TOTP token.
        """
        totp = pyotp.TOTP(secret)
        return totp.now()

    @staticmethod
    def generate_backup_codes(count: int = 8) -> list[str]:
        """Generate backup recovery codes.

        Args:
            count: Number of backup codes to generate (default: 8).

        Returns:
            List of backup codes.
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes
