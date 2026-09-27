# Reproduction guide

Run from the repository root with Python 3.12+ and SQLite built with FTS5. The project was tested with Python 3.14.2 and SQLite 3.50.4. Inference has no required third-party package; `psutil` is optional for memory reporting. The supplied competition TSVs are **not in Git**; place them under `Dataset/student_resource/dataset/{train,test}/` or change `--data-dir`. Do not use external lookup/enrichment. See `code/business_entity_resolution/README.md` for detailed commands.

```powershell
python -m unittest discover -s code/business_entity_resolution/tests -v
python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split train --index work/train_index.sqlite
python code/business_entity_resolution/src/audit_data.py --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --manifest work/split_manifest.tsv --report work/audit_report.json
python code/business_entity_resolution/src/pipeline.py evaluate --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --partition dev --limit 100000 --variant rare_both --config work/dev_rare_both_full.json
python code/business_entity_resolution/src/pipeline.py evaluate --data-dir Dataset/student_resource/dataset --index work/train_index.sqlite --partition holdout --fixed-threshold 0.65 --limit 100000 --variant rare_both --config work/holdout_rare_both_full.json
python code/business_entity_resolution/src/pipeline.py build-index --data-dir Dataset/student_resource/dataset --split test --index work/test_index.sqlite
```

For a safe bounded end-to-end check, use a **new output directory**, not `output/` or `best/`:

```powershell
python code/business_entity_resolution/src/pipeline.py predict --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --variant rare_both --threshold 0.65 --limit 10000
python code/business_entity_resolution/src/pipeline.py check --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --limit 10000 --report work/repro_10k_check.json
python code/business_entity_resolution/src/pipeline.py make-fixture --data-dir Dataset/student_resource/dataset --index work/test_index.sqlite --output-dir work/repro_10k --fixture-dir work/repro_10k_fixture
python Dataset/student_resource/utils/validate_submission.py --matching work/repro_10k/matching_results.tsv --candidate work/repro_10k/candidate_pairs.tsv --test-dir work/repro_10k_fixture --check-ids
```

To reproduce full output in a *new* directory when time and disk allow, run `predict --variant rare_both --threshold 0.65 --output-dir work/repro_full`, followed by `check` and the official validator against the complete `dataset/test/`. Do not overwrite the preserved pair merely to prove reproduction. The previous full inference measured 13,737.2 seconds wall time including an observed host pause; index build and full checking add time. A fresh index built by current code includes FTS vocabulary metadata. For an older complete index, use the documented `prepare-vocab` command first. Generated SQLite indexes are several GB and remain outside Git/ZIP.

Full package creation is guarded by `code/business_entity_resolution/src/package_submission.py`, but **do not regenerate the already validated ZIP during this transfer task**. A regenerated ZIP has a new artifact identity and needs its own checker/validator/manifest/CRC/hash evidence.
