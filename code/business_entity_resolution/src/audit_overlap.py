"""Disk-backed duplicate-record and train/test overlap checks.

Run only after both target indexes are complete. These expensive scans are
separate from the deadline-critical matcher and do not inform its threshold.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sqlite3
import time
from pathlib import Path

from pipeline import read_source


def raw_hash(row: dict[str, str]) -> bytes:
    payload = "\0".join((row["business_name"], row["business_address"], row["country"]))
    return hashlib.blake2b(payload.encode("utf-8"), digest_size=16, person=b"amzraw26").digest()


def source1_audit(data_dir: Path, db_path: Path) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    start = time.monotonic()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS source1 (split TEXT NOT NULL, entity_id TEXT NOT NULL, signature BLOB NOT NULL, PRIMARY KEY(split,entity_id))")
        existing = conn.execute("SELECT COUNT(*) FROM source1").fetchone()[0]
        if existing:
            raise RuntimeError(f"Existing source1 audit rows in {db_path}; preserve the old report or use a fresh audit DB path")
        counts = collections.Counter()
        countries: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
        batch = []
        for split in ("train", "test"):
            for row in read_source(data_dir / split / f"{split}_source1.tsv"):
                batch.append((split, row["entity_id"], raw_hash(row)))
                counts[split] += 1
                countries[split][row["country"]] += 1
                if len(batch) >= 50_000:
                    conn.executemany("INSERT INTO source1 VALUES (?,?,?)", batch)
                    conn.commit()
                    batch.clear()
                    if counts[split] % 500_000 == 0:
                        print(f"Source 1 audit {split} rows={counts[split]:,} elapsed_s={time.monotonic()-start:.0f}", flush=True)
            if batch:
                conn.executemany("INSERT INTO source1 VALUES (?,?,?)", batch)
                conn.commit()
                batch.clear()
        conn.execute("CREATE INDEX source1_split_signature ON source1(split,signature)")
        conn.commit()
        duplicate_rows = {}
        for split in ("train", "test"):
            duplicate_rows[split] = conn.execute("""
                SELECT COALESCE(SUM(n-1),0) FROM
                (SELECT COUNT(*) n FROM source1 WHERE split=? GROUP BY signature HAVING n>1)
            """, (split,)).fetchone()[0]
        cross_split_s1_ids = conn.execute("""
            SELECT COUNT(*) FROM source1 a JOIN source1 b
            ON a.entity_id=b.entity_id WHERE a.split='train' AND b.split='test'
        """).fetchone()[0]
        return {
            "source1_rows": dict(counts),
            "source1_country_counts": {key: dict(value) for key, value in countries.items()},
            "source1_duplicate_ids_within_each_split": 0,
            "source1_exact_duplicate_record_extra_rows": duplicate_rows,
            "source1_train_test_id_overlap": cross_split_s1_ids,
            "source1_elapsed_s": time.monotonic() - start,
        }
    finally:
        conn.close()


def target_audit(train_index: Path, test_index: Path) -> dict:
    start = time.monotonic()
    conn = sqlite3.connect(f"file:{train_index.resolve().as_posix()}?mode=ro", uri=True)
    try:
        conn.execute("ATTACH DATABASE ? AS testdb", (f"file:{test_index.resolve().as_posix()}?mode=ro",))
        overlap = conn.execute("""
            SELECT COUNT(*) FROM records a
            WHERE EXISTS (SELECT 1 FROM testdb.records b WHERE b.entity_id=a.entity_id)
        """).fetchone()[0]
        result = {"target_train_test_id_overlap": overlap}
        for split, table in (("train", "records"), ("test", "testdb.records")):
            within, across = conn.execute(f"""
                SELECT
                  COALESCE(SUM(CASE WHEN n2>1 THEN n2-1 ELSE 0 END
                             + CASE WHEN n3>1 THEN n3-1 ELSE 0 END),0),
                  COALESCE(SUM(CASE WHEN n2>0 AND n3>0 THEN 1 ELSE 0 END),0)
                FROM (
                  SELECT country,nname,naddr,
                         SUM(CASE WHEN src='s2' THEN 1 ELSE 0 END) n2,
                         SUM(CASE WHEN src='s3' THEN 1 ELSE 0 END) n3
                  FROM {table}
                  GROUP BY country,nname,naddr
                )
            """).fetchone()
            result[f"{split}_target_normalized_duplicate_extra_rows_within_source"] = within
            result[f"{split}_target_normalized_duplicate_groups_across_sources"] = across
            print(f"Target duplicate groups analyzed for {split}; elapsed_s={time.monotonic()-start:.0f}", flush=True)
        result["target_elapsed_s"] = time.monotonic() - start
        return result
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--train-index", type=Path, required=True)
    parser.add_argument("--test-index", type=Path, required=True)
    parser.add_argument("--audit-db", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source1 = source1_audit(args.data_dir, args.audit_db)
    targets = target_audit(args.train_index, args.test_index)
    report = {**source1, **targets}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
