# Amazon ML Challenge 2026 — business entity resolution

The runnable pipeline is entirely CPU-based and uses only the supplied challenge TSVs. It builds a disk-backed SQLite index over Source 2/3, retrieves bounded country-scoped exact-name and exact-address candidates from each source, and optionally adds document-frequency-gated rare address/name token routes when exact retrieval is sparse. Every emitted candidate is scored before writing both required output TSVs. It preserves Indic and other non-Latin scripts during normalization. No external business lookup, geocoding, enrichment service, GPU, or pretrained model is used. The `rare_both` primary has complete validated outputs in `output/` and `best/`; the exact-only `narrow` pipeline has separate validated fallback outputs in `fallback/`.

## Environment

Tested with Python 3.14.2 and SQLite 3.50.4 with FTS5 enabled; Python 3.12+ should work. No third-party package is required for inference. `psutil` is optional and used only to report process peak memory when installed. See `requirements.txt`. Ensure several gigabytes of free disk space for generated SQLite indexes outside the final ZIP.

The commands below run from the submission workspace root with the supplied dataset at `Dataset/student_resource/dataset/`. If the ZIP is extracted elsewhere, change `--data-dir` to the directory containing `train/` and `test/`.

## Build, tune, and reproduce

```text
python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split train --index work/train_index.sqlite
python code/business_entity_resolution/src/audit_data.py --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --manifest work/split_manifest.tsv --report work/audit_report.json
python code/business_entity_resolution/src/pipeline.py evaluate --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --partition dev --limit 100000 --variant rare_both --config work/dev_rare_both_full.json
python code/business_entity_resolution/src/pipeline.py evaluate --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --partition holdout --fixed-threshold 0.65 --limit 100000 --variant rare_both --config work/holdout_rare_both_full.json
python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split test --index work/test_index.sqlite
python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --variant rare_both --threshold 0.65
python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --report work/full_check_report.json
python Dataset/student_resource/utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir Dataset/student_resource/dataset/test
```

The primary threshold `0.65` was selected on all 44,098 fixed dev anchors, not holdout. The evaluator refuses holdout evaluation without a dev-fixed threshold. The Source 1 split is stable by normalized name/address identity group, so no anchor is split by candidate-pair rows. Train/dev/holdout counts are 2,118,511 / 44,098 / 44,212. The complete primary holdout score at fixed 0.65 was 0.561627 macro F0.5; the complete fallback holdout score at fixed 0.68 was 0.499692. The larger primary uses 13.37 mean candidates versus 3.63, and the official candidate-efficiency weighting is unknown.

Fresh indexes built by this version include the FTS5 vocabulary metadata needed by `rare_both`. For a pre-existing complete index built by an older version, run `python code/business_entity_resolution/src/pipeline.py prepare-vocab --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite` once before read-only primary inference. The vocabulary derives solely from the supplied target index.

The `broad` and `balanced` CLI variants issue FTS5 OR queries and are for bounded research only. The initial broad implementation failed the deadline runtime gate; **do not use it for full inference**. The safe CLI default and preserved fallback are `narrow` at threshold 0.68. The promoted, completely validated primary is `rare_both` at frozen threshold 0.65.

## Bounded reproduction and validation

Use a separate directory for a partial output. A partial output cannot pass the official validator against the complete test directory, so create a matching fixture:

```text
python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/sample_output --variant rare_both --threshold 0.65 --limit 10000
python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/sample_output --limit 10000
python code/business_entity_resolution/src/pipeline.py make-fixture --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/sample_output --fixture-dir work/sample_fixture
python Dataset/student_resource/utils/validate_submission.py --matching work/sample_output/matching_results.tsv --candidate work/sample_output/candidate_pairs.tsv --test-dir work/sample_fixture --check-ids
python -m unittest discover -s code/business_entity_resolution/tests -v
```

The real primary 10,000-anchor fixture included US, India, and France, and passed both the independent check and the official validator with `--check-ids`. The full official validator should be run without `--check-ids` to avoid its high-memory target-ID set; the separate `check` command checks **every** candidate target ID against the disk-backed test index, along with row order, complete coverage, duplicate IDs, country agreement, and `matches ⊆ candidates`.

The final ZIP is generated only after complete validation and methodology updates:

```text
python code/business_entity_resolution/src/package_submission.py --workspace . --output amazon_ml_challenge_2026_submission.zip --check-report work/full_check_report.json
```

Large SQLite indexes, manifests, and fixtures stay outside the ZIP. The packaging script includes the two final TSVs, runnable source, environment information, methodology, summary, and research reports.
