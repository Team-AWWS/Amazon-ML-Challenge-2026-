"""Measure exact and partial-identity overlap across Source 1 split partitions.

Same-name/different-address and same-address/different-name are only leakage
*proxies*: shared names and buildings need not denote the same real entity.
"""

from __future__ import annotations

import argparse
import collections
import json
import sqlite3
import time
from pathlib import Path

from pipeline import normalize, read_source, split_bucket


def run(source1: Path, db_path: Path, report_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    start = time.monotonic()
    try:
        exists = conn.execute("SELECT name FROM sqlite_master WHERE name='anchors'").fetchone()
        if exists:
            raise RuntimeError(f"Existing leakage audit table in {db_path}; use a fresh audit DB path")
        conn.execute("""CREATE TABLE anchors (
            entity_id TEXT PRIMARY KEY,
            country TEXT NOT NULL,
            partition TEXT NOT NULL,
            nname TEXT NOT NULL,
            naddr TEXT NOT NULL
        )""")
        count = 0
        batch = []
        for row in read_source(source1):
            bucket = split_bucket(row)
            partition = "dev" if bucket < 2 else "holdout" if bucket < 4 else "train"
            batch.append((row["entity_id"], row["country"], partition,
                          normalize(row["business_name"]), normalize(row["business_address"])))
            if len(batch) >= 50_000:
                conn.executemany("INSERT INTO anchors VALUES (?,?,?,?,?)", batch)
                count += len(batch)
                batch.clear()
                conn.commit()
                if count % 500_000 == 0:
                    print(f"Leakage audit loaded {count:,} anchors; elapsed_s={time.monotonic()-start:.0f}", flush=True)
        if batch:
            conn.executemany("INSERT INTO anchors VALUES (?,?,?,?,?)", batch)
            count += len(batch)
            conn.commit()
        conn.execute("CREATE INDEX anchors_country_name_partition ON anchors(country,nname,partition)")
        conn.execute("CREATE INDEX anchors_country_addr_partition ON anchors(country,naddr,partition)")
        conn.commit()

        exact_groups_crossing = conn.execute("""
            SELECT COUNT(*) FROM (
                SELECT country,nname,naddr FROM anchors
                GROUP BY country,nname,naddr HAVING COUNT(DISTINCT partition)>1
            )
        """).fetchone()[0]
        strong_name_proxy = conn.execute("""
            SELECT COUNT(*) FROM anchors a WHERE a.partition!='train' AND a.nname!=''
              AND EXISTS (SELECT 1 FROM anchors b WHERE b.country=a.country AND b.nname=a.nname
                          AND b.partition='train' AND b.naddr!=a.naddr)
        """).fetchone()[0]
        strong_address_proxy = conn.execute("""
            SELECT COUNT(*) FROM anchors a WHERE a.partition!='train' AND a.naddr!=''
              AND EXISTS (SELECT 1 FROM anchors b WHERE b.country=a.country AND b.naddr=a.naddr
                          AND b.partition='train' AND b.nname!=a.nname)
        """).fetchone()[0]
        examples = [dict(zip(("heldout_id", "train_id", "country", "name", "heldout_address", "train_address"), row))
                    for row in conn.execute("""
                        SELECT a.entity_id,b.entity_id,a.country,a.nname,a.naddr,b.naddr
                        FROM anchors a JOIN anchors b ON a.country=b.country AND a.nname=b.nname
                        WHERE a.partition!='train' AND b.partition='train' AND a.naddr!=b.naddr
                        LIMIT 5
                    """)]
        report = {
            "anchors": count,
            "exact_name_address_groups_crossing_partitions": exact_groups_crossing,
            "dev_or_holdout_anchors_sharing_exact_name_but_different_address_with_train": strong_name_proxy,
            "dev_or_holdout_anchors_sharing_exact_address_but_different_name_with_train": strong_address_proxy,
            "name_proxy_examples": examples,
            "interpretation": "Partial-field overlaps are leakage-risk proxies, not confirmed shared entities.",
            "elapsed_s": time.monotonic()-start,
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source1", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    run(args.source1, args.db, args.report)


if __name__ == "__main__":
    main()
