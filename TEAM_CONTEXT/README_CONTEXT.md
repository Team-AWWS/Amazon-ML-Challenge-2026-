# Team context: start here

Snapshot: 2026-09-27, Asia/Kolkata. This directory is a knowledge transfer, not a new model run. The competition ML round ends 2026-09-27 23:59 IST; the final four-hour delivery buffer begins 19:59 IST. Check the portal independently before upload.

Read in this order: `README_CONTEXT.md` → `../FINAL_TEAM_HANDOFF.md` → `MODEL_REGISTRY.md` → `ARCHITECTURE.md` → `REPRODUCTION.md`. Then use the specialized files for validation, submission, France, issues, and rollback.

**Current choice:** `rare_both`, a deterministic CPU pipeline with exact name/address retrieval plus gated rare address/name token retrieval, threshold **0.65**. It produced complete validated outputs in local `output/` and `best/`. The independent exact-only `narrow` fallback at threshold **0.68** is preserved in local `fallback/`. The Git repository intentionally excludes the large output TSVs, ZIP, raw dataset, and SQLite indexes. Teammates need the supplied dataset and the validated artifact transferred separately, with hashes checked before use.

**Evidence discipline:** The current output and ZIP hashes were re-read from disk during this packaging pass and matched `work/release_integrity_2026-09-26.md`. Local scores come from checked-in JSON reports; test accuracy is `UNKNOWN` because test labels do not exist. A report of `PASS` only applies to the exact files identified by its hashes. See `SUBMISSION_STATE.md` and `VALIDATION_CHECKLIST.md` before anyone uploads or regenerates anything.

The remote `main` branch had only `README.md` at inspection. No separate teammate model implementation was discoverable there or in this workspace. That is an inventory result, not a claim that teammates have done no work elsewhere. Ask each teammate for their branch, path, or artifact before recording a model as present.
