# Hybrid Trust Architecture (HTA) Specification
**Date:** January 18, 2026
**Status:** DRAFT v1.0

## 1. Executive Summary
The Hybrid Trust Architecture (HTA) moves Aura beyond a simple "AI Detector." It implements a **"Swiss Cheese" Defense Model** where multiple imperfect layers of verification stack to prevent false trust. It combines deterministic cryptographic checks (C2PA) with probabilistic forensic analysis (AI Detection).

## 2. System Architecture Diagram

```mermaid
graph TD
    subgraph Client ["Client Layer (Mobile/Web)"]
        A[📸 Input Media] --> B{🔐 C2PA Check}
        B -- "Signature Valid" --> C[✅ Display 'Verified Source']
        B -- "Signature Missing/Invalid" --> D[☁️ Request Forensic Analysis]
        F[🏷️ Render Risk Label]
    end

    subgraph Cloud ["Aura Trust Cloud"]
        D --> E{🧠 Risk Engine}
        
        subgraph Analysis ["Forensic Pipeline"]
            E --> |Layer 1| G[📉 Signal Noise Analysis]
            E --> |Layer 2| H[🌊 Watermark Search<br>(SynthID/Digimarc)]
            E --> |Layer 3| I[👁️ Semantic Anomaly Detector]
        end

        G & H & I --> J[📊 Probability Aggregator]
        J --> K{⚖️ Calibration Gate}
        K -- "Confidence > 95%" --> L[🔴/🟢 High Confidence Result]
        K -- "Confidence < 95%" --> M[⚪ Inconclusive / Risk of Interpretation]
    end

    L & M --> F
    C -.-> |Optional| D
    
    style A fill:#eceff1,stroke:#455a64
    style C fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style L fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style M fill:#eceff1,stroke:#78909c,stroke-dasharray: 5 5
```

## 3. Core Components

### 3.1. Layer 1: The Cryptographic Gate (C2PA)
*   **Function:** Checks for the presence of a valid `application/c2pa` manifest.
*   **Handling "Provenance Piggybacking":**
    *   Even if a C2PA signature is valid, the media is *still* sent to the Forensic Pipeline if the signing credential is not from a "High Trust" issuer (e.g., BBC, Nikon, Adobe).
    *   This mitigates attacks where valid credentials are used to sign manipulated content.

### 3.2. Layer 2: The Forensic Pipeline
If Layer 1 fails (missing signature) or flags caution, Layer 2 engages. It is **Probabilistic**, not Deterministic.
*   **A. Signal Noise Analysis:** Analyzes PRNU (Photo Response Non-Uniformity) and CFA (Color Filter Array) artifacts. Real sensors leave specific noise footprints; Diffusers (AI) leave Gaussian/Structured noise.
*   **B. Watermark Search:** Scans for "blind" hints of SynthID (Google), Meta AI, or hidden frequency-domain watermarks.
*   **C. Semantic Anomaly:** Uses Vision-Language Models (VLMs) to check for "impossible physics" (e.g., inconsistent shadows, impossible reflections).

### 3.3. Layer 3: The Calibration Gate
This is the **Strategic Check** derived from our "Do Not Classify What You Can't Prove" policy.
*   **Input:** Aggregated Probability Score (0.0 - 1.0).
*   **Logic:**
    *   `if score > 0.95`: Return **"High Probability AI"** (Red Label).
    *   `if score < 0.05`: Return **"High Probability Authentic"** (Green Label).
    *   `else`: Return **"Inconclusive / Mixed Signals"** (Grey Label).
*   **Outcome:** We filter out the "noisy" middle ground (the 10-90% range) where false positives occur.

## 4. Threat Model Mitigation

| Threat Vector | Mitigation Strategy | Component |
|---------------|---------------------|-----------|
| **Manifest Stripping** | Social platforms stripping metadata | **Forensic Pipeline** (Layer 2) acts as the fallback. |
| **Soft-Binding Collision** | Deepfake pasted on verified background | **Semantic Anomaly Detector** flags visual inconsistency despite valid metadata. |
| **Adversarial Noise** | AI adding noise to fool detectors | **Trust Calibration** (Layer 3) forces "Inconclusive" outcome rather than a false "Real" classification. |

## 5. References
*   *Adversarial Attacks on Content Credentials*, SecCongress 2024.
*   *Trust Calibration in Human-AI Teams*, Berkeley 2024.
