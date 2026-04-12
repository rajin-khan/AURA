import os
import sys
import tempfile
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from aura.data_engine.manifest import load_pair_manifest_jsonl, write_pair_manifest_jsonl
from aura.data_engine.schema import PairSample
from aura.data_engine.splits import assign_random_splits
from aura.data_engine.validate import validate_samples


class TestDataEngine(unittest.TestCase):
    def test_validate_good_samples(self):
        samples = [
            PairSample(
                id="a",
                dataset="demo",
                split="train",
                domain="natural-image",
                source_type="internal-controlled",
                original_path="orig.jpg",
                edited_path="edit.jpg",
                label="cosmetic",
                edit_family="crop",
            )
        ]
        report = validate_samples(samples)
        self.assertTrue(report.ok)
        self.assertEqual(len(report.errors), 0)

    def test_reject_duplicate_ids(self):
        s1 = PairSample(
            id="dup",
            dataset="demo",
            split="train",
            domain="natural-image",
            source_type="internal-controlled",
            original_path="a.jpg",
            edited_path="b.jpg",
            label="cosmetic",
            edit_family="crop",
        )
        s2 = PairSample(
            id="dup",
            dataset="demo",
            split="val",
            domain="natural-image",
            source_type="internal-controlled",
            original_path="c.jpg",
            edited_path="d.jpg",
            label="ai",
            edit_family="inpaint-removal",
        )
        report = validate_samples([s1, s2])
        self.assertFalse(report.ok)
        self.assertTrue(any("duplicate id" in e.message for e in report.errors))

    def test_split_assignment_preserves_count(self):
        samples = [
            PairSample(
                id=f"id-{i}",
                dataset="demo",
                split="unspecified",
                domain="natural-image",
                source_type="internal-controlled",
                original_path=f"orig-{i}.jpg",
                edited_path=f"edit-{i}.jpg",
                label="cosmetic" if i % 2 == 0 else "ai",
                edit_family="crop" if i % 2 == 0 else "inpaint-removal",
            )
            for i in range(10)
        ]
        assigned = assign_random_splits(samples, seed=1)
        self.assertEqual(len(assigned), len(samples))
        self.assertTrue(all(s.split in {"train", "val", "test"} for s in assigned))

    def test_manifest_roundtrip(self):
        sample = PairSample(
            id="rt-1",
            dataset="demo",
            split="train",
            domain="natural-image",
            source_type="internal-controlled",
            original_path="orig.jpg",
            edited_path="edit.jpg",
            label="cosmetic",
            edit_family="crop",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "manifest.jsonl")
            write_pair_manifest_jsonl(path, [sample])
            loaded = load_pair_manifest_jsonl(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].id, "rt-1")


if __name__ == "__main__":
    unittest.main()
