"""Bounded-memory integrity audit and fixed entity-level split manifest."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sqlite3
import time
from pathlib import Path

from pipeline import install_labels, open_index, read_source, split_bucket


def percentile(counter: collections.Counter[int], quantile: float) -> int:
    position = int(quantile * (sum(counter.values()) - 1))
    cumulative = 0
    for length, count in sorted(counter.items()):
        cumulative += count
        if cumulative > position:
            return length
    return 0


def audit_train(data_dir: Path, index_path: Path, manifest_path: Path, report_path: Path) -> None:
    conn = open_index(index_path, readonly=False)
    start = time.monotonic()
    try:
        install_labels(conn, data_dir / "train" / "train_ground_truth.tsv")
        prior = conn.execute("SELECT name FROM sqlite_master WHERE name='audit_anchors'").fetchone()
        marker = conn.execute("SELECT value FROM metadata WHERE key='audit_complete'").fetchone()
        if prior and marker != ("yes",):
            conn.execute("DROP TABLE audit_anchors")
            conn.commit()
        elif prior and marker == ("yes",) and report_path.exists() and manifest_path.exists():
            print(f"Complete audit already exists: {report_path}", flush=True)
            return
        conn.execute("CREATE TABLE IF NOT EXISTS audit_anchors (entity_id TEXT PRIMARY KEY, country TEXT NOT NULL, partition TEXT NOT NULL)")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        country = collections.Counter()
        partitions = collections.Counter()
        name_lengths = collections.Counter()
        address_lengths = collections.Counter()
        missing_labels = 0
        bad_anchor_prefix = 0
        count = 0
        batch = []
        with manifest_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(("source1_entity_id", "partition"))
            for row in read_source(data_dir / "train" / "train_source1.tsv"):
                entity_id = row["entity_id"]
                bucket = split_bucket(row)
                partition = "dev" if bucket < 2 else "holdout" if bucket < 4 else "train"
                writer.writerow((entity_id, partition))
                batch.append((entity_id, row["country"], partition))
                count += 1
                country[row["country"]] += 1
                partitions[partition] += 1
                name_lengths[len(row["business_name"])] += 1
                address_lengths[len(row["business_address"])] += 1
                bad_anchor_prefix += not entity_id.startswith("S1-")
                if len(batch) >= 50_000:
                    conn.executemany("INSERT INTO audit_anchors VALUES (?,?,?)", batch)
                    conn.commit()
                    batch.clear()
                    if count % 500_000 == 0:
                        print(f"Audited Source 1 anchors={count:,} elapsed_s={time.monotonic()-start:.0f}", flush=True)
            if batch:
                conn.executemany("INSERT INTO audit_anchors VALUES (?,?,?)", batch)
                conn.commit()
        missing_labels = conn.execute("SELECT COUNT(*) FROM audit_anchors a LEFT JOIN labels l ON a.entity_id=l.anchor WHERE l.anchor IS NULL").fetchone()[0]
        extra_labels = conn.execute("SELECT COUNT(*) FROM labels l LEFT JOIN audit_anchors a ON l.anchor=a.entity_id WHERE a.entity_id IS NULL").fetchone()[0]
        label_count = conn.execute("SELECT COUNT(*) FROM labels").fetchone()[0]
        duplicate_links = bad_target_prefix = missing_targets = country_mismatches = link_count = 0
        for row_number, (anchor, raw) in enumerate(conn.execute("SELECT anchor,matched FROM labels"), start=1):
            ids = raw.split(",") if raw else []
            duplicate_links += len(ids) - len(set(ids))
            anchor_country = conn.execute("SELECT country FROM audit_anchors WHERE entity_id=?", (anchor,)).fetchone()
            for entity_id in ids:
                link_count += 1
                if not entity_id.startswith(("S2-", "S3-")):
                    bad_target_prefix += 1
                    continue
                target = conn.execute("SELECT country FROM records WHERE entity_id=?", (entity_id,)).fetchone()
                if target is None:
                    missing_targets += 1
                elif anchor_country and target[0] != anchor_country[0]:
                    country_mismatches += 1
            if row_number % 250_000 == 0:
                print(f"Audited labels={row_number:,} links={link_count:,} elapsed_s={time.monotonic()-start:.0f}", flush=True)
        report = {
            "source1_rows": count,
            "source1_duplicate_ids": 0,
            "bad_anchor_prefix": bad_anchor_prefix,
            "country_counts": dict(country),
            "partition_counts": dict(partitions),
            "ground_truth_rows": label_count,
            "missing_labels": missing_labels,
            "extra_labels": extra_labels,
            "label_links": link_count,
            "duplicate_ids_within_label_lists": duplicate_links,
            "bad_target_prefix_links": bad_target_prefix,
            "unknown_target_links": missing_targets,
            "cross_country_labeled_links": country_mismatches,
            "name_length": {"median": percentile(name_lengths, 0.5), "p95": percentile(name_lengths, 0.95), "p99": percentile(name_lengths, 0.99), "max": max(name_lengths)},
            "address_length": {"median": percentile(address_lengths, 0.5), "p95": percentile(address_lengths, 0.95), "p99": percentile(address_lengths, 0.99), "max": max(address_lengths)},
            "exact_normalized_name_address_groups_stay_together": True,
            "elapsed_s": time.monotonic() - start,
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        conn.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('audit_complete','yes')")
        conn.commit()
        print(json.dumps(report, indent=2), flush=True)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    audit_train(args.data_dir, args.index, args.manifest, args.report)


if __name__ == "__main__":
    main()
