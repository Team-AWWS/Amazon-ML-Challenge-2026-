# Final build specification

Status: the `rare_both` primary has complete validated test outputs in `output/` and `best/`. The independently preserved narrow fallback is in `fallback/`.

## Inputs

The supplied `dataset/train/` and `dataset/test/` TSVs only. No external business lookup, geocoding, enrichment service, GPU, or pretrained model is used by either pipeline.

## Pipeline

1. Normalize Unicode/case/spacing/punctuation while preserving non-Latin scripts and original source records.
2. Build a disk-backed SQLite records and FTS5 index for Source 2/3 within each split. The preserved fallback uses only exact B-tree routes. The primary additionally uses FTS5 single-token lookup with an index-derived document-frequency gate; the vocabulary is metadata over the supplied target index, not external text.
3. Retrieve independent exact name/address routes for each target source and country. When fewer than eight exact candidates are found, the primary queries one rare address token and one rare name token (document frequency 2–1,000), each separately for Source 2/3, with six results per route. Deduplicate IDs and cap the list at 36. The initial broad OR/BM25 FTS5 route failed the runtime gate and is not used.
4. Score each actual candidate using token overlap, character trigrams, and address-number agreement.
5. Choose a threshold by exact Source 1 entity-level macro F0.5 on the fixed development partition.
6. Write the two complete test output TSVs atomically from temporary files, then run the official validator and separate complete target-ID/country/subset/coverage checks.

## Environment and reproducibility

Tested on Python **3.14.2**, SQLite **3.50.4** with FTS5, CPU-only. Inference uses no required third-party Python package; `psutil` is optional for resource reporting. See `code/business_entity_resolution/README.md` for exact commands. Large SQLite indexes and temporary files are outside the final submission ZIP. The ZIP contains code, outputs, and the filled methodology template.

## Measured requirements and final selected commands

Promoted primary: `--variant rare_both --threshold 0.65`. On all 44,098 dev anchors it scored macro F0.5 **0.560165**, link recall **0.431252**, mean 13.3885 candidates; on all 44,212 untouched holdout anchors, fixed threshold 0.65 scored **0.561627**, recall **0.430373**, mean 13.3683. Complete unlabeled test inference processed **1,732,544** anchors, including **259,452 France**, and scored **24,702,044** candidates (mean **14.2577**, median **13**, P90 **25**, P95 **26**, P99 **28**, max **31**). It predicted **3,327,344** IDs in **13,737.2 seconds** wall time including an observed host pause, at **136.2 MB** peak working set. The independent full checker, strict output/hash/anomaly scan, and supplied validator passed. Matching/candidate SHA-256 are `df1415117c62d350ca33d51bffa678934f1f2c6282997fb0103087995178ff05` and `3d5b2e71e32e11f168d22725c03757f62b0853147e7f3ba7cfa0f4bf7cc3f9c5`. Test accuracy and true candidate recall are **NOT MEASURABLE** without labels.

Fallback: `--variant narrow --threshold 0.68`. Full dev macro F0.5 **0.497433**, recall **0.297894**, mean 3.6499; full untouched holdout fixed-threshold macro F0.5 **0.499692**, recall **0.298817**, mean 3.6298. Both complete fallback TSVs passed the independent full target-ID/country/subset/coverage checker and supplied validator, and are preserved with hashes in `fallback/`. Train and test indexes took 1,235 and 1,284 seconds respectively. Restore exact files from `fallback/` only if the primary develops an unresolved correctness problem.
