import sys
import csv
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pipeline import build_index, candidates, check_outputs, entity_f05, evaluate, make_fixture, normalize, open_index, predict, similarity, split_bucket
from audit_data import audit_train
from audit_overlap import source1_audit, target_audit


class MetricTests(unittest.TestCase):
    def test_empty_truth(self):
        self.assertEqual(entity_f05(set(), set()), 1.0)
        self.assertEqual(entity_f05(set(), {"S2-1"}), 0.0)

    def test_nonempty(self):
        self.assertEqual(entity_f05({"a"}, set()), 0.0)
        self.assertEqual(entity_f05({"a", "b"}, {"a", "b"}), 1.0)
        self.assertAlmostEqual(entity_f05({"a", "b"}, {"a", "c"}), 5 / 10)

    def test_unicode_preserved(self):
        self.assertIn("राज", normalize("राज Investments"))
        self.assertEqual(normalize("Payne Énterprises"), "payne enterprises")

    def test_group_split_stable(self):
        row = {"business_name": "Acme, Inc.", "business_address": "500 Market St"}
        self.assertEqual(split_bucket(row), split_bucket(dict(row)))
        self.assertEqual(split_bucket(row), split_bucket({"business_name": "ACME INC", "business_address": "500 market st."}))

    def test_similarity_orders_clear_match(self):
        close = similarity(normalize("Payne Enterprises"), normalize("3315 Fremont Street"), normalize("Payne Enterprices"), normalize("3315 Fremont St"))
        far = similarity(normalize("Payne Enterprises"), normalize("3315 Fremont Street"), normalize("Other Foods"), normalize("9979 Baker Road"))
        self.assertGreater(close, far)

    def test_holdout_cannot_select_its_own_threshold(self):
        with self.assertRaises(ValueError):
            evaluate(Path("unused"), Path("unused"), "holdout", 10, None, "narrow")


class EndToEndFixtureTests(unittest.TestCase):
    def test_index_retrieval_prediction_and_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test = root / "test"
            test.mkdir()

            def write_source(number, rows):
                with (test / f"test_source{number}.tsv").open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream, delimiter="\t")
                    writer.writerow(("entity_id", "business_name", "business_address", "country"))
                    writer.writerows(rows)

            write_source(1, [
                ("S1-1", "Acme Stores", "12 Main Street", "US"),
                ("S1-2", "राज Foods", "12 River Road", "India"),
                ("S1-3", "Nobody", "99 No-Match Lane", "US"),
                ("S1-4", "Boulangerie Étoile", "7 Rue Victor Hugo", "France"),
            ])
            write_source(2, [
                ("S2-1", "Acme Store", "12 Main St", "US"),
                ("S2-2", "Different Name", "12 River Road", "India"),
                ("S2-3", "Boulangerie Etoile", "7 Rue Victor Hugo", "France"),
            ])
            write_source(3, [
                ("S3-1", "Other", "9 Separate Road", "US"),
                ("S3-2", "राज Foods", "", "India"),
                ("S3-3", "Other France", "20 Rue de la Paix", "France"),
            ])
            index = root / "index.sqlite"
            build_index(root, "test", index)
            conn = open_index(index)
            try:
                row = {"business_name": "राज Foods", "business_address": "12 River Road", "country": "India"}
                found = {record[0] for record in candidates(conn, row)}
                self.assertIn("S2-2", found)
                self.assertIn("S3-2", found)
            finally:
                conn.close()
            output = root / "output"
            predict(root, index, output, threshold=0.5, limit=0)
            check_outputs(root, index, output, limit=0)
            with (output / "matching_results.tsv").open(encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream, delimiter="\t"))
                self.assertEqual(len(rows), 4)
                self.assertEqual(rows[2]["matched_entity_ids"], "")
                self.assertEqual(len(rows[1]["matched_entity_ids"].split(",")), 2)
                self.assertIn("S2-3", rows[3]["matched_entity_ids"])
            validator = Path(__file__).resolve().parents[3] / "Dataset" / "student_resource" / "utils" / "validate_submission.py"
            if validator.exists():
                fixture = root / "fixture"
                make_fixture(root, index, output, fixture)
                result = subprocess.run(
                    [sys.executable, str(validator), "--matching", str(output / "matching_results.tsv"),
                     "--candidate", str(output / "candidate_pairs.tsv"), "--test-dir", str(fixture), "--check-ids"],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            train = root / "train"
            train.mkdir()
            for source in (2, 3):
                shutil.copyfile(test / f"test_source{source}.tsv", train / f"train_source{source}.tsv")
            with (train / "train_source1.tsv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, delimiter="\t")
                writer.writerow(("entity_id", "business_name", "business_address", "country"))
                writer.writerow(("S1-1", "Acme Stores", "12 Main Street", "US"))
                writer.writerow(("S1-2", "राज Foods", "12 River Road", "India"))
            with (train / "train_ground_truth.tsv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, delimiter="\t")
                writer.writerow(("source1_entity_id", "matched_entity_ids"))
                writer.writerow(("S1-1", "S2-1"))
                writer.writerow(("S1-2", "S2-2,S3-2"))
            train_index = root / "train_index.sqlite"
            build_index(root, "train", train_index)
            report_file = root / "audit.json"
            audit_train(root, train_index, root / "split.tsv", report_file)
            audit = json.loads(report_file.read_text(encoding="utf-8"))
            self.assertEqual(audit["source1_rows"], 2)
            self.assertEqual(audit["label_links"], 3)
            self.assertEqual(audit["unknown_target_links"], 0)
            overlap = source1_audit(root, root / "overlap.sqlite")
            self.assertEqual(overlap["source1_train_test_id_overlap"], 2)
            target_overlap = target_audit(train_index, index)
            self.assertEqual(target_overlap["target_train_test_id_overlap"], 6)
            france_output = root / "france_output"
            predict(root, index, france_output, 0.5, 0, "narrow", country="France")
            check_outputs(root, index, france_output, 0, country="France")


if __name__ == "__main__":
    unittest.main()
