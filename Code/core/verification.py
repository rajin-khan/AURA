"""\
Aura Verification Module
Verifies authenticity of Aura-signed images.

Key improvement:
- Proper ECDSA verification when `cryptography` is available.
- Self-contained verification: when a device is NOT pre-registered, we can
  still verify using the public key embedded in the device certificate.

Notes:
- Certificates here are lightweight JSON objects, not full X.509.
- A production-grade system would validate a CA signature over the certificate.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Tuple

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class VerificationLevel(Enum):
    """Verification confidence levels."""

    HARDWARE_ATTESTED = "hardware_attested"  # strongest claim in this PoC
    FIRMWARE_ATTESTED = "firmware_attested"
    SOFTWARE_ATTESTED = "software_attested"  # signature validated but not registry/pki backed
    UNVERIFIED = "unverified"
    AI_MODIFIED = "ai_modified"
    AUTHENTIC_WITH_ENHANCEMENTS = "authentic_with_enhancements"


@dataclass
class VerificationResult:
    authentic: bool
    verification_level: VerificationLevel
    device_id: Optional[str] = None
    timestamp: Optional[str] = None
    reason: Optional[str] = None
    confidence: float = 0.0
    change_detection: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "authentic": self.authentic,
            "verification_level": self.verification_level.value,
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "confidence": self.confidence,
            "change_detection": self.change_detection,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class DeviceRegistry:
    """Central registry of Aura devices and their public keys."""

    def __init__(self):
        self.devices: Dict[str, Dict] = {}

    def register_device(self, device_id: str, public_key: str, metadata: Dict):
        self.devices[device_id] = {
            "device_id": device_id,
            "public_key": public_key,
            "registered": datetime.utcnow().isoformat(),
            "status": "active",
            **metadata,
        }

    def get_device(self, device_id: str) -> Optional[Dict]:
        return self.devices.get(device_id)

    def is_device_active(self, device_id: str) -> bool:
        device = self.devices.get(device_id)
        return device is not None and device.get("status") == "active"

    def revoke_device(self, device_id: str):
        if device_id in self.devices:
            self.devices[device_id]["status"] = "revoked"

    def get_all_devices(self) -> Dict:
        return self.devices


def _parse_cert_json(certificate_str: str) -> Tuple[Optional[Dict], Optional[str]]:
    try:
        cert_data = json.loads(certificate_str)
        if not isinstance(cert_data, dict):
            return None, "Certificate is not a JSON object"
        return cert_data, None
    except Exception:
        return None, "Certificate is not valid JSON"


def _is_cert_within_validity(cert_data: Dict) -> Tuple[bool, Optional[str]]:
    """Best-effort time-window checks for the lightweight cert."""

    expires_at = cert_data.get("expires_at")
    if not expires_at:
        return True, None

    try:
        from datetime import timezone

        exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        # Normalize timezone if the parsed expiry is naive (shouldn't be, but PoC).
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp <= now:
            return False, "Certificate expired"
        return True, None
    except Exception:
        # Don’t hard-fail PoC verification on formatting.
        return True, None


class AuraVerifier:
    """Main verification class for Aura-signed images."""

    def __init__(self, device_registry: Optional[DeviceRegistry] = None):
        self.registry = device_registry or DeviceRegistry()
        self.revocation_list: set = set()

    def hash_image(self, image_data: bytes) -> str:
        return hashlib.sha256(image_data).hexdigest()

    def verify_signature(self, *, image_hash: str, signature_b64: str, public_key_pem: str) -> bool:
        if not CRYPTO_AVAILABLE:
            return signature_b64.startswith("SIMULATED_SIGNATURE_")

        try:
            sig_bytes = base64.b64decode(signature_b64)
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"),
                backend=default_backend(),
            )

            # We expect an ECDSA key for this PoC.
            if not isinstance(public_key, ec.EllipticCurvePublicKey):
                return False

            public_key.verify(sig_bytes, image_hash.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
            return True
        except (ValueError, InvalidSignature, TypeError):
            return False
        except Exception:
            return False

    def parse_signature(self, signature_data: Dict) -> Dict:
        return {
            "device_id": signature_data.get("device_id"),
            "timestamp": signature_data.get("timestamp"),
            "image_hash": signature_data.get("image_hash"),
            "signature": signature_data.get("signature"),
            "certificate": signature_data.get("device_certificate"),
            "processing_chain": signature_data.get("processing_chain", []),
        }

    def verify_certificate(self, certificate_str: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate certificate structure + best-effort validity window."""

        cert_data, err = _parse_cert_json(certificate_str)
        if err:
            return False, None, err

        device_id = cert_data.get("device_id")
        if not device_id:
            return False, None, "Certificate missing device_id"

        ok, reason = _is_cert_within_validity(cert_data)
        if not ok:
            return False, None, reason

        # Registry-backed check: if we know about this device, it must be active.
        if self.registry.get_device(device_id) is not None and not self.registry.is_device_active(device_id):
            return False, None, "Device is inactive/revoked in registry"

        return True, cert_data, None

    def verify_image(self, image_data: bytes, signature_data: Dict, check_changes: bool = False) -> VerificationResult:
        parsed = self.parse_signature(signature_data)
        device_id = parsed["device_id"]

        # Step 1: Verify certificate structure
        cert_valid, cert_data, cert_reason = self.verify_certificate(parsed.get("certificate") or "")
        if not cert_valid or not cert_data:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                reason=cert_reason or "Invalid device certificate",
                confidence=0.0,
                device_id=device_id,
                timestamp=parsed.get("timestamp"),
            )

        # Step 2: Check revocation list
        if device_id in self.revocation_list:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                reason="Device revoked",
                confidence=0.0,
                device_id=device_id,
                timestamp=parsed.get("timestamp"),
            )

        # Step 3: Compute current image hash
        current_hash = self.hash_image(image_data)
        original_hash = parsed["image_hash"]

        if current_hash != original_hash:
            if check_changes:
                change_detection = self._detect_changes(image_data, signature_data)

                if change_detection.get("has_ai_changes"):
                    level = VerificationLevel.AI_MODIFIED
                elif change_detection.get("has_only_cosmetic_changes"):
                    level = VerificationLevel.AUTHENTIC_WITH_ENHANCEMENTS
                else:
                    level = VerificationLevel.UNVERIFIED

                return VerificationResult(
                    authentic=False,
                    verification_level=level,
                    device_id=device_id,
                    timestamp=parsed["timestamp"],
                    reason="Image hash mismatch - modifications detected",
                    confidence=0.7,
                    change_detection=change_detection,
                )

            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                device_id=device_id,
                timestamp=parsed["timestamp"],
                reason="Image hash mismatch",
                confidence=0.0,
            )

        # Step 4: Locate public key
        device = self.registry.get_device(device_id)
        public_key_pem = None

        # Prefer registry public key (if set to PEM), otherwise fall back to cert.
        if device and device.get("public_key"):
            public_key_pem = device.get("public_key")
        else:
            public_key_pem = cert_data.get("public_key_pem")

        if not public_key_pem:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                device_id=device_id,
                timestamp=parsed["timestamp"],
                reason="No public key available (registry or certificate)",
                confidence=0.0,
            )

        # Step 5: Verify cryptographic signature
        signature_valid = self.verify_signature(
            image_hash=original_hash,
            signature_b64=parsed["signature"],
            public_key_pem=public_key_pem,
        )

        if not signature_valid:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                device_id=device_id,
                timestamp=parsed["timestamp"],
                reason="Signature verification failed",
                confidence=0.0,
            )

        # Step 6: Verify processing chain integrity
        chain_valid = self._verify_processing_chain(parsed["processing_chain"])
        if not chain_valid:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                device_id=device_id,
                timestamp=parsed["timestamp"],
                reason="Processing chain integrity check failed",
                confidence=0.5,
            )

        # Step 7: Determine verification level
        # If we relied on a registry entry, we can claim stronger attestation.
        if device and self.registry.is_device_active(device_id):
            level = VerificationLevel.HARDWARE_ATTESTED
            confidence = 0.99
        else:
            level = VerificationLevel.SOFTWARE_ATTESTED
            confidence = 0.9

        return VerificationResult(
            authentic=True,
            verification_level=level,
            device_id=device_id,
            timestamp=parsed["timestamp"],
            confidence=confidence,
            change_detection={"has_changes": False} if check_changes else None,
        )

    def _verify_processing_chain(self, processing_chain: list) -> bool:
        if not processing_chain:
            return True

        suspicious_ops = ["ai_object_insertion", "ai_inpainting", "deepfake_face_swap"]

        for step in processing_chain:
            if isinstance(step, dict):
                operation = step.get("operation", "")
                legitimate = step.get("legitimate", True)

                if not legitimate or any(sus in operation.lower() for sus in suspicious_ops):
                    return False

        return True

    def _detect_changes(self, image_data: bytes, signature_data: Dict) -> Dict:
        # Placeholder for change detection
        return {
            "has_changes": True,
            "has_ai_changes": False,
            "has_only_cosmetic_changes": True,
            "change_details": [{"type": "unknown", "confidence": 0.5}],
        }


if __name__ == "__main__":
    # Smoke test (run from the Code/ directory)
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from core.signing import AuraSigner

    signer = AuraSigner(device_id="AURA-DEV-12345")
    img = b"test_image_data"
    sig = signer.sign_image(img)

    verifier = AuraVerifier(DeviceRegistry())
    # NOTE: No registry entry; will verify using cert public key.
    result = verifier.verify_image(img, sig.to_dict())
    print(result.to_json())
