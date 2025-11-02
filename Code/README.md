# Aura Code Implementation

<div align="center">

**Production-ready code implementations for Aura's hardware-level cryptographic attestation system**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-development-yellow)](https://github.com/yourusername/aura)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

</div>

---

## 📁 Project Structure

```
Code/
├── core/
│   ├── __init__.py          # Core module exports
│   ├── signing.py           # Image signing module
│   ├── verification.py      # Image verification module
│   ├── change_detection.py  # AI vs cosmetic change detection
│   └── pki.py               # Public Key Infrastructure management
├── api/
│   └── verification_server.py  # RESTful verification API server
├── examples/
│   └── basic_usage.py       # Usage examples
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### 1. Signing an Image

```python
from core.signing import AuraSigner

# Initialize signer
signer = AuraSigner(device_id="AURA-DEV-12345")

# Sign image
with open("image.jpg", "rb") as f:
    image_data = f.read()

signature = signer.sign_image(image_data)
print(signature.to_json())
```

#### 2. Verifying an Image

```python
from core.verification import AuraVerifier, DeviceRegistry

# Set up device registry
registry = DeviceRegistry()
registry.register_device(
    device_id="AURA-DEV-12345",
    public_key="DEVICE_PUBLIC_KEY",
    metadata={"manufacturer": "CameraCorp"}
)

# Verify
verifier = AuraVerifier(registry)
result = verifier.verify_image(image_data, signature_data)
print(f"Authentic: {result.authentic}")
```

#### 3. Running the API Server

```bash
cd api
python verification_server.py
```

The server will start on `http://localhost:5000`

---

## 📚 Core Modules

### 1. Signing Module (`core/signing.py`)

**AuraSigner**: Main class for cryptographic signing
- `sign_image()`: Create complete signature for image
- `hash_image()`: Generate SHA-256 hash
- `sign_hash()`: Cryptographically sign hash
- `add_processing_step()`: Add processing step to chain

**Features**:
- Hardware-level cryptographic signing simulation
- Processing chain tracking
- Metadata embedding
- Device certificate integration

### 2. Verification Module (`core/verification.py`)

**AuraVerifier**: Main verification class
- `verify_image()`: Complete image verification
- `verify_signature()`: Verify cryptographic signature
- `verify_certificate()`: Verify device certificate

**VerificationLevel Enum**:
- `HARDWARE_ATTESTED`: Highest confidence (Level 5)
- `FIRMWARE_ATTESTED`: High confidence (Level 4)
- `SOFTWARE_ATTESTED`: Medium confidence (Level 3)
- `UNVERIFIED`: No verification (Level 0)
- `AI_MODIFIED`: Detected AI modifications
- `AUTHENTIC_WITH_ENHANCEMENTS`: Cosmetic changes only

### 3. Change Detection (`core/change_detection.py`)

**ChangeDetector**: AI vs Cosmetic change classification
- `detect_changes()`: Detect and classify changes
- `_detect_ai_changes()`: Detect AI-generated modifications
- `_detect_cosmetic_changes()`: Detect legitimate edits

**ChangeType Enum**:
- `NO_CHANGES`: Image unchanged
- `COSMETIC_ONLY`: Only cosmetic edits
- `AI_INSERTION`: AI objects/scenes added
- `AI_REMOVAL`: AI inpainting/removal
- `AI_MODIFICATION`: AI content modification
- `MIXED`: Combination of AI and cosmetic
- `UNKNOWN`: Unable to classify

### 4. PKI Management (`core/pki.py`)

**AuraPKI**: Certificate Authority operations
- `issue_certificate()`: Issue device certificates
- `revoke_certificate()`: Revoke compromised devices
- `verify_certificate()`: Verify certificate validity
- `renew_certificate()`: Renew expired certificates

**CertificateStatus Enum**:
- `ACTIVE`: Certificate is valid
- `REVOKED`: Certificate has been revoked
- `EXPIRED`: Certificate has expired
- `PENDING`: Certificate is pending approval

---

## 🌐 API Server

### Endpoints

#### Health Check
```
GET /api/v1/health
```

#### Verify Image
```
POST /api/v1/verify
Content-Type: application/json

{
    "image": "<base64_encoded_image>",
    "signature_data": {...},
    "check_changes": true
}
```

#### Get Device Information
```
GET /api/v1/device/<device_id>
```

#### Register Device
```
POST /api/v1/device
Content-Type: application/json

{
    "device_id": "...",
    "public_key": "...",
    "manufacturer": "...",
    "model": "..."
}
```

#### Batch Verify
```
POST /api/v1/batch/verify
Content-Type: application/json

{
    "images": [
        {"image": "...", "signature_data": {...}},
        ...
    ]
}
```

---

## 🔧 Configuration

### Development Mode

The code includes simulation modes for development:

- **Cryptographic Signing**: Uses simulated signatures if `cryptography` library unavailable
- **Device Registry**: In-memory registry for testing
- **Change Detection**: Simplified detection algorithms (full implementation would use ML models)

### Production Considerations

For production deployment:

1. **Hardware Security Module (HSM)**: Integrate with actual HSM for key storage
2. **Database**: Replace in-memory registry with persistent database
3. **ML Models**: Integrate advanced AI detection models
4. **Certificate Chain**: Implement full X.509 certificate chain validation
5. **Rate Limiting**: Add API rate limiting and authentication
6. **Logging**: Comprehensive logging and monitoring
7. **Caching**: Add caching layer for verification results

---

## 📊 Example Workflows

### Complete Signing and Verification

```python
from core.signing import AuraSigner
from core.verification import AuraVerifier, DeviceRegistry
from core.pki import AuraPKI

# 1. Set up PKI
pki = AuraPKI()

# 2. Issue device certificate
cert = pki.issue_certificate(
    device_id="AURA-DEV-12345",
    public_key="PUBLIC_KEY",
    metadata={"manufacturer": "CameraCorp"}
)

# 3. Sign image
signer = AuraSigner(device_id="AURA-DEV-12345")
signature = signer.sign_image(image_data)

# 4. Register device and verify
registry = DeviceRegistry()
registry.register_device(
    device_id="AURA-DEV-12345",
    public_key="PUBLIC_KEY",
    metadata={}
)

verifier = AuraVerifier(registry)
result = verifier.verify_image(image_data, signature.to_dict())
```

### Change Detection Workflow

```python
from core.change_detection import ChangeDetector

detector = ChangeDetector()

# Detect changes
result = detector.detect_changes(
    original_hash=original_hash,
    modified_image_data=modified_image,
    original_signature=signature_data
)

if result.has_changes:
    if result.change_type == ChangeType.AI_MODIFICATION:
        print("⚠️ AI modifications detected!")
    elif result.change_type == ChangeType.COSMETIC_ONLY:
        print("✅ Only cosmetic changes detected")
```

---

## 🧪 Testing

Run examples:

```bash
python examples/basic_usage.py
```

Test API server:

```bash
# Start server
python api/verification_server.py

# Test health endpoint
curl http://localhost:5000/api/v1/health
```

---

## 📝 Notes

### Current Implementation Status

- ✅ Core signing module
- ✅ Core verification module
- ✅ Basic change detection
- ✅ PKI management
- ✅ RESTful API server
- ✅ Example usage code

### Future Enhancements

- [ ] Advanced AI detection models (deepfake, inpainting)
- [ ] Full image forensic analysis
- [ ] Database integration
- [ ] HSM integration
- [ ] Production-grade security hardening
- [ ] Performance optimization
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] Kubernetes deployment configs

---

## 🔒 Security Considerations

⚠️ **Development Mode**: This implementation is for development and demonstration purposes. Production deployment requires:

1. **Secure Key Storage**: Use hardware security modules (HSM)
2. **Certificate Authority**: Proper CA hierarchy and certificate management
3. **Network Security**: TLS/HTTPS for all API communication
4. **Access Control**: Authentication and authorization for API endpoints
5. **Audit Logging**: Complete audit trail of all operations
6. **Security Audits**: Regular security reviews and penetration testing

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

This is a research project in active development. Contributions welcome!

---

*Last updated: January 2025*
