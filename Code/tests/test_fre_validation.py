import unittest

from aura.fre.fusion import fuse_evidence
from aura.fre.schema import EvidenceItem
from aura.fre.validate import ValidationError


class TestFREValidation(unittest.TestCase):
    def test_probability_bounds(self):
        evidence = [
            EvidenceItem(stream="provenance", name="x", weight=0.0, score=0.0),
            EvidenceItem(stream="forensic", name="y", weight=0.0, score=0.0),
            EvidenceItem(stream="semantic", name="z", weight=0.0, score=0.0),
        ]

        with self.assertRaises(ValidationError):
            fuse_evidence(
                p_prov_auth=-0.1,
                p_forensic_synth=0.5,
                p_sem_anomaly=0.5,
                evidence=evidence,
            )

        with self.assertRaises(ValidationError):
            fuse_evidence(
                p_prov_auth=0.5,
                p_forensic_synth=1.1,
                p_sem_anomaly=0.5,
                evidence=evidence,
            )

    def test_normalizes_weights(self):
        evidence = [
            EvidenceItem(stream="provenance", name="x", weight=0.0, score=0.0),
            EvidenceItem(stream="forensic", name="y", weight=0.0, score=0.0),
            EvidenceItem(stream="semantic", name="z", weight=0.0, score=0.0),
        ]
        card, _ = fuse_evidence(
            p_prov_auth=1.0,
            p_forensic_synth=0.0,
            p_sem_anomaly=0.0,
            evidence=evidence,
        )
        self.assertGreaterEqual(card.confidence, 0.0)
        self.assertLessEqual(card.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
