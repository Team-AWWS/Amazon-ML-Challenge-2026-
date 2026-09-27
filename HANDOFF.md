# Amazon ML Challenge 2026 — forensic engineering handoff

## Final validation update — September 26, 2026, approximately 22:40 IST

The primary `rare_both` full inference exited normally at threshold 0.65. Its
complete 1,732,544-row output passed the independent target-ID/country/subset
checker, the official validator, and a separate strict TSV/empty-field/hash/
anomaly scan. There are **24,702,044** actual scored candidate pairs and
**3,327,344** predicted IDs. Candidate mean/median/P90/P95/P99/max are
**14.2577/13/25/26/28/31**. All **259,452 France** anchors are present. Full
test F0.5, precision, prediction recall, FP/FN, and true candidate recall are
**NOT MEASURABLE** because test labels are absent. The full inference reported
13,737.2 seconds wall time, including a host pause, and 136.2 MB peak working
set. The complete checker took 1,496.8 seconds.

The original validated narrow submission was copied to `fallback/` and its
hashes verified before the primary files were promoted to `best/`. The primary
files are also in `output/`. Primary SHA-256: matching
`df1415117c62d350ca33d51bffa678934f1f2c6282997fb0103087995178ff05`,
candidates `3d5b2e71e32e11f168d22725c03757f62b0853147e7f3ba7cfa0f4bf7cc3f9c5`.
Fallback SHA-256: matching
`4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e`,
candidates `5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8`.
Eight tests passed, and a fresh 10,000-anchor reproduction exactly matched
the first 10,000 full-output rows and passed its independent checker and
official validator with ID checking enabled. Documentation and the input
duplicate/overlap audit were subsequently completed.
The input overlap audit subsequently found **zero** train/test Source 1 ID
overlap, **zero** train/test target ID overlap, and **zero** extra exact raw
Source 1 duplicate rows. Within-source normalized target duplicate extra rows
numbered **143,071 train** and **125,646 test**; normalized groups shared by
Source 2 and Source 3 numbered **6,895 train** and **12,565 test**. Raw target
text duplicates were not separately counted. The fixed-threshold primary
holdout rerun measured TP/FP/FN **61,129/13,038/92,159**, micro precision
**0.824208**, and micro prediction recall **0.398785**. Its macro F0.5 and
candidate recall matched the earlier saved holdout report. These are labeled
local measurements; the full test remains unlabeled.

The final refreshed submission ZIP is `amazon_ml_challenge_2026_submission.zip`
(174,257,174 bytes, 23 entries, SHA-256
`91fe000809e29459fb75f3164b787d39b5d5cb8e8e3a6ec2f21a314f1a38b194`).
Its CRC and every manifest entry's archived SHA-256/size passed an independent
check. After promotion, the copied `fallback/` files independently passed the
complete checker again on all 1,732,544 anchors (804.9 seconds), and the
supplied validator returned explicit PASS on that location. The older
time-stamped live-state sections below are historical and
must not be read as the current process state.

Snapshot: 2026-09-26, approximately 21:35 IST. Workspace: C:\Users\ANSH DARJI\Documents\ChatGPT\Amazon ML Challenge. This is a live-state document: the primary inference process can advance while this file is being read. Recheck its process/session and output files before acting. Values marked measured come from the repository reports or commands, not from the old planning context.

## Executive status

CURRENT STATUS: VALIDATED FALLBACK COMPLETE; IMPROVED PRIMARY SELECTED AND FULL INFERENCE RUNNING. THE PRIMARY IS NOT YET A VALIDATED FULL SUBMISSION.

| Item | Current fact |
| --- | --- |
| Project / competition | Amazon ML Challenge 2026, Business Entity Resolution. The ML round deadline was verified earlier against the live competition listing as 2026-09-27 11:59 p.m. IST. Hard delivery/rollback buffer starts 7:59 p.m. IST that day. |
| Problem | For each Source 1 business, return zero or more matching Source 2 and Source 3 record IDs, and disclose exactly the candidates scored. |
| Compute | Windows / PowerShell, CPU-only Intel Core i7-1255U and approximately 16 GB RAM from the earlier machine inspection. Current jobs run with Python 3.14.2 and SQLite 3.50.4/FTS5. |
| Current best measured local method | Exact country-scoped name/address retrieval, then gated rare address and rare name token retrieval; deterministic pair scoring; threshold 0.65 selected on dev. Variant name: rare_both. |
| Current best measured score | Full dev 44,098 anchors: macro F0.5 0.560165 and link candidate recall 0.431252. Untouched full holdout 44,212 anchors at fixed 0.65: macro F0.5 0.561627 and recall 0.430373. No public/private score exists. |
| Safe submission | Complete exact-only narrow output at threshold 0.68 in best/. Both full TSVs passed the independent checker and official validator. |
| Live process | The improved full test inference started at 18:17:36 IST on 2026-09-26 as Python PID 25348, using work/test_index.sqlite and writing output/*.part. At this snapshot it had passed about 980,000 of 1,732,544 anchors; verify a later count in the live terminal. |
| Most important next action | Keep that one heavy process running. On successful exit, run the independent complete checker and then the supplied validator before promoting or packaging. Do not overwrite best/ beforehand. |
| Major unresolved issues | Primary full-file validation; raw/normalized duplicate-record and train/test ID overlap audit; France has no labels; official candidate-efficiency weighting is unknown. |

No leaderboard upload has been attempted by this project. The permitted number of uploads was not confirmed. Team and member names intentionally remain placeholders. An older MEGA_CONTEXT.md describes the pre-implementation state and is background only; do not use its “no model built” statement as current status. An earlier PROJECT_HANDOFF_2026-09-26.md is likewise a time-stamped, older snapshot.

## Competition contract and scoring

Each source table is UTF-8 TSV with columns entity_id, business_name, business_address, country. Source membership comes from ID prefixes S1-, S2-, S3-; there is no shared business identifier. Source 1 is the anchor list. Source 2 and 3 are target vendor records. Train data includes US and India; the test set additionally has France. One Source 1 anchor may have zero, one, or several true target IDs, including more than one from the same target source. The training label file has one Source 1 row and a comma-separated full target-ID set, or an empty cell. Test labels are unavailable.

The conceptual flow is:

    Source 1 anchor + disk-backed Source 2/3 index
      → country-scoped candidate retrieval
      → deduplicated candidate set
      → deterministic scoring of EVERY emitted candidate
      → threshold decision
      → final match set

The required output files are output/matching_results.tsv with header source1_entity_id<TAB>matched_entity_ids and output/candidate_pairs.tsv with header source1_entity_id<TAB>candidate_entity_ids. They contain one row per test Source 1 ID; lists are comma-separated and genuinely empty cells represent no IDs. The candidate list is the set actually fed to the matcher, not a broad pre-filter pool and not merely the accepted matches. Predicted matches must be a subset of those candidates. All France anchors must be present. The later organizer announcement says candidate size/code influence final ranking alongside matching score but gives no numeric weighting; this is not a proven tie-break rule.

The local metric implementation is entity_f05 in code/business_entity_resolution/src/pipeline.py. For nonempty truth T and prediction P:

    TP = |T ∩ P|; FP = |P − T|; FN = |T − P|
    entity F0.5 = 5 TP / (5 TP + 4 FP + FN)
    macro F0.5 = arithmetic mean of entity scores over Source 1 anchors

Empty truth plus empty prediction scores 1; empty truth plus any prediction scores 0; nonempty truth plus empty prediction scores 0. The function and cases are unit-tested in code/business_entity_resolution/tests/test_pipeline.py. The high false-positive coefficient motivates conservative scoring, but the scorer cannot recover a true link absent from candidates. Candidate-link recall is therefore measured independently as retrieved true links divided by all true links; candidate-oracle macro F0.5 is also reported. Do not substitute pair-level micro F0.5.

## Dataset and audit — measured versus pending

All supplied data is extracted under Dataset/student_resource/dataset/. The original ZIP remains at Dataset/6ab10eb3b23ba_student_resource.zip. The complete train integrity audit is work/audit_report.json, produced by code/business_entity_resolution/src/audit_data.py. Row counts, country/missingness and multiplicity are recorded in research/audit.md from complete streaming measurements.

| File | Rows | Country counts | Measured missingness |
| --- | ---: | --- | --- |
| train_source1.tsv | 2,206,821 | US 1,323,633; India 883,188 | no missing fields reported |
| train_source2.tsv | 5,034,616 | US 3,016,817; India 2,017,799 | address 168,967 |
| train_source3.tsv | 5,285,603 | US 3,170,056; India 2,115,547 | address 175,916 |
| train_ground_truth.tsv | 2,206,821 | n/a | 123,247 empty match lists |
| test_source1.tsv | 1,732,544 | US 663,106; India 809,986; France 259,452 | no missing fields reported |
| test_source2.tsv | 4,887,273 | US 1,871,330; India 2,312,565; France 703,378 | address 129,408 |
| test_source3.tsv | 5,082,316 | US 1,945,701; India 2,405,000; France 731,615 | address 136,098 |

The label audit measured 7,638,365 links, of which 3,693,619 point to S2 and 3,944,746 to S3. Anchor multiplicity: zero 123,247 (5.585%), singleton 119,157 (5.399%), multiple 1,964,417 (89.016%), maximum 11. Full frequency counts for 0–11 are in research/audit.md. Train Source 1 raw name lengths: median 24, P95 37, P99 42, maximum 105 characters. Address lengths: median 41, P95 103, P99 124, maximum 256. The train audit found 2,206,821 unique Source 1 IDs, exactly one ground-truth row per anchor, no bad S1 prefixes, no duplicate target IDs within label lists, no bad target prefixes, no nonexistent labeled target IDs, and no cross-country labeled links. The Source 2/3 index builds use a UNIQUE entity_id constraint and completed with exactly 10,320,219 train and 9,969,589 test target rows, so duplicate target IDs within those indexed splits were rejected or absent.

Pending / NOT VERIFIED: duplicate record values within and across target sources; train/test Source 1 and target ID overlap; within-source and cross-source normalized duplicate group counts. code/business_entity_resolution/src/audit_overlap.py exists for this, but its full job must wait until the primary inference and validation no longer need the machine. Do not fill these values from intuition. The current output validator found no duplicate output rows/IDs, which is a different question from duplicate input record values.

### Genuine linked noise examples

The following are real train Source 1 rows and their labeled target IDs queried from work/train_index.sqlite using work/inspect_labeled_examples.py. Target text below is the index's NORMALIZED name/address, not the untouched raw vendor TSV. They are examples, not prevalence estimates.

| Pattern | Actual observed pair | What it means for the implementation |
| --- | --- | --- |
| Name typo | S1-133037285 “Christ Chapel” links to S2-407207105 “christ chape1”. | Exact-name blocking misses this target; the address and rare-token routes may retrieve it. Character-trigram similarity offers partial scoring tolerance. |
| DBA/trade name | The same anchor links to S3-183080822 “ectosyn dba christ chapel”. S1-925783039 “Orelee's Barbershop” links to S3-698172821 “orelee s services”. | Partial name containment and independent address retrieval help; a completely changed name is still a recall risk. |
| Abbreviation / legal suffix | S1-773889195 “Prime Money” links to “prime money inc”, “primemoney com”, and “primemoney”; its address appears with road/rd and OK/Oklahoma. | Stopword and token overlap help; char trigrams help concatenation, but no full abbreviation lexicon is implemented. |
| Punctuation / token order | S1-925783039 “Orelee's Barbershop”, 1795 Westchester Drive, High Point, NC links to targets with “orelee s”, “westchester dr”, and address components reordered as “nc high point”. | NFKD/casefold/punctuation-to-space and set-based token overlap handle some order changes. |
| Numeric conflict in a true link | “Christ Chapel” at 2100 Cameron Drive links to S3-476003339 with 210 Cameron Drive; S1-773889195 at 17560 Ellis Road links to a normalized 0017560 address. | Exact address misses these. The score's number-conflict penalty can also hurt genuine noisy pairs; this is unresolved. |
| Partial or missing target address | S1-851869949 “Custom Wealth Services LLC”, 5559 Orville Avenue links to S3-807524060 with an empty indexed address; other links show 555 or 005559. | Name route and explicit missing-address score fallback help, but numeric discrepancies remain difficult. |
| Unicode / mixed scripts | S1-755362802 in West Bengal links to S3-440254853 with Bengali “পশ্চিমবঙ্গ” in the normalized address; S1-785847572 in Maharashtra links to S2-682432196 with “महाराष्ट्र”. | Normalization retains non-Latin letters/marks, rather than deleting this evidence. Latin-to-Indian-script translation/transliteration is not implemented. |
| Reordered/shortened address | S1-27541239 “Nexus Anchor Rain”, 1111 Church Street, Unit 2007, Nashville links to S2-85756610 “nashville tn 1111 church street” and S3-893131105 “1111 church street 2007 nashville tennessee”. | Address token overlap is order-insensitive; exact-address retrieval is not. |

The code does not have a separate trained transliterator, postal parser, business registry, geocoder, or external enrichment. Some organizer video examples in MEGA_CONTEXT.md are illustrative and must not be passed off as dataset rows.

## Fixed train/dev/holdout split and leakage protection

split_bucket in pipeline.py computes BLAKE2b (8-byte digest, personalization amzml26) of normalized Source 1 business name, a zero separator, and normalized address; bucket is digest modulo 100. There is no RNG or random seed. Buckets 0–1 are dev, 2–3 holdout, 4–99 train: actual counts 44,098 / 44,212 / 2,118,511 respectively. This is Source 1 entity-level, never pair-row-level; exact normalized name+address groups land together. work/split_manifest.tsv materializes every assignment. code/business_entity_resolution/src/audit_leakage.py scanned all 2,206,821 train anchors into a separate SQLite DB and found ZERO exact normalized name+address groups crossing partitions. It also found 34,145 dev/holdout anchors with the same name but a different address as some train anchor, and 4,631 with the same address but a different name. These are related-record leakage proxies, not confirmed same legal entity.

No learned classifier was fitted on the train partition. Labels were installed in the train SQLite index for integrity checks and evaluation; target document frequencies are unsupervised statistics over supplied target records. Dev selected blocking variants, features and thresholds. Holdout was not used for threshold search: the mature narrow and combined pipelines were each evaluated once across all 44,212 holdout anchors with their dev-frozen thresholds 0.68 and 0.65. Related but non-identical records could still cross groups, so even the holdout is not a guarantee of private-test transfer.

## Repository map and ownership

| Path | Actual purpose / status |
| --- | --- |
| Dataset/student_resource/dataset/{train,test}/ | Original extracted TSVs; do not edit. Original ZIP retained under Dataset/. |
| Dataset/student_resource/utils/validate_submission.py | Organizer validator, read/used on fixture and full fallback. Not a scorer. |
| code/business_entity_resolution/src/pipeline.py | Root-owned production implementation: normalizer, metric, SQLite index, candidate routes, scorer, evaluate/predict/check/fixture CLI. SHA-256 at the primary-run checkpoint: 7d4b7814968effb25663e2247c55492f343b546a80216ed01c924f5e054d2b1e. Freeze it until live inference finishes. |
| code/business_entity_resolution/src/audit_data.py | Full train labels/ID/country/length audit and split manifest. Completed. |
| code/business_entity_resolution/src/audit_leakage.py | Exact and partial-field split-overlap audit. Completed. |
| code/business_entity_resolution/src/audit_overlap.py | Full raw/normalized duplicate and train/test ID-overlap audit. Implemented but full run pending. |
| code/business_entity_resolution/src/package_submission.py | ZIP builder with full-coverage, France, semantic-flag and SHA-256 gates. Not run for final ZIP yet. |
| code/business_entity_resolution/tests/ | Eight unit/integration tests and a small synthetic US/India/France fixture; passed before current full inference. Rerun before delivery. |
| code/business_entity_resolution/README.md; requirements.txt | Reproduction commands and standard-library-only runtime specification. |
| work/train_index.sqlite; work/test_index.sqlite | Derived disk-backed target indexes (~3.66 GB and ~3.39 GB); excluded from package. Both complete. The current test index had FTS vocabulary metadata prepared. |
| work/*.json; work/split_manifest.tsv | Measured audit, dev/holdout, fixture and output-check reports; inspect exact file before citing. work/full_check_report.json STILL describes the validated narrow fallback until the new full check runs. |
| output/*.tsv | At this snapshot, still the completed narrow fallback files. They can be replaced at successful primary exit. |
| output/*.tsv.part | Currently growing improved primary files. Do not delete or rename while PID 25348 lives. |
| best/ | Validated narrow fallback matching/candidate TSVs, score_report.md, pipeline_baseline.py. Do not overwrite until a replacement passes all checks; preserve fallback separately when promoting. |
| research/ | audit, experiment log, five-agent review, France proxy and candidate frontier. |
| Documentation_template.md; APPROACH_SUMMARY.md; FINAL_ARCHITECTURE.md; FINAL_BUILD_SPEC.md | Drafted methodology, short approach, architecture and build specification; update full primary measured output numbers after validation. Team identifiers remain placeholders by request. |
| MEGA_CONTEXT.md; PROJECT_HANDOFF_2026-09-26.md | Earlier context and earlier live snapshot; not current proof of execution. |

Git status at inspection: branch master has NO commits yet; project files are untracked. There is no meaningful git diff/commit hash to restore, and no AGENTS.md was found in this workspace. Five research agents were read-only; root owns production source and artifact promotion.

## Production pipeline: precise implementation

### Input, normalization and index build

read_source in pipeline.py opens UTF-8 with BOM tolerance, parses TAB delimiters with csv.DictReader, and requires exactly the four source columns in order. IDs remain strings. Commas inside business addresses are data; commas only split the target-ID list field in ground truth/output. build_index streams test or train Source 2 then Source 3 in batches of 50,000, validates each S2-/S3- prefix, and inserts normalized name/address with entity_id, country and source into SQLite records(rowid INTEGER PRIMARY KEY, entity_id UNIQUE, country, src, nname, naddr). It creates country/name and country/address B-tree indexes and an external-content FTS5 table over country, src, nname, naddr with unicode61/remove_diacritics 2. An FTS5 vocabulary virtual table exposes per-field document frequencies. Derived indexes have metadata complete=yes only at successful end; open_index refuses incomplete indexes for read-only use. Index build used PRAGMA synchronous=OFF for speed because the DB is regenerable; do not treat an interrupted index as durable.

normalize case-folds then NFKD-decomposes text. Letters and numbers are retained. Latin combining marks are removed (accent-insensitive Latin); combining marks in other scripts are kept, preserving Indic evidence. Non-letter/number/retained-mark characters become spaces; whitespace is collapsed. Thus punctuation and case disappear, but the pipeline does NOT expand rd to road, translate state names, transliterate scripts, remove all legal suffixes in the index, or canonicalize address numbers. The raw supplied TSVs remain unchanged.

### Candidate retrieval and candidate-file semantics

candidates first runs four exact B-tree routes: normalized name and normalized address, each independently against s2 and s3 within the exact country string. Each route has SQL LIMIT 6. Selected IDs are unioned in insertion order through a dict, never intersected. A target found on multiple routes is scored once. The narrow baseline stops there (maximum 24 possible IDs before dedup).

The primary rare_both variant activates extra retrieval only if the exact union has fewer than eight IDs. For each normalized address and then normalized name, rare_term considers distinct tokens of at least four characters that contain a letter and are not on the appropriate stopword list. It looks up column document frequency in the supplied target FTS5 index, allows only frequencies 2 through 1,000, and selects the lowest-frequency token (term string breaks ties). For each field/token it runs separate FTS5 MATCH queries including the country and s2/s3 source, each with LIMIT 6 and NO BM25 sort. Returned IDs join the existing union. The code has a 36-ID final cap; given the activation condition and four extra six-ID routes, the observed maximum is 31. There is no cross-source assignment constraint, no candidate pair prefilter after this union, and no hidden scorer before candidate_pairs.tsv. All IDs emitted by candidates are passed to pair_scores and written to candidate_pairs.tsv. A true match that never enters this union is irrecoverable by the threshold/scorer; measured primary holdout link recall of 0.430373 quantifies that limitation. The rare_name and rare_address variants use one extra field each. The broad and balanced variants still exist in the CLI but their OR/BM25 implementation is too slow for full inference and must not be selected.

The FTS5 result SQL has LIMIT 6 without an explicit ORDER BY. It is bounded and has behaved consistently with this built index/SQLite, but SQL row ordering is not formally guaranteed across different query planners/SQLite versions; reproduce with the documented environment and run the bounded fixture before relying on byte-for-byte output identity. The source/code hash and TSV hashes, not an assumption about implicit SQL order, are the forensic identity of this run.

### Features, scoring and decisions

pair_scores normalizes the anchor and calls similarity on each candidate's normalized target fields. Name tokens omit a small legal-suffix/stopword set (inc, incorporated, corp, corporation, co, company, llc, llp, ltd, limited, private, pvt, plc, the, and). Address tokens omit a small address/common-country set. Name and address each compute token Jaccard and containment; score is max(Jaccard, 0.82 × containment). If below 0.7, a set-of-character-trigrams Dice score can raise it, scaled 0.90 for name or 0.86 for address. Address digit strings are extracted into sets. Number overlap adds 0.05; conflicting nonempty number sets with address score below 0.55 multiply the final score by 0.82. The base weighted score is 0.52 × name + 0.43 × address + 0.05 × number-overlap. Missing target address allows a 0.72 × name fallback; very weak name (<0.2) allows a 0.68 × address + 0.04 × number fallback. Final score is capped at 1.0. These are hand-set deterministic weights, not trained coefficients.

The only learned/selected scalar is the acceptance threshold, searched on dev over 0.10–1.00 in 0.01 increments with the exact entity macro F0.5. For primary it is 0.65; for narrow fallback it is 0.68. A candidate is accepted when score >= threshold. Zero, one and multiple candidates can be accepted; there is no top-1 rule, maximum-match cap, bipartite assignment, probability calibration, fitted classifier, neural model, negative sampling, class balancing, or external model weights. “Training time”, training examples for a classifier, feature dimension of a vector model, model license and parameter count are NOT APPLICABLE here. Train labels supported audit and dev/holdout evaluation only. The source code uses Python standard library plus optional psutil for resource reporting.

predict streams all test Source 1 rows, writes one row per anchor to matching_results.tsv.part and candidate_pairs.tsv.part, closes them, then replaces the completed TSV names. This is atomic per file, not atomic as a two-file transaction: a crash between replacements could leave a mixed pair. Always rerun the complete checker after successful exit or rollback. The checker iterates source/output rows together with strict zip, verifies schema/order/coverage, no repeated IDs in a list, match subset, target prefix, target existence and same country via disk-backed SQLite lookups, and calculates count distributions/country slices/SHA-256. The full check is mandatory because the official validator's default does not load all target IDs and treats candidate-subset violations as warnings.

### Exact command surface

pipeline.py subcommands: build-index, prepare-vocab, evaluate, predict, check, make-fixture. Relevant flags: --data-dir, --split train|test, --index, --variant narrow|rare_name|rare_address|rare_both|balanced|broad, --partition dev|holdout|all, --fixed-threshold, --threshold, --limit, --country, --output-dir, --report, --config, --fixture-dir. evaluate uses at most half its requested --limit per country to keep bounded samples balanced; requesting --limit 50000 therefore gave 42,600 rather than all 44,098 dev anchors because US capped at 25,000. Use --limit 100000 for the complete dev or holdout split. Holdout evaluate refuses to run without --fixed-threshold.

## Chronological experiment and decision history

All scores below are LOCAL labeled development or holdout results. The organizer leaderboard has not supplied a score.

| Stage | Actual test and measured result | Decision |
| --- | --- | --- |
| Initial synthetic correctness | Small US/India/France fixture covered empty, singleton and multi-match outputs; eight tests passed, and supplied validator passed fixture with ID checking. | Establish schema/metric/index/checker correctness before scaling. |
| Index/audit | Train target index: 10,320,219 rows, 1,235 s, observed build peak <200 MB. Test target index: 9,969,589 rows, 1,284 s, peak <190 MB. Full train integrity audit 819.1 s. | SQLite disk-backed approach feasible on CPU/RAM. |
| Broad FTS OR/BM25 runtime gate — FAILED | Fewer than 1,000 dev anchors in >100 s; extrapolated full runtime >47 h, ~100 MB process memory. No valid macro F0.5 or recall for this variant was measured. | Killed early; LIMIT bounded returned rows but not the expensive posting/ranking traversal. Balanced FTS was not established as a competitive full variant. |
| Narrow exact route, 10k balanced dev | Macro F0.5 0.488891, recall 0.291607, mean 3.6837, median 2, P90/P95 12, P99 13, max 19; 83.9 s, 113.5 MB. | Fallback feasible but recall-limited. |
| Narrow full dev (44,098) | 0.497433 macro F0.5 at selected 0.68, recall 0.297894, oracle 0.526975; mean 3.6499, P99 13, 252.1 s, peak 164.3 MB. | Freeze 0.68 and run full fallback. |
| Narrow complete test — SUCCESS | 1,732,544 anchors, 6,371,588 candidates, 2,164,462 predictions, inference 1,856.2 s; full checker 526.1 s, official validator PASS. | Preserve exact validated outputs/code/report in best/. |
| E1 rare-name, same 10k dev | 0.514004 macro F0.5 at 0.65, recall 0.337545, mean 8.2505, P99 17; 110.5 s, peak 123.6 MB. | Promising bounded route, but not enough evidence to promote. |
| E2 rare-address, same 10k dev | 0.538925 at 0.65, recall 0.398999, mean 9.0, P99 18; 82.4 s, peak 126.5 MB. | Address route stronger than E1. A 42,600-anchor dev run scored 0.544346/recall 0.398986, but omitted 1,498 US dev anchors due the per-country cap; do not call it full dev. |
| E3 combined rare-address+name, same 10k dev | 0.554542 at 0.65, recall 0.432535, mean 13.4954, P99 28; 102.2 s, peak 134.6 MB. | Additional 0.015617 F0.5 / 0.033536 recall versus E2, at 4.4954 more candidates and ~24% longer runtime. Advance to full dev. |
| E3 full dev (44,098) | 0.560165 at 0.65, recall 0.431252, oracle 0.639304; mean 13.3885, median 13, P90 25, P95 26, P99 28, max 31; 363.3 s, peak 245.6 MB. | Compared with narrow, +12.6% relative F0.5 and +0.133358 absolute recall. Advance to one fixed-threshold holdout. |
| Untouched full holdout (44,212) | Narrow fixed 0.68: score 0.499692, recall 0.298817, mean 3.6298, P99 13, 261.6 s, 164.0 MB. E3 fixed 0.65: score 0.561627, recall 0.430373, mean 13.3683, P99 28, 650.1 s, 245.4 MB. | Repeatable +0.061935 absolute/+12.39% relative F0.5, at 3.68× mean candidates. E3 selected conditionally; no holdout tuning. |
| E3 real test fixture (10,000) | US 3,891 / India 4,619 / France 1,490; 142,118 scored candidates, mean 14.2118, median 13, P90 25, P95 26, P99 28, max 31; 106.55 s, peak 105.4 MB. Independent ID/country/subset check and supplied validator with --check-ids PASS. | Safe to launch complete inference. This is test structure/runtime, NOT test F0.5. |
| E3 complete test | Running at snapshot; ~980k/1,732,544 anchors. A ~2-hour wall-clock pause occurred between 730k and 740k while CPU time barely increased; exact host cause unverified, active throughput recovered. | Keep running; full correctness and validator NOT YET RUN on E3. |

research/log.md is the chronology and individual questions/hypotheses/changes/decisions; work/dev_*.json and work/holdout_*.json are measured reports. research/candidate_efficiency.md contains the frontier. No model training or hard-negative mining experiment was performed; suggestions in MEGA_CONTEXT.md are historical ideas, not implementation.

## Five-agent research process actually completed

The user explicitly requested five CPU-light read-only research agents while indexes/full inference were prioritized. Agent 1 proposed exactly six families: harden deterministic baseline, rare-token inverted retrieval, character n-gram LSH, structured address-first, lightweight pairwise ranker, cross-source consistency graph. Agent 2 argued potential gains for bounded rare/address recall and later ranker/cross-source support. Agent 3 stressed high fanout/posting cost, country/script brittleness and propagation risk, killed full LSH and graph for this deadline, and deferred a trained ranker until candidate recall improved. Agent 4 red-teamed options and prioritized E1 rare name, E2 address, then an OPTIONAL cheap deterministic rescoring/threshold check under explicit 1k/10k and runtime gates; the broad FTS path was not retried unchanged. After E1 and E2, root instead measured the combined name+address route as E3. Agent 5 first recommended a gated two-stage route with narrow fallback provisionally, then after measured dev/holdout results selected rare_both with threshold 0.65 as CONDITIONAL primary and the fully validated narrow artifacts as fallback. Its conditions were mixed-country test benchmark, full complete output checks, official validator, deadline buffer, and explicit France uncertainty. Outputs are in research/agent_reviews.md. Agents 1–4 did not edit production code; root made all source/artifact changes. This decision is evidence-based, not proof by agent consensus.

## Why these choices were made

| Decision | Alternatives / evidence | Trade-off or limitation |
| --- | --- | --- |
| Disk-backed SQLite/FTS5, not all-pairs | ~10 million targets per split and ~16 GB RAM; 20-minute measured index builds, <200 MB build working set. | Several GB disk per index; build is reproducible but not free. |
| Independent name and address routes | Genuine labels include changed trade names at close addresses and noisy addresses with stable names. Exact-only baseline already produced a valid complete submission. | Exact retrieval captured only 29.8% of dev links. |
| Rare address then name, only on sparse exact union | E1/E2/E3 same-sample and full E3 dev/holdout measurements show recall/score gain. DF gate and no BM25 avoid broad query failure. | 3.68× holdout mean candidates versus narrow; unknown official efficiency weighting. |
| Hand-weighted deterministic scorer | CPU simplicity, no training/weight-license issue; dev/holdout consistent at one threshold. | Calibration is imperfect; oracle gap and false merges remain. |
| Threshold 0.65 for primary | Exhaustive 0.01 dev grid over exact macro F0.5; full holdout at frozen threshold confirms gain. | France has no labels; this threshold is not proven optimal there. |
| No transformer/LLM, ranker, graph or LSH in final path | CPU/deadline/no-GPU constraint, broad FTS failure, Agent 3 risks, and no measured result surpassing E3. | This is a deadline decision, not a general claim those methods can never work. |
| No negatives/class balancing | No classifier is trained. | “Negative sampling” is not an omitted step in a fitted model; it is not applicable to the current deterministic scorer. |

## Best artifact, output status and leaderboard

“Best measured local method” and “best validated submission” are not yet the same thing. rare_both is best by measured full-dev/full-holdout F0.5, but its complete test files are still running and therefore NOT VALIDATED. The best currently safe submission is the narrow fallback in best/:

| Fallback artifact | State |
| --- | --- |
| best/matching_results.tsv | Complete, validated, SHA-256 4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e |
| best/candidate_pairs.tsv | Complete, validated, SHA-256 5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8 |
| best/score_report.md | Dev/full-test counts, checker/official PASS, hashes and limitations |
| best/pipeline_baseline.py | Snapshot of production source used for fallback inference |

The completed output/*.tsv at this snapshot still match the fallback files; the primary is writing output/*.part. The fallback full checker reported PASS for 1,732,544 anchors, all 259,452 France rows, 6,371,588 valid same-country target IDs, 2,164,462 predictions contained in scored candidates, no duplicate list IDs, exact row coverage/order, mean 3.6776 candidates, P99 13, max 24. The supplied full validator reported PASS with its optional --check-ids OFF; the independent checker supplied the complete ID check. The primary 10k test fixture passed both checks, including official --check-ids, but its FULL validation status is NOT YET RUN. work/full_check_report.json still has fallback hashes, so do not package changed primary output against it.

NO LEADERBOARD SUBMISSION RECORDED by this project. Public score, private score, permitted upload count and any team upload outside this workspace are UNKNOWN / NOT VERIFIED.

## France distribution shift and candidate-efficiency frontier

France has 259,452 test anchors but zero labeled train/dev/holdout anchors. The actual proxy applies a single dev-frozen threshold to both observed countries and compares their holdout slices; it is NOT a leave-one-country-out threshold fit. Under E3 on holdout: US score 0.581115/recall 0.423757; India score 0.532503/recall 0.440219. This difference demonstrates observed country variability but does not quantify France accuracy. On full unlabeled fallback test, mean candidates were US 3.255, India 3.774, France 4.456; predicted matches/anchor 1.247, 0.992, 2.058. On unlabeled E3 10k test fixture, mean candidates were US 13.771, India 13.917, France 16.277; P95 26, 25, 27; empty-prediction rates 22.82%, 23.40%, 11.74%. All fixture France IDs/countries passed structure checks. Different France output rates could reflect different entity multiplicity or false matches. No France F0.5 can be measured. See research/france_shift.md.

The measured efficiency frontier is narrow (10k dev 0.488891 score, 0.291607 recall, 3.6837 mean/P99 13), rare-name (0.514004, 0.337545, 8.2505/P99 17), rare-address (0.538925, 0.398999, 9.0/P99 18), and combined (0.554542, 0.432535, 13.4954/P99 28) on the SAME balanced 10k dev anchors. Broad OR/BM25 has no meaningful score/recall measurement because it failed the runtime gate. The full E3 holdout score/recall gain came with 13.3683 mean candidates versus narrow 3.6298; the official efficiency weighting is UNKNOWN. Do not claim a total competition-ranking improvement from F0.5 alone.

## Resource profile, estimates and live anomaly

Measured index disk sizes at inspection: train_index.sqlite 3,657,859,072 bytes and test_index.sqlite 3,388,915,712 bytes. The narrow full output files are 50,787,199 bytes (matches) and 104,792,184 bytes (candidates); copies exist in best/. Free C: space was approximately 111 GB in an earlier live check; this is changing. No GPU or third-party runtime package is required. A virtual environment or package-manager configuration was not verified. psutil is optional and present enough for memory reporting, but its exact version was not measured.

Training/fitted-model time: NOT APPLICABLE. Measured index builds: 1,235 s train and 1,284 s test. Narrow full test inference: 1,856.2 s; complete independent check: 526.1 s. E3 full dev: 363.3 s/44,098, peak 245.6 MB; E3 holdout: 650.1 s/44,212, peak 245.4 MB. E3 mixed-country test 10k: 106.55 s, 93.9 anchors/s, peak 105.4 MB. The original conservative linear full E3 extrapolation was 1,732,544 / 93.9 ≈ 5.13 hours active time, with 1.5× slowdown reserve ≈7.7 hours; this was an ESTIMATE, not a full measured runtime. After warmup, active full inference ran substantially faster. Around 730k→740k, wall/monotonic time jumped by about 7,400 seconds while CPU advanced little, consistent with host sleep/pause but not independently diagnosed. Final full wall time must include this anomaly and should not be confused with active compute time. At first 20%-runtime checkpoint 340k anchors had completed in 1,904 s with ~131 MB current/~136 MB peak working set; continuation was justified.

## Known risks and failures

| Severity | Issue / observed evidence | Impact and current mitigation |
| --- | --- | --- |
| High | Candidate recall: E3 full holdout 0.430373; oracle macro F0.5 0.640236 versus actual 0.561627. | Missing true candidates cannot be rescued by scorer. Gated rare routes improved recall, but transliteration/renames/number errors remain. No more heavy research before delivery. |
| High | Primary full outputs not yet validated at snapshot. | Keep best/ narrow fallback; run full checker and official validator before any promotion. |
| High | France entirely unseen in labels; unlabeled France candidate/prediction rates differ. | Explicit France coverage/ID checks, no France accuracy claims, retain fallback. |
| Medium | Candidate-efficiency cost: mean 13.37 vs 3.63 on holdout; organizer ranking weighting unstated. | Document frontier honestly; no invented composite score. |
| Medium | True labeled numeric mismatches (2100/210, 17560/0017560) can trigger number-conflict penalty; same-building address evidence can create false positives. | Address/name corroboration and F0.5 threshold partly mitigate; inspect if a post-deadline version is developed. |
| Medium | Partial-field related records cross train/dev/holdout (34,145 same-name/diff-address; 4,631 same-address/diff-name proxies). | Exact duplicate groups stay together; avoid claiming complete leakage independence. |
| Medium | SQL LIMIT 6 without explicit ORDER BY may change byte-level candidates on another SQLite planner/version. | Tested environment and generated-index procedure documented; compare fixture and final hashes. |
| Medium | Primary run experienced an unexplained ~2h wall-clock pause with low CPU progress. | Process recovered; keep host awake/plugged in, monitor deadline. |
| Medium | Official validator default skips target ID existence, candidate file can be optional, and candidate-subset violation is a warning. | Mandatory independent disk-backed full checker is stricter. |
| Low/medium | Full target duplicate-record and train/test overlap audit pending. | audit_overlap.py exists; run one heavy job at a time after inference/validation, but do not endanger a valid package. |
| Low | Two output files replace sequentially after .part completion. | Never trust file existence alone; full check and SHA gate prevent mixed-pair packaging. |

No out-of-memory condition or swap pressure was observed. Broad FTS was a runtime failure, not a memory failure. No learned model or external data service was tried.

## Completion checklist and prioritized continuation

DONE / measured: dataset extracted; full row/country/missingness/multiplicity counts; train label/target/country integrity; fixed entity-level split and exact-group leakage check; train/test target indexes; macro F0.5 implementation/tests; complete validated narrow fallback and best/ preservation; five-agent research; E1/E2/E3 bounded experiments; full E3 dev and fixed-threshold holdout comparison; E3 real mixed-country 10k fixture with ID checks and official validator; research stop; primary full inference STARTED. Existing methodology/summary/architecture/build-spec drafts are not yet final.

P0 — absolutely required before shipping:

1. Observe the EXISTING PID 25348/session to successful exit; do not start a second full inference or touch output/*.part. The last progress at this document's initial snapshot was ~980k; get a fresh count. If it fails, keep or restore both validated fallback TSVs from best/.
2. After successful exit, confirm exactly two completed output TSVs and no .part remnants. Run the complete independent checker with --limit omitted and overwrite work/full_check_report.json with the new PRIMARY hashes. Require 1,732,544 anchors, 259,452 France, all IDs existing/same-country, match subset, unique lists/rows, exact order/coverage.
3. Run the supplied official validator against the COMPLETE test directory. Its default no-ID mode is acceptable only because step 2 verified every target ID. If ambiguous failure, allow at most 10 minutes debugging; document in research/validator_issue.md if needed and protect the rollback buffer.
4. Preserve the prior validated narrow fallback separately (e.g. fallback/), then copy the new verified pair/report/source to best/. If primary fails any gate, restore BOTH fallback TSVs to output/, rerun checker/official validator, and ship that pair.
5. Rerun eight unit/integration tests and bounded end-to-end fixture reproduction on the frozen final code; verify source SHA, documentation values and team placeholders. Update research/log.md, audit.md, france_shift.md, candidate_efficiency.md, Documentation_template.md, APPROACH_SUMMARY.md, FINAL_ARCHITECTURE.md and FINAL_BUILD_SPEC.md with actual full-run/check data.
6. Run package_submission.py only after output SHA-256 matches the NEW full check report. Verify ZIP CRC/manifest/structure. No portal upload has been done by this work.

P1 — requested, if time remains after safe primary validation: run audit_overlap.py to measure duplicate values and train/test ID overlap; add its factual output to research/audit.md and this handoff. Only one heavy local job at a time. P2 — optional and currently deferred: further ranker/LSH/graph/new scoring research; this is lower value than protecting a valid submission.

Hard rollback point: 2026-09-27 7:59 p.m. IST, four hours before the verified 11:59 p.m. deadline. No new heavy experiment begins inside that buffer. If primary remains incomplete or has unresolved validation issues then, restore the already validated fallback, validate/package it, and stop debugging the primary.

### Exact continuation commands from workspace root

Check the live process without disturbing it:

    Get-Process -Id 25348 | Select-Object Id,CPU,WorkingSet64,PeakWorkingSet64,StartTime
    Get-Item 'output/matching_results.tsv.part','output/candidate_pairs.tsv.part' | Select-Object Name,Length

Full new output check and organizer validator (ONLY AFTER the current predict process exits successfully):

    python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --report work/full_check_report.json
    python Dataset/student_resource/utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir Dataset/student_resource/dataset/test

Restore validated fallback if needed, using BOTH files and then rechecking:

    Copy-Item -LiteralPath 'best/matching_results.tsv' -Destination 'output/matching_results.tsv' -Force
    Copy-Item -LiteralPath 'best/candidate_pairs.tsv' -Destination 'output/candidate_pairs.tsv' -Force
    python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --report work/full_check_report.json
    python Dataset/student_resource/utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir Dataset/student_resource/dataset/test

Fresh reproduction from the supplied data (do not run a second full predict merely for proof unless it fits the deadline):

    python --version
    python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split train --index work/train_index.sqlite
    python code/business_entity_resolution/src/audit_data.py --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --manifest work/split_manifest.tsv --report work/audit_report.json
    python code/business_entity_resolution/src/pipeline.py evaluate --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --partition dev --variant rare_both --limit 100000 --config work/dev_rare_both_full.json
    python code/business_entity_resolution/src/pipeline.py evaluate --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --partition holdout --variant rare_both --fixed-threshold 0.65 --limit 100000 --config work/holdout_rare_both_full.json
    python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split test --index work/test_index.sqlite
    python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --variant rare_both --threshold 0.65

Fresh indexes built by the current code include FTS vocabulary metadata. For an older existing complete test index without it, first run:

    python code/business_entity_resolution/src/pipeline.py prepare-vocab --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite

Audit still pending, on a NEW audit DB path after the heavy inference/checker is done:

    python code/business_entity_resolution/src/audit_overlap.py --data-dir Dataset/student_resource/dataset --train-index work/train_index.sqlite --test-index work/test_index.sqlite --audit-db work/overlap_audit.sqlite --report work/overlap_report.json

Bounded reproduction and tests, with a SEPARATE output directory so the full pair is never overwritten:

    python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --variant rare_both --threshold 0.65 --limit 10000
    python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --limit 10000 --report work/repro_10k_check.json
    python code/business_entity_resolution/src/pipeline.py make-fixture --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --fixture-dir work/repro_10k_fixture
    python Dataset/student_resource/utils/validate_submission.py --matching work/repro_10k/matching_results.tsv --candidate work/repro_10k/candidate_pairs.tsv --test-dir work/repro_10k_fixture --check-ids
    python -m unittest discover -s code/business_entity_resolution/tests -v

Package only after updated full check:

    python code/business_entity_resolution/src/package_submission.py --workspace . --output amazon_ml_challenge_2026_submission.zip --check-report work/full_check_report.json

There is no model-install or training command: requirements.txt has no required third-party package and the final matcher is deterministic. The Python version/SQLite FTS5 are the environment requirements. Package script verifies full count/France/semantic flags and SHA-256 equality with the checker, includes outputs/source/docs/research, writes a MANIFEST.json, and ZIP-CRC checks the archive. It excludes multi-GB SQLite indexes and dataset TSVs. Do not hand-write a ZIP that bypasses its gates.

## Compliance and “DO NOT BREAK THESE”

| Check | Present evidence and honest status |
| --- | --- |
| External business data/API/geocoding/entity-resolution service | PASS by source inspection for the implemented pipeline: no network lookup, enrichment or third-party matching call; only supplied TSVs and derived indexes are read. |
| External model license / <=8B parameters | No external or pretrained model weights are loaded; these model-weight constraints are NOT APPLICABLE to the current deterministic scorer. An overall organizer compliance determination is not independently certified. |
| Candidate file semantics | PASS on complete narrow fallback and E3 10k fixture; full E3 PENDING. predict writes exactly IDs returned by candidates and scored by pair_scores. |
| Submission schema, coverage, France, target IDs, duplicates, match subset | PASS on complete fallback; PASS on bounded E3 fixture; complete E3 NOT YET RUN at snapshot. |
| Leaderboard score / final rank | UNKNOWN; NO LEADERBOARD SUBMISSION RECORDED here. |

DO NOT BREAK THESE:

- Preserve TSV delimiter TAB and IDs as text; addresses contain commas. Empty match/candidate fields must remain truly empty, not “nan” or a null token. There is one output row per test S1, not one row per candidate pair.
- Do not split Source 1 into random candidate-pair rows; macro F0.5 and validation are Source 1 entity-level. Do not use holdout to choose another threshold.
- Never report candidate IDs that were not actually scored, or omit scored IDs from candidate_pairs.tsv. Require final matches ⊆ candidates. Allow zero and multiple matches, including multiple within one vendor.
- Do not skip France because it is absent from labeled train. Country remains an open string; full France coverage is 259,452 anchors.
- Do not trust official validator alone: optional ID existence is OFF by default and candidate-subset problems can be warnings. Run the independent full checker.
- Do not trust a file merely because it exists. output/*.tsv are fallback until the primary .part files finish; a two-file replace can leave mixed files if interrupted. work/full_check_report.json currently hashes fallback output.
- Do not remove/rebuild the current test index or edit production pipeline.py while live PID 25348 uses it. An incomplete derived index is rejected by its completion marker. Do not launch another large scan while full inference or full checker runs.
- Preserve best/ until a replacement passes both full checks. There is no Git commit to recover from. If the primary fails, restore BOTH validated fallback files and regenerate the check report before packaging.
- Keep the computer awake/plugged in. A large wall-clock pause has already occurred; its exact cause was not verified.
- Do not claim France accuracy, private leaderboard performance, an official efficiency formula, measured duplicate-overlap counts not yet audited, or a trained model that does not exist.

## Final state snapshot (at the document's initial inspection)

CURRENT BEST APPROACH: rare_both gated rare-address + rare-name retrieval and deterministic scorer, threshold 0.65, selected by full dev and fixed-threshold holdout; complete test run in progress.

CURRENT BEST SCORE: local full holdout macro F0.5 0.5616271143. Public/private score NOT MEASURED.

CURRENT CANDIDATE RECALL: local full holdout link recall 0.4303728929.

CURRENT CANDIDATE COUNT: local full holdout mean 13.3683, median 13, P90 25, P95 26, P99 28, max 31. E3 10k test fixture mean 14.2118; full E3 test count PENDING.

CURRENT RUNTIME: E3 10k real-test 106.55 s; complete E3 test runtime PENDING. Full run has experienced an unexplained ~2h wall pause; do not use its interim overall rate as active throughput.

CURRENT MEMORY: E3 full holdout peak 245.4 MB; real-test 10k peak 105.4 MB; live full process roughly 136 MB peak at checked checkpoint, subject to change.

CURRENT SUBMISSION STATUS: validated complete narrow fallback in best/ and completed output/*.tsv at snapshot; no final ZIP or leaderboard upload recorded. E3 full .part files still running.

CURRENT VALIDATION STATUS: narrow full independent checker PASS and supplied official validator PASS; E3 10k independent and official with ID mode PASS; E3 full checker/official NOT YET RUN.

CURRENT BIGGEST RISK: a true match absent from the bounded candidate union (only ~43% link recall), plus unknown France accuracy and candidate-efficiency weighting; immediate delivery risk is primary full validation pending.

CURRENT MOST IMPORTANT NEXT TASK: let the existing primary process finish, then run full independent check and supplied validator without disrupting best/.

CURRENT FALLBACK: best/matching_results.tsv and best/candidate_pairs.tsv at narrow threshold 0.68, with best/score_report.md and best/pipeline_baseline.py; complete hashes and restore commands above.
