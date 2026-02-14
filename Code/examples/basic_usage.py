"""
Basic Usage Examples for Aura
Demonstrates signing and verification workflow
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.signing import AuraSigner, ImageSignature
from core.verification import AuraVerifier, DeviceRegistry
from core.change_detection import ChangeDetector
import hashlib


def example_1_signing():
    """Example 1: Sign an image"""
    print("\n=== Example 1: Signing an Image ===")
    
    # Initialize signer with device ID
    signer = AuraSigner(device_id="AURA-DEV-12345")
    
    # Simulate image data (in production, would load from file)
    image_data = b"This is simulated image data for testing purposes"
    
    # Sign the image
    signature = signer.sign_image(
        image_data=image_data,
        metadata={
            "location": "New York, NY",
            "camera_settings": {"iso": 400, "shutter": "1/60"}
        }
    )
    
    print("Image signed successfully!")
    print(f"Device ID: {signature.device_id}")
    print(f"Timestamp: {signature.timestamp}")
    print(f"Image Hash: {signature.image_hash[:16]}...")
    print(f"Signature: {signature.signature[:32]}...")
    print("\nFull signature (JSON):")
    print(signature.to_json())


def example_2_verification():
    """Example 2: Verify an image (registry-less + registry-backed)."""
    print("\n=== Example 2: Verifying an Image ===")

    signer = AuraSigner(device_id="AURA-DEV-12345")

    # Simulate image data (in production, would load from file)
    image_data = b"This is simulated image data for testing purposes"

    # Sign the image (produces a certificate containing the public key PEM)
    signature = signer.sign_image(image_data=image_data)

    # A) Verify WITHOUT a registry entry (uses public key from the certificate)
    verifier_no_registry = AuraVerifier(DeviceRegistry())
    result_a = verifier_no_registry.verify_image(image_data, signature.to_dict())

    print("A) Registry-less verification:")
    print(f"   Authentic: {result_a.authentic}")
    print(f"   Level: {result_a.verification_level.value}")
    print(f"   Confidence: {result_a.confidence:.2f}")

    # B) Verify WITH a registry entry (stronger attestation claim)
    registry = DeviceRegistry()
    registry.register_device(
        device_id="AURA-DEV-12345",
        public_key=signer.get_public_key_pem(),
        metadata={"manufacturer": "CameraCorp", "model": "ProShot X1"},
    )

    verifier_with_registry = AuraVerifier(registry)
    result_b = verifier_with_registry.verify_image(image_data, signature.to_dict())

    print("\nB) Registry-backed verification:")
    print(f"   Authentic: {result_b.authentic}")
    print(f"   Level: {result_b.verification_level.value}")
    print(f"   Confidence: {result_b.confidence:.2f}")

    if result_b.reason:
        print(f"   Reason: {result_b.reason}")


def example_3_change_detection():
    """Example 3: Detect changes in image"""
    print("\n=== Example 3: Change Detection ===")
    
    # Initialize change detector
    detector = ChangeDetector()
    
    # Simulate original image
    original_image_data = b"Original image data"
    original_hash = hashlib.sha256(original_image_data).hexdigest()
    
    # Simulate modified image
    modified_image_data = b"Modified image data with changes"
    
    original_signature = {
        "device_id": "AURA-DEV-12345",
        "processing_chain": [
            {"operation": "raw_capture", "legitimate": True},
            {"operation": "color_correction", "legitimate": True}
        ]
    }
    
    # Detect changes
    result = detector.detect_changes(
        original_hash=original_hash,
        modified_image_data=modified_image_data,
        original_signature=original_signature
    )
    
    print("Change Detection Result:")
    print(f"Has Changes: {result.has_changes}")
    print(f"Change Type: {result.change_type.value}")
    print(f"AI Changes Detected: {result.ai_changes['detected']}")
    print(f"Cosmetic Changes Detected: {result.cosmetic_changes['detected']}")
    print(f"Confidence: {result.confidence:.2f}")
    print("\nFull result (JSON):")
    print(result.to_dict())


def example_4_processing_chain():
    """Example 4: Add processing steps to chain"""
    print("\n=== Example 4: Processing Chain ===")
    
    signer = AuraSigner(device_id="AURA-DEV-12345")
    
    # Initial capture
    image_data = b"Image data"
    signature = signer.sign_image(image_data)
    
    print("Initial signature with raw capture:")
    print(f"Processing steps: {len(signature.processing_chain)}")
    
    # Add legitimate processing step
    signature = signer.add_processing_step(
        signature,
        operation="color_correction",
        parameters={"brightness": 0.1, "contrast": 0.05},
        legitimate=True
    )
    
    print(f"\nAfter adding color correction:")
    print(f"Processing steps: {len(signature.processing_chain)}")
    for step in signature.processing_chain:
        print(f"  - {step['operation']} (legitimate: {step.get('legitimate', True)})")
    
    # Add suspicious step (this would be flagged)
    signature = signer.add_processing_step(
        signature,
        operation="ai_object_insertion",
        parameters={"object": "person"},
        legitimate=False
    )
    
    print(f"\nAfter adding AI operation (suspicious):")
    print(f"Processing steps: {len(signature.processing_chain)}")
    for step in signature.processing_chain:
        legitimate = step.get("legitimate", True)
        marker = "✅" if legitimate else "⚠️"
        print(f"  {marker} {step['operation']}")


if __name__ == "__main__":
    print("Aura Basic Usage Examples")
    print("=" * 50)
    
    example_1_signing()
    example_2_verification()
    example_3_change_detection()
    example_4_processing_chain()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
