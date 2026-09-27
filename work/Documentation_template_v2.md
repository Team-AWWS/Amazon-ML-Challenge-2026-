# ML Challenge 2026: Business Entity Resolution Solution

## Method

The solution uses only supplied competition data and CPU-based SQLite retrieval. Target records are normalized and indexed by country, source, name, and address. For each Source 1 record, the pipeline unions bounded exact name/address matches with the rarest normalized name token, rarest address token, and a distinct rare numeric address token when available. Tokens with corpus frequency above 500 are excluded from posting retrieval; a name/address conjunction handles selective common-token cases. Candidates are country-scoped, deduplicated, fast-ranked by normalized token overlap and number agreement, and capped at 36. `candidate_pairs.tsv` contains exactly the retained records scored by the matcher.

The deterministic matcher combines name and address token overlap, character trigram similarity, missing-address handling, and address-number agreement/conflict. The decision threshold was selected on the fixed development split and then frozen before holdout evaluation.

## Validation

The frozen configuration used `max_df=500`, one rare route per text field plus a numeric-address route, a 36-candidate cap, and threshold 0.75.

On 10,000 labeled development anchors it achieved macro F0.5 0.734561, candidate recall 0.878053, and 30.07 candidates per anchor. On the untouched 44,212-anchor holdout it achieved macro F0.5 0.746470, candidate recall 0.882430, candidate-oracle macro F0.5 0.953387, and 30.03 candidates per anchor. The previous validated baseline scored 0.561627 on that holdout.

Full test inference generated 1,732,544 rows, 53,452,192 candidate links, and 4,480,505 predicted links. Streaming validation checked every candidate ID against the test index and country, Source 1 coverage/order, per-row uniqueness, and prediction subset semantics. The supplied validator also passed for the matching output. No test labels or external data were used.
