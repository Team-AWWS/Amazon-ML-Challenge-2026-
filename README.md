# Amazon ML Challenge 2026 — Business Entity Resolution

This repository contains our CPU-only entity-resolution pipeline, evaluation and validation tools, measured experiment reports, and teammate handoff. The task is to find every Source 2/3 business record that refers to each Source 1 business, despite noisy names and addresses. A Source 1 entity can have zero, one, or many matches.

> **Submission status (27 September 2026):** V2 is the strongest complete, locally validated candidate: its fixed-threshold holdout macro F₀.₅ is **0.746470**. Its holdout candidate oracle is **0.953387**, so this retrieval configuration cannot support a 0.98–0.99 score on the same distribution. No leaderboard upload, portal acceptance, or leaderboard score is recorded here. The validated TSVs and ZIP are **not in Git**; see [submission state](TEAM_CONTEXT/SUBMISSION_STATE.md) before transferring or uploading anything.

The recorded ML-round deadline is **27 September 2026, 23:59 IST**. Reserve the final four hours for validation, rollback, packaging, and upload; confirm the live portal before acting. Development was done on a CPU-only machine with approximately 16 GB RAM.

## Start here

| If you need to… | Read |
| --- | --- |
| Understand the current state quickly | [Team context](TEAM_CONTEXT/README_CONTEXT.md) → [final team handoff](FINAL_TEAM_HANDOFF.md) |
| Compare implemented and proposed models | [Model registry](TEAM_CONTEXT/MODEL_REGISTRY.md) and [experiment registry](TEAM_CONTEXT/EXPERIMENT_REGISTRY.md) |
| Understand the matching design | [Architecture](TEAM_CONTEXT/ARCHITECTURE.md) and [final build specification](FINAL_BUILD_SPEC.md) |
| Run the code | [Reproduction guide](TEAM_CONTEXT/REPRODUCTION.md) and [pipeline README](code/business_entity_resolution/README.md) |
| Check an artifact before submission | [Validation checklist](TEAM_CONTEXT/VALIDATION_CHECKLIST.md) and [submission state](TEAM_CONTEXT/SUBMISSION_STATE.md) |
| Recover the exact-only baseline | [Rollback guide](TEAM_CONTEXT/ROLLBACK.md) |

## Problem, inputs, and outputs

Each supplied source file is tab-separated and has `entity_id`, `business_name`, `business_address`, and `country`. Source 1 (`S1-`) is the reference; Sources 2 and 3 (`S2-`/`S3-`) are the possible matches. Training labels cover **US and India**. Test also includes **France**, with no supplied France labels. The repository includes the organizer's [problem README](Dataset/student_resource/README.md), [submission validator](Dataset/student_resource/utils/validate_submission.py), and template, but **not** the raw competition records.

The supplied data has 2,206,821 labeled training Source 1 entities, 10,320,219 training S2/S3 records, and 7,638,365 labeled links. Test has 1,732,544 Source 1 entities and 9,969,589 S2/S3 records. The full input audit and data-quality findings are in [research/audit.md](research/audit.md).

The final package has two TSVs, each with exactly one row per test Source 1 entity:

| File | Exact columns | Meaning |
| --- | --- | --- |
| `output/matching_results.tsv` | `source1_entity_id`, `matched_entity_ids` | Final S2/S3 predictions; the second field is comma-separated or truly empty. This is the leaderboard upload file. |
| `output/candidate_pairs.tsv` | `source1_entity_id`, `candidate_entity_ids` | The exact S2/S3 IDs actually scored by the matcher, not an earlier unscored blocking pool. |

Every predicted ID must appear among that entity's candidates. IDs must exist in the **test** target sources, match the Source 1 country, and never be duplicated within a list. Evaluation is **macro F₀.₅ per Source 1 entity** (with both truth and prediction empty scoring 1); labeled-link candidate recall is measured separately. Test F₀.₅ cannot be computed locally without test labels.

## Strongest locally validated candidate: V2

[`retrieval_v2.py`](code/business_entity_resolution/src/retrieval_v2.py) is the strongest complete candidate produced in this repository. It keeps retrieval country-scoped and scores every emitted candidate with the existing deterministic matcher at a fixed threshold of **0.75**. Its bounded retrieval combines exact name/address routes with rare name, address, and numeric-address routes; it ranks and caps the scored set at **36 candidates per Source 1 entity**.

The complete test output is local at `work/v2_candidate_full/`:

| Artifact | SHA-256 | Test-set summary |
| --- | --- | --- |
| `matching_results.tsv` | `10e85d58c69387b18fdf8ecedb8e2f150cf2c40a41fb7ad8ef3cbe3ba74bce53` | 1,732,544 rows; 4,480,505 predicted IDs |
| `candidate_pairs.tsv` | `7c5d83b5a5c4168d790cae444bdd87cba8c0096e86f0c2ff8b27ab81e4a2f086` | 53,452,192 candidates; mean 30.852; P95 and maximum 36 |
| `amazon_ml_challenge_2026_submission_v2.zip` | `1d7870966bca8ae09e7b5c6e1455ea7edbac44f0e0e0f11ebecda221347166e9` | 337,482,868 bytes; ZIP CRC checked |

The streaming integrity check confirms complete row coverage and order, unique and country-correct candidate IDs, and that every predicted ID is a scored candidate. The organizer validator also passed for the matching TSV. See [V2 full-output check](work/v2_candidate_full_check.json) and [V2 holdout report](work/holdout_retrieval_v2_fast_full.json).

## Validated baseline pipeline

The promoted `rare_both` variant is implemented in [`pipeline.py`](code/business_entity_resolution/src/pipeline.py), with a frozen dev-selected score threshold of **0.65**:

1. Normalize case, Unicode, spacing, and punctuation while preserving Indic and other non-Latin marks.
2. Build a disk-backed SQLite index of normalized Source 2/3 names and addresses; keep retrieval scoped by country and target source.
3. Retrieve bounded exact-name and exact-address candidates. If fewer than eight distinct exact candidates are found, add one rare address-token route and one rare name-token route. Tokens must occur in 2–1,000 indexed target records; each source/route returns at most six rows.
4. Deduplicate and score **every emitted candidate** with deterministic name/address token overlap, character trigrams, and address-number agreement. Predict IDs whose score is at least 0.65.

The preserved `narrow` fallback uses only the exact routes and a dev-selected threshold of **0.68**. Neither approach needs a GPU, external business lookup, geocoding, pretrained model, or a fitted classifier. The early broad FTS5 OR/BM25 route was stopped because its measured runtime was not viable for full inference. Other research variants and their status are kept separate in the [model registry](TEAM_CONTEXT/MODEL_REGISTRY.md).

## Measured results

The fixed split is at the **Source 1 entity/normalized identity-group** level, not candidate-pair level: 2,118,511 train, 44,098 dev, and 44,212 holdout entities. Thresholds were selected on dev; the serious comparison used fixed thresholds on holdout.

| Labeled local evaluation | `narrow` fallback | `rare_both` primary |
| --- | ---: | ---: |
| Full-dev macro F₀.₅ | 0.497433 | **0.560165** |
| Full-dev labeled-link candidate recall | 0.297894 | **0.431252** |
| Holdout macro F₀.₅ | 0.499692 | **0.561627** |
| Holdout labeled-link candidate recall | 0.298817 | **0.430373** |
| Holdout mean candidates/entity | 3.630 | 13.368 |

V2 used a fixed threshold selected on a 10,000-entity dev subset, then evaluated once on the full holdout. The candidate oracle is the best score possible if the matcher made perfect choices within V2's emitted candidate lists; it is an upper bound for this retrieval design.

| V2 local evaluation | Result |
| --- | ---: |
| Dev subset macro F₀.₅ (10,000 entities) | 0.734561 |
| Dev subset labeled-link candidate recall | 0.878053 |
| Full holdout macro F₀.₅ (44,212 entities) | **0.746470** |
| Full holdout labeled-link candidate recall | **0.882430** |
| Full holdout candidate-oracle macro F₀.₅ | **0.953387** |
| Full holdout mean candidates/entity | 30.030 |

Sources: [V2 dev report](work/dev_retrieval_v2_fast10k.json), [V2 holdout report](work/holdout_retrieval_v2_fast_full.json), and [candidate diagnosis](work/candidate_diagnosis.json). A wider exploratory retrieval reached a 0.967697 dev-subset candidate oracle with roughly 89 candidates/entity, still below 0.98 and with materially higher candidate volume; it was not packaged.

On the **unlabeled complete test set**, the primary wrote 1,732,544 Source 1 rows, including all 259,452 France rows. It scored **24,702,044** candidate IDs and predicted **3,327,344** IDs. Candidate counts per entity: mean **14.258**, median **13**, P95 **26**, P99 **28**, maximum **31**. Full inference took 13,737.2 seconds wall time, including an observed host pause, and reached 136.2 MB peak process working set. The independent full target-ID/country/coverage/subset check, strict TSV scan, and organizer validator passed for the recorded output hashes. Sources: [dev report](work/dev_rare_both_full.json), [holdout report](work/holdout_rare_both_full.json), [full-output check](work/full_check_report.json), and [release integrity record](work/release_integrity_2026-09-26.md).

These local scores do **not** establish a France or private-test score. The official weighting, if any, between matching F₀.₅ and candidate efficiency is unknown; the primary's higher candidate load is a real tradeoff. See [candidate efficiency](research/candidate_efficiency.md), [France shift](research/france_shift.md), and [known issues](TEAM_CONTEXT/KNOWN_ISSUES.md).

## Reproduce safely

Tested with Python **3.14.2** and SQLite **3.50.4** with FTS5; Python 3.12+ is expected to work. Inference requires only the standard library; `psutil` is optional for memory reporting. Provide the official data at `Dataset/student_resource/dataset/{train,test}/` (or change `--data-dir`). Building the test index requires several GB of free disk. Run commands from the repository root.

```powershell
python -m unittest discover -s code/business_entity_resolution/tests -v
python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split test --index work/test_index.sqlite
```

For a **bounded** 10,000-entity reproduction, use a new work directory so the validated `output/` and `best/` files cannot be overwritten:

```powershell
python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --variant rare_both --threshold 0.65 --limit 10000
python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --limit 10000 --report work/repro_10k_check.json
python code/business_entity_resolution/src/pipeline.py make-fixture --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --fixture-dir work/repro_10k_fixture
python Dataset/student_resource/utils/validate_submission.py --matching work/repro_10k/matching_results.tsv --candidate work/repro_10k/candidate_pairs.tsv --test-dir work/repro_10k_fixture --check-ids
```

A partial output must be validated against its **matching fixture**, not the complete test directory. For a full reproduction, train/dev/holdout evaluation, older-index vocabulary preparation, and guarded ZIP creation, follow the [pipeline README](code/business_entity_resolution/README.md). Do not regenerate the current validated submission merely to test the code.

## Repository and artifact boundaries

```text
code/business_entity_resolution/  Runnable pipeline, audits, checker, packager, tests
research/                    Audit, experiment log, candidate frontier, France analysis
work/*.json                  Compact measured reports committed as evidence
TEAM_CONTEXT/                Current-state, model, reproduction, validation, rollback handoff
best/                        Small source/report snapshots in Git; validated TSVs local only
fallback/                    Small source/report snapshots in Git; validated TSVs local only
output/                      Validated primary TSVs, local only
Dataset/student_resource/    Supplied instructions/validator in Git; raw dataset local only
```

`.gitignore` deliberately excludes raw data, large output TSVs, the **174 MB baseline ZIP**, the **337 MB V2 ZIP**, SQLite indexes, caches, and secrets. A Git clone alone is **not a submission**. The V2 ZIP SHA-256 is `1d7870966bca8ae09e7b5c6e1455ea7edbac44f0e0e0f11ebecda221347166e9`; the preserved baseline ZIP SHA-256 is `91fe000809e29459fb75f3164b787d39b5d5cb8e8e3a6ec2f21a314f1a38b194`. Verify exact bytes after any transfer. Both output hashes and fallback hashes are recorded in [submission state](TEAM_CONTEXT/SUBMISSION_STATE.md). Never treat a regenerated ZIP or edited TSV as covered by the old validation evidence.

One documentation-only discrepancy is recorded: the existing validated ZIP contains an older methodology sentence saying full-test totals were pending; the repository's `Documentation_template.md` has the corrected totals. The ZIP was **not** rebuilt. See [submission state](TEAM_CONTEXT/SUBMISSION_STATE.md) before deciding whether a newly validated package is warranted.

## Remaining handoff decisions

Confirm team/member placeholders and portal submission rules, transfer the exact validated ZIP through an approved channel, and verify its hash at the receiving end. No leaderboard upload or portal score is recorded by this repository. If any artifact hash, independent checker, or official validator fails, stop and follow the [validation checklist](TEAM_CONTEXT/VALIDATION_CHECKLIST.md) and [rollback guide](TEAM_CONTEXT/ROLLBACK.md); do not silently replace the evidence or call a changed artifact verified.
