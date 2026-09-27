# Experiment log

All results below must be measured locally on the supplied challenge data. Development-set decisions use the fixed Source 1 entity-level hash partition; holdout is reserved for mature comparisons. No leaderboard score has been used.

## Baseline, in progress

- **Question:** Can a deterministic, disk-backed name/address retriever and similarity scorer produce a valid full submission within the CPU deadline?
- **Hypothesis:** Exact and FTS5 name/address routes, followed by token/character/number scoring, provide a useful first complete result without a GPU or external data.
- **Change:** Built a standard-library SQLite index, a Unicode-preserving normalizer, a macro F0.5 scorer, and full output writer/checker.
- **Metrics planned:** 10,000-anchor throughput and peak working set; candidate recall; mean, median, P90, P95, P99, maximum candidates; dev macro F0.5; complete output validation.
- **Measured result so far:** Six unit/integration tests pass. A small fixture containing empty, singleton, and multi-match results plus US, India, and France anchors passes the supplied official validator. The train index built 10,320,219 target records in 1,235 seconds (~20.6 minutes), with observed peak process working set under 200 MB. Labeled-data retrieval performance is pending the integrity audit.
- **Decision:** Do not start full inference until the benchmark projection fits the deadline.

### Early broad-route runtime gate

- **Question:** Is four-route FTS5 retrieval affordable across the full test set?
- **Hypothesis:** BM25 can widen recall within the CPU deadline.
- **Change:** Broad name/address FTS5 retrieval for both target sources.
- **Metrics:** First 1,000-anchor throughput gate and memory.
- **Measured result:** Fewer than 1,000 dev anchors completed in over 100 seconds; projected full-run time exceeded 47 hours. Process remained CPU-bound around 100 MB. The run was stopped before 10,000 anchors.
- **Decision:** Kill this broad implementation for full inference. Optimize FTS retrieval separately; do not let it block the first complete submission.

### Indexed exact-name/address fallback, 10,000 dev anchors

- **Question:** Does exact name/address blocking produce a valid, timely fallback?
- **Hypothesis:** Four indexed exact routes will fit the remaining window, but recall will be limited by noise.
- **Change:** `--variant narrow`, with name and address equality routes separately capped for Source 2 and 3.
- **Metrics:** Exact macro F0.5, candidate recall, counts, throughput, peak process working set.
- **Measured result:** 10,000 anchors (5,000 US, 5,000 India), macro F0.5 0.488891 at dev-selected threshold 0.68; link-level candidate recall 0.291607 (US 0.332132; India 0.250962); mean candidates 3.6837, median 2, P90 12, P95 12, P99 13, max 19; 83.9 seconds total / 119.2 anchors per second; peak working set 113.5 MB. Multiplicity: 558 zero, 541 singleton, 8,901 multiple. A linear full-test projection is about 4.04 hours; this remains a projection until the test benchmark.
- **Decision:** Proceed to test-index build and bounded test benchmark, then run full fallback inference if the test benchmark confirms feasibility. Do not promote before full validation.

The test target index completed with 9,969,589 records in 1,284 seconds (~21.4 minutes), with observed peak process working set under 190 MB. The full-dev narrow result follows.

### Full fixed dev partition, narrow fallback

- **Question:** Does the 10k dev threshold and runtime hold across every dev Source 1 entity?
- **Hypothesis:** The 0.68 threshold is stable; the exact route remains bounded and CPU-feasible.
- **Change:** Evaluate all 44,098 dev anchors, with no holdout access.
- **Metrics and measured result:** Macro F0.5 **0.497433** at threshold **0.68**; candidate recall **0.297894**; candidate-oracle macro F0.5 **0.526975**; mean candidates 3.6499, median 2, P90/P95 12, P99 13, max 21; 252.1 seconds / 175.0 anchors per second; peak process working set 164.3 MB. US 26,498 anchors scored 0.536236 with candidate recall 0.330868; India 17,600 scored 0.439013 with recall 0.248280. There were 2,343 zero-match, 2,370 singleton, and 39,385 multi-match entities.
- **Decision:** Keep threshold 0.68 for bounded test and first full inference. The candidate-oracle gap over the actual score is only ~0.0295, confirming that retrieval is the dominant bottleneck. Holdout remains untouched until a mature comparison.

### First complete test inference — validated fallback

- **Question:** Can the chosen narrow fallback produce both complete outputs within the CPU deadline?
- **Hypothesis:** The 10k real test fixture projects a safe full run, including France.
- **Change:** Run `predict --variant narrow --threshold 0.68` over the complete supplied test set, writing temporary `.part` files and replacing the final names only after success.
- **Metrics and measured result:** 1,732,544 anchors, 6,371,588 actual scored candidates, 2,164,462 predicted matches, 1,856.2 seconds (~30.9 minutes). Output files are 50,787,199 and 104,792,184 bytes. The two completed TSVs are in `output/`; no `.part` files remain.
- **Validation:** The independent full checker passed all 1,732,544 rows, including all 259,452 France anchors. All 6,371,588 candidate IDs exist in the test target index and have the correct country; all 2,164,462 predicted IDs are contained in their scored candidates. Source 1 rows are unique and in input order. Mean 3.6776 candidates, median 2, P90/P95 12, P99 13, maximum 24. Checker runtime 526.1 seconds. SHA-256: matching `4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e`; candidates `5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8`. The supplied validator separately passed both complete output files (ID checking disabled there because the independent checker already checked every ID).
- **Decision:** Preserve both exact validated files, a score report, and the baseline source in `best/` before experiments. No leaderboard upload has been attempted.

### E1: document-frequency-gated rare-name route

- **Question:** Can a single rare name token recover missing candidates without the broad-FTS posting and ranking cost?
- **Hypothesis:** Querying at most one country/source-scoped name token with document frequency 2–1,000, only when exact retrieval returns fewer than eight candidates, raises recall and macro F0.5 within a bounded CPU runtime.
- **Change:** Add one FTS5 rare-name route per target source, six results per source, no BM25 sort. The index-derived FTS5 vocabulary supplies document frequencies; no external corpus is used. The validated `best/` baseline remains unchanged.
- **Metrics:** Same fixed dev anchors as the narrow route, macro F0.5, link recall, candidate counts, throughput, memory.
- **Measured result:** On a 1,000-anchor balanced gate, narrow scored 0.509081 with 0.294781 recall, while rare-name scored 0.533253 with 0.338968 recall at threshold 0.68. On the same 10,000-anchor balanced dev sample, rare-name scored **0.514004** at its dev-selected threshold 0.65, recall **0.337545**, mean candidates 8.2505, median 11, P90 14, P95 15, P99 17, max 19; 110.5 seconds / 90.5 anchors per second; peak working set 123.6 MB. The same-sample narrow baseline scored 0.488891 with recall 0.291607 and mean 3.6837 candidates.
- **Decision:** Pass the 1k/10k early gate. Do not promote on this sample alone; compare the address route, full dev, runtime projection, and holdout before any replacement full run.

### E2: document-frequency-gated rare-address route

- **Question:** Do distinctive address tokens recover more true links than the name-token route when exact blocking is sparse?
- **Hypothesis:** A single rare normalized address token per anchor, queried within country and each target source without BM25 sorting, can recover noisy and cross-script business names while keeping candidate counts and runtime bounded.
- **Change:** Use the same exact routes, then add one address-token FTS5 route per source only when exact retrieval returns fewer than eight candidates. Require document frequency 2–1,000; return at most six per source. The route uses only the supplied target index.
- **Metrics:** Same dev anchors and full candidate/score/runtime/memory metrics as E1.
- **Measured result:** On the 1,000-anchor gate, macro F0.5 0.553354, candidate recall 0.400356, mean candidates 8.91, 10.1 seconds; threshold 0.66. On the same balanced 10,000-anchor dev sample, macro F0.5 **0.538925** at dev-selected threshold **0.65**, candidate recall **0.398999**, mean 9.0, median 12, P90 14, P95 16, P99 18, max 19; 82.4 seconds / 121.4 anchors per second; peak working set 126.5 MB. This exceeds E1's 0.514004 score and 0.337545 recall on that sample, though it adds 0.75 candidates per anchor.
- **Decision:** Pass the bounded gate and run the full fixed dev split. Promotion still requires a mature comparison, test-side throughput, and complete validation; the preserved baseline is unchanged.

### E3: combined rare-address and rare-name routes

- **Question:** Does adding the name route after the address route recover enough additional true links to justify more candidates and CPU time?
- **Hypothesis:** The two independent routes are complementary on cross-script and noisy multi-match records.
- **Change:** When exact retrieval yields fewer than eight candidates, query at most one rare address token and one rare name token per target source (each frequency 2–1,000; six results per source). Preserve the exact candidates and deduplicate IDs; score every emitted candidate.
- **Metrics:** Same balanced 10,000 dev anchors and candidate/score/runtime/memory measures as E1 and E2.
- **Measured result:** On a 1,000-anchor gate, macro F0.5 0.563692, recall 0.429715, mean candidates 13.51, 16.2 seconds. On the same 10,000 dev anchors, macro F0.5 **0.554542** at threshold **0.65**, recall **0.432535**, mean candidates 13.4954, median 13, P90 25, P95 26, P99 28, max 31; 102.2 seconds / 97.8 anchors per second; peak working set 134.6 MB. Versus E2 address-only, score rises by 0.015617 (2.90% relative), recall by 0.033536, but mean candidates rise by 4.4954 and runtime by 24% on this sample.
- **Full-dev measured result:** On **all 44,098** fixed dev anchors, combined retrieval scored **0.5601653910 macro F0.5** at threshold **0.65**, versus narrow's 0.4974333241. Link candidate recall was **0.4312524062** versus 0.2978942766; candidate-oracle macro F0.5 was 0.639304. Mean candidates 13.3885, median 13, P90 25, P95 26, P99 28, maximum 31. US score 0.579133/recall 0.424639; India score 0.531608/recall 0.441203. Runtime 363.3 seconds / 121.4 anchors per second; peak process working set 245.6 MB. The macro F0.5 gain over narrow is 0.062732 absolute, 12.6% relative, at ~3.67 times the candidates per anchor.
- **Decision:** Pass the full-dev gate for a single fixed-threshold holdout comparison. The official efficiency weighting is unknown, so do not claim a combined-score winner based on F0.5 alone. Preserve the validated narrow fallback until any replacement passes complete output checks.

### Untouched holdout, mature-pipeline comparison

- **Question:** Does the full-dev improvement persist on Source 1 identity groups not used for threshold or retrieval choices?
- **Hypothesis:** The combined rare-token route outperforms the narrow fallback with thresholds fixed from dev.
- **Change:** Evaluate both pipelines on all 44,212 holdout anchors, narrow at dev threshold 0.68 and combined at dev threshold 0.65. No holdout threshold search or feature selection.
- **Metrics:** Entity-level macro F0.5, link candidate recall, country slices, candidate distribution, runtime, memory.
- **Measured narrow baseline:** **0.4996922783 macro F0.5**, candidate recall **0.2988166066**, mean 3.6298 candidates, median 2, P90/P95 12, P99 13, max 20; US score 0.539478/recall 0.333268; India score 0.440234/recall 0.247549. Runtime 261.6 seconds; peak working set 164.0 MB.
- **Combined measured result:** **0.5616271143 macro F0.5**, candidate recall **0.4303728929**, mean 13.3683 candidates, median 13, P90 25, P95 26, P99 28, max 31; US score 0.581115/recall 0.423757; India score 0.532503/recall 0.440219. Runtime 650.1 seconds; peak working set 245.4 MB. The score gain over narrow is **0.061935 absolute / 12.39% relative**, with recall up 0.131556 absolute. Both dev and holdout show similar gains.
- **Decision:** The combined route is the leading primary by the stated macro F0.5-first priority, conditional on a real-test throughput gate, France coverage, complete checker, and supplied official validator. The preserved `best/` fallback remains valid until a replacement passes all checks. The official candidate-efficiency weighting remains unknown.

### Improved primary: real-test throughput and structural gate

- **Question:** Does the combined route remain CPU- and memory-feasible on the unseen-country test distribution while satisfying output semantics?
- **Hypothesis:** The bounded rare-token routes remain within the deadline and produce exactly scored, valid target IDs for every country.
- **Change:** Run the frozen combined route at threshold 0.65 on the first 10,000 mixed-country test anchors in a separate fixture directory, then run the independent checker and supplied validator with `--check-ids` against its matching test fixture.
- **Measured result:** 10,000 anchors (US 3,891, India 4,619, France 1,490) in **106.55 seconds**, 93.9 anchors/sec, 105.4 MB peak working set. 142,118 actual scored candidate pairs; mean 14.2118, median 13, P90 25, P95 26, P99 28, max 31. France mean 16.277, candidate P95 27. All target IDs and countries valid, all predicted IDs within scored candidates, no duplicate/coverage issues. The supplied validator passed the fixture with ID checking enabled.
- **Runtime decision:** A naive projection is 5.13 hours for 1,732,544 anchors; even a conservative 1.5× slowdown plus complete checking and rollback fits before the reserved final-four-hour buffer. The full 44,212-anchor holdout took 10.84 minutes and peak 245.4 MB, also well inside 16 GB RAM. Start full improved inference, monitor progress, and preserve `best/` until validation.

### Research stop and hardening transition

Three prioritized experiments have been measured. The combined route is materially ahead of the preserved baseline on both full dev and untouched holdout, and its test fixture passes runtime/memory and structural gates. Further graph, LSH, broad FTS, or supervised ranker research has poor deadline-adjusted expected value and would compete with full inference and validation. **STOP RESEARCH → HARDEN → FULL INFERENCE → VALIDATE → PACKAGE.** Full primary inference began on September 26 with `.part` outputs; `best/` remains the validated fallback. At the earlier of 60 minutes or 20% of projected runtime, check that the run has positive anchor/output progress and acceptable memory. Do not begin another heavy local job while it runs.

**First full-inference checkpoint (about 20% of the projected runtime):** The primary processed 340,000 of 1,732,544 anchors in 1,904 seconds (~31.7 minutes), at 178.6 anchors/sec overall and 14.25 mean actual candidates. The process remained active with approximately 131 MB working set and 136 MB peak, far below the available ~16 GB. This is a positive prerequisite milestone with no swap/resource issue; continue the full run. The validated narrow fallback remains untouched in `best/`.

The frozen primary source file `code/business_entity_resolution/src/pipeline.py` had SHA-256 `7d4b7814968effb25663e2247c55492f343b546a80216ed01c924f5e054d2b1e` during the full run; no production-code edits will be made until inference and validation finish.

**Wall-clock pause observed:** Between the 730,000- and 740,000-anchor progress messages, the monotonic elapsed timer advanced from 3,459 to 10,859 seconds while the process accumulated little CPU time. This is consistent with the host sleeping or pausing, but the exact cause was not established. The process remained alive, its output files stayed staged, and the next 10,000 anchors completed in 42 seconds. Runtime projections should exclude this pause when estimating active throughput but include it in the final reported wall time. The deadline margin remained sufficient; no fallback was triggered.

### Complete primary inference, validation, and promotion

- **Question:** Does the dev-selected combined route produce a complete valid test submission with stable candidate behavior?
- **Hypothesis:** Its capped exact and rare-token retrieval passes all full-file checks and preserves the local gain while staying within CPU memory.
- **Change:** Run frozen `rare_both` at threshold 0.65 over every test anchor; run the full independent checker, official validator, and a separate strict row/empty-field/hash/anomaly scan; preserve the fallback transactionally before promotion.
- **Metrics and measured result:** Inference exited normally with 1,732,544 anchors, 24,702,044 actual scored candidates, 3,327,344 predicted IDs, 13,737.2 seconds wall time including the observed host pause, and 136.2 MB peak process working set. Candidate mean 14.2577, median 13, P90 25, P95 26, P99 28, max 31. Empty-prediction rates: US 21.93%, India 23.73%, France 11.54%, close to the 10k fixture. The full independent checker passed every target ID, country, row and candidate-subset check in 1,496.8 seconds; the supplied complete validator exited 0 with explicit PASS. A second strict scan independently confirmed exact TSV shape, 1,732,544 unique and ordered Source 1 rows, 259,452 France rows, genuinely empty cells, no placeholder tokens, the candidate bound, fresh report hashes, and different primary versus fallback hashes.
- **Decision:** Promote validated primary outputs to `best/` after independently copying and hashing the original baseline in `fallback/`. The test set has no labels, so test macro F0.5, precision, prediction recall, FP/FN, and true candidate recall are **NOT MEASURABLE**. Full dev/holdout F0.5 and labeled candidate recall remain the only measured accuracy evidence. The official candidate-efficiency weighting is unknown.

### Fixed-threshold local holdout error counts

The frozen primary was rerun on all 44,212 labeled holdout entities at the
already chosen 0.65 threshold, solely to count errors. It recovered **61,129
true links**, predicted **13,038 false positives**, and missed **92,159 links**:
micro precision **0.824208**, micro prediction recall **0.398785**, entity-level
macro F0.5 **0.5616271143**, and link candidate recall **0.4303728929**. The
last two match the saved holdout report. US: TP/FP/FN **36,566/6,367/55,114**,
precision **0.851699**, prediction recall **0.398844**, macro F0.5 **0.581115**,
candidate recall **0.423757**. India: **24,563/6,671/37,045**, precision
**0.786419**, prediction recall **0.398698**, macro F0.5 **0.532503**, candidate
recall **0.440219**. The test set remains unlabeled, so none of these are
private-test or France accuracy measurements.

### Independently restorable fallback

After promotion, the copied narrow files in `fallback/` were rerun through the
complete disk-backed checker: **PASS** on all **1,732,544** anchors and
**6,371,588** candidate IDs, including every France anchor, in **804.9 seconds**.
It reconfirmed target existence, same-country candidates, unique ordered rows,
and predictions contained in candidates. The copied matching/candidate hashes
are exactly `4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e`
and `5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8`.
The supplied validator also returned **PASS**, exit 0, on the copied fallback.
The promoted primary remains the submission choice.
