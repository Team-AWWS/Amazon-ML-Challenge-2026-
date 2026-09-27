"""Package only validated outputs, runnable code, and methodology documents."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


EXPECTED_TEST_ANCHORS = 1_732_544
EXPECTED_FRANCE_ANCHORS = 259_452


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package(workspace: Path, destination: Path, check_report: Path) -> None:
    report = json.loads(check_report.read_text(encoding="utf-8"))
    if report.get("anchors") != EXPECTED_TEST_ANCHORS:
        raise ValueError("Full Source 1 coverage report is missing or incomplete")
    if report.get("country_counts", {}).get("France") != EXPECTED_FRANCE_ANCHORS:
        raise ValueError("France coverage is incomplete")
    for key in ("target_ids_all_exist", "matches_subset_of_candidates", "rows_unique_and_in_source1_order"):
        if report.get(key) is not True:
            raise ValueError(f"Failed output integrity gate: {key}")
    expected_hashes = report.get("output_sha256", {})
    for name in ("matching_results.tsv", "candidate_pairs.tsv"):
        actual = sha256(workspace / "output" / name)
        if expected_hashes.get(name) != actual:
            raise ValueError(f"Output changed after the full integrity check: {name}")

    paths = [
        "output/matching_results.tsv",
        "output/candidate_pairs.tsv",
        "code/business_entity_resolution/README.md",
        "code/business_entity_resolution/requirements.txt",
        "Documentation_template.md",
        "APPROACH_SUMMARY.md",
        "FINAL_ARCHITECTURE.md",
        "FINAL_BUILD_SPEC.md",
        "research/audit.md",
        "research/log.md",
        "research/france_shift.md",
        "research/candidate_efficiency.md",
        "research/agent_reviews.md",
    ]
    paths += [str(path.relative_to(workspace)).replace("\\", "/")
              for path in sorted((workspace / "code/business_entity_resolution/src").glob("*.py"))]
    paths += [str(path.relative_to(workspace)).replace("\\", "/")
              for path in sorted((workspace / "code/business_entity_resolution/tests").glob("*.py"))]
    missing = [name for name in paths if not (workspace / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Submission files missing: {missing}")

    manifest = {name: {"sha256": sha256(workspace / name), "bytes": (workspace / name).stat().st_size}
                for name in paths}
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for name in paths:
            archive.write(workspace / name, arcname=name)
        archive.writestr("MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    partial.replace(destination)
    with zipfile.ZipFile(destination) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise IOError(f"ZIP CRC verification failed: {bad}")
    print(json.dumps({"zip": str(destination), "bytes": destination.stat().st_size,
                      "files": len(paths) + 1, "output_sha256": {
                          "matching_results.tsv": manifest["output/matching_results.tsv"]["sha256"],
                          "candidate_pairs.tsv": manifest["output/candidate_pairs.tsv"]["sha256"]}}, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-report", type=Path, required=True)
    args = parser.parse_args()
    package(args.workspace.resolve(), args.output.resolve(), args.check_report.resolve())


if __name__ == "__main__":
    main()
