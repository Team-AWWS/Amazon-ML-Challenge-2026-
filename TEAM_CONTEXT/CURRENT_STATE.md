# Current state

As of 2026-09-27, the submission candidate is the already validated `rare_both` run. No experiment, model change, output regeneration, or leaderboard upload was made during this packaging pass.

| Item | Verified local state / source |
| --- | --- |
| Primary | `code/business_entity_resolution/src/pipeline.py`, variant `rare_both`, frozen threshold 0.65; source SHA-256 `7d4b7814968effb25663e2247c55492f343b546a80216ed01c924f5e054d2b1e` |
| Fallback | Variant `narrow`, threshold 0.68; preserved local files and report in `fallback/` |
| Fixed Source 1 split | Train 2,118,511; dev 44,098; holdout 44,212 (`work/audit_report.json`) |
| Primary dev | Macro F0.5 0.5601653910; link candidate recall 0.4312524062 (`work/dev_rare_both_full.json`) |
| Primary untouched holdout | Macro F0.5 0.5616271143; link candidate recall 0.4303728929 (`work/holdout_rare_both_full.json`) |
| Full test | 1,732,544 Source 1 rows, 24,702,044 scored candidates, 3,327,344 predicted IDs (`work/full_check_report.json`) |
| Current output validation | Independent complete checker, strict scan, and official validator passed for the recorded hashes; see `SUBMISSION_STATE.md` |
| ZIP | Local `amazon_ml_challenge_2026_submission.zip`, SHA-256 `91fe000809e29459fb75f3164b787d39b5d5cb8e8e3a6ec2f21a314f1a38b194` |
| Portal upload / private score | `UNKNOWN`; no upload was performed or recorded by this work |

The verified ZIP and TSVs are deliberately not stored in Git. Git carries runnable code, reports, manifests of identity, and documentation. `HANDOFF.md` and `PROJECT_HANDOFF_2026-09-26.md` are historical snapshots and contain obsolete in-progress state; use this directory for the current state.
