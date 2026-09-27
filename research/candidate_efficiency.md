# Candidate-efficiency frontier

Status: bounded variant frontier, complete dev and holdout comparisons, and complete unlabeled test candidate statistics measured. The selected combined primary passed full-output validation.

Measure candidate recall separately from macro F0.5. For each tested variant record candidate count mean, median, P90, P95, P99, maximum, runtime, and peak memory. The official challenge material does not specify a numeric weighting between candidate efficiency and F0.5; no such weighting is assumed here.

| Variant | Candidate recall | Mean | Median | P90 | P95 | P99 | Max | Macro F0.5 | Runtime | Peak memory |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Narrow exact-name/address fallback (10k dev) | 0.291607 | 3.6837 | 2 | 12 | 12 | 13 | 19 | 0.488891 | 83.9 s / 10k anchors | 113.5 MB |
| Broad four-route FTS5 (early killed) | not measured | not measured | not measured | not measured | not measured | not measured | ≤64 by design | not measured | >100 s / <1k anchors | ~100 MB at stop |
| Narrow exact-name/address fallback (full 44,098 dev) | 0.297894 | 3.6499 | 2 | 12 | 12 | 13 | 21 | 0.497433 | 252.1 s / 44,098 anchors | 164.3 MB |
| Rare-name plus narrow (10k dev) | 0.337545 | 8.2505 | 11 | 14 | 15 | 17 | 19 | 0.514004 | 110.5 s / 10k anchors | 123.6 MB |
| Rare-address plus narrow (10k dev) | 0.398999 | 9.0000 | 12 | 14 | 16 | 18 | 19 | 0.538925 | 82.4 s / 10k anchors | 126.5 MB |
| Rare-address plus narrow (42,600 dev; US capped at 25,000) | 0.398986 | 8.9478 | 12 | 14 | 16 | 18 | 19 | 0.544346 | 462.9 s / 42,600 anchors | 205.5 MB |
| Rare-address + rare-name plus narrow (10k dev) | 0.432535 | 13.4954 | 13 | 25 | 26 | 28 | 31 | 0.554542 | 102.2 s / 10k anchors | 134.6 MB |
| Rare-address + rare-name plus narrow (full 44,098 dev) | 0.431252 | 13.3885 | 13 | 25 | 26 | 28 | 31 | 0.560165 | 363.3 s / 44,098 anchors | 245.6 MB |

The broad row is an early runtime gate, **not** a full candidate-frontier measurement; no recall or score is inferred from it. The 42,600-anchor run omitted 1,498 US dev anchors because the benchmark's per-country cap was half the requested 50,000 limit; it is not mislabeled as the complete 44,098-anchor dev split. The combined route adds 0.015617 macro F0.5 versus address-only on the same 10k sample, but increases mean candidates by 4.4954 and runtime by 24%. The test distribution includes France, which has no training labels, so this measured dev frontier is not a private-test guarantee. No official score/efficiency weighting is invented.

For the selected combined route, the untouched full holdout at fixed threshold 0.65 scored macro F0.5 **0.561627**, link recall **0.430373**, mean 13.3683 candidates, median 13, P90 25, P95 26, P99 28, max 31, in 650.1 seconds at 245.4 MB peak working set. The narrow fallback on the identical holdout scored 0.499692, recall 0.298817, mean 3.6298, median 2, P90/P95 12, P99 13, max 20, in 261.6 seconds at 164.0 MB. This confirms a score/recall gain but a significant efficiency cost. On an unlabeled mixed-country 10k **test** fixture, combined retrieval produced mean 14.2118 candidates, median 13, P90 25, P95 26, P99 28, max 31, and ran in 106.55 seconds at 105.4 MB peak; no test candidate recall or F0.5 can be computed without labels.

On the **complete unlabeled test**, the promoted combined route scored **24,702,044 actual candidates** across 1,732,544 anchors: mean **14.2577**, median **13**, P90 **25**, P95 **26**, P99 **28**, maximum **31**. Full inference took **13,737.2 seconds wall time including an observed host pause** and reached **136.2 MB peak process working set**. For comparison, the validated narrow fallback produced 6,371,588 actual test candidates: mean 3.6776, median 2, P90/P95 12, P99 13, max 24, in 1,856.2 seconds. Test candidate recall and macro F0.5 are **NOT MEASURABLE** without test labels. The organizer's candidate-efficiency weighting remains unspecified, so the local F0.5 gain does not prove a higher combined competition score.
