# Release artifact integrity gate — September 26, 2026

Status: **VERIFIED** at approximately 23:56 IST. No hard-stop condition fired.
No submission artifact was regenerated, replaced, committed, pushed, or uploaded
during this gate.

## Exact artifact identity

- Current ZIP `amazon_ml_challenge_2026_submission.zip` SHA-256:
  `91fe000809e29459fb75f3164b787d39b5d5cb8e8e3a6ec2f21a314f1a38b194`.
  This equals the recorded validated artifact hash in `HANDOFF.md`.
- Current `output/matching_results.tsv`, `best/matching_results.tsv`, the fresh
  checker report, the prior full checker report, and the ZIP manifest all
  agree on SHA-256
  `df1415117c62d350ca33d51bffa678934f1f2c6282997fb0103087995178ff05`.
- The same five-way agreement for `candidate_pairs.tsv` is SHA-256
  `3d5b2e71e32e11f168d22725c03757f62b0853147e7f3ba7cfa0f4bf7cc3f9c5`.
- No `output/*.part` files remain. The ZIP has 23 entries; every archived
  entry's size and SHA-256 matches `MANIFEST.json`. The ZIP file itself retains
  the recorded hash, so the CRC check from the validated packaging run applies
  to these exact bytes.

## Fresh checks on the current output files

- Complete independent checker: **PASS**, exit 0, on 1,732,544 Source 1 rows,
  including all 259,452 France rows. It checked 24,702,044 scored candidate
  IDs for existence and country, unique/order coverage, and predictions as a
  subset of candidates. Fresh report:
  `work/release_gate_check_2026-09-26.json`.
- Supplied official validator: **PASS**, exit 0, on both complete TSVs. Its
  optional in-memory ID mode was off; the independent checker above covered
  every candidate ID.
- Separate strict TSV/empty-field/candidate-bound/hash gate: **PASS**, exit 0.
  It confirmed no malformed rows or placeholder null values, 31 maximum
  candidates, and exact agreement with the fresh checker hashes. Fresh report:
  `work/release_gate_strict_2026-09-26.json`.

No commit, push, or leaderboard upload was performed. If any current artifact
hash changes after this gate, downgrade this status until the changed artifact
has a fresh complete checker and validator pass plus independent ZIP validation.
