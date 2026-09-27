# Validated primary: rare_both, threshold 0.65

Promotion evidence, September 26, 2026. This deterministic CPU pipeline uses
only the supplied challenge records. No leaderboard upload has been attempted.

## Labeled local evaluation

| Fixed Source 1 split | Macro F0.5 | US F0.5 | India F0.5 | Link candidate recall | Candidate oracle F0.5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full dev, 44,098 entities; threshold selected here | 0.5601653910 | 0.5791332942 | 0.5316079196 | 0.4312524062 | 0.6393037592 |
| Untouched holdout, 44,212 entities; threshold fixed at 0.65 | 0.5616271143 | 0.5811150338 | 0.5325029881 | 0.4303728929 | 0.6402356128 |

The validated narrow fallback scored 0.4996922783 macro F0.5 on that same
holdout at its dev-fixed threshold 0.68. The primary gain is 0.0619348360
absolute, or 12.39% relative, with about 3.68 times as many candidates.
The fixed-threshold holdout was rerun solely to measure confusion counts. Its
macro F0.5 and candidate recall matched the saved holdout report. These are
**micro** precision and prediction recall across labeled links; the challenge
score remains entity-level macro F0.5.

| Labeled holdout slice | TP | FP | FN | Micro precision | Micro prediction recall | Macro F0.5 | Link candidate recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Overall, 44,212 entities | 61,129 | 13,038 | 92,159 | 0.824208 | 0.398785 | 0.561627 | 0.430373 |
| US, 26,488 entities | 36,566 | 6,367 | 55,114 | 0.851699 | 0.398844 | 0.581115 | 0.423757 |
| India, 17,724 entities | 24,563 | 6,671 | 37,045 | 0.786419 | 0.398698 | 0.532503 | 0.440219 |

Candidate recall above is link recall on labeled local data, not a test-set
metric. The test set has no France labels.

## Complete unlabeled test inference and validation

- Source 1 entities: 1,732,544 (US 663,106; India 809,986; France 259,452).
- Candidate IDs actually scored: 24,702,044; predicted target IDs: 3,327,344.
- Candidate count per entity: mean 14.257672, median 13, P90 25, P95 26,
  P99 28, maximum 31. The algorithmic cap is 36; the observed maximum is
  consistent with the tighter 31-candidate route structure.
- Empty match fields: 367,629; empty candidate fields: 42,487. The strict
  full-file scan confirmed these are genuinely empty TSV cells, with no null
  placeholders or malformed rows.
- Empty-prediction rates: US 21.9344%, India 23.7337%, France 11.5401%.
  These track the 10,000-anchor mixed-country fixture (22.82%, 23.40%,
  11.74%, respectively); no anomaly gate fired.
- Inference elapsed time: 13,737.2 seconds, including a roughly two-hour
  observed host pause. Peak process working set: 136.2 MB.
- Complete independent target-ID, same-country, coverage, uniqueness, and
  match-subset checker: **PASS**, 1,496.8 seconds. Its report was generated
  after the full primary output and its SHA-256 hashes match the files.
- Separate strict shape/source-count/empty-field/anomaly scan: **PASS**.
- Supplied official validator on the complete test files: **PASS**, exit 0.
  Its memory-heavy optional ID mode was disabled; the independent full
  checker verified all candidate IDs against the disk-backed test index.

The test set has no labels. Its macro F0.5 (overall or by country), precision,
prediction recall, FP, FN, and true candidate recall are **not measurable**.
No France accuracy or private-test score is claimed.

## SHA-256 of validated primary output

- `matching_results.tsv`: `df1415117c62d350ca33d51bffa678934f1f2c6282997fb0103087995178ff05`
- `candidate_pairs.tsv`: `3d5b2e71e32e11f168d22725c03757f62b0853147e7f3ba7cfa0f4bf7cc3f9c5`
- Frozen inference source `pipeline.py`: `7d4b7814968effb25663e2247c55492f343b546a80216ed01c924f5e054d2b1e`

The original validated narrow files and source are preserved separately in
`fallback/`. The official weighting of candidate efficiency is unknown.
