# Submission state and artifact identity

Status at the 2026-09-27 packaging inspection: **locally verified, not uploaded by this work**. Full-test leaderboard score, private-test score, and portal acceptance are `UNKNOWN`. The public listing did not establish an upload-attempt limit; conserve attempts. Team name/member placeholders remain in the approach document.

| Current local artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/matching_results.tsv` | 65,584,651 | `df1415117c62d350ca33d51bffa678934f1f2c6282997fb0103087995178ff05` |
| `output/candidate_pairs.tsv` | 340,756,092 | `3d5b2e71e32e11f168d22725c03757f62b0853147e7f3ba7cfa0f4bf7cc3f9c5` |
| `amazon_ml_challenge_2026_submission.zip` | 174,257,174 | `91fe000809e29459fb75f3164b787d39b5d5cb8e8e3a6ec2f21a314f1a38b194` |

`best/` holds copies with the same primary TSV hashes. The ZIP contains 23 manifest-checked entries; CRC/manifest verification and the complete checker/strict scan/official validator were recorded in `work/release_integrity_2026-09-26.md`. The 2026-09-27 packaging pass re-read current hashes and freshly reran the official validator; consult `VALIDATION_CHECKLIST.md` for the hard-stop rule. The ZIP and large TSVs are intentionally excluded from Git to avoid a misleading or oversized repository. Transfer the exact ZIP through an approved channel and verify its hash at the receiving end.

**Documentation-only divergence:** the ZIP's archived `Documentation_template.md` is the validated pre-handoff version and still says full-test candidate totals were pending. The repository's current `Documentation_template.md` corrects that sentence using the measured full report. A read-only comparison of every ZIP manifest path against the current workspace found this as the **only** mismatch; both TSVs and production code still match their archived hashes. The ZIP was not regenerated because this task expressly forbids it. Do not claim the current Git methodology text is already inside the ZIP. If the team elects to refresh the ZIP, it becomes a new artifact requiring fresh full validation, manifest/CRC checks, and a new hash.

Current outputs: 1,732,544 test anchors (US 663,106; India 809,986; France 259,452), 24,702,044 scored candidate IDs, 3,327,344 predicted IDs, 367,629 empty match rows, and 42,487 empty candidate rows. Candidate count mean 14.257672, median 13, P90 25, P95 26, P99 28, max 31. All target-ID/country/order/coverage/uniqueness/subset checks passed in the independent full report. This is a structural submission state, **not** measured test accuracy.

Fallback identity: `fallback/matching_results.tsv` SHA-256 `4337e005594f60763e3b77258450b390d5f5dc6964b5a22adf1269270863461e`; `fallback/candidate_pairs.tsv` SHA-256 `5e917412aabc367bb709eb70584cdfd7cc440b764f03828c9f6601525dcf34e8`. Both are locally preserved, not committed to Git, and their validation evidence is in `work/fallback_check_report.json` and `fallback/score_report.md`.
