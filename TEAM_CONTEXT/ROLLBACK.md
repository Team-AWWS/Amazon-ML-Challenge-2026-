# Rollback procedure

The hard rollback buffer starts 2026-09-27 **19:59 IST**, four hours before the 23:59 IST ML-round deadline. No new heavy experiment belongs inside it. This file describes recovery; it does **not** authorize overwriting the present validated outputs during this documentation task.

Current primary is `output/` and `best/` at `rare_both` threshold 0.65. The validated exact-only fallback is `fallback/` at `narrow` threshold 0.68. Both TSVs must move as a pair; never mix a primary match file with fallback candidates. Their exact hashes are in `SUBMISSION_STATE.md`.

If the primary suffers an unresolved integrity/correctness failure, first preserve its two files and ZIP under clearly named separate backup paths. Verify the fallback's two hashes against `SUBMISSION_STATE.md`. Copy **both** fallback TSVs into a *new* output directory, then run the complete independent checker and official validator against that directory using the full test set. Confirm every ID, country, row, and candidate-subset condition. Only then designate the fallback as current and make a new package through `package_submission.py` with a matching newly generated check report. That new ZIP requires its own manifest, CRC, SHA-256, and validation evidence; do not reuse the primary ZIP hash or claim it remains verified.

If any file is missing or its hash differs, stop and investigate. Git intentionally does not contain the large preserved TSVs; retrieve an exact known-good local/approved-channel copy, or regenerate only if enough time remains for full inference and validation. Regeneration is a last resort, not an assumed quick rollback.
