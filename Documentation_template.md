# ML Challenge 2026: Business Entity Resolution Solution

**Team Name:** [Team name]  
**Team Members:** [Team members]  
**Submission Date:** September 27, 2026

## 1. Executive Summary

We resolve Source 1 businesses against the supplied Source 2 and Source 3 records with a CPU-feasible, disk-backed, country-scoped retrieval and pair-scoring pipeline. The validated fallback uses independent exact normalized-name and normalized-address routes. The selected primary adds document-frequency-gated single-token name and address retrieval only when exact blocking is sparse. Every retrieved record is scored by name/address token and character similarity plus address-number agreement. The primary is promoted only if its complete outputs pass all structural checks; no external business data or pretrained model is used.

## 2. Methodology

### 2.1 Problem Analysis

The train set contains 2,206,821 Source 1 anchors and 10,320,219 target records across US and India. Ground truth has 7,638,365 links, 123,247 zero-match anchors, and up to 11 target matches per anchor. The test set has 1,732,544 Source 1 anchors, including 259,452 from France, a country absent from labeled training. Missing target addresses, misspellings, reordered components, transliteration, unrelated trade names at matching addresses, and legal suffix variants make exact equality an incomplete retrieval strategy. The full train integrity audit found no missing/extra labels, unknown target IDs, duplicate IDs in label lists, or cross-country labeled links. Further duplicate-record and train/test overlap checks are documented in `research/audit.md`.

### 2.2 Solution Strategy

**Approach type:** Multi-route blocking plus deterministic pair scoring.  
**Core design:** Keep target lookup disk-backed and country-scoped, measure candidate recall separately from the final entity-level score, and preserve a complete validated baseline before promoting a variant. Unicode normalization retains Indic and other non-Latin scripts; the original supplied TSV records remain available for reproduction. The stable Source 1 split hashes normalized name/address groups so exact duplicate groups stay together: train 2,118,511, dev 44,098, holdout 44,212. A full leakage audit found zero exact normalized name/address groups crossing partitions, though partial-field related-record risks remain.

## 3. Candidate Generation (Blocking)

The baseline indexes normalized target names and addresses in SQLite. For each Source 1 anchor, it retrieves bounded exact-name and exact-address candidates independently from Source 2 and Source 3, within the same country. The primary adds one rare address token and one rare name token when fewer than eight exact candidates are found. Terms must occur in 2–1,000 supplied target records; each country/source-scoped FTS5 query returns at most six rows, without an expensive BM25 sort. Candidate IDs are deduplicated and every retained candidate is scored; `candidate_pairs.tsv` contains exactly those scored IDs. An unrestricted four-route OR/BM25 query failed an early CPU runtime gate and is not used.

On the full 44,098-anchor dev split, exact blocking recovered 29.7894% of labeled links; combined rare-token blocking recovered **43.1252%**. The primary produced a mean of **13.3885** candidates per anchor (median 13, P90 25, P95 26, P99 28, max 31), versus 3.6499 for narrow exact blocking. Its candidate-limited oracle macro F0.5 was 0.639304, versus narrow's 0.526975. Complete unlabeled test inference later scored **24,702,044** candidates across **1,732,544** anchors (mean 14.2577, median 13, P95 26, maximum 31); independent full checks and the supplied validator passed. Test candidate recall remains unknown without labels.

## 4. Matching Model

**Features:** normalized-name token Jaccard/containment; normalized-address token Jaccard/containment; character-trigram Dice similarity; address-number overlap/conflict; missing-address handling.  
**Model type:** Deterministic feature-weighted scorer for both pipelines; no pretrained model or external enrichment.  
**Threshold selection:** Maximize exact per-Source-1 macro F0.5 on dev only, including the empty-truth/empty-prediction case. The selected primary threshold is **0.65**; the preserved narrow fallback uses **0.68**. Holdout was evaluated once at these frozen thresholds and did not select features or thresholds.

## 5. Results and Error Analysis

| Local measurement | Narrow fallback | Combined primary |
| --- | ---: | ---: |
| Full-dev entity-level macro F0.5 (44,098 anchors) | 0.497433 | **0.560165** |
| Dev candidate recall (labeled links) | 0.297894 | **0.431252** |
| Candidate-oracle macro F0.5 | 0.526975 | **0.639304** |
| US dev macro F0.5 / candidate recall | 0.536236 / 0.330868 | **0.579133 / 0.424639** |
| India dev macro F0.5 / candidate recall | 0.439013 / 0.248280 | **0.531608 / 0.441203** |
| Full holdout macro F0.5 (44,212, frozen thresholds) | 0.499692 | **0.561627** |
| Holdout candidate recall | 0.298817 | **0.430373** |
| Dev elapsed time / peak process working set | 252.1 s / 164.3 MB | 363.3 s / 245.6 MB |

At the fixed 0.65 threshold on all 44,212 labeled holdout anchors, the
combined primary had 61,129 true-positive links, 13,038 false-positive links,
and 92,159 false-negative links. Micro precision was 0.824208 and micro
prediction recall was 0.398785. By country, US TP/FP/FN were
36,566/6,367/55,114 (precision 0.851699, prediction recall 0.398844), and
India were 24,563/6,671/37,045 (precision 0.786419, prediction recall
0.398698). These link-level diagnostics supplement, but do not replace, the
entity-level macro F0.5 score. No test or France labels were supplied.

The main known weakness remains false negatives from candidate exclusion: even the improved route retrieves only ~43% of labeled links, and typos, transliterations, missing/partial addresses, and trade-name changes may remain uncovered. Shared-building and common-token candidates can create false positives, which F0.5 penalizes. The lower US-versus-India score gap and completely unlabeled France test country caution against assuming private-test transfer. The official candidate-efficiency weighting is unspecified, so the primary's ~3.7× larger candidate lists may affect the competition score despite its 12.4% relative holdout F0.5 improvement.

**Full-test output validation:** The complete narrow fallback passed the supplied official validator and separate full target-ID, country, row-coverage, duplicate, France-coverage, and match-subset checks, and remains in `fallback/`. The promoted combined primary passed the same complete checks, plus a strict TSV shape/empty-field/hash/anomaly scan. It covered all 1,732,544 test anchors, including 259,452 France anchors; scored 24,702,044 actual candidates (mean 14.2577, median 13, P90 25, P95 26, P99 28, max 31); and predicted 3,327,344 IDs. Full inference took 13,737.2 seconds wall time including an observed host pause and reached 136.2 MB peak process working set. Its full checker took 1,496.8 seconds. Test macro F0.5, precision, prediction recall, FP/FN, and true candidate recall are **not measurable** because no test labels were supplied.

## 6. Conclusion

The disk-backed combined rare-token route is the measured primary, with a complete validated exact-route fallback. Both are reproducible on CPU from the supplied records. The selected architecture, candidate-efficiency tradeoff, and measured experiments are recorded separately in `FINAL_ARCHITECTURE.md`, `research/candidate_efficiency.md`, and `research/log.md`. No private-test or France accuracy claim is made.

## Appendix A. Code Artefacts

All runtime source is under `code/business_entity_resolution/src/`; `pipeline.py` is the indexing, validation, inference, and output entry point. `README.md` gives exact commands, and `requirements.txt` documents the standard-library runtime. Large SQLite indexes are generated from the supplied data and excluded from the final ZIP. No GPU, external business lookup, geocoding, entity-resolution service, or externally trained model is required.

## Appendix B. Additional Results

See `research/audit.md`, `research/candidate_efficiency.md`, `research/france_shift.md`, and `research/log.md` for split integrity, candidate frontiers, shift limitations, and experiment contracts.
