# France distribution shift

Training labels cover US and India only; **France is present only in unlabeled test data**. Thus France F0.5, precision, prediction recall, and true candidate recall are `UNKNOWN`. `research/france_shift.md` documents the limited proxy in full.

The primary output includes all **259,452** France Source 1 entities. For France, the complete independent report measured **16.128** candidates per anchor (P95 27), **2.443** predicted IDs per anchor, and **11.540%** empty match rows. US/India candidate means were 13.836/14.004 and predicted IDs per anchor 1.789/1.860. The mixed-country 10k fixture showed similar structural rates. These facts show coverage and a distribution difference, not accuracy.

On labeled holdout at one frozen 0.65 threshold, US macro F0.5 was 0.581115 and India 0.532503. This gap is a warning that performance varies by country even where labels exist. No French threshold was tuned. A read-only inspection of high-prediction France rows also found some unrelated business names sharing the same precise or city-only address among predicted target IDs; these may be false positives, but lack labels and must not be reported as proven errors. Do not use unlabeled France output patterns to claim a private-test score.
