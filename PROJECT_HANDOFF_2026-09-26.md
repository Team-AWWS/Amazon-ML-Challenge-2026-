# Amazon ML Challenge 2026 — live project handoff

Snapshot: **September 26, 2026, 6:42 p.m. IST**. Workspace: `C:\Users\ANSH DARJI\Documents\ChatGPT\Amazon ML Challenge`. This is a status handoff, not a claim that the improved submission is finished. Read the current files and process state before acting; the main inference job may have advanced since this snapshot.

## Deadline and operating rules

- The verified ML-round deadline is **September 27, 2026, 11:59 p.m. IST**. The hard rollback/delivery buffer begins **September 27, 7:59 p.m. IST**. Do not begin a heavy experiment inside that buffer.
- CPU-only machine, approximately 16 GB RAM. Use only supplied challenge records; no external business lookup, geocoding, enrichment, GPU, or pretrained model.
- No leaderboard upload has been attempted. The number of permitted uploads was not confirmed by the public listing; conserve attempts.
- Team name and member names remain placeholders in `APPROACH_SUMMARY.md` and `Documentation_template.md` by user request.
- Priority: valid submission, preserve current best, correctness, macro F0.5, candidate recall/efficiency, runtime, then further research. Research has been stopped for delivery.

## Critical live state — do not disrupt

The selected **primary** is running full test inference:

```text
python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --variant rare_both --threshold 0.65
```

At this snapshot, Python PID **25348** was alive, started at 6:17:36 p.m. IST, using about **132 MB** working memory. The last progress observed in the parent task was **250,000 of 1,732,544** anchors, with mean ~14.25 scored candidates per anchor and roughly 183 anchors/second overall. `output/matching_results.tsv.part` and `output/candidate_pairs.tsv.part` were growing. The completed `output/*.tsv` files had **not** yet been replaced; they still held the validated narrow fallback. The `.part` pair becomes final only when inference exits successfully. Do not delete, rename, edit, or independently restart this job, its index, or its temporary output files.

The primary's real-test 10k benchmark was 106.55 seconds, 93.9 anchors/second, 105.4 MB peak working set; conservative planning allowed ~7.7 hours plus checks. Observed ongoing throughput was better than that benchmark at the snapshot. For this >1-hour run, apply the requested checkpoint at **60 minutes or 20% of projected runtime, whichever comes first**. Check actual anchor progress and memory; continuation is justified while progress remains positive and the delivery buffer is safe.

While full inference runs, do **not** start another large index, audit, training, or experiment process. CPU-light documentation/read-only checks are safe. The main thread owns production-code changes.

## Safe, already validated fallback

`best/matching_results.tsv`, `best/candidate_pairs.tsv`, `best/score_report.md`, and `best/pipeline_baseline.py` preserve the complete **narrow exact-name/address** fallback (threshold **0.68**). This copy passed:

1. the independent disk-backed full checker, including all target-ID existence, same-country, complete Source 1 and France coverage, duplicate, row-order, and `predictions ⊆ actual candidates` checks; and
2. the supplied official validator against the **complete** test files. Its optional high-memory ID check was off because the independent checker verified every ID.

Fallback output: **1,732,544** Source 1 rows including **259,452 France**, **6,371,588** scored candidate pairs, and **2,164,462** predicted matches. Full inference took **1,856.2 seconds** and the independent check **526.1 seconds**. Mean candidates **3.6776**, median 2, P90/P95 12, P99 13, max 24. Validated SHA-256:

```text
matching_results.tsv  4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e
candidate_pairs.tsv   5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8
```

`work/full_check_report.json` currently describes this **fallback**, not the in-progress primary. Do not package a newly completed primary against that old report; rerun `check` first. Do not overwrite `best/` until the primary passes every complete-file gate. If primary fails or cannot validate before the hard rollback point, restore the exact `best/*.tsv` copies to `output/` and ship the fallback.

## Data and integrity findings

Source files are under `Dataset/student_resource/dataset/{train,test}`. The completed indexes are `work/train_index.sqlite` (**10,320,219** Source 2/3 rows) and `work/test_index.sqlite` (**9,969,589** target rows). Test index FTS5 vocabulary metadata has already been prepared for `rare_both`.

Training: **2,206,821** Source 1 anchors (US and India), **7,638,365** labeled links, **123,247** zero-match anchors. Test: **1,732,544** Source 1 anchors (US 663,106; India 809,986; France 259,452). All train Source 1 IDs and label rows are unique/covered; all labeled target IDs exist, have valid prefixes, no duplicates within lists, and match anchor country. No exact normalized name+address identity group crosses the fixed train/dev/holdout split. The split sizes are **2,118,511 / 44,098 / 44,212**. Partial-field overlap remains a caution: 34,145 dev/holdout anchors share an exact name with a different-address train anchor, and 4,631 share an exact address with a different-name train anchor; these are proxies, not proven same entities. Details: `research/audit.md`, `work/audit_report.json`, `work/leakage_report.json`.

Pending noncritical-but-requested audit: raw/normalized duplicate-record values within/across sources and train/test ID overlap. The disk-backed script is `code/business_entity_resolution/src/audit_overlap.py`. Run it **after** the current heavy inference/validation, one heavy job at a time, and update `research/audit.md`. Do not let it jeopardize submission delivery.

## Metric, model, and experiments

Evaluation is **macro F0.5 per Source 1 entity**, including empty truth/prediction cases. Candidate-link recall is reported separately. The pipeline checks that matches are a subset of exactly the emitted/scored candidates. Thresholds and retrieval decisions used dev; the full holdout was evaluated once at dev-fixed thresholds.

| Full split | Narrow fallback | Combined `rare_both` primary |
| --- | ---: | ---: |
| Dev macro F0.5, 44,098 anchors | 0.497433 at 0.68 | **0.560165 at 0.65** |
| Dev candidate-link recall | 0.297894 | **0.431252** |
| Holdout macro F0.5, 44,212 anchors | 0.499692 at fixed 0.68 | **0.561627 at fixed 0.65** |
| Holdout candidate-link recall | 0.298817 | **0.430373** |
| Holdout mean candidates / P99 | 3.63 / 13 | 13.37 / 28 |

The primary adds a single rare address token and a single rare name token only if exact country/source-scoped retrieval yields fewer than eight candidates. A token must occur in **2–1,000** supplied target records; each FTS5 route returns at most six rows per source without BM25 sorting. IDs are deduplicated and scored with deterministic name/address token overlap, character trigrams, and address-number agreement. Normalization keeps Indic/non-Latin combining marks. On the untouched holdout, the F0.5 gain was **0.061935 absolute / 12.39% relative**, but candidate count rose **3.68×**. The official weighting between F0.5 and candidate efficiency is unknown, so no total-leaderboard improvement is claimed. France has no labels, so no France accuracy is claimed.

Exactly three bounded improvement experiments were measured: E1 rare-name (10k dev F0.5 **0.514004**, recall **0.337545**), E2 rare-address (**0.538925**, **0.398999**), E3 combined (**0.554542**, **0.432535**). The original broad FTS5 OR/BM25 route was stopped after >100 seconds before 1,000 anchors; projected full runtime was infeasible. Five read-only, CPU-light agents completed the requested framework. Agent 5's final measured decision selected E3 conditionally, with narrow fallback. Full reasoning: `research/agent_reviews.md` and `research/log.md`.

The primary passed a real mixed-country 10k test fixture: US 3,891, India 4,619, France 1,490; **142,118** scored candidate pairs; mean 14.2118, P99 28, max 31. The independent checker and supplied validator **with `--check-ids`** passed this fixture. This is structural/runtime evidence, not test accuracy.

## Exact next gates, in order

1. Let the existing primary inference process complete. Inspect exit code and output; ensure no `.part` files remain. If it fails, leave `best/` alone and use the preserved fallback.
2. Run the independent checker against the **complete** test set:

   ```text
   python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --report work/full_check_report.json
   ```

   Require 1,732,544 unique Source 1 rows in input order; 259,452 France rows; valid same-country Source 2/3 target IDs; no duplicate candidate/match IDs; and every predicted match present among the actual scored candidates. Inspect candidate mean/median/P90/P95/P99/max and SHA-256 values in the new report.
3. Run the supplied official validator **against the complete test files**:

   ```text
   python Dataset/student_resource/utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir Dataset/student_resource/dataset/test
   ```

   The separate checker performs complete target-ID existence; full official `--check-ids` is avoided for memory. If official validation fails ambiguously, use the plan's 10-minute diagnostic limit, run manual checks, record `research/validator_issue.md`, and protect the delivery buffer.
4. Only after both gates pass, preserve the old fallback separately (for example `fallback/`), then promote the new validated outputs and measured score report to `best/`. Do not destroy the fallback. If any primary gate fails, restore the old `best/*.tsv` to `output/` and validate the restored pair.
5. Complete `research/audit.md` with duplicate/overlap findings when safe; finalize `research/france_shift.md`, `research/candidate_efficiency.md`, `research/log.md`, `Documentation_template.md`, `APPROACH_SUMMARY.md`, `FINAL_ARCHITECTURE.md`, and `FINAL_BUILD_SPEC.md` with **measured full-run** numbers. Do not present France or private-test accuracy as known. The one- to two-page approach document is `APPROACH_SUMMARY.md`; placeholders remain for team details.
6. Run unit tests and bounded end-to-end reproduction. The previous fixture and **8 tests** passed, but tests should be rerun on the final source. Avoid a second full inference solely for reproduction unless it fits before the buffer.
7. Package only after the current output hashes match the latest full checker report:

   ```text
   python code/business_entity_resolution/src/package_submission.py --workspace . --output amazon_ml_challenge_2026_submission.zip --check-report work/full_check_report.json
   ```

   Inspect ZIP integrity and contents. It includes `output/`, runnable `code/business_entity_resolution/src/`, README, requirements, methodology, approach summary, final architecture/build spec, and research reports. Large SQLite indexes and intermediate files stay outside the package.

No portal upload has been performed or recorded by this work; the prepared artifact can be submitted by the team once final checks pass.

## Key files

- `code/business_entity_resolution/src/pipeline.py`: normalization, index, macro F0.5, retrieval/scoring, evaluate/predict/check/fixture CLI.
- `code/business_entity_resolution/src/audit_data.py`, `audit_leakage.py`, `audit_overlap.py`: streaming/disk-backed audits.
- `code/business_entity_resolution/src/package_submission.py`: gated ZIP builder.
- `code/business_entity_resolution/README.md`, `requirements.txt`, `tests/`: reproduction and tests.
- `work/dev_narrow_full.json`, `work/dev_rare_both_full.json`, `work/holdout_narrow_full.json`, `work/holdout_rare_both_full.json`: full local metrics.
- `work/rare_both_test_10k_check.json`: representative test structural/efficiency result.
- `work/full_check_report.json`: currently validated **fallback** complete-report hashes; replace only by rerunning full `check` after primary completion.
- `best/`: validated fallback until a fully checked primary is promoted.
- `output/`: validated fallback completed files at this snapshot, alongside growing primary `.part` files.
- `research/`: audit, experiment log, France-shift proxy, candidate frontier, five-agent decision.

Do not confuse a process having produced `.part` files with a validated submission. Completion requires the independent full checker, the supplied validator, documentation, and a verified ZIP.
