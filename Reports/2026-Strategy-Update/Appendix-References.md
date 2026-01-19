# Appendix: Research & References
**Date:** January 18, 2026

This document compiles the academic research and technical reports underpinning Aura's 2026 Strategy Update.

## 1. Adversarial Attacks on Provenance (C2PA)
Current research highlights that while C2PA provides a robust chain of custody, it is vulnerable to specific attack vectors when used in isolation.

*   **Provenance Piggybacking & Soft-Binding Collisions**
    *   *Concept:* Attackers layer deepfakes over authentic, C2PA-credentialed backgrounds. The manifest remains valid for the background, potentially misleading the user into trusting the entire image.
    *   *Relevance to Aura:* This justifies our "Forensic Analysis" layer, which must detect the *visual anomaly* of the deepfake even if the C2PA signature is valid.
    *   *Reference:* *Adversarial Attacks on Content Credentials* (Security Congress, late 2024).

*   **Manifest Stripping**
    *   *Concept:* 90% of social platforms still strip metadata upon upload for compression.
    *   *Relevance:* C2PA is "fragile." Aura must assume the manifest is missing and rely on "Blind Verification" (watermark/noise analysis).

## 2. Watermarking Robustness
*   **Diffusion-Based Removal**
    *   *Concept:* Attacks using diffusion models can scrub "invisible" watermarks (like SynthID) by treating them as noise to be "denoised."
    *   *Relevance:* Reliance on a single watermark is dangerous. Aura's "Risk Engine" analyzes *multiple* signal layers (PRNU, CFA artifacts, Compression history) to create a robust score.
    *   *Reference:* *W-Bench: Benchmarking Robustness of Watermarks* (2025).

## 3. Trust Calibration in AI Systems
*   **The "Overtrust" Hazard**
    *   *Concept:* Users tend to over-rely on AI "Confidence Scores" if they are presented as objective percentages without context. "Miscalibrated confidence" leads to catastrophic errors.
    *   *Relevance:* Supporting our move to **"Risk Labels"** with qualitative descriptions (e.g., "Inconclusive") rather than just raw numbers.
    *   *Reference:* *Trust Calibration in Human-AI Teams* (Berkeley AI Research, 2024).

## 4. Key Standards
*   **C2PA Specification v2.1 (2025 Update)**
    *   Focuses on "hard binding" updates to prevent "soft-binding collisions."
*   **EU AI Act (Transparency Provisions)**
    *   Article 50: Mandates distinct labeling for Deepfakes and AI-generated content in public interest areas.
