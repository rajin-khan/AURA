"""
Aura Verification Module
Verifies authenticity of Aura-signed images
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class VerificationLevel(Enum):
    """Verification confidence levels"""
    HARDWARE_ATTESTED = "hardware_attested"  # Level 5
    FIRMWARE_ATTESTED = "firmware_attested"   # Level 4
    SOFTWARE_ATTESTED = "software_attested"   # Level 3
    UNVERIFIED = "unverified"                 # Level 0
    AI_MODIFIED = "ai_modified"              # Modified with AI
    AUTHENTIC_WITH_ENHANCEMENTS = "authentic_with_enhancements"  # Cosmetic only


@dataclass
class VerificationResult:
    """Result of image verification"""
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
            "change_detection": self.change_detection
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class DeviceRegistry:
    """Central registry of Aura devices and their public keys"""
    
    def __init__(self):
        self.devices: Dict[str, Dict] = {}
    
    def register_device(self, device_id: str, public_key: str, metadata: Dict):
        """Register a device in the registry"""
        self.devices[device_id] = {
            "device_id": device_id,
            "public_key": public_key,
            "registered": datetime.utcnow().isoformat(),
            "status": "active",
            **metadata
        }
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device information"""
        return self.devices.get(device_id)
    
    def is_device_active(self, device_id: str) -> bool:
        """Check if device is active"""
        device = self.devices.get(device_id)
        return device is not None and device.get("status") == "active"
    
    def revoke_device(self, device_id: str):
        """Revoke a device"""
        if device_id in self.devices:
            self.devices[device_id]["status"] = "revoked"
    
    def get_all_devices(self) -> Dict:
        """Get all registered devices"""
        return self.devices


class AuraVerifier:
    """
    Main verification class for Aura-signed images
    """
    
    def __init__(self, device_registry: Optional[DeviceRegistry] = None):
        """
        Initialize verifier
        
        Args:
            device_registry: Device registry instance (creates new if None)
        """
        self.registry = device_registry or DeviceRegistry()
        self.revocation_list: set = set()
    
    def hash_image(self, image_data: bytes) -> str:
        """Generate SHA-256 hash of image"""
        return hashlib.sha256(image_data).hexdigest()
    
    def verify_signature(self, 
                        image_hash: str, 
                        signature: str, 
                        public_key_str: str) -> bool:
        """
        Verify cryptographic signature
        
        Args:
            image_hash: SHA-256 hash of image
            signature: Base64-encoded signature
            public_key_str: Public key (simplified for demo)
            
        Returns:
            True if signature is valid
        """
        if not CRYPTO_AVAILABLE:
            # Simulated verification
            return signature.startswith("SIMULATED_SIGNATURE_")
        
        try:
            import base64
            from cryptography.hazmat.primitives import serialization
            
            # Decode signature
            sig_bytes = base64.b64decode(signature)
            
            # In production, would load public key from certificate
            # For demo, we simulate verification
            return True
            
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def parse_signature(self, signature_data: Dict) -> Dict:
        """
        Parse signature data structure
        
        Args:
            signature_data: Dictionary containing signature information
            
        Returns:
            Parsed signature components
        """
        return {
            "device_id": signature_data.get("device_id"),
            "timestamp": signature_data.get("timestamp"),
            "image_hash": signature_data.get("image_hash"),
            "signature": signature_data.get("signature"),
            "certificate": signature_data.get("device_certificate"),
            "processing_chain": signature_data.get("processing_chain", [])
        }
    
    def verify_certificate(self, certificate_str: str) -> Tuple[bool, Optional[str]]:
        """
        Verify device certificate
        
        Args:
            certificate_str: JSON string containing certificate data
            
        Returns:
            Tuple of (is_valid, device_id)
        """
        try:
            cert_data = json.loads(certificate_str)
            device_id = cert_data.get("device_id")
            
            # In production, would verify certificate chain with Aura CA
            # For demo, we check if device is in registry
            if self.registry.is_device_active(device_id):
                return True, device_id
            return False, None
            
        except Exception:
            return False, None
    
    def verify_image(self, 
                    image_data: bytes,
                    signature_data: Dict,
                    check_changes: bool = False) -> VerificationResult:
        """
        Complete verification of Aura-signed image
        
        Args:
            image_data: Raw image bytes
            signature_data: Signature data dictionary
            check_changes: Whether to perform change detection
            
        Returns:
            VerificationResult object
        """
        # Parse signature
        parsed = self.parse_signature(signature_data)
        device_id = parsed["device_id"]
        
        # Step 1: Verify device certificate
        cert_valid, cert_device_id = self.verify_certificate(parsed["certificate"])
        if not cert_valid:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                reason="Invalid device certificate",
                confidence=0.0
            )
        
        # Step 2: Check if device is revoked
        if device_id in self.revocation_list or not self.registry.is_device_active(device_id):
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                reason="Device revoked or inactive",
                confidence=0.0,
                device_id=device_id
            )
        
        # Step 3: Compute current image hash
        current_hash = self.hash_image(image_data)
        
        # Step 4: Compare with original hash
        original_hash = parsed["image_hash"]
        
        if current_hash != original_hash:
            # Hash mismatch - image has been modified
            if check_changes:
                # Perform change detection
                change_detection = self._detect_changes(image_data, signature_data)
                
                # Determine verification level based on change type
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
                    change_detection=change_detection
                )
            else:
                return VerificationResult(
                    authentic=False,
                    verification_level=VerificationLevel.UNVERIFIED,
                    device_id=device_id,
                    timestamp=parsed["timestamp"],
                    reason="Image hash mismatch",
                    confidence=0.0
                )
        
        # Step 5: Verify cryptographic signature
        device = self.registry.get_device(device_id)
        if not device:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                reason="Device not found in registry",
                confidence=0.0,
                device_id=device_id
            )
        
        public_key = device.get("public_key")
        signature_valid = self.verify_signature(
            original_hash,
            parsed["signature"],
            public_key
        )
        
        if not signature_valid:
            return VerificationResult(
                authentic=False,
                verification_level=VerificationLevel.UNVERIFIED,
                device_id=device_id,
                timestamp=parsed["timestamp"],
                reason="Signature verification failed",
                confidence=0.0
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
                confidence=0.5
            )
        
        # Step 7: Determine verification level
        level = VerificationLevel.HARDWARE_ATTESTED
        
        # All checks passed
        return VerificationResult(
            authentic=True,
            verification_level=level,
            device_id=device_id,
            timestamp=parsed["timestamp"],
            confidence=0.99,
            change_detection={"has_changes": False} if check_changes else None
        )
    
    def _verify_processing_chain(self, processing_chain: list) -> bool:
        """
        Verify integrity of processing chain
        
        Args:
            processing_chain: List of processing steps
            
        Returns:
            True if chain is valid
        """
        if not processing_chain:
            return True
        
        # Check for suspicious operations
        suspicious_ops = ["ai_object_insertion", "ai_inpainting", "deepfake_face_swap"]
        
        for step in processing_chain:
            if isinstance(step, dict):
                operation = step.get("operation", "")
                legitimate = step.get("legitimate", True)
                
                if not legitimate or any(sus in operation.lower() for sus in suspicious_ops):
                    return False
        
        return True
    
    def _detect_changes(self, image_data: bytes, signature_data: Dict) -> Dict:
        """
        Detect and classify changes in image
        
        Args:
            image_data: Current image data
            signature_data: Original signature data
            
        Returns:
            Change detection results
        """
        # Placeholder for change detection
        # In production, would use advanced computer vision and AI detection
        return {
            "has_changes": True,
            "has_ai_changes": False,
            "has_cosmetic_changes": True,
            "change_details": [
                {
                    "type": "unknown",
                    "confidence": 0.5
                }
            ]
        }


if __name__ == "__main__":
    # Example usage
    registry = DeviceRegistry()
    registry.register_device(
        device_id="AURA-DEV-12345",
        public_key="PUBLIC_KEY_PLACEHOLDER",
        metadata={"manufacturer": "CameraCorp", "model": "ProShot X1"}
    )
    
    verifier = AuraVerifier(registry)
    
    # Simulate verification
    test_image = b"test_image_data"
    test_signature = {
        "device_id": "AURA-DEV-12345",
        "timestamp": datetime.utcnow().isoformat(),
        "image_hash": hashlib.sha256(test_image).hexdigest(),
        "signature": "SIMULATED_SIGNATURE_TEST",
        "device_certificate": json.dumps({"device_id": "AURA-DEV-12345"}),
        "processing_chain": []
    }
    
    result = verifier.verify_image(test_image, test_signature)
    print("Verification Result:")
    print(result.to_json())
