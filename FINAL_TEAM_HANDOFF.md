# Final team handoff — Amazon ML Challenge 2026

Snapshot 2026-09-27, IST. Read `TEAM_CONTEXT/README_CONTEXT.md` first. This is the current repository/documentation handoff; older `HANDOFF.md` files record earlier in-progress snapshots and are not current submission status.

## Problem and constraints

For every Source 1 business entity, find zero, one, or many matching Source 2/3 records from noisy names and addresses. All files are TSV; Source records have `entity_id`, `business_name`, `business_address`, `country`. Train labels are US/India; test adds unlabeled France. Produce one row per test Source 1 ID in each output: comma-separated `matched_entity_ids` in `matching_results.tsv` and the **actual scored** `candidate_entity_ids` in `candidate_pairs.tsv`. An empty list is an empty TSV cell. Every predicted ID must be a valid same-country S2/S3 test ID and present among its candidates. Only supplied records may inform matching; the implementation is CPU-only, has no external enrichment, GPU, or pretrained model.

Competition metric is Source 1 entity-level macro F0.5, including an empty-truth/empty-prediction score of 1 and empty-truth/nonempty-prediction score of 0. Candidate-link recall is tracked separately. The organizer's numeric weighting for candidate efficiency is `UNKNOWN`. Test labels and France accuracy are unavailable.

## Current model and evidence

The current **validated primary** is deterministic `rare_both` at dev-selected threshold **0.65**. `code/business_entity_resolution/src/pipeline.py` builds a disk-backed SQLite index, normalizes Unicode without destroying Indic evidence, retrieves country/source-scoped exact name/address candidates, and (only when fewer than eight exact candidates exist) adds one rare address and one rare name token route. Document frequencies 2–1,000 and route caps keep it CPU-feasible. It scores every emitted candidate with token/character/address-number similarity. The exact-only `narrow` fallback at threshold **0.68** is preserved separately in `fallback/`.

The fixed entity-level split has 2,118,511 train, 44,098 dev, and 44,212 holdout anchors; exact normalized identity groups stay together. On full dev, primary macro F0.5 was **0.5601653910**, link candidate recall **0.4312524062**. On untouched holdout at fixed 0.65, macro F0.5 was **0.5616271143**, recall **0.4303728929**, and mean candidates **13.3683**. Fallback holdout F0.5 was **0.4996922783**, recall **0.2988166066**, mean candidates **3.6298**. The primary gains 12.39% relative F0.5 at ~3.68× candidate load. Sources: `work/dev_rare_both_full.json`, `work/holdout_rare_both_full.json`, `work/holdout_narrow_full.json`.

The complete unlabeled test run produced **1,732,544** rows (US 663,106; India 809,986; France 259,452), **24,702,044** scored candidate IDs, and **3,327,344** predicted IDs. Candidate counts: mean **14.257672**, median **13**, P90 **25**, P95 **26**, P99 **28**, max **31**. Inference wall time **13,737.2 s**, including an observed host pause; measured peak working set **136.2 MB**. The independent full target-ID/country/order/subset checker, strict TSV scan, and supplied official validator passed; current hashes still match their recorded evidence. These are integrity facts, not a measured test score.

## Artifact and repository boundaries

Current local ZIP: `amazon_ml_challenge_2026_submission.zip`, SHA-256 **`91fe000809e29459fb75f3164b787d39b5d5cb8e8e3a6ec2f21a314f1a38b194`**. Output SHA-256: matching **`df1415117c62d350ca33d51bffa678934f1f2c6282997fb0103087995178ff05`**; candidates **`3d5b2e71e32e11f168d22725c03757f62b0853147e7f3ba7cfa0f4bf7cc3f9c5`**. `best/` mirrors those two TSVs; `fallback/` contains the separately validated narrow pair. The ZIP/TSVs, raw dataset, fixtures, and multi-GB SQLite indexes are **intentionally excluded from Git**. A teammate needs the exact ZIP from an approved transfer channel; compare its hash on receipt. No leaderboard upload was performed by this work; portal acceptance and score are `UNKNOWN`.

The archived ZIP methodology has one stale sentence saying full-test totals were pending; the repository `Documentation_template.md` now corrects that sentence. A read-only manifest comparison found no other workspace-versus-ZIP mismatch, and the validated ZIP remains unchanged. This is a documentation discrepancy, not an output-integrity failure. Do not assume the corrected methodology is inside the existing ZIP; refreshing it would create a new artifact requiring independent revalidation.

## What was tried, what was not found

The initial broad FTS5 OR/BM25 route failed an early runtime gate (>100 s for <1k dev anchors; >47 h projected full run). Narrow exact blocking became the first validated full fallback. Three bounded rare-token variants were measured: rare name (10k dev F0.5 0.514004), rare address (0.538925), and combined (0.554542), then combined advanced through full dev, fixed-threshold holdout, mixed-country test fixture, complete test inference, and full validation. No supervised ranker, LSH, or graph propagation was implemented as a production model. See `TEAM_CONTEXT/EXPERIMENT_REGISTRY.md` and `research/log.md`.

The inspected remote `main` branch contained only a README. The local workspace contains the one pipeline module and its variants, not a verifiable separate teammate model. For teammate ownership, architecture, metrics, and status, see `TEAM_CONTEXT/MODEL_REGISTRY.md`; unavailable details are `UNKNOWN`. Ask teammates for branches/artifacts before merging or attributing work.

## Handoff actions

Use `TEAM_CONTEXT/REPRODUCTION.md` for bounded reproduction and `VALIDATION_CHECKLIST.md` before any upload. Do not overwrite the validated primary or fallback while exploring. The most important unresolved issue is retrieval recall (~43% of labeled holdout links reached the primary candidate set), followed by France accuracy/false-positive uncertainty and the unknown efficiency weighting. France is fully covered but unlabeled. Fill team/member placeholders; confirm portal deadline/attempts; transfer and hash-check the exact ZIP; make the portal submission if authorized. The hard four-hour delivery buffer begins **2026-09-27 19:59 IST**. If an integrity gate fails, stop and use `TEAM_CONTEXT/ROLLBACK.md`; never silently update the recorded hashes or call a changed ZIP verified.
