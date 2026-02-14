"""\
Aura Core Signing Module
Hardware-level cryptographic signing for image attestation

This module is intentionally "research-grade" and ergonomic:
- It can run in a simulated mode for demos.
- When `cryptography` is available, it performs real ECDSA signing.
- Certificates are JSON objects (not full X.509) to keep the PoC light.

Key improvement:
- The generated certificate now includes a PEM-encoded public key so that
  verifiers can validate signatures without a pre-shared registry.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    # Keep prints to a minimum: this is a library module.


@dataclass
class ImageSignature:
    """Structure for Aura image signature."""

    device_id: str
    timestamp: str
    image_hash: str
    signature: str
    device_certificate: str
    processing_chain: list
    metadata: Dict

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ProcessingStep:
    """Represents a step in the image processing chain."""

    operation: str
    parameters: Dict
    timestamp: str
    signature: Optional[str] = None
    legitimate: bool = True


class AuraSigner:
    """Core signing module for Aura-attested images."""

    def __init__(self, device_id: str, private_key_path: Optional[str] = None):
        self.device_id = device_id
        self.private_key = None
        self.public_key = None

        if CRYPTO_AVAILABLE and private_key_path:
            self._load_key_pair(private_key_path)
        else:
            self._generate_keys()

    def _generate_keys(self):
        """Generate keys for development/testing."""

        if CRYPTO_AVAILABLE:
            self.private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = "SIMULATED_PRIVATE_KEY"
            self.public_key = "SIMULATED_PUBLIC_KEY"

    def _load_key_pair(self, key_path: str):
        """Load private key from storage.

        In production this would be HSM-backed. For now we load PEM if present.
        """

        if not CRYPTO_AVAILABLE:
            self._generate_keys()
            return

        with open(key_path, "rb") as f:
            key_bytes = f.read()

        self.private_key = serialization.load_pem_private_key(
            key_bytes,
            password=None,
            backend=default_backend(),
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self) -> str:
        if not CRYPTO_AVAILABLE or not self.public_key or isinstance(self.public_key, str):
            return "SIMULATED_PUBLIC_KEY"

        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem.decode("utf-8")

    def hash_image(self, image_data: bytes) -> str:
        return hashlib.sha256(image_data).hexdigest()

    def sign_hash(self, image_hash: str) -> str:
        """Sign the hex SHA-256 hash string.

        We sign the *bytes* of the hash string for portability in this PoC.
        A production version would define a canonical byte-level signing format.
        """

        if not CRYPTO_AVAILABLE or isinstance(self.private_key, str):
            return f"SIMULATED_SIGNATURE_{image_hash[:16]}"

        sig = self.private_key.sign(image_hash.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(sig).decode("utf-8")

    def sign_image(
        self,
        image_data: bytes,
        metadata: Optional[Dict] = None,
        processing_chain: Optional[list] = None,
        *,
        issued_by: str = "Aura CA (PoC)",
        validity_days: int = 365 * 5,
    ) -> ImageSignature:
        """Create complete Aura signature for image."""

        image_hash = self.hash_image(image_data)
        timestamp = datetime.utcnow().isoformat() + "Z"

        signature = self.sign_hash(image_hash)

        device_certificate = self._generate_device_certificate(
            issued_by=issued_by,
            validity_days=validity_days,
        )

        if metadata is None:
            metadata = {}

        if processing_chain is None:
            processing_chain = [
                {
                    "operation": "raw_capture",
                    "timestamp": timestamp,
                    "legitimate": True,
                }
            ]

        return ImageSignature(
            device_id=self.device_id,
            timestamp=timestamp,
            image_hash=image_hash,
            signature=signature,
            device_certificate=device_certificate,
            processing_chain=processing_chain,
            metadata=metadata,
        )

    def _generate_device_certificate(self, *, issued_by: str, validity_days: int) -> str:
        """Generate a lightweight JSON certificate.

        This is *not* an X.509 certificate. It's a structured PoC artifact that:
        - identifies the device
        - embeds the public key (PEM)
        - includes validity window
        """

        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(days=int(validity_days))

        cert_data = {
            "format": "aura-device-cert/v1",
            "device_id": self.device_id,
            "issued_by": issued_by,
            "issued_at": issued_at.isoformat() + "Z",
            "expires_at": expires_at.isoformat() + "Z",
            "public_key_pem": self.get_public_key_pem(),
        }

        # NOTE: In a real PKI, the CA would sign this certificate.
        return json.dumps(cert_data)

    def add_processing_step(
        self,
        signature: ImageSignature,
        operation: str,
        parameters: Dict,
        legitimate: bool = True,
    ) -> ImageSignature:
        step = {
            "operation": operation,
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "legitimate": legitimate,
        }

        new_chain = signature.processing_chain + [step]

        # For PoC we preserve the original signature (raw capture) and attach steps.
        return ImageSignature(
            device_id=signature.device_id,
            timestamp=signature.timestamp,
            image_hash=signature.image_hash,
            signature=signature.signature,
            device_certificate=signature.device_certificate,
            processing_chain=new_chain,
            metadata=signature.metadata,
        )


class SignatureEmbedder:
    """Utility to embed/extract signature data.

    Current approach:
    - write a sidecar `<image>.aura.json` bundle

    Why: EXIF/XMP embedding is format-specific and would add heavy deps.
    """

    @staticmethod
    def embed_signature(image_path: str, signature: ImageSignature, output_path: str):
        """Copy image and write a sidecar signature bundle."""

        try:
            from PIL import Image

            img = Image.open(image_path)
            img.save(output_path)
        except Exception:
            # Fallback: just copy bytes
            with open(image_path, "rb") as src, open(output_path, "wb") as dst:
                dst.write(src.read())

        signature_file = output_path + ".aura.json"
        with open(signature_file, "w", encoding="utf-8") as f:
            f.write(signature.to_json())

    @staticmethod
    def extract_signature(image_path: str) -> Optional[ImageSignature]:
        signature_file = image_path + ".aura.json"
        try:
            with open(signature_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ImageSignature(**data)
        except FileNotFoundError:
            return None


if __name__ == "__main__":
    signer = AuraSigner(device_id="AURA-DEV-12345")
    test_image_data = b"fake_image_data_for_testing"
    signature = signer.sign_image(test_image_data)
    print(signature.to_json())
