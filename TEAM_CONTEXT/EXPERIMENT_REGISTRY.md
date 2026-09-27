# Experiment registry

All accuracy figures below are **labeled local** results; none is a leaderboard score. Primary evidence: `research/log.md`, `research/candidate_efficiency.md`, and machine-readable `work/dev_*.json`, `work/holdout_*.json`.

| Stage | Dataset/gate | F0.5 | Link candidate recall | Mean candidates | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| Broad FTS5 OR/BM25 | <1k dev, >100 s | UNKNOWN | UNKNOWN | UNKNOWN | Stopped: >47 h projected full run |
| Narrow exact | Full dev 44,098 | 0.497433 | 0.297894 | 3.6499 | Preserve fallback, threshold 0.68 |
| Rare name | Same balanced 10k dev | 0.514004 | 0.337545 | 8.2505 | Research only |
| Rare address | Same balanced 10k dev | 0.538925 | 0.398999 | 9.0000 | Research only |
| Combined rare address + name | Same balanced 10k dev | 0.554542 | 0.432535 | 13.4954 | Advance to full dev |
| Combined `rare_both` | Full dev 44,098 | 0.560165 | 0.431252 | 13.3885 | Freeze threshold 0.65 |
| Narrow fallback | Untouched holdout 44,212 | 0.499692 | 0.298817 | 3.6298 | Validated fallback |
| Combined `rare_both` | Same holdout, fixed 0.65 | 0.561627 | 0.430373 | 13.3683 | Promote after full-file checks |

The holdout gain over narrow is 0.061935 absolute macro F0.5 (12.39% relative) at roughly 3.68 times the mean candidates. The official efficiency weighting is unspecified. The full-test run is unlabeled, so it has no measured F0.5 or true candidate recall. The proposed ranker, LSH, and graph propagation were **not run**. The five-agent reasoning/decision is recorded in `research/agent_reviews.md`; it is analysis, not a separate model implementation.
