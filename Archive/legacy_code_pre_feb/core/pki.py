"""
Aura Public Key Infrastructure (PKI) Management
Central authority for device certificate management
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class CertificateStatus(Enum):
    """Certificate status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class DeviceCertificate:
    """Device certificate structure"""
    device_id: str
    public_key: str
    issued_by: str
    issued_at: str
    expires_at: str
    serial_number: str
    status: CertificateStatus
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return {
            "device_id": self.device_id,
            "public_key": self.public_key,
            "issued_by": self.issued_by,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "serial_number": self.serial_number,
            "status": self.status.value,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def is_valid(self) -> bool:
        """Check if certificate is currently valid"""
        if self.status != CertificateStatus.ACTIVE:
            return False
        
        expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        now = datetime.utcnow()
        
        return expires > now


class AuraPKI:
    """
    Aura Public Key Infrastructure
    Manages device certificates and key distribution
    """
    
    def __init__(self, ca_name: str = "Aura Certificate Authority"):
        """
        Initialize PKI
        
        Args:
            ca_name: Name of the Certificate Authority
        """
        self.ca_name = ca_name
        self.certificates: Dict[str, DeviceCertificate] = {}
        self.revocation_list: List[str] = []  # List of serial numbers
        self.certificate_validity_years = 5
    
    def generate_serial_number(self, device_id: str) -> str:
        """Generate unique certificate serial number"""
        data = f"{device_id}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()
    
    def issue_certificate(self,
                         device_id: str,
                         public_key: str,
                         metadata: Optional[Dict] = None) -> DeviceCertificate:
        """
        Issue a new device certificate
        
        Args:
            device_id: Unique device identifier
            public_key: Device's public key
            metadata: Optional device metadata
            
        Returns:
            DeviceCertificate object
        """
        # Check if certificate already exists
        if device_id in self.certificates:
            existing = self.certificates[device_id]
            if existing.is_valid():
                raise ValueError(f"Certificate already exists for device {device_id}")
        
        # Generate serial number
        serial_number = self.generate_serial_number(device_id)
        
        # Set dates
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(days=365 * self.certificate_validity_years)
        
        # Create certificate
        certificate = DeviceCertificate(
            device_id=device_id,
            public_key=public_key,
            issued_by=self.ca_name,
            issued_at=issued_at.isoformat() + 'Z',
            expires_at=expires_at.isoformat() + 'Z',
            serial_number=serial_number,
            status=CertificateStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        # Store certificate
        self.certificates[device_id] = certificate
        
        return certificate
    
    def revoke_certificate(self, device_id: str, reason: Optional[str] = None):
        """
        Revoke a device certificate
        
        Args:
            device_id: Device identifier
            reason: Optional revocation reason
        """
        if device_id not in self.certificates:
            raise ValueError(f"Certificate not found for device {device_id}")
        
        certificate = self.certificates[device_id]
        certificate.status = CertificateStatus.REVOKED
        
        # Add to revocation list
        if certificate.serial_number not in self.revocation_list:
            self.revocation_list.append(certificate.serial_number)
        
        # Update metadata with revocation info
        certificate.metadata["revoked_at"] = datetime.utcnow().isoformat() + 'Z'
        if reason:
            certificate.metadata["revocation_reason"] = reason
    
    def get_certificate(self, device_id: str) -> Optional[DeviceCertificate]:
        """Get certificate for device"""
        return self.certificates.get(device_id)
    
    def verify_certificate(self, certificate: DeviceCertificate) -> tuple[bool, Optional[str]]:
        """
        Verify certificate validity
        
        Args:
            certificate: Certificate to verify
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        # Check if certificate is in our database
        if certificate.device_id not in self.certificates:
            return False, "Certificate not found in registry"
        
        # Check if revoked
        if certificate.serial_number in self.revocation_list:
            return False, "Certificate has been revoked"
        
        # Check status
        if certificate.status != CertificateStatus.ACTIVE:
            return False, f"Certificate status is {certificate.status.value}"
        
        # Check expiration
        if not certificate.is_valid():
            return False, "Certificate has expired"
        
        # Compare with stored certificate
        stored = self.certificates[certificate.device_id]
        if stored.serial_number != certificate.serial_number:
            return False, "Certificate serial number mismatch"
        
        return True, None
    
    def renew_certificate(self, device_id: str) -> DeviceCertificate:
        """
        Renew an existing certificate
        
        Args:
            device_id: Device identifier
            
        Returns:
            New DeviceCertificate
        """
        old_cert = self.certificates.get(device_id)
        if not old_cert:
            raise ValueError(f"Certificate not found for device {device_id}")
        
        # Revoke old certificate
        self.revoke_certificate(device_id, reason="Renewed")
        
        # Issue new certificate with same device info
        new_cert = self.issue_certificate(
            device_id=device_id,
            public_key=old_cert.public_key,
            metadata=old_cert.metadata
        )
        
        return new_cert
    
    def get_revocation_list(self) -> List[str]:
        """Get current revocation list"""
        return self.revocation_list.copy()
    
    def check_revocation(self, serial_number: str) -> bool:
        """Check if certificate serial number is revoked"""
        return serial_number in self.revocation_list
    
    def get_all_certificates(self) -> Dict[str, DeviceCertificate]:
        """Get all certificates"""
        return self.certificates.copy()
    
    def export_certificate(self, device_id: str) -> str:
        """Export certificate as JSON string"""
        cert = self.certificates.get(device_id)
        if not cert:
            raise ValueError(f"Certificate not found for device {device_id}")
        
        return cert.to_json()


if __name__ == "__main__":
    # Example usage
    pki = AuraPKI()
    
    # Issue certificate
    cert = pki.issue_certificate(
        device_id="AURA-DEV-12345",
        public_key="PUBLIC_KEY_PLACEHOLDER",
        metadata={"manufacturer": "CameraCorp", "model": "ProShot X1"}
    )
    
    print("Issued Certificate:")
    print(cert.to_json())
    
    # Verify certificate
    is_valid, reason = pki.verify_certificate(cert)
    print(f"\nCertificate Valid: {is_valid}")
    if reason:
        print(f"Reason: {reason}")
    
    # Revoke certificate
    print("\nRevoking certificate...")
    pki.revoke_certificate(cert.device_id, reason="Device compromised")
    
    # Verify again
    is_valid, reason = pki.verify_certificate(cert)
    print(f"Certificate Valid: {is_valid}")
    print(f"Reason: {reason}")
