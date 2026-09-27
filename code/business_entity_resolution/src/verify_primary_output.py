"""Independent streaming gates for a complete, already checked test output.

The disk-backed pipeline checker verifies target existence and country. This
second pass verifies strict TSV shape, source coverage, report freshness, and
the measured distribution before promotion.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from datetime import datetime, timezone
from itertools import zip_longest
from pathlib import Path


MATCH_HEADER = ["source1_entity_id", "matched_entity_ids"]
CANDIDATE_HEADER = ["source1_entity_id", "candidate_entity_ids"]
SOURCE_HEADER = ["entity_id", "business_name", "business_address", "country"]
FIXTURE_EMPTY_RATES = {"US": 0.228218966846569, "India": 0.23403334054990257,
                       "France": 0.1174496644295302}
NULL_TOKENS = {"nan", "null", "none", "n/a", "na", "nil"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(path: Path, header: list[str]):
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        if next(reader, None) != header:
            raise ValueError(f"Bad header in {path}")
        for line_number, row in enumerate(reader, 2):
            if len(row) != len(header):
                raise ValueError(f"Malformed {path} row at line {line_number}: {len(row)} columns")
            yield row


def ids(value: str, label: str, line_number: int) -> list[str]:
    if not value:
        return []
    parts = value.split(",")
    if any(not item or item.strip() != item or item.casefold() in NULL_TOKENS
           for item in parts):
        raise ValueError(f"Invalid/placeholder {label} item at line {line_number}")
    if len(parts) != len(set(parts)):
        raise ValueError(f"Duplicate {label} item at line {line_number}")
    if any(not item.startswith(("S2-", "S3-")) for item in parts):
        raise ValueError(f"Invalid {label} target prefix at line {line_number}")
    return parts


def verify(data_dir: Path, output_dir: Path, report_path: Path,
           fallback_dir: Path) -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    match_path = output_dir / "matching_results.tsv"
    candidate_path = output_dir / "candidate_pairs.tsv"
    fallback_hashes = {name: sha256(fallback_dir / name)
                       for name in ("matching_results.tsv", "candidate_pairs.tsv")}
    actual_hashes = {name: sha256(output_dir / name)
                     for name in ("matching_results.tsv", "candidate_pairs.tsv")}
    if report.get("output_sha256") != actual_hashes:
        raise ValueError("Full checker hashes do not match current output files")
    if any(actual_hashes[name] == fallback_hashes[name] for name in actual_hashes):
        raise ValueError("Primary output hash equals the preserved fallback")
    if report_path.stat().st_mtime < max(match_path.stat().st_mtime,
                                         candidate_path.stat().st_mtime):
        raise ValueError("Full checker report is older than the output files")
    if not all(report.get(key) is True for key in
               ("target_ids_all_exist", "matches_subset_of_candidates",
                "rows_unique_and_in_source1_order")):
        raise ValueError("Full checker did not pass all integrity gates")

    source = rows(data_dir / "test" / "test_source1.tsv", SOURCE_HEADER)
    matching = rows(match_path, MATCH_HEADER)
    candidates = rows(candidate_path, CANDIDATE_HEADER)
    country_counts = collections.Counter()
    country_empty = collections.Counter()
    candidate_sizes = collections.Counter()
    n_matches = n_candidates = 0
    seen = set()
    for line_number, triple in enumerate(zip_longest(source, matching, candidates), 2):
        anchor, match, candidate = triple
        if anchor is None or match is None or candidate is None:
            raise ValueError(f"Source/output row count mismatch at line {line_number}")
        source_id, _, _, country = anchor
        if source_id in seen:
            raise ValueError(f"Duplicate Source 1 input ID at line {line_number}: {source_id}")
        seen.add(source_id)
        if match[0] != source_id or candidate[0] != source_id:
            raise ValueError(f"Output coverage/order mismatch at line {line_number}")
        match_ids = ids(match[1], "match", line_number)
        candidate_ids = ids(candidate[1], "candidate", line_number)
        if not set(match_ids).issubset(candidate_ids):
            raise ValueError(f"Prediction outside scored candidates at line {line_number}")
        country_counts[country] += 1
        country_empty[country] += not match_ids
        candidate_sizes[len(candidate_ids)] += 1
        n_matches += len(match_ids)
        n_candidates += len(candidate_ids)
    anchors = len(seen)
    if anchors != report.get("anchors") or dict(country_counts) != report.get("country_counts"):
        raise ValueError("Independently measured source coverage differs from checker")
    if n_candidates != report.get("candidate_pairs") or n_matches != report.get("predicted_matches"):
        raise ValueError("Independently measured ID totals differ from checker")
    maximum = max(candidate_sizes, default=0)
    if maximum != report.get("candidate_max") or maximum > 31:
        raise ValueError(f"Unexpected candidate maximum: {maximum}")
    empty_rates = {country: country_empty[country] / count
                   for country, count in country_counts.items()}
    if set(empty_rates) != set(FIXTURE_EMPTY_RATES):
        raise ValueError(f"Unexpected test countries: {sorted(empty_rates)}")
    large_shifts = {country: rate - FIXTURE_EMPTY_RATES[country]
                    for country, rate in empty_rates.items()
                    if abs(rate - FIXTURE_EMPTY_RATES[country]) > 0.05}
    if large_shifts:
        raise ValueError(f"Large empty-prediction shift: {large_shifts}")
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "anchors": anchors, "country_counts": dict(country_counts),
        "candidate_pairs": n_candidates, "predicted_matches": n_matches,
        "candidate_max": maximum, "candidate_size_histogram": dict(candidate_sizes),
        "country_empty_prediction_rate": empty_rates,
        "empty_match_rows": sum(country_empty.values()),
        "empty_candidate_rows": candidate_sizes[0],
        "output_sha256": actual_hashes, "fallback_sha256": fallback_hashes,
        "strict_tsv_shape": True, "placeholder_fields_absent": True,
        "source1_ids_unique_and_covered": True,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check-report", type=Path, required=True)
    parser.add_argument("--fallback-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.data_dir, args.output_dir, args.check_report,
                    args.fallback_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS: strict full-output promotion gates", flush=True)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
