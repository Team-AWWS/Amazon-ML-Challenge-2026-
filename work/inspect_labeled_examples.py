"""Read a few genuine labeled train pairs for the engineering handoff."""

from __future__ import annotations

import csv
import json
import sqlite3
import sys
from pathlib import Path


data = Path("Dataset/student_resource/dataset/train/train_source1.tsv")
index = Path("work/train_index.sqlite")
sys.stdout.reconfigure(encoding="utf-8")
conn = sqlite3.connect(f"file:{index.resolve().as_posix()}?mode=ro", uri=True)
try:
    with data.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for position, row in enumerate(reader):
            if position >= 8:
                break
            raw = conn.execute("SELECT matched FROM labels WHERE anchor=?", (row["entity_id"],)).fetchone()
            linked = []
            for target_id in raw[0].split(",") if raw and raw[0] else []:
                record = conn.execute("SELECT nname,naddr,country FROM records WHERE entity_id=?", (target_id,)).fetchone()
                linked.append({"target_id": target_id, "normalized_name": record[0], "normalized_address": record[1], "country": record[2]})
            print(json.dumps({"source1": row, "linked_targets": linked}, ensure_ascii=False))
finally:
    conn.close()
