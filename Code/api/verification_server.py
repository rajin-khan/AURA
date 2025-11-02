"""
Aura Verification API Server
RESTful API for image verification service
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import hashlib
from typing import Dict, Optional
import base64

# Import Aura modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.verification import AuraVerifier, DeviceRegistry, VerificationLevel
from core.change_detection import ChangeDetector
from core.signing import ImageSignature

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Initialize global components
device_registry = DeviceRegistry()
verifier = AuraVerifier(device_registry)
change_detector = ChangeDetector()


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Aura Verification Service",
        "version": "1.0.0"
    })


@app.route('/api/v1/verify', methods=['POST'])
def verify_image():
    """
    Verify an Aura-signed image
    
    Expected payload:
    {
        "image": <base64_encoded_image_data>,
        "signature_data": {
            "device_id": "...",
            "timestamp": "...",
            "image_hash": "...",
            "signature": "...",
            "device_certificate": "...",
            "processing_chain": [...]
        },
        "check_changes": true/false
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Invalid request",
                "message": "No JSON data provided"
            }), 400
        
        # Extract image data
        image_base64 = data.get("image")
        if not image_base64:
            return jsonify({
                "error": "Missing image",
                "message": "Image data is required"
            }), 400
        
        # Decode image
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({
                "error": "Invalid image data",
                "message": str(e)
            }), 400
        
        # Extract signature data
        signature_data = data.get("signature_data")
        if not signature_data:
            return jsonify({
                "error": "Missing signature",
                "message": "Signature data is required"
            }), 400
        
        # Check if change detection requested
        check_changes = data.get("check_changes", False)
        
        # Verify image
        result = verifier.verify_image(image_data, signature_data, check_changes=check_changes)
        
        # If changes detected, perform detailed change analysis
        change_detection = None
        if check_changes and not result.authentic:
            if result.change_detection and result.change_detection.get("has_changes"):
                # Perform full change detection
                original_hash = signature_data.get("image_hash")
                change_result = change_detector.detect_changes(
                    original_hash,
                    image_data,
                    signature_data
                )
                change_detection = change_result.to_dict()
        
        # Build response
        response = {
            "authentic": result.authentic,
            "verification_level": result.verification_level.value,
            "device_id": result.device_id,
            "timestamp": result.timestamp,
            "confidence": result.confidence,
            "change_detection": change_detection or result.change_detection
        }
        
        if result.reason:
            response["reason"] = result.reason
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "Verification failed",
            "message": str(e)
        }), 500


@app.route('/api/v1/device/<device_id>', methods=['GET'])
def get_device(device_id: str):
    """Get device information"""
    device = device_registry.get_device(device_id)
    
    if not device:
        return jsonify({
            "error": "Device not found",
            "device_id": device_id
        }), 404
    
    return jsonify(device), 200


@app.route('/api/v1/device', methods=['POST'])
def register_device():
    """
    Register a new device
    
    Expected payload:
    {
        "device_id": "...",
        "public_key": "...",
        "manufacturer": "...",
        "model": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Invalid request"
            }), 400
        
        device_id = data.get("device_id")
        public_key = data.get("public_key")
        
        if not device_id or not public_key:
            return jsonify({
                "error": "Missing required fields",
                "message": "device_id and public_key are required"
            }), 400
        
        metadata = {
            "manufacturer": data.get("manufacturer", "Unknown"),
            "model": data.get("model", "Unknown")
        }
        
        device_registry.register_device(device_id, public_key, metadata)
        
        return jsonify({
            "status": "success",
            "message": "Device registered",
            "device_id": device_id
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": "Registration failed",
            "message": str(e)
        }), 500


@app.route('/api/v1/devices', methods=['GET'])
def list_devices():
    """List all registered devices"""
    devices = device_registry.get_all_devices()
    return jsonify({
        "devices": list(devices.values()),
        "count": len(devices)
    }), 200


@app.route('/api/v1/verifications', methods=['GET'])
def get_verifications():
    """
    Get verification history
    
    Query parameters:
    - device_id: Filter by device ID
    - limit: Maximum number of results
    """
    device_id = request.args.get("device_id")
    limit = int(request.args.get("limit", 100))
    
    # In production, would query from database
    # For demo, return placeholder
    return jsonify({
        "verifications": [],
        "count": 0,
        "message": "Verification history not yet implemented"
    }), 200


@app.route('/api/v1/batch/verify', methods=['POST'])
def batch_verify():
    """
    Verify multiple images in batch
    
    Expected payload:
    {
        "images": [
            {
                "image": <base64>,
                "signature_data": {...}
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or "images" not in data:
            return jsonify({
                "error": "Invalid request",
                "message": "images array is required"
            }), 400
        
        results = []
        for item in data["images"]:
            try:
                image_base64 = item.get("image")
                signature_data = item.get("signature_data")
                
                if not image_base64 or not signature_data:
                    results.append({
                        "error": "Missing image or signature data"
                    })
                    continue
                
                image_data = base64.b64decode(image_base64)
                result = verifier.verify_image(image_data, signature_data)
                
                results.append(result.to_dict())
                
            except Exception as e:
                results.append({
                    "error": str(e)
                })
        
        return jsonify({
            "results": results,
            "count": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Batch verification failed",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    # Register some demo devices
    device_registry.register_device(
        device_id="AURA-DEV-12345",
        public_key="DEMO_PUBLIC_KEY_1",
        metadata={"manufacturer": "CameraCorp", "model": "ProShot X1"}
    )
    
    device_registry.register_device(
        device_id="AURA-DEV-67890",
        public_key="DEMO_PUBLIC_KEY_2",
        metadata={"manufacturer": "PhotoTech", "model": "AuthenticCam 2.0"}
    )
    
    print("Starting Aura Verification API Server...")
    print("API Documentation:")
    print("  GET  /api/v1/health - Health check")
    print("  POST /api/v1/verify - Verify single image")
    print("  GET  /api/v1/device/<device_id> - Get device info")
    print("  POST /api/v1/device - Register device")
    print("  GET  /api/v1/devices - List all devices")
    print("  POST /api/v1/batch/verify - Batch verify images")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
