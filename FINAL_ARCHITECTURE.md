# Final architecture decision

Status: **combined rare-token primary promoted after complete validation**. The complete narrow fallback is preserved separately in `fallback/`.

Preserved fallback: disk-backed **exact** name/address blocking, deterministic token/character/address-number scoring, dev threshold 0.68, and fully validated outputs in `fallback/`. The initial broad four-route FTS5 path failed its runtime gate and is not part of the fallback. No private-test performance is claimed.

Agent 5's final measured recommendation selected the combined rare-address + rare-name route as the **promoted primary**, with exact routes first and rare-token routes only when fewer than eight exact candidates are found. Each rare token must appear in 2–1,000 target records, each query is country/source scoped and returns at most six records, and every returned candidate is deterministically scored. The dev-selected threshold is frozen at **0.65**. The ranker, full n-gram LSH, unchanged broad FTS, and graph propagation are deferred for the deadline.

## Decision and evidence

| Fixed identity-level split | Narrow fallback | Combined primary |
| --- | ---: | ---: |
| Full dev, 44,098 anchors: macro F0.5 | 0.497433 | **0.560165** |
| Full dev: link candidate recall | 0.297894 | **0.431252** |
| Untouched holdout, 44,212 anchors: macro F0.5 | 0.499692 | **0.561627** |
| Holdout: link candidate recall | 0.298817 | **0.430373** |
| Holdout: mean candidates / P99 | 3.63 / 13 | 13.37 / 28 |

The combined route gained 0.061935 holdout macro F0.5 (12.39% relative) with thresholds fixed on dev, at 3.68× mean candidate count. The official candidate-efficiency weighting is unknown, so this is not a claim of total competition-score improvement. The complete primary run processed 1,732,544 anchors and scored 24,702,044 candidates in 13,737.2 seconds wall time, including an observed host pause, with 136.2 MB peak working set. The independent full ID/country/subset checker, separate strict TSV/empty-field/hash/anomaly scan, and supplied official validator all passed. The observed candidate maximum was 31. Test labels do not exist, so full-test F0.5 and true candidate recall are not measurable.

## Known weaknesses and rollback

Unseen France labels, transliteration, missing addresses, and renamed businesses may reduce recall. Complete France coverage and similar fixture/full output rates confirm structural behavior, not accuracy. The complete validated baseline is in `fallback/`; restore it to `output/` only if the primary develops a new correctness problem.

**Hard rollback point:** September 27, 2026, **7:59 p.m. IST** (four hours before the 11:59 p.m. IST deadline). No new heavy experiment starts inside that buffer. The promoted primary was validated before this point; preserve both primary and fallback artifacts through final delivery.
