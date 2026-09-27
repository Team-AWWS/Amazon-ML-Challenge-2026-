# Validated baseline score and integrity report

This is the preserved fallback submission. It uses only supplied challenge records, a disk-backed SQLite target index, exact normalized name/address routes, deterministic similarity, and the dev-selected threshold 0.68. No leaderboard upload has been attempted.

## Local labeled development result

- Fixed Source 1 entity-level dev partition: 44,098 anchors (US 26,498; India 17,600).
- Macro F0.5: **0.4974333241**; candidate-link recall: **0.2978942766**; candidate-oracle macro F0.5: **0.5269753450**.
- US macro F0.5 0.536236; India 0.439013. Holdout had not been used when this baseline was chosen.
- Mean candidates 3.6499; median 2; P90/P95 12; P99 13; max 21.

## Complete test output

- 1,732,544 Source 1 rows, including **all 259,452 France rows**.
- 6,371,588 candidate pairs actually scored; 2,164,462 predicted matches.
- Mean candidates 3.6775908722; median 2; P90/P95 12; P99 13; max 24.
- Inference runtime 1,856.2 seconds (~30.9 minutes). Independent complete check runtime 526.1 seconds.
- Every target ID exists and has the matching country. Predicted IDs are a subset of scored candidate IDs. No duplicate rows or listed IDs; Source 1 coverage and order are exact.
- Supplied official validator: **PASS — no blocking issues found** on the complete files. Its optional ID-existence mode was off; the independent full checker supplied that check.

## SHA-256

- `matching_results.tsv`: `4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e`
- `candidate_pairs.tsv`: `5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8`

The low candidate recall is this baseline's main weakness. Preserve these validated files until a fully checked replacement shows a meaningful dev improvement and meets runtime constraints.
