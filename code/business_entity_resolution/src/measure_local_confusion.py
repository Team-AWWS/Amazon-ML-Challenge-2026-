"""Measure fixed-threshold labeled dev/holdout precision and error counts.

This does not tune a threshold or use unlabeled test data. It keeps the frozen
production matcher in pipeline.py unchanged.
"""

from __future__ import annotations

import argparse
import collections
import json
import time
from pathlib import Path

from pipeline import (candidates, entity_f05, open_index, pair_scores,
                      read_source, split_bucket)


def measure(data_dir: Path, index_path: Path, partition: str,
            variant: str, threshold: float) -> dict:
    if partition not in ("dev", "holdout"):
        raise ValueError("Measure only a fixed dev or holdout partition")
    conn = open_index(index_path)
    counts = collections.defaultdict(lambda: collections.Counter())
    start = time.monotonic()
    try:
        marker = conn.execute("SELECT value FROM metadata WHERE key='labels_complete'").fetchone()
        if marker != ("yes",):
            raise RuntimeError("Training index labels are not complete")
        for row in read_source(data_dir / "train" / "train_source1.tsv"):
            bucket = split_bucket(row)
            if (partition == "dev" and bucket >= 2) or (partition == "holdout" and not 2 <= bucket < 4):
                continue
            raw = conn.execute("SELECT matched FROM labels WHERE anchor=?",
                               (row["entity_id"],)).fetchone()
            if raw is None:
                raise ValueError(f"Missing label: {row['entity_id']}")
            truth = set(raw[0].split(",")) if raw[0] else set()
            found = candidates(conn, row, variant)
            predicted = {entity_id for entity_id, score in pair_scores(row, found)
                         if score >= threshold}
            retrieved = {entity_id for entity_id, _, _ in found}
            values = counts[row["country"]]
            values["anchors"] += 1
            values["tp"] += len(truth & predicted)
            values["fp"] += len(predicted - truth)
            values["fn"] += len(truth - predicted)
            values["true_links"] += len(truth)
            values["retrieved_true_links"] += len(truth & retrieved)
            values["macro_f05_sum"] += entity_f05(truth, predicted)
            if sum(item["anchors"] for item in counts.values()) % 10000 == 0:
                print(f"Measured {sum(item['anchors'] for item in counts.values()):,} anchors", flush=True)
    finally:
        conn.close()
    overall = collections.Counter()
    for values in counts.values():
        overall.update(values)

    def summarize(values: collections.Counter) -> dict:
        tp, fp, fn = values["tp"], values["fp"], values["fn"]
        return {
            "anchors": values["anchors"], "tp": tp, "fp": fp, "fn": fn,
            "micro_precision": tp / (tp + fp) if tp + fp else None,
            "micro_recall": tp / (tp + fn) if tp + fn else None,
            "macro_f05": values["macro_f05_sum"] / values["anchors"],
            "link_candidate_recall": values["retrieved_true_links"] / values["true_links"]
            if values["true_links"] else None,
        }

    return {"partition": partition, "variant": variant, "fixed_threshold": threshold,
            "overall": summarize(overall),
            "by_country": {country: summarize(values) for country, values in counts.items()},
            "elapsed_s": time.monotonic() - start,
            "scope_note": "Labeled local split only; no test truth was supplied"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--partition", choices=("dev", "holdout"), required=True)
    parser.add_argument("--variant", choices=("narrow", "rare_both"), required=True)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = measure(args.data_dir, args.index, args.partition,
                     args.variant, args.threshold)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
