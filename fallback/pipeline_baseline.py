"""CPU and memory-conscious baseline for business entity resolution.

No external business data or pretrained models are used. Python 3.12+ and SQLite
with FTS5 are the only runtime requirements.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import sqlite3
import statistics
import sys
import time
import unicodedata
from pathlib import Path

try:
    import psutil  # optional; scoring and inference remain standard-library only
except ImportError:
    psutil = None


NAME_STOP = frozenset({"inc", "incorporated", "corp", "corporation", "co", "company", "llc", "llp", "ltd", "limited", "private", "pvt", "plc", "the", "and"})
ADDRESS_STOP = frozenset({"road", "rd", "street", "st", "avenue", "ave", "lane", "ln", "drive", "dr", "floor", "fl", "near", "city", "state", "district", "block", "india", "usa", "france"})
NUMBER = re.compile(r"\d+", re.UNICODE)
SCHEMA = ("entity_id", "business_name", "business_address", "country")
MATCH_HEADER = ("source1_entity_id", "matched_entity_ids")
CANDIDATE_HEADER = ("source1_entity_id", "candidate_entity_ids")


def normalize(value: str) -> str:
    # Strip Latin accents, but retain combining marks in Indic and other scripts.
    # Removing all Mn characters destroys words such as Devanagari "राज".
    parts: list[str] = []
    base_script = ""
    for char in unicodedata.normalize("NFKD", value.casefold()):
        category = unicodedata.category(char)
        if category.startswith("L") or category.startswith("N"):
            parts.append(char)
            base_script = unicodedata.name(char, "").split(" ", 1)[0]
        elif category.startswith("M"):
            if base_script != "LATIN":
                parts.append(char)
        else:
            parts.append(" ")
            base_script = ""
    return " ".join("".join(parts).split())


def tokens(value: str, stop: frozenset[str] = frozenset()) -> set[str]:
    return {token for token in value.split() if token not in stop}


def char_dice(left: str, right: str) -> float:
    left = left.replace(" ", "")
    right = right.replace(" ", "")
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    if len(left) < 3 or len(right) < 3:
        return 0.0
    a = {left[i:i + 3] for i in range(len(left) - 2)}
    b = {right[i:i + 3] for i in range(len(right) - 2)}
    return 2.0 * len(a & b) / (len(a) + len(b))


def overlap(left: set[str], right: set[str]) -> tuple[float, float]:
    if not left or not right:
        return 0.0, 0.0
    common = len(left & right)
    return common / len(left | right), common / min(len(left), len(right))


def histogram_percentile(counts: collections.Counter[int], fraction: float) -> int:
    position = int(fraction * (sum(counts.values()) - 1))
    cumulative = 0
    for value, count in sorted(counts.items()):
        cumulative += count
        if cumulative > position:
            return value
    return 0


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def similarity(anchor_name: str, anchor_address: str, target_name: str, target_address: str) -> float:
    name_left = tokens(anchor_name, NAME_STOP)
    name_right = tokens(target_name, NAME_STOP)
    address_left = tokens(anchor_address, ADDRESS_STOP)
    address_right = tokens(target_address, ADDRESS_STOP)
    name_jaccard, name_containment = overlap(name_left, name_right)
    address_jaccard, address_containment = overlap(address_left, address_right)
    name_score = max(name_jaccard, 0.82 * name_containment)
    address_score = max(address_jaccard, 0.82 * address_containment)
    if name_score < 0.7:
        name_score = max(name_score, 0.9 * char_dice(anchor_name, target_name))
    if address_score < 0.7:
        address_score = max(address_score, 0.86 * char_dice(anchor_address, target_address))
    left_nums = set(NUMBER.findall(anchor_address))
    right_nums = set(NUMBER.findall(target_address))
    number_match = 1.0 if left_nums and right_nums and left_nums & right_nums else 0.0
    number_conflict = bool(left_nums and right_nums and not left_nums & right_nums)
    score = 0.52 * name_score + 0.43 * address_score + 0.05 * number_match
    if not target_address:
        score = max(score, 0.72 * name_score)
    if name_score < 0.2:
        score = max(score, 0.68 * address_score + 0.04 * number_match)
    if number_conflict and address_score < 0.55:
        score *= 0.82
    return min(1.0, score)


def entity_f05(truth: set[str], prediction: set[str]) -> float:
    if not truth:
        return 1.0 if not prediction else 0.0
    tp = len(truth & prediction)
    fp = len(prediction - truth)
    fn = len(truth - prediction)
    return 5.0 * tp / (5.0 * tp + 4.0 * fp + fn)


def read_source(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if tuple(reader.fieldnames or ()) != SCHEMA:
            raise ValueError(f"Wrong source columns in {path}: {reader.fieldnames}")
        yield from reader


def row_source_id(entity_id: str) -> str:
    if entity_id.startswith("S2-"):
        return "s2"
    if entity_id.startswith("S3-"):
        return "s3"
    raise ValueError(f"Invalid target ID: {entity_id}")


def open_index(path: Path, readonly: bool = True) -> sqlite3.Connection:
    if readonly:
        conn = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
        complete = conn.execute("SELECT value FROM metadata WHERE key='complete'").fetchone()
        if complete != ("yes",):
            conn.close()
            raise RuntimeError(f"Index is not complete: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
    conn.execute("PRAGMA cache_size=-65536")
    conn.execute("PRAGMA temp_store=FILE")
    return conn


def build_index(data_dir: Path, split: str, index_path: Path) -> None:
    if index_path.exists():
        try:
            with open_index(index_path):
                print(f"Complete index already exists: {index_path}", flush=True)
                return
        except (sqlite3.Error, RuntimeError):
            raise RuntimeError(f"Incomplete index exists at {index_path}; move it aside before rebuilding")
    conn = open_index(index_path, readonly=False)
    start = time.monotonic()
    try:
        conn.executescript("""
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=OFF;
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE records (
                rowid INTEGER PRIMARY KEY,
                entity_id TEXT NOT NULL UNIQUE,
                country TEXT NOT NULL,
                src TEXT NOT NULL,
                nname TEXT NOT NULL,
                naddr TEXT NOT NULL
            );
        """)
        total = 0
        next_report = 500_000
        for source in (2, 3):
            path = data_dir / split / f"{split}_source{source}.tsv"
            batch = []
            for row in read_source(path):
                entity_id = row["entity_id"]
                if row_source_id(entity_id) != f"s{source}":
                    raise ValueError(f"ID prefix does not match file: {entity_id}")
                batch.append((entity_id, row["country"], f"s{source}", normalize(row["business_name"]), normalize(row["business_address"])))
                if len(batch) >= 50_000:
                    conn.executemany("INSERT INTO records(entity_id,country,src,nname,naddr) VALUES(?,?,?,?,?)", batch)
                    total += len(batch)
                    batch.clear()
                    if total >= next_report:
                        conn.commit()
                        print(f"Indexed rows={total:,} elapsed_s={time.monotonic()-start:.0f}", flush=True)
                        next_report += 500_000
            if batch:
                conn.executemany("INSERT INTO records(entity_id,country,src,nname,naddr) VALUES(?,?,?,?,?)", batch)
                total += len(batch)
                conn.commit()
            print(f"Loaded {path.name}, total={total:,}", flush=True)
        conn.execute("CREATE INDEX records_country_name ON records(country,nname)")
        conn.execute("CREATE INDEX records_country_addr ON records(country,naddr)")
        conn.execute("CREATE VIRTUAL TABLE search USING fts5(country,src,nname,naddr,content='records',content_rowid='rowid',tokenize='unicode61 remove_diacritics 2')")
        conn.execute("INSERT INTO search(search) VALUES('rebuild')")
        conn.execute("INSERT INTO metadata(key,value) VALUES('complete','yes')")
        conn.execute("INSERT INTO metadata(key,value) VALUES('rows',?)", (str(total),))
        conn.commit()
        print(f"Complete index={index_path} rows={total:,} elapsed_s={time.monotonic()-start:.0f}", flush=True)
    finally:
        conn.close()


def query_terms(value: str, stop: frozenset[str]) -> list[str]:
    useful = [term for term in value.split() if term not in stop and len(term) >= 2]
    useful.sort(key=lambda term: (any(char.isdigit() for char in term), len(term)), reverse=True)
    return useful[:3]


def fts_expression(country: str, src: str, field: str, terms: list[str]) -> str:
    quoted = " OR ".join('"' + term.replace('"', '') + '"' for term in terms)
    return f'country:"{country.replace(chr(34), "")}" AND src:"{src}" AND {field}:({quoted})'


def candidates(conn: sqlite3.Connection, row: dict, variant: str = "narrow") -> list[tuple[str, str, str]]:
    if variant not in ("broad", "balanced", "narrow"):
        raise ValueError(f"Unknown retrieval variant: {variant}")
    fts_limit = {"broad": 10, "balanced": 5, "narrow": 0}[variant]
    max_candidates = 24 + 4 * fts_limit
    country = row["country"]
    nname = normalize(row["business_name"])
    naddr = normalize(row["business_address"])
    selected: dict[str, tuple[str, str, str]] = {}
    for field, value in (("nname", nname), ("naddr", naddr)):
        if not value:
            continue
        # The country/name and country/address B-trees return a stable rowid
        # order from a reproducibly built index without sorting large ties.
        sql = f"SELECT entity_id,nname,naddr FROM records WHERE country=? AND src=? AND {field}=? LIMIT 6"
        for src in ("s2", "s3"):
            for entity_id, name, address in conn.execute(sql, (country, src, value)):
                selected.setdefault(entity_id, (entity_id, name, address))
    for field, value, stop in (("nname", nname, NAME_STOP), ("naddr", naddr, ADDRESS_STOP)):
        if not fts_limit:
            break
        terms = query_terms(value, stop)
        if not terms:
            continue
        sql = f"""SELECT records.entity_id,records.nname,records.naddr
                 FROM search JOIN records ON search.rowid=records.rowid
                 WHERE search MATCH ? ORDER BY bm25(search), records.entity_id LIMIT {fts_limit}"""
        for src in ("s2", "s3"):
            expression = fts_expression(country, src, field, terms)
            for entity_id, name, address in conn.execute(sql, (expression,)):
                selected.setdefault(entity_id, (entity_id, name, address))
    return list(selected.values())[:max_candidates]


def pair_scores(row: dict, found: list[tuple[str, str, str]]) -> list[tuple[str, float]]:
    nname = normalize(row["business_name"])
    naddr = normalize(row["business_address"])
    return [(entity_id, similarity(nname, naddr, name, address)) for entity_id, name, address in found]


def split_bucket(row: dict) -> int:
    key = normalize(row["business_name"]) + "\0" + normalize(row["business_address"])
    digest = hashlib.blake2b(key.encode("utf-8"), digest_size=8, person=b"amzml26").digest()
    return int.from_bytes(digest, "big") % 100


def install_labels(conn: sqlite3.Connection, ground_truth: Path) -> None:
    exists = conn.execute("SELECT name FROM sqlite_master WHERE name='labels'").fetchone()
    if exists:
        marker = conn.execute("SELECT value FROM metadata WHERE key='labels_complete'").fetchone()
        if marker == ("yes",):
            return
        # A prior interrupted load is generated data, not a valid label table.
        conn.execute("DROP TABLE labels")
        conn.commit()
    conn.execute("CREATE TABLE labels(anchor TEXT PRIMARY KEY, matched TEXT NOT NULL)")
    with ground_truth.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if tuple(reader.fieldnames or ()) != MATCH_HEADER:
            raise ValueError("Invalid ground truth header")
        batch = []
        for row in reader:
            batch.append((row["source1_entity_id"], row["matched_entity_ids"]))
            if len(batch) >= 50_000:
                conn.executemany("INSERT INTO labels VALUES (?,?)", batch)
                conn.commit()
                batch.clear()
        if batch:
            conn.executemany("INSERT INTO labels VALUES (?,?)", batch)
            conn.commit()
    conn.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('labels_complete','yes')")
    conn.commit()


def evaluate(data_dir: Path, index_path: Path, partition: str, limit: int, config_path: Path | None, variant: str = "narrow", fixed_threshold: float | None = None, country: str | None = None) -> None:
    if partition == "holdout" and fixed_threshold is None:
        raise ValueError("Holdout evaluation requires --fixed-threshold chosen on dev")
    conn = open_index(index_path, readonly=False)
    try:
        install_labels(conn, data_dir / "train" / "train_ground_truth.tsv")
        examples: list[tuple[str, set[str], list[tuple[str, float]]]] = []
        candidate_sizes = []
        candidate_oracle_scores = []
        true_links = candidate_links = 0
        country_counter = collections.Counter()
        multiplicity_counter = collections.Counter()
        start = time.monotonic()
        for row in read_source(data_dir / "train" / "train_source1.tsv"):
            if country is not None and row["country"] != country:
                continue
            bucket = split_bucket(row)
            if partition == "dev" and bucket >= 2:
                continue
            if partition == "holdout" and not 2 <= bucket < 4:
                continue
            # The supplied training file is country-clustered; keep both training
            # countries represented in a bounded benchmark rather than stopping
            # after only the first country's rows.
            if country_counter[row["country"]] >= max(1, limit // 2):
                continue
            raw = conn.execute("SELECT matched FROM labels WHERE anchor=?", (row["entity_id"],)).fetchone()
            if raw is None:
                raise ValueError(f"Missing label for {row['entity_id']}")
            truth = set(raw[0].split(",")) if raw[0] else set()
            found = candidates(conn, row, variant)
            scored = pair_scores(row, found)
            examples.append((row["country"], truth, scored))
            candidate_sizes.append(len(found))
            candidate_oracle_scores.append(entity_f05(truth, truth & {x[0] for x in found}))
            true_links += len(truth)
            candidate_links += len(truth & {x[0] for x in found})
            country_counter[row["country"]] += 1
            multiplicity_counter["zero" if not truth else "singleton" if len(truth) == 1 else "multiple"] += 1
            if len(examples) % 1000 == 0:
                print(f"{partition} anchors={len(examples):,} elapsed_s={time.monotonic()-start:.1f}", flush=True)
            if len(examples) >= limit:
                break
        if not examples:
            raise RuntimeError("No anchors selected")
        thresholds = [fixed_threshold] if fixed_threshold is not None else [round(x / 100, 2) for x in range(10, 101)]
        scores = []
        for threshold in thresholds:
            score = statistics.fmean(entity_f05(truth, {key for key, value in scored if value >= threshold}) for _, truth, scored in examples)
            scores.append((score, threshold))
        best_score, best_threshold = max(scores, key=lambda item: (item[0], item[1]))
        country_scores: dict[str, list[float]] = collections.defaultdict(list)
        country_recall: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
        for example_country, truth, scored in examples:
            predicted = {key for key, value in scored if value >= best_threshold}
            candidate_ids = {key for key, _ in scored}
            country_scores[example_country].append(entity_f05(truth, predicted))
            country_recall[example_country][0] += len(truth & candidate_ids)
            country_recall[example_country][1] += len(truth)
        candidate_sizes.sort()
        report = {
            "partition": partition,
            "variant": variant,
            "threshold_selection": "fixed" if fixed_threshold is not None else "optimized_on_dev_sample",
            "anchors": len(examples),
            "country_counts": dict(country_counter),
            "country_macro_f05": {key: statistics.fmean(values) for key, values in country_scores.items()},
            "country_candidate_recall": {key: (matched / total if total else None) for key, (matched, total) in country_recall.items()},
            "multiplicity_counts": dict(multiplicity_counter),
            "best_threshold": best_threshold,
            "macro_f05": best_score,
            "candidate_recall": candidate_links / true_links if true_links else None,
            "candidate_oracle_macro_f05": statistics.fmean(candidate_oracle_scores),
            "candidate_mean": statistics.fmean(candidate_sizes),
            "candidate_median": statistics.median(candidate_sizes),
            "candidate_p90": candidate_sizes[int(0.90 * (len(candidate_sizes) - 1))],
            "candidate_p95": candidate_sizes[int(0.95 * (len(candidate_sizes) - 1))],
            "candidate_p99": candidate_sizes[int(0.99 * (len(candidate_sizes) - 1))],
            "candidate_max": candidate_sizes[-1],
            "elapsed_s": time.monotonic() - start,
            "throughput_anchors_s": len(examples) / (time.monotonic() - start),
        }
        if psutil is not None:
            memory = psutil.Process().memory_info()
            report["peak_working_set_mb"] = round(getattr(memory, "peak_wset", memory.rss) / 1048576, 1)
        print(json.dumps(report, indent=2), flush=True)
        if config_path is not None:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    finally:
        conn.close()


def predict(data_dir: Path, index_path: Path, output_dir: Path, threshold: float, limit: int, variant: str = "narrow", country: str | None = None) -> None:
    conn = open_index(index_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    count = 0
    total_candidates = total_matches = 0
    match_path = output_dir / "matching_results.tsv"
    candidate_path = output_dir / "candidate_pairs.tsv"
    match_partial = output_dir / "matching_results.tsv.part"
    candidate_partial = output_dir / "candidate_pairs.tsv.part"
    try:
        with match_partial.open("w", encoding="utf-8", newline="") as match_stream, candidate_partial.open("w", encoding="utf-8", newline="") as candidate_stream:
            match_writer = csv.writer(match_stream, delimiter="\t", lineterminator="\n")
            candidate_writer = csv.writer(candidate_stream, delimiter="\t", lineterminator="\n")
            match_writer.writerow(MATCH_HEADER)
            candidate_writer.writerow(CANDIDATE_HEADER)
            for row in read_source(data_dir / "test" / "test_source1.tsv"):
                if country is not None and row["country"] != country:
                    continue
                found = candidates(conn, row, variant)
                scored = pair_scores(row, found)
                ids = [entity_id for entity_id, _, _ in found]
                matches = [entity_id for entity_id, score in scored if score >= threshold]
                candidate_writer.writerow((row["entity_id"], ",".join(ids)))
                match_writer.writerow((row["entity_id"], ",".join(matches)))
                count += 1
                total_candidates += len(ids)
                total_matches += len(matches)
                if count % 10_000 == 0:
                    seconds = time.monotonic() - start
                    print(f"Predicted {count:,} elapsed_s={seconds:.1f} rows_per_s={count/seconds:.1f} avg_candidates={total_candidates/count:.2f}", flush=True)
                if limit and count >= limit:
                    break
    finally:
        conn.close()
    match_partial.replace(match_path)
    candidate_partial.replace(candidate_path)
    result = {"anchors": count, "variant": variant, "candidates": total_candidates, "matches": total_matches,
              "elapsed_s": time.monotonic()-start, "matching": str(match_path), "candidate_pairs": str(candidate_path)}
    if psutil is not None:
        memory = psutil.Process().memory_info()
        result["peak_working_set_mb"] = round(getattr(memory, "peak_wset", memory.rss) / 1048576, 1)
    print(json.dumps(result), flush=True)


def check_outputs(data_dir: Path, index_path: Path, output_dir: Path, limit: int, report_path: Path | None = None, country: str | None = None) -> None:
    conn = open_index(index_path)
    match_path = output_dir / "matching_results.tsv"
    candidate_path = output_dir / "candidate_pairs.tsv"
    checked = 0
    country_counts = collections.Counter()
    candidate_size_counts = collections.Counter()
    country_candidate_totals = collections.Counter()
    country_match_totals = collections.Counter()
    country_empty_predictions = collections.Counter()
    country_candidate_sizes: dict[str, collections.Counter[int]] = collections.defaultdict(collections.Counter)
    total_candidates = total_matches = 0
    start = time.monotonic()
    try:
        with match_path.open("r", encoding="utf-8", newline="") as mstream, candidate_path.open("r", encoding="utf-8", newline="") as cstream:
            matches = csv.DictReader(mstream, delimiter="\t")
            candidates_reader = csv.DictReader(cstream, delimiter="\t")
            if tuple(matches.fieldnames or ()) != MATCH_HEADER or tuple(candidates_reader.fieldnames or ()) != CANDIDATE_HEADER:
                raise ValueError("Output header mismatch")
            source_rows = (row for row in read_source(data_dir / "test" / "test_source1.tsv") if country is None or row["country"] == country)
            for source, match, candidate in zip(source_rows, matches, candidates_reader, strict=True):
                anchor = source["entity_id"]
                if match["source1_entity_id"] != anchor or candidate["source1_entity_id"] != anchor:
                    raise ValueError(f"Row order or anchor coverage mismatch near {anchor}")
                final_ids = match["matched_entity_ids"].split(",") if match["matched_entity_ids"] else []
                candidate_ids = candidate["candidate_entity_ids"].split(",") if candidate["candidate_entity_ids"] else []
                if len(final_ids) != len(set(final_ids)) or len(candidate_ids) != len(set(candidate_ids)):
                    raise ValueError(f"Duplicate target ID near {anchor}")
                if not set(final_ids).issubset(candidate_ids):
                    raise ValueError(f"Match missing from candidates near {anchor}")
                for target_id in candidate_ids:
                    if not target_id.startswith(("S2-", "S3-")):
                        raise ValueError(f"Invalid target ID: {target_id}")
                    target = conn.execute("SELECT country FROM records WHERE entity_id=?", (target_id,)).fetchone()
                    if target is None:
                        raise ValueError(f"Unknown target ID: {target_id}")
                    if target[0] != source["country"]:
                        raise ValueError(f"Cross-country candidate: {anchor} -> {target_id}")
                checked += 1
                country_counts[source["country"]] += 1
                country_candidate_totals[source["country"]] += len(candidate_ids)
                country_match_totals[source["country"]] += len(final_ids)
                country_empty_predictions[source["country"]] += not final_ids
                country_candidate_sizes[source["country"]][len(candidate_ids)] += 1
                total_candidates += len(candidate_ids)
                total_matches += len(final_ids)
                candidate_size_counts[len(candidate_ids)] += 1
                if checked % 100_000 == 0:
                    print(f"Checked {checked:,} anchors", flush=True)
                if limit and checked >= limit:
                    break
    finally:
        conn.close()
    report = {
        "anchors": checked,
        "country_counts": dict(country_counts),
        "country_candidate_mean": {country: country_candidate_totals[country] / count for country, count in country_counts.items()},
        "country_candidate_p95": {country: histogram_percentile(country_candidate_sizes[country], 0.95) for country in country_counts},
        "country_matches_per_anchor": {country: country_match_totals[country] / count for country, count in country_counts.items()},
        "country_empty_prediction_rate": {country: country_empty_predictions[country] / count for country, count in country_counts.items()},
        "candidate_pairs": total_candidates,
        "candidate_mean": total_candidates / checked if checked else 0,
        "candidate_median": histogram_percentile(candidate_size_counts, 0.5),
        "candidate_p90": histogram_percentile(candidate_size_counts, 0.9),
        "candidate_p95": histogram_percentile(candidate_size_counts, 0.95),
        "candidate_p99": histogram_percentile(candidate_size_counts, 0.99),
        "candidate_max": max(candidate_size_counts, default=0),
        "predicted_matches": total_matches,
        "target_ids_all_exist": True,
        "matches_subset_of_candidates": True,
        "rows_unique_and_in_source1_order": True,
        "output_sha256": {
            "matching_results.tsv": file_sha256(match_path),
            "candidate_pairs.tsv": file_sha256(candidate_path),
        },
        "elapsed_s": time.monotonic() - start,
    }
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: complete local target-ID and candidate-subset check for {checked:,} anchors", flush=True)
    print(json.dumps(report, indent=2), flush=True)


def make_fixture(data_dir: Path, index_path: Path, output_dir: Path, fixture_dir: Path) -> None:
    """Create a matching small test directory for the official validator."""
    conn = open_index(index_path)
    fixture_dir.mkdir(parents=True, exist_ok=True)
    try:
        with (output_dir / "candidate_pairs.tsv").open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        anchors = {row["source1_entity_id"] for row in rows}
        targets = {item for row in rows for item in row["candidate_entity_ids"].split(",") if item}
        with (fixture_dir / "test_source1.tsv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(SCHEMA)
            for row in read_source(data_dir / "test" / "test_source1.tsv"):
                if row["entity_id"] in anchors:
                    writer.writerow([row[key] for key in SCHEMA])
                    anchors.remove(row["entity_id"])
                    if not anchors:
                        break
            if anchors:
                raise ValueError(f"Fixture output contains unknown anchors: {len(anchors)}")
        for source in (2, 3):
            with (fixture_dir / f"test_source{source}.tsv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
                writer.writerow(SCHEMA)
                for entity_id in sorted(targets):
                    if entity_id.startswith(f"S{source}-"):
                        target = conn.execute("SELECT nname,naddr,country FROM records WHERE entity_id=?", (entity_id,)).fetchone()
                        if target is None:
                            raise ValueError(f"Fixture output contains unknown target: {entity_id}")
                        writer.writerow((entity_id, target[0], target[1], target[2]))
    finally:
        conn.close()
    print(f"Fixture written to {fixture_dir}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build-index", "evaluate", "predict", "check", "make-fixture"))
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--split", choices=("train", "test"), default="train")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--fixture-dir", type=Path, default=Path("work/fixture"))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--partition", choices=("all", "dev", "holdout"), default="all")
    parser.add_argument("--threshold", type=float, default=0.56)
    parser.add_argument("--fixed-threshold", type=float)
    parser.add_argument("--variant", choices=("broad", "balanced", "narrow"), default="narrow")
    parser.add_argument("--country", help="Country filter for evaluation or bounded prediction/check fixtures; omit for full inference")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    if args.command == "build-index":
        build_index(args.data_dir, args.split, args.index)
    elif args.command == "evaluate":
        evaluate(args.data_dir, args.index, args.partition, args.limit or 20_000, args.config, args.variant, args.fixed_threshold, args.country)
    elif args.command == "predict":
        predict(args.data_dir, args.index, args.output_dir, args.threshold, args.limit, args.variant, args.country)
    elif args.command == "check":
        check_outputs(args.data_dir, args.index, args.output_dir, args.limit, args.report, args.country)
    elif args.command == "make-fixture":
        make_fixture(args.data_dir, args.index, args.output_dir, args.fixture_dir)


if __name__ == "__main__":
    main()
