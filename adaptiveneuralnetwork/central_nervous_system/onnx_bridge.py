import logging
import os

import onnx
import torch

logger = logging.getLogger(__name__)

class ONNXBridge:
    """
    Handles the crystallization of Błyskawica's weights.
    Exports PyTorch modules to ONNX format for deployment in the Spores (Edge instanced).
    Implements Task 1.2 from the Expansion Plan.
    """
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.keys_dir = os.path.join(output_dir, "keys")
        os.makedirs(self.keys_dir, exist_ok=True)
        self.private_key_path = os.path.join(self.keys_dir, "blyskawica_private.pem")
        self.public_key_path = os.path.join(self.keys_dir, "blyskawica_public.pem")
        self._ensure_cryptographic_keys()

    def _ensure_cryptographic_keys(self):
        """Generates RSA private/public keys if they do not exist."""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        if not os.path.exists(self.private_key_path) or not os.path.exists(self.public_key_path):
            logger.info("Generating new cryptographic key pair for model crystallization...")
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            # Save private key
            with open(self.private_key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                )
            # Save public key
            public_key = private_key.public_key()
            with open(self.public_key_path, "wb") as f:
                f.write(
                    public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )
            logger.info("Key pair generated successfully.")

    def sign_crystallized_core(self, onnx_path: str) -> str | None:
        """Signs the ONNX model file and outputs a detached signature file (.sig)."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        if not os.path.exists(onnx_path):
            logger.error(f"Cannot sign model: file {onnx_path} does not exist.")
            return None

        signature_path = onnx_path + ".sig"
        try:
            with open(self.private_key_path, "rb") as f:
                private_key = load_pem_private_key(f.read(), password=None)

            with open(onnx_path, "rb") as f:
                model_data = f.read()

            signature = private_key.sign(
                model_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            with open(signature_path, "wb") as f:
                f.write(signature)

            logger.info(f"Model signature written to: {signature_path}")
            return signature_path
        except Exception as e:
            logger.error(f"Cryptographic signing failed: {str(e)}")
            return None

    def verify_crystallized_core_signature(self, onnx_path: str, signature_path: str) -> bool:
        """Verifies the detached signature of the ONNX model using the public key."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        if not os.path.exists(onnx_path) or not os.path.exists(signature_path):
            logger.error("Verification files missing.")
            return False

        try:
            with open(self.public_key_path, "rb") as f:
                public_key = load_pem_public_key(f.read())

            with open(onnx_path, "rb") as f:
                model_data = f.read()

            with open(signature_path, "rb") as f:
                signature = f.read()

            public_key.verify(
                signature,
                model_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            logger.info(f"Cryptographic Signature Valid: {onnx_path} matches signature {signature_path}")
            return True
        except Exception as e:
            logger.error(f"Cryptographic signature verification failed: {str(e)}")
            return False

    def export_crystallized_core(self,
                                 model: torch.nn.Module,
                                 input_sample: torch.Tensor,
                                 model_name: str = "blyskawica_core"):
        """
        Exports a frozen version of the model to ONNX.
        This represents 'What she knows' (Crystallized Core).
        """
        export_path = os.path.join(self.output_dir, f"{model_name}.onnx")
        logger.info(f"Crystallizing Core: Exporting to {export_path}")

        # Ensure model is in eval mode
        model.eval()

        try:
            torch.onnx.export(
                model,
                input_sample,
                export_path,
                export_params=True,
                opset_version=15,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
            )
            logger.info(f"Crystallization Complete: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"Crystallization Failed: {str(e)}")
            return None

    def verify_onnx_integrity(self, onnx_path: str) -> bool:
        """Checks if the exported ONNX model is valid."""
        try:
            onnx_model = onnx.load(onnx_path)
            onnx.checker.check_model(onnx_model)
            logger.info(f"ONNX Integrity Verified: {onnx_path}")
            return True
        except Exception as e:
            logger.error(f"ONNX Integrity Check Failed: {str(e)}")
            return False
