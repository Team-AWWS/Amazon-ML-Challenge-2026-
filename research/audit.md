# Dataset audit

Status: train label/ID/country integrity, Source 1 split leakage, train/test ID overlap, and disk-backed normalized duplicate-record checks completed. Counts below were measured by streaming every supplied TSV on 2026-09-26; no sampled counts are presented as full-dataset results.

## File sizes and rows

| File | Rows | Bytes | Country distribution | Missing fields |
| --- | ---: | ---: | --- | --- |
| train_source1.tsv | 2,206,821 | 210,069,713 | US 1,323,633; India 883,188 | none |
| train_source2.tsv | 5,034,616 | 489,301,488 | US 3,016,817; India 2,017,799 | address 168,967 |
| train_source3.tsv | 5,285,603 | 503,705,637 | US 3,170,056; India 2,115,547 | address 175,916 |
| train_ground_truth.tsv | 2,206,821 | 127,015,583 | n/a | matched IDs empty 123,247 |
| test_source1.tsv | 1,732,544 | 175,022,086 | US 663,106; India 809,986; France 259,452 | none |
| test_source2.tsv | 4,887,273 | 509,456,422 | US 1,871,330; India 2,312,565; France 703,378 | address 129,408 |
| test_source3.tsv | 5,082,316 | 506,002,772 | US 1,945,701; India 2,405,000; France 731,615 | address 136,098 |

## Labels

- 7,638,365 labeled links; mean 3.461 per Source 1 record; maximum observed 11.
- 3,693,619 labeled links target Source 2; 3,944,746 target Source 3.
- Match-count frequencies: zero 123,247; one 119,157; two 375,212; three 530,841; four 484,115; five 321,957; six 164,868; seven 63,968; eight 18,680; nine 4,205; ten 534; eleven 37.
- The zero-match share is about 5.6%, so an all-empty prediction would be a poor competitive baseline even though it would satisfy the output schema.

## Real labeled examples inspected

- An English US name was badly misspelled while another linked vendor record had a completely unrelated trade name and a close address. Retrieval needs independent name and address routes.
- Several India matches used Tamil or Devanagari business names while Source 1 used Latin characters. Their addresses retained overlapping tokens. Unicode normalization must retain non-Latin scripts.
- Linked addresses included missing values, reversed components, typo-heavy street names, abbreviations, partial units, and English/Indian-script state names.
- These are examples from eight labeled Source 1 rows, not prevalence estimates.

## Integrity and leakage checks

- The train Source 2/3 index completed with 10,320,219 rows; the test index completed with 9,969,589 rows. Each exactly equals its two measured source-file counts. Their `entity_id` uniqueness constraints found no duplicate target IDs during construction.
- Full train Source 1 audit: 2,206,821 unique IDs; no bad `S1-` prefixes. Ground-truth rows equal 2,206,821 with zero missing/extra anchors.
- All 7,638,365 labeled links have valid `S2-`/`S3-` prefixes, exist in the train target index, have no duplicate IDs within lists, and agree with their anchor's country. There were zero violations of each type.
- Train Source 1 raw name length: median 24, P95 37, P99 42, max 105 characters. Address length: median 41, P95 103, P99 124, max 256 characters.
- The independent complete fallback-output check covered every test Source 1 row in original order, with no duplicate rows or missing IDs, including all 259,452 France anchors. Thus test Source 1 IDs are unique within the file. Every emitted target ID exists in the test index and has the anchor's country.
- The complete disk-backed follow-up check in `work/overlap_audit_report.json` found **zero** train/test Source 1 ID overlap and **zero** train/test target ID overlap. It found **zero** extra exact raw Source 1 duplicate rows in both train and test. Source 1 IDs were unique in each split.
- For Source 2/3, after the production Unicode/name/address normalization and within each country, duplicate **extra rows within a source** numbered **143,071 train** and **125,646 test**. Normalized name/address/country groups present in **both** target sources numbered **6,895 train** and **12,565 test**. These count matching field values across distinct IDs, not duplicate IDs or proof of a true entity match. Raw target-text duplicate counts were not separately measured.
- Related-but-not-identical validation overlap is quantified below.

The full train audit report is `work/audit_report.json`, the fixed entity split is `work/split_manifest.tsv`, and the complete input overlap/duplicate report is `work/overlap_audit_report.json`.

## Complete primary output integrity

The combined rare-token output passed the independent full checker over every **1,732,544** test Source 1 row, including **259,452 France** rows. Its 24,702,044 candidate IDs all exist in the supplied test target index and agree with the anchor country. All 3,327,344 predicted IDs are among the scored candidates. A separate strict TSV scan verified exact two-column rows, unique Source 1 input IDs, source/order coverage, genuine empty fields rather than placeholder tokens, and a maximum of 31 candidates. The full official validator also returned explicit PASS. Its optional memory-heavy ID mode was off; the independent checker supplied the complete ID check. Full test labels are absent, so test accuracy and true candidate recall are **NOT MEASURABLE**.

The full leakage audit scanned all 2,206,821 train Source 1 anchors: **zero** exact normalized name-and-address groups cross train/dev/holdout. Among dev and holdout anchors, 34,145 share an exact name but a different address with at least one train anchor, and 4,631 share an exact address but a different name. These are conservative related-record risk proxies, not confirmed same-entity leaks; shared company names and shared buildings can be legitimate. The detailed report and examples are in `work/leakage_report.json`. This split is safer than pair-row randomization but cannot guarantee independence of related businesses.

## Fixed validation split

Each train Source 1 entity is assigned by a stable BLAKE2b hash of its normalized business name and address: buckets 0–1 are dev, 2–3 are holdout, and 4–99 are train. This assigns identical normalized name/address groups to the same partition; the anchor is never split by candidate-pair row. The materialized split has train 2,118,511; dev 44,098; holdout 44,212. Similar-but-not-identical related records may still cross partitions; this is a known leakage risk to inspect before relying on holdout comparisons.
