"""
Aura Core Signing Module
Hardware-level cryptographic signing for image attestation
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not available. Using simulated signing.")


@dataclass
class ImageSignature:
    """Structure for Aura image signature"""
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
    """Represents a step in the image processing chain"""
    operation: str
    parameters: Dict
    timestamp: str
    signature: Optional[str] = None
    legitimate: bool = True


class AuraSigner:
    """
    Core signing module for Aura-attested images.
    Simulates hardware-level cryptographic signing.
    """
    
    def __init__(self, device_id: str, private_key_path: Optional[str] = None):
        """
        Initialize Aura signer
        
        Args:
            device_id: Unique device identifier
            private_key_path: Path to private key (for production, this would be in HSM)
        """
        self.device_id = device_id
        self.private_key = None
        self.public_key = None
        self.device_certificate = None
        
        if CRYPTO_AVAILABLE and private_key_path:
            self._load_key_pair(private_key_path)
        else:
            # Simulated mode for development
            self._generate_simulated_keys()
    
    def _generate_simulated_keys(self):
        """Generate simulated keys for development/testing"""
        if CRYPTO_AVAILABLE:
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(), 
                default_backend()
            )
            self.public_key = self.private_key.public_key()
        else:
            # Fallback: simulated keys
            self.private_key = "SIMULATED_PRIVATE_KEY"
            self.public_key = "SIMULATED_PUBLIC_KEY"
    
    def _load_key_pair(self, key_path: str):
        """Load private key from secure storage (would use HSM in production)"""
        # In production, this would load from hardware security module
        # For now, we generate new keys
        self._generate_simulated_keys()
    
    def hash_image(self, image_data: bytes) -> str:
        """
        Generate SHA-256 hash of image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(image_data).hexdigest()
    
    def sign_hash(self, image_hash: str) -> str:
        """
        Cryptographically sign image hash
        
        Args:
            image_hash: SHA-256 hash of image
            
        Returns:
            Base64-encoded signature
        """
        if not CRYPTO_AVAILABLE:
            # Simulated signature
            return f"SIMULATED_SIGNATURE_{image_hash[:16]}"
        
        # Sign using ECDSA
        signature = self.private_key.sign(
            image_hash.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
        
        # Encode signature
        import base64
        return base64.b64encode(signature).decode('utf-8')
    
    def sign_image(self, 
                   image_data: bytes, 
                   metadata: Optional[Dict] = None,
                   processing_chain: Optional[list] = None) -> ImageSignature:
        """
        Create complete Aura signature for image
        
        Args:
            image_data: Raw image bytes
            metadata: Optional metadata (location, camera settings, etc.)
            processing_chain: Optional list of ProcessingStep objects
            
        Returns:
            ImageSignature object
        """
        # Generate image hash
        image_hash = self.hash_image(image_data)
        
        # Get timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Sign the hash
        signature = self.sign_hash(image_hash)
        
        # Generate device certificate (simplified)
        device_certificate = self._generate_device_certificate()
        
        # Default metadata
        if metadata is None:
            metadata = {}
        
        # Default processing chain
        if processing_chain is None:
            processing_chain = [
                {
                    "operation": "raw_capture",
                    "timestamp": timestamp,
                    "legitimate": True
                }
            ]
        
        return ImageSignature(
            device_id=self.device_id,
            timestamp=timestamp,
            image_hash=image_hash,
            signature=signature,
            device_certificate=device_certificate,
            processing_chain=processing_chain,
            metadata=metadata
        )
    
    def _generate_device_certificate(self) -> str:
        """Generate device certificate (simplified)"""
        cert_data = {
            "device_id": self.device_id,
            "issued_by": "Aura CA",
            "valid_from": datetime.utcnow().isoformat(),
            "public_key": self.public_key if isinstance(self.public_key, str) else "PUBLIC_KEY_PLACEHOLDER"
        }
        return json.dumps(cert_data)
    
    def add_processing_step(self, 
                          signature: ImageSignature,
                          operation: str,
                          parameters: Dict,
                          legitimate: bool = True) -> ImageSignature:
        """
        Add a processing step to the chain
        
        Args:
            signature: Existing ImageSignature
            operation: Processing operation name
            parameters: Operation parameters
            legitimate: Whether this is a legitimate operation
            
        Returns:
            Updated ImageSignature with new processing step
        """
        step = {
            "operation": operation,
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "legitimate": legitimate
        }
        
        new_chain = signature.processing_chain + [step]
        
        # Re-sign the image with updated chain
        # In production, this would maintain cryptographic integrity
        return ImageSignature(
            device_id=signature.device_id,
            timestamp=signature.timestamp,
            image_hash=signature.image_hash,
            signature=signature.signature,  # Original signature preserved
            device_certificate=signature.device_certificate,
            processing_chain=new_chain,
            metadata=signature.metadata
        )


class SignatureEmbedder:
    """Utility to embed signature data into image metadata"""
    
    @staticmethod
    def embed_signature(image_path: str, signature: ImageSignature, output_path: str):
        """
        Embed signature into image EXIF/metadata
        
        Args:
            image_path: Path to original image
            signature: ImageSignature to embed
            output_path: Path for output image with embedded signature
        """
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            # Open image
            img = Image.open(image_path)
            
            # Create metadata dictionary
            metadata = {
                "AURA_DEVICE_ID": signature.device_id,
                "AURA_TIMESTAMP": signature.timestamp,
                "AURA_HASH": signature.image_hash,
                "AURA_SIGNATURE": signature.signature,
                "AURA_CERTIFICATE": signature.device_certificate,
                "AURA_PROCESSING_CHAIN": json.dumps(signature.processing_chain)
            }
            
            # Try to save with metadata
            img.save(output_path, exif=img.getexif() if hasattr(img, 'getexif') else None)
            
            # Note: Full metadata embedding requires additional libraries
            # For now, we'll save signature separately
            signature_file = output_path + '.aura'
            with open(signature_file, 'w') as f:
                f.write(signature.to_json())
            
        except ImportError:
            print("PIL/Pillow not available. Saving signature to separate file.")
            signature_file = output_path + '.aura'
            with open(signature_file, 'w') as f:
                f.write(signature.to_json())
    
    @staticmethod
    def extract_signature(image_path: str) -> Optional[ImageSignature]:
        """
        Extract signature from image metadata
        
        Args:
            image_path: Path to image
            
        Returns:
            ImageSignature if found, None otherwise
        """
        # Try to read from separate .aura file
        signature_file = image_path + '.aura'
        try:
            with open(signature_file, 'r') as f:
                data = json.load(f)
                return ImageSignature(**data)
        except FileNotFoundError:
            return None


if __name__ == "__main__":
    # Example usage
    signer = AuraSigner(device_id="AURA-DEV-12345")
    
    # Simulate signing an image
    test_image_data = b"fake_image_data_for_testing"
    signature = signer.sign_image(test_image_data)
    
    print("Generated Signature:")
    print(signature.to_json())
