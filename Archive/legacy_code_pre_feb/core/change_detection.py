"""
Aura Change Detection Module
Detects and classifies AI vs Cosmetic changes in images
"""

import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    """Types of changes detected"""
    NO_CHANGES = "no_changes"
    COSMETIC_ONLY = "cosmetic_only"
    AI_INSERTION = "ai_insertion"
    AI_REMOVAL = "ai_removal"
    AI_MODIFICATION = "ai_modification"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class CosmeticChangeType(Enum):
    """Types of cosmetic changes"""
    COLOR_ADJUSTMENT = "color_adjustment"
    BRIGHTNESS_CONTRAST = "brightness_contrast"
    SHARPENING = "sharpening"
    BLUR = "blur"
    CROPPING = "cropping"
    ROTATION = "rotation"
    FILTER = "filter"
    NOISE_REDUCTION = "noise_reduction"
    WHITE_BALANCE = "white_balance"


@dataclass
class ChangeRegion:
    """Represents a changed region in an image"""
    x: int
    y: int
    width: int
    height: int
    change_type: ChangeType
    confidence: float
    details: Optional[Dict] = None


@dataclass
class ChangeDetectionResult:
    """Result of change detection analysis"""
    has_changes: bool
    change_type: ChangeType
    ai_changes: Dict
    cosmetic_changes: Dict
    changed_regions: List[ChangeRegion]
    confidence: float
    
    def to_dict(self) -> Dict:
        return {
            "has_changes": self.has_changes,
            "change_type": self.change_type.value,
            "ai_changes": self.ai_changes,
            "cosmetic_changes": self.cosmetic_changes,
            "changed_regions": [
                {
                    "x": r.x,
                    "y": r.y,
                    "width": r.width,
                    "height": r.height,
                    "change_type": r.change_type.value,
                    "confidence": r.confidence,
                    "details": r.details
                }
                for r in self.changed_regions
            ],
            "confidence": self.confidence
        }


class ChangeDetector:
    """
    Detects and classifies changes in images
    """
    
    def __init__(self):
        self.ai_detection_threshold = 0.75
        self.cosmetic_detection_threshold = 0.60
    
    def detect_changes(self,
                      original_hash: str,
                      modified_image_data: bytes,
                      original_signature: Dict) -> ChangeDetectionResult:
        """
        Detect and classify changes between original and modified image
        
        Args:
            original_hash: SHA-256 hash of original image
            modified_image_data: Bytes of potentially modified image
            original_signature: Original signature data
            
        Returns:
            ChangeDetectionResult
        """
        # Step 1: Hash comparison
        modified_hash = hashlib.sha256(modified_image_data).hexdigest()
        
        if modified_hash == original_hash:
            return ChangeDetectionResult(
                has_changes=False,
                change_type=ChangeType.NO_CHANGES,
                ai_changes={"detected": False, "probability": 0.0, "regions": []},
                cosmetic_changes={"detected": False, "types": []},
                changed_regions=[],
                confidence=1.0
            )
        
        # Step 2: Analyze processing chain for suspicious operations
        processing_chain = original_signature.get("processing_chain", [])
        chain_analysis = self._analyze_processing_chain(processing_chain)
        
        # Step 3: Perform image forensic analysis
        forensic_analysis = self._forensic_analysis(modified_image_data)
        
        # Step 4: Detect AI changes
        ai_detection = self._detect_ai_changes(modified_image_data, forensic_analysis)
        
        # Step 5: Detect cosmetic changes
        cosmetic_detection = self._detect_cosmetic_changes(modified_image_data, forensic_analysis)
        
        # Step 6: Classify overall change type
        change_type = self._classify_change_type(ai_detection, cosmetic_detection, chain_analysis)
        
        # Step 7: Identify changed regions
        changed_regions = self._identify_changed_regions(modified_image_data, ai_detection, cosmetic_detection)
        
        # Step 8: Calculate overall confidence
        confidence = self._calculate_confidence(ai_detection, cosmetic_detection, forensic_analysis)
        
        return ChangeDetectionResult(
            has_changes=True,
            change_type=change_type,
            ai_changes=ai_detection,
            cosmetic_changes=cosmetic_detection,
            changed_regions=changed_regions,
            confidence=confidence
        )
    
    def _analyze_processing_chain(self, processing_chain: List[Dict]) -> Dict:
        """
        Analyze processing chain for suspicious operations
        
        Returns:
            Analysis results
        """
        suspicious_ops = []
        legitimate_ops = []
        
        ai_operations = [
            "ai_object_insertion",
            "ai_inpainting",
            "deepfake_face_swap",
            "ai_style_transfer",
            "ai_outpainting",
            "ai_enhancement"
        ]
        
        legitimate_operations = [
            "demosaicing",
            "noise_reduction",
            "color_correction",
            "brightness_adjustment",
            "sharpening",
            "cropping",
            "rotation"
        ]
        
        for step in processing_chain:
            if isinstance(step, dict):
                operation = step.get("operation", "").lower()
                legitimate = step.get("legitimate", True)
                
                if not legitimate:
                    suspicious_ops.append(operation)
                elif any(ai_op in operation for ai_op in ai_operations):
                    suspicious_ops.append(operation)
                elif any(leg_op in operation for leg_op in legitimate_operations):
                    legitimate_ops.append(operation)
        
        return {
            "suspicious_operations": suspicious_ops,
            "legitimate_operations": legitimate_ops,
            "has_ai_operations": len(suspicious_ops) > 0
        }
    
    def _forensic_analysis(self, image_data: bytes) -> Dict:
        """
        Perform image forensic analysis
        
        Args:
            image_data: Image bytes
            
        Returns:
            Forensic analysis results
        """
        # Placeholder for advanced forensic analysis
        # In production, would use:
        # - Frequency domain analysis (DCT, FFT)
        # - Color histogram analysis
        # - Noise pattern analysis
        # - Compression artifact analysis
        
        return {
            "frequency_anomalies": False,
            "color_anomalies": False,
            "noise_pattern_score": 0.5,
            "compression_consistency": True,
            "overall_ai_probability": 0.3
        }
    
    def _detect_ai_changes(self, image_data: bytes, forensic_analysis: Dict) -> Dict:
        """
        Detect AI-generated changes
        
        Args:
            image_data: Image bytes
            forensic_analysis: Results from forensic analysis
            
        Returns:
            AI detection results
        """
        # Combine forensic signals
        ai_probability = forensic_analysis.get("overall_ai_probability", 0.0)
        
        # Check for specific AI artifacts
        has_frequency_anomalies = forensic_analysis.get("frequency_anomalies", False)
        has_color_anomalies = forensic_analysis.get("color_anomalies", False)
        noise_score = forensic_analysis.get("noise_pattern_score", 0.5)
        
        # Increase probability if anomalies detected
        if has_frequency_anomalies:
            ai_probability += 0.2
        if has_color_anomalies:
            ai_probability += 0.15
        if noise_score > 0.7:
            ai_probability += 0.1
        
        # Cap at 1.0
        ai_probability = min(ai_probability, 1.0)
        
        detected = ai_probability > self.ai_detection_threshold
        
        return {
            "detected": detected,
            "probability": ai_probability,
            "regions": [],
            "model_fingerprints": [],  # Would identify specific AI model
            "details": {
                "frequency_anomalies": has_frequency_anomalies,
                "color_anomalies": has_color_anomalies,
                "noise_pattern_score": noise_score
            }
        }
    
    def _detect_cosmetic_changes(self, image_data: bytes, forensic_analysis: Dict) -> Dict:
        """
        Detect cosmetic/legitimate changes
        
        Args:
            image_data: Image bytes
            forensic_analysis: Results from forensic analysis
            
        Returns:
            Cosmetic change detection results
        """
        # In production, would analyze:
        # - Color space transformations
        # - Global vs local changes
        # - Filter applications
        # - Geometric transformations
        
        # Simplified detection
        compression_consistent = forensic_analysis.get("compression_consistency", True)
        noise_score = forensic_analysis.get("noise_pattern_score", 0.5)
        
        # If compression is consistent and noise is normal, likely cosmetic
        cosmetic_probability = 0.7 if compression_consistent and 0.3 < noise_score < 0.7 else 0.3
        
        detected = cosmetic_probability > self.cosmetic_detection_threshold
        
        # Identify types of cosmetic changes
        change_types = []
        if detected:
            change_types = [
                {
                    "type": CosmeticChangeType.COLOR_ADJUSTMENT.value,
                    "confidence": 0.6,
                    "regions": ["full_image"]
                }
            ]
        
        return {
            "detected": detected,
            "types": change_types,
            "probability": cosmetic_probability
        }
    
    def _classify_change_type(self,
                             ai_detection: Dict,
                             cosmetic_detection: Dict,
                             chain_analysis: Dict) -> ChangeType:
        """
        Classify overall change type
        
        Args:
            ai_detection: AI detection results
            cosmetic_detection: Cosmetic detection results
            chain_analysis: Processing chain analysis
            
        Returns:
            ChangeType enum
        """
        has_ai = ai_detection.get("detected", False) or chain_analysis.get("has_ai_operations", False)
        has_cosmetic = cosmetic_detection.get("detected", False)
        
        if has_ai and has_cosmetic:
            return ChangeType.MIXED
        elif has_ai:
            # Determine specific AI type
            if chain_analysis.get("suspicious_operations"):
                ops = chain_analysis["suspicious_operations"]
                if any("insertion" in op for op in ops):
                    return ChangeType.AI_INSERTION
                elif any("removal" in op or "inpainting" in op for op in ops):
                    return ChangeType.AI_REMOVAL
                else:
                    return ChangeType.AI_MODIFICATION
            return ChangeType.AI_MODIFICATION
        elif has_cosmetic:
            return ChangeType.COSMETIC_ONLY
        else:
            return ChangeType.UNKNOWN
    
    def _identify_changed_regions(self,
                                  image_data: bytes,
                                  ai_detection: Dict,
                                  cosmetic_detection: Dict) -> List[ChangeRegion]:
        """
        Identify specific regions that changed
        
        Args:
            image_data: Image bytes
            ai_detection: AI detection results
            cosmetic_detection: Cosmetic detection results
            
        Returns:
            List of ChangeRegion objects
        """
        regions = []
        
        # In production, would use computer vision to identify regions
        # For now, return placeholder
        if ai_detection.get("detected"):
            regions.append(ChangeRegion(
                x=0, y=0, width=100, height=100,
                change_type=ChangeType.AI_MODIFICATION,
                confidence=ai_detection.get("probability", 0.5)
            ))
        
        if cosmetic_detection.get("detected"):
            regions.append(ChangeRegion(
                x=0, y=0, width=0, height=0,  # Full image
                change_type=ChangeType.COSMETIC_ONLY,
                confidence=cosmetic_detection.get("probability", 0.5),
                details={"type": "global_color_adjustment"}
            ))
        
        return regions
    
    def _calculate_confidence(self,
                              ai_detection: Dict,
                              cosmetic_detection: Dict,
                              forensic_analysis: Dict) -> float:
        """
        Calculate overall confidence in change detection
        
        Args:
            ai_detection: AI detection results
            cosmetic_detection: Cosmetic detection results
            forensic_analysis: Forensic analysis results
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence from detection probabilities
        ai_prob = ai_detection.get("probability", 0.0)
        cosmetic_prob = cosmetic_detection.get("probability", 0.0)
        
        # Higher confidence if one type clearly dominates
        if abs(ai_prob - cosmetic_prob) > 0.3:
            confidence = max(ai_prob, cosmetic_prob)
        else:
            # Lower confidence if ambiguous
            confidence = (ai_prob + cosmetic_prob) / 2 * 0.8
        
        # Adjust based on forensic analysis quality
        compression_consistent = forensic_analysis.get("compression_consistency", True)
        if compression_consistent:
            confidence += 0.1
        
        return min(confidence, 1.0)


if __name__ == "__main__":
    # Example usage
    detector = ChangeDetector()
    
    # Simulate change detection
    original_hash = "original_hash_placeholder"
    modified_image = b"modified_image_data"
    original_signature = {
        "processing_chain": [
            {"operation": "raw_capture", "legitimate": True},
            {"operation": "color_correction", "legitimate": True}
        ]
    }
    
    result = detector.detect_changes(original_hash, modified_image, original_signature)
    print("Change Detection Result:")
    print(json.dumps(result.to_dict(), indent=2))
