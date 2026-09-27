# Validation and integrity checklist

The current primary evidence is in `work/full_check_report.json`, `work/release_gate_check_2026-09-26.json`, `work/release_gate_strict_2026-09-26.json`, and `work/release_integrity_2026-09-26.md`. The official validator also passed freshly during the 2026-09-27 packaging pass, with its optional `--check-ids` mode off. The independent checker covers every target ID using the disk-backed index. The current output/ZIP hashes were re-read from disk and matched the recorded evidence.

Before upload or declaring any file verified:

1. Hash `output/matching_results.tsv`, `output/candidate_pairs.tsv`, and the ZIP. Compare exact SHA-256 values with `SUBMISSION_STATE.md` and the latest checker/manifest. Check `best/` separately if it is meant to mirror `output/`.
2. Confirm the complete test set has exactly 1,732,544 Source 1 rows, including 259,452 France rows, and each output has one row per Source 1 ID in input order with no duplicates.
3. Confirm exact TSV headers, two fields per row, empty cells truly empty, and no duplicate listed target IDs.
4. Confirm every listed target is an existing test S2/S3 ID of the same country. Confirm every prediction is among the actual candidates scored for that anchor.
5. Run the independent full checker and official validator on the *same pair of files*; compare fresh report hashes with the current files. The validator's default ID mode is insufficient on its own.
6. Verify ZIP CRC and each archived entry against `MANIFEST.json`, then match the ZIP's own SHA-256 to the validated artifact identity.
7. If any integrity condition fails, **stop commit/push or upload of the affected artifact state**. Preserve files, record the exact mismatch, identify which version produced prior evidence, and downgrade `VERIFIED` until the new artifact passes all checks. Do not silently rewrite a hash or report.

The official command is:

```powershell
python Dataset/student_resource/utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir Dataset/student_resource/dataset/test
```

The independent command is:

```powershell
python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir output --report work/new_check_report.json
```

For the preserved fallback, use a separate directory or point these same checks at `fallback/` without modifying its files. A historical PASS is not transferable to edited bytes or a newly built ZIP.
