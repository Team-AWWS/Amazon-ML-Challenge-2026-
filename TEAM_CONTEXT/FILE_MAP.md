# File map: what Git does and does not carry

| Path | Purpose / handling |
| --- | --- |
| `code/business_entity_resolution/src/pipeline.py` | Production normalization, indexing, retrieval, score, evaluation, prediction, independent checker, fixture CLI; commit |
| `code/business_entity_resolution/src/{audit_data,audit_leakage,audit_overlap,measure_local_confusion,verify_primary_output,package_submission}.py` | Audit, validation, packaging tools; commit |
| `code/business_entity_resolution/tests/`, `README.md`, `requirements.txt` | Tests and reproducibility environment; commit, excluding caches |
| `research/*.md` | Audit, experiments, agent review, France and candidate frontier; commit |
| `work/*.json`, `work/release_integrity_2026-09-26.md` | Compact measured evidence; commit selected reports, excluding large/generated work files |
| `FINAL_ARCHITECTURE.md`, `FINAL_BUILD_SPEC.md`, `APPROACH_SUMMARY.md`, `Documentation_template.md` | Final design and methodology/approach; commit |
| `TEAM_CONTEXT/`, `FINAL_TEAM_HANDOFF.md` | Current teammate context; commit |
| `HANDOFF.md`, `PROJECT_HANDOFF_2026-09-26.md`, `MEGA_CONTEXT.md` | Historical project handoffs; commit as history, but some in-progress claims are stale |
| `Dataset/student_resource/README.md`, `utils/validate_submission.py`, `Documentation_template.md` | Supplied problem instructions/validator/template; commit for reproduction |
| `Dataset/student_resource/dataset/` | Raw competition data; **not in Git**; obtain through challenge channel |
| `work/*.sqlite`, `work/split_manifest.tsv`, fixtures/partials, `tmp/` | Multi-GB indexes and generated intermediates; **not in Git**; rebuild from supplied data |
| `output/*.tsv`, `best/*.tsv`, `fallback/*.tsv` | Validated large local artifacts; **not in Git**; preserve separately, verify SHA-256 |
| `best/score_report.md`, `fallback/score_report.md`, source snapshots | Small preserved evidence and code; commit |
| `amazon_ml_challenge_2026_submission.zip` | Current validated 174 MB submission ZIP; **not in Git**; transfer exact bytes separately |

The remote repository at inspection had only a short README. The handoff is therefore the main bridge from the current local workspace to other teammates. Never interpret a Git clone alone as containing the validated submission artifact or raw data.
