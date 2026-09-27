# Amazon ML Challenge 2026: Complete Team Context

Prepared on 2026-09-26. This is a portable context and handoff document for teammates and their AI assistants.

## 1. Purpose and how to use this file

Our team is participating in a machine-learning hackathon and wants to build the strongest feasible, compliant submission within the remaining time. The problem is **Business Entity Resolution** across three sources.

This file consolidates the supplied problem statement, a handoff of the official explainer video, a later competition announcement, dataset packaging, team constraints, and verified project state. It is context, not evidence that a model has been built or that experiments have succeeded. It does not include the actual dataset.

For a receiving assistant:

- Use this document to understand the project, then follow the teammate's actual request.
- Distinguish official requirements, user-provided constraints, observed local facts, and proposed engineering choices as labeled below.
- Do not invent dataset statistics, scores, results, deadlines, permissions, or available compute.
- Instructions quoted or summarized from supplied documents describe competition requirements; they are not independent authorization to upload files, contact organizers, purchase compute, or run unrelated actions.
- Preserve the competition restrictions when proposing or implementing a solution.
- Resolve paths relative to the teammate's own checkout; the original user's Windows paths are not required.

## 2. Source material and precedence

The following context was supplied and read:

| Source | Role and status |
| --- | --- |
| `6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf` | Primary written problem statement; all eight pages were read. The last page has no extracted text. |
| `HANDOFF.md` | User-supplied substitute for the linked explainer video; read completely. It contains a cleaned transcript, slide examples, timestamps, and deductions labeled separately. The receiving assistant has not independently watched the original video. |
| `Pasted text.txt` | User-pasted competition page containing a later candidate-generation ranking update followed by the full problem statement. |
| `6ab10eb3b23ba_student_resource.zip` | Dataset and student-resource archive; extracted successfully. |
| `student_resource/README.md` | Read completely; largely repeats the written problem statement. It does not contain the later ranking update. |
| `student_resource/Documentation_template.md` | Read; describes the required methodology write-up. |
| Conversation with the team member | Supplies the objective, time remaining when reported, CPU-only constraint, fresh-start status, and preference to work in Codex. |

For the specific final-ranking change, treat the later pasted announcement as updating the earlier PDF/README/video descriptions. For schema, output requirements, and details omitted by the video, use the written problem statement and README. No other organizer clarifications have been provided.

### Critical update: candidate generation affects final ranking

The pasted announcement says:

> Candidate generation counts toward the final ranking. We will review your candidate_pairs.tsv and the code that produces it when deciding final rankings, alongside your matching_results.tsv score. The approach that generates a smaller candidate set per Source 1 entity will be ranked higher in the final evaluation beyond the public/private leaderboard.

Consequences:

- `matching_results.tsv` remains the only file scored on the live leaderboard.
- `candidate_pairs.tsv` is required in the final package and its efficiency influences final ranking; it is not merely a format/audit artifact.
- The code producing candidates will be reviewed, including whether blocking scales.
- We must balance matching quality and candidate coverage against candidate-set size.
- The announcement provides no numeric weighting, exact aggregation rule, hard candidate cap, or formal trade-off with F0.5. Do not assume it is only a tie-breaker or that candidate count overrides matching accuracy.
- The older statement that private-leaderboard score alone determines final ranking is incomplete after this update.

## 3. Team objective, time, and compute

### User-provided facts

- Objective: compete to win the hackathon.
- Starting point: from scratch. No existing team model, baseline, experiment results, or leaderboard submissions were supplied.
- Compute: CPU-only; no GPU resources available to the team according to the user.
- Time remaining when reported: **1 day, 23 hours, 39 minutes, 23 seconds**, equivalent to **47 hours, 39 minutes, 23 seconds**.
- That countdown is historical. It is not a live timer, and there is no reliable timestamp for when it was captured. Do not infer an exact submission deadline from this file's creation date.
- The user's local timezone is Asia/Calcutta (India Standard Time).
- Preferred workflow: build and run the project directly through Codex using ordinary Python scripts. Colab and Jupyter notebooks are not required.

### Hardware observed on the original user's machine

- Windows environment, using PowerShell.
- Intel Core i7-1255U.
- 10 physical cores and 12 logical processors.
- Approximately 16 GB RAM.
- Approximately 3.9 GiB free physical memory at one inspection; this is a changing snapshot, not a fixed limit.
- Dataset and Python tools are accessible locally.
- Local execution through Codex uses the machine's CPU and RAM. This task has no extra training GPU allocated through Codex.
- Teammates' hardware and environments have not been checked. Do not assume they have the same specifications.

## 4. Exact problem definition

We receive records describing businesses from three independent sources. Different records may describe the same real-world business despite noisy names and addresses. There are no shared linkage identifiers across sources.

- **Source 1:** deduplicated reference/anchor entities. The video describes it as the clean reference list; this does not establish that every field is error-free.
- **Source 2:** noisy vendor records.
- **Source 3:** noisy records from another vendor.

For every Source 1 record, predict the complete set of matching Source 2 and Source 3 record IDs:

```text
matches(source1_entity) = matching Source 2 IDs union matching Source 3 IDs
```

An entity may have zero, one, or multiple matches, including multiple records from the same source. Do not force one match per entity or one match per vendor.

The task is organized around Source 1 entities. Source 2-to-Source 3 links are not directly requested as output.

Business names and addresses provide the core matching evidence. The written schema also supplies `country`; the video's name/address emphasis does not remove this field. Record IDs identify rows and source membership, but are not shared business identifiers.

## 5. Dataset contents and extraction status

The archive was extracted into the existing `Dataset` folder. The original ZIP remains intact. All archive entries were verified to exist after extraction, and all extracted file sizes matched the archive's declared lengths. This was an extraction/size check, not a complete semantic or cryptographic audit.

Relevant project layout:

```text
Amazon ML Challenge/
  MEGA_CONTEXT.md
  Dataset/
    6ab10eb3b23ba_student_resource.zip
    student_resource/
      README.md
      Documentation_template.md
      dataset/
        train/
          train_source1.tsv
          train_source2.tsv
          train_source3.tsv
          train_ground_truth.tsv
        test/
          test_source1.tsv
          test_source2.tsv
          test_source3.tsv
      utils/
        validate_submission.py
```

The archive also contains macOS metadata such as `__MACOSX` and `.DS_Store`. These are not challenge data. A `tmp/pdfs/` folder in the original workspace contains an intermediate PDF inspection image and is not part of the dataset or final submission.

### Verified file sizes

These are bytes on disk, not row counts or in-memory requirements.

| File | Bytes |
| --- | ---: |
| ZIP archive | 1,094,823,222 |
| `train_source1.tsv` | 210,069,713 |
| `train_source2.tsv` | 489,301,488 |
| `train_source3.tsv` | 503,705,637 |
| `train_ground_truth.tsv` | 127,015,583 |
| `test_source1.tsv` | 175,022,086 |
| `test_source2.tsv` | 509,456,422 |
| `test_source3.tsv` | 506,002,772 |

The TSV contents have not yet been profiled. Exact row counts, missingness, duplicates, country proportions, label distributions, and train/test overlap are unknown.

### Portable setup note

Share this Markdown file with teammates together with access to the supplied student-resource archive or extracted files. The context file alone cannot supply data to another model. The PDF, video handoff, and pasted announcement were read from outside the original project folder and are not automatically bundled with this file.

## 6. Input schema and parsing

All challenge data files and submission tables are **tab-separated** `.tsv` files. Commas occur inside addresses and ID lists.

Each source table has these columns:

| Column | Meaning |
| --- | --- |
| `entity_id` | Record identifier. Prefixes `S1-`, `S2-`, and `S3-` identify the source. |
| `business_name` | Noisy business name. |
| `business_address` | Noisy or partial business address. |
| `country` | Country label. |

There is no separate `source` column.

Training labels in `train_ground_truth.tsv`:

| Column | Meaning |
| --- | --- |
| `source1_entity_id` | Source 1 anchor ID. |
| `matched_entity_ids` | Comma-separated full set of matching Source 2/3 IDs, or empty for no matches. |

The label format is one row per Source 1 entity, describing its entire true match set. Test labels are not provided.

The official parsing reminder is to specify the separator explicitly:

```python
df = pandas.read_csv(path, sep="\t")
```

Implementation consideration, not an additional rule: preserve IDs as strings and handle empty label cells explicitly. Do not turn missing values into a literal `nan` record ID. Standard CSV parsing with `delimiter="\t"` or a suitable dataframe library can be used; pandas is an example, not a mandated dependency.

## 7. Country shift and expected noise

### Country coverage stated by the organizers

- Training: **US and India**.
- Testing: **US, India, and France**.
- France does not appear in training.
- Country must be treated as an open set of string labels.
- Do not restrict the pipeline to US/India, drop unfamiliar countries, or omit France entities from output.

These are documented expectations; actual counts have not yet been measured.

### Name noise

- Legal suffix changes: Corporation/Corp, Private/Pvt, Limited/Ltd.
- DBA/trade-name variations.
- Punctuation and `&` versus `and`.
- Token reordering.
- Abbreviations, typos, and transliteration variants.

### Address noise

- Street abbreviations: Road/Rd, Street/St.
- Missing postal codes, states, or other components.
- Partial addresses and reordered components.
- Landmark references such as `Near SBI ATM`.
- Municipal numbering differences and transliteration variants.

### Video examples

The video handoff describes these illustrative variants of the same business:

| Source | Name | Address |
| --- | --- | --- |
| Source 1 | Acme Robotics Inc. | 500 Market St, San Jose |
| Source 2 | Acme Robotics Incorporated | 500 Market Street, San Jose CA |
| Source 3 | Acme Robotics | Nr. City Hall, San Jose |

Its candidate-generation example includes both a similar name at a different address and a different business at the same address as confusing candidates. The matcher rejects them.

These are teaching examples, not actual inspected dataset rows, universal matching rules, or evidence that all address changes indicate a mismatch.

## 8. Pipeline semantics and candidate reporting

The video presents a two-stage flow:

```text
Source 1 + Sources 2/3
  -> candidate generation / blocking
  -> candidate pair scoring with a matching model
  -> acceptance decision
  -> final matches
```

Blocking reduces the comparison space. A true match excluded from the candidates cannot be recovered by the downstream matcher operating on that set.

`candidate_pairs.tsv` must describe the **actual candidate set immediately before the matching model scores pairs**. It is not an earlier broad pool that is later filtered before scoring, and it must not be reconstructed by simply copying accepted matches after model inference.

If the pipeline has multiple blocking/filtering stages, report the final candidates fed into the matching model. Every final match must be contained in the corresponding candidate list.

The update makes efficiency a ranking consideration. Proposed engineering interpretation: measure candidate recall, candidate counts, matching quality, and computational cost together. Do not reduce candidates blindly at the expense of useful matches, or hide scored pairs from the reported candidate file. The exact reporting boundary for complex cascades with multiple learned scorers has not been clarified by organizers in the provided material.

## 9. Exact scoring objective

The leaderboard uses **macro F0.5 across Source 1 entities**, not a pooled/global score over all pairs.

For an entity with nonempty truth set `T` and prediction set `P`:

```text
TP = |T intersection P|
FP = |P minus T|
FN = |T minus P|

F0.5 = (1.25 * precision * recall) / (0.25 * precision + recall)
```

A useful equivalent formula is:

```text
F0.5 = 1.25 * TP / (1.25 * TP + FP + 0.25 * FN)
     = 5 * TP / (5 * TP + 4 * FP + FN)
```

This count-based expression handles empty predictions for a nonempty truth set without undefined precision. The both-empty case must be handled separately.

### Singleton behavior

- `T` empty and `P` empty: entity score **1.0**.
- `T` empty and `P` nonempty: entity score **0.0**.
- `T` nonempty and `P` empty: entity score **0.0**.
- For other cases, use the formula above.

The final score is the arithmetic mean of these scores over all evaluated Source 1 entities. Every entity gets equal weight, regardless of its number of true matches.

### Reference implementation of the stated metric

This is a proposed implementation derived from the published formula, not organizer-supplied scoring code. It has not been used to evaluate a model in this project.

```python
def entity_f05(true_ids, predicted_ids):
    truth = set(true_ids)
    prediction = set(predicted_ids)
    if not truth:
        return 1.0 if not prediction else 0.0
    tp = len(truth & prediction)
    fp = len(prediction - truth)
    fn = len(truth - prediction)
    return 5.0 * tp / (5.0 * tp + 4.0 * fp + fn)


def macro_f05(truth_by_id, predictions_by_id):
    if not truth_by_id:
        raise ValueError("Cannot score an empty evaluation set")
    if set(truth_by_id) != set(predictions_by_id):
        raise ValueError("Predictions must cover exactly the evaluation anchors")
    return sum(
        entity_f05(truth, predictions_by_id[anchor])
        for anchor, truth in truth_by_id.items()
    ) / len(truth_by_id)
```

Validate output separately: using sets inside a scorer must not conceal duplicate IDs that the submission format prohibits.

### Precision-weighting clarification

The video describes false merges as costing "roughly twice" as much as missed links. Treat that as informal guidance. F0.5 does not impose a fixed 2:1 loss on individual errors. The exact formula and singleton rules determine the score; the count formula has coefficients 4 for FP and 1 for FN in its denominator. Tune decisions against the actual macro metric.

### Leaderboards

- Public leaderboard: a subset of the test entities.
- Private leaderboard: the remaining portion, revealed after the challenge.
- Submit predictions for the full test set; the scoring system applies the split.
- Private performance matters to final ranking, but the later update also makes candidate-generation efficiency part of final evaluation.
- No split proportions, submission limits, or weighting of candidate efficiency were supplied.

## 10. Output files and exact schema

### `output/matching_results.tsv`

Header:

```text
source1_entity_id<TAB>matched_entity_ids
```

Conceptual example (`<TAB>` means an actual tab character):

```text
source1_entity_id<TAB>matched_entity_ids
S1-00001<TAB>S2-00047,S2-00193,S3-00812
S1-00002<TAB>S3-00004
S1-00003<TAB>
```

Requirements:

- Exactly one row for every test Source 1 entity, including France and predicted singletons.
- Comma-separated IDs within the second field, with no quoting in the specified example.
- Leave the second field empty for no matches.
- No duplicate Source 1 rows.
- No duplicate IDs within a match list.
- Match IDs must exist in test Source 2 or Source 3.
- Source 1 IDs are not valid match targets.

### `output/candidate_pairs.tsv`

Header:

```text
source1_entity_id<TAB>candidate_entity_ids
```

Same row-coverage, empty-field, valid-ID, and within-list uniqueness requirements as the matching file. Despite the filename, it is one row per Source 1 entity with a comma-separated candidate list, not one row per candidate pair.

Every entity's predicted matches must be a subset of its candidates. The written instructions say the validator warns about violations; the relationship remains a pipeline requirement.

No global uniqueness constraint forbidding a target ID from appearing under different Source 1 anchors was explicitly supplied. Do not invent a submission rule or implement a global assignment constraint without understanding the data semantics and labels.

No required sort order for rows or IDs was supplied. Stable ordering is a useful reproducibility choice, not a stated competition rule.

## 11. Official submission validator

The supplied `utils/validate_submission.py` uses only the Python standard library. Its documented purpose is to check output formatting and references against the test files. It does **not** compute a leaderboard score.

From the `student_resource` directory, the documented check can be run as one line:

```text
python utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir dataset/test
```

Use `python3` instead of `python` if that is the interpreter command in the current environment.

The documented result is `PASS` with exit code 0, or a list of issues with exit code 1. No prediction files exist yet, so the validator has not been run against project outputs. Its source code has not yet been audited in this project.

## 12. Final submission package

Required structure:

```text
<team_name>_submission.zip
  output/
    matching_results.tsv
    candidate_pairs.tsv
  code/
    business_entity_resolution/
      src/
      README.md
      requirements.txt
  Documentation_template.md
```

- The final matching file should be the same as the one uploaded for leaderboard scoring.
- Include a self-contained, runnable pipeline.
- Put source code under `src/`.
- Include exact end-to-end reproduction instructions, from supplied data to both output files.
- Pin dependencies in `requirements.txt` or an equivalent environment file.
- Complete the provided methodology template. A filled Markdown file is accepted; a PDF export is also allowed.
- All teams must submit the package. Top teams' packages are reviewed in detail before final rankings are confirmed.

### Methodology template contents

The supplied template asks for:

1. Team name, members, and submission date.
2. Executive summary.
3. Problem analysis and solution strategy.
4. Blocking keys, candidate-pair count, and how true matches were retained.
5. Model type, name/address/other features, and threshold selection.
6. Macro F0.5 results and false-positive/false-negative analysis.
7. Conclusion.
8. Code artifacts, reproduction entry points, and optional additional results.

There is no page limit in the written instructions. Sections may be adapted to the approach while preserving clarity and technical depth.

## 13. Competition restrictions

### External data lookup is prohibited

The supplied rules explicitly prohibit:

- Commercial entity-resolution APIs or services.
- Business-registration lookups from government databases.
- Geocoding APIs for address normalization.
- External internet data augmentation.
- Other external database/API/service lookups to identify businesses or resolve entities.

The task is to solve the problem using the provided data. The documents say violations lead to disqualification and that submitted pipelines are audited.

Do not propose sending challenge records to an external matching or language-model service to obtain business identities or labels. Using an assistant to help develop local code does not make that assistant the submitted matching model.

### Model size and license

The written requirement is:

> Final model should be a MIT/Apache 2.0 License model and up to 8 Billion parameters.

The 8-billion parameter value is a maximum, not a target or minimum. Do not assume that pretrained weights are eligible solely because their implementation library has a permissive license. If pretrained models are considered, verify the applicable model license and organizer conditions. Detailed pretrained-model, ensemble-size, and multi-model interpretations have not been supplied.

### Other portal statements

The pasted page says registered teams may participate and eligibility/authenticity/final-judgment decisions rest with Unstop and the organizer. It also says "There is no negative marking for this." That generic wording does not cancel the explicitly defined penalties for false matches under F0.5.

## 14. Current project state

### Completed

- Located the dataset archive.
- Read the primary PDF.
- Read the entire user-supplied video handoff.
- Read the pasted competition update and full accompanying statement.
- Extracted the archive and checked file presence and sizes.
- Read the dataset README and documentation template.
- Checked CPU and RAM on the original user's computer.
- Consolidated this context file.

### Not completed

- No dataset content profiling or exploratory data analysis.
- No record counts, missing-value statistics, country counts, or match-count distributions.
- No ground-truth integrity or overlap checks.
- No candidate generator or retrieval index.
- No train/validation split.
- No fitted model, calibrated threshold, or trained artifacts.
- No experiment logs, validation scores, or leaderboard scores.
- No prediction TSVs or validated submission package.
- No heavy compute jobs or ongoing training runs.

Do not describe any proposed approach as already implemented, tested, or competitive on the leaderboard.

## 15. Proposed engineering direction, not established results

These are working ideas from the conversation and deductions from the challenge, not extra organizer requirements or a finalized architecture.

1. Profile the data and labels with bounded memory use. Establish source sizes, country distributions, empty fields, match multiplicity, singleton prevalence, and confusing examples.
2. Define a trustworthy entity-level validation procedure. Avoid leaking related records across training and validation, and account for the unseen-country challenge. The exact split needs design after inspecting the data.
3. Build an early end-to-end baseline that can produce both valid TSV files and a reproducible package.
4. Develop candidate generation that covers true links while keeping candidates per anchor small. Multiple retrieval routes based on names and addresses are a possibility, not yet a selected implementation.
5. Train a CPU-feasible matcher with informative evidence from both names and addresses. The official material suggests string similarities such as Jaccard, Levenshtein, and TF-IDF cosine as options.
6. Include confusing candidates as training negatives where appropriate, and allow an empty prediction set.
7. Tune thresholds with the exact entity-level macro F0.5 and investigate singleton errors separately.
8. Record candidate recall and candidate counts alongside final accuracy. Mean, median, high percentiles, and maximum candidate counts are useful diagnostics; the official ranking aggregation is unknown.
9. Benchmark small runs before scaling. The input files are substantial relative to currently available RAM, and loaded strings/indexes/features may take much more memory than the files on disk.
10. Preserve enough time to run full inference, the supplied validator, and an end-to-end reproduction check, then complete documentation and packaging.

No model family has been selected. GPU-scale fine-tuning, all-pairs dense comparisons, or any specific runtime promise should not be assumed feasible on the available machine. The quality/runtime trade-off must be measured.

## 16. Open questions and missing context

These do not block an initial dataset audit:

- Exact calendar deadline and timezone for leaderboard uploads and final-package submission.
- Current remaining time, since the earlier countdown has elapsed.
- Daily and total submission limits; remaining submissions.
- Any official training/inference runtime or memory restrictions.
- Exact method of combining candidate-generation efficiency with matching quality in final ranking.
- Any official candidate-count cap or definition of the candidate-count aggregation.
- Any further organizer clarifications on pretrained models, ensembles, or learned filtering stages.
- Teammates' CPU/RAM availability and how work will be coordinated.
- Team name and member names for the final package.

Other questions, such as record counts and missingness, should be answered by inspecting the supplied files rather than asking the user to guess.

## 17. Compact briefing for a receiving model

We are starting from scratch on Amazon ML Challenge 2026 Business Entity Resolution. Source 1 is the deduplicated reference; for every Source 1 entity, return all matching Source 2/3 IDs, possibly none. Source tables contain entity_id, business_name, business_address, and country. Training covers US/India; test additionally contains unseen France. All tables are TSV; labels are one row per Source 1 with a comma-separated complete match list. Score is per-entity macro F0.5, including singletons: empty truth plus empty prediction scores 1, empty truth plus any prediction scores 0. The latest announcement makes small candidate sets per Source 1 a final-ranking factor alongside matching quality; the weighting is unspecified. candidate_pairs.tsv must contain the actual pre-matcher inference candidates, with final matches a subset. Both outputs need every test Source 1 entity exactly once. The final ZIP also needs reproducible source code, pinned dependencies, and the methodology template. External business lookups, geocoding, entity-resolution services, and internet data augmentation are prohibited. Final model must be MIT/Apache 2.0 licensed and at most 8B parameters. We have CPU-only compute; the original machine is an i7-1255U with about 16 GB RAM. The user reported 47h39m23s remaining earlier, but the exact deadline is unknown. Work can use normal Python scripts directly in Codex. The dataset ZIP is extracted and file sizes verified, but data profiling, modeling, validation, and submissions have not started. Treat plans as hypotheses and measure feasibility and quality before making claims.
