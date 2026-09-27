# France distribution-shift stress test

Status: limited country-transfer proxy; both the validated narrow baseline and the promoted combined primary have complete test output statistics. France has no labels.

## Method

Training labels cover US and India, while France appears only in test. We compare country-specific development and untouched-holdout retrieval and macro F0.5 under one frozen threshold per pipeline (narrow 0.68; combined 0.65), then inspect unlabeled candidate and prediction behavior by country. Applying a country-neutral threshold to both observed countries is a limited transfer stress proxy, not proof of private-test France performance. We do not fit or optimize any threshold on test records.

## Result

On all 44,098 dev entities, US macro F0.5 was **0.536236** with link candidate recall **0.330868** (26,498 anchors). India macro F0.5 was **0.439013** with recall **0.248280** (17,600 anchors). The India–US gaps are −0.097223 macro F0.5 and −0.082588 candidate recall. The same country-neutral normalization and threshold were used, so this difference is a warning that retrieval quality varies across observed countries. France has no labels, and no France F0.5 is reported.

On the complete unlabeled test set, the validated narrow baseline generated mean 3.255 candidates per US anchor, 3.774 per India anchor, and **4.456 per France anchor** (259,452 France anchors, all covered). Candidate P95 was 12 in all three countries. Predicted matches per anchor were 1.247 US, 0.992 India, and 2.058 France; the empty-prediction rates were 30.51%, 38.99%, and 15.53%, respectively. These different France output rates suggest distribution shift or different match multiplicity, but with no France truth they cannot establish whether extra predictions are correct.

On a separate **unlabeled** 10,000-anchor mixed-country fixture, the combined rare-token route produced mean candidates 13.771 US (3,891 anchors), 13.917 India (4,619), and **16.277 France (1,490)**, with candidate P95 26/25/27 respectively. Its predicted matches per anchor were 1.735/1.868/2.392, and empty-prediction rates 22.82%/23.40%/11.74%. Every fixture target ID and country passed the independent checker, and the supplied validator passed with ID checking enabled. These are structural/distribution observations, not accuracy estimates.

On the **complete** unlabeled test set, the combined primary generated mean candidates **13.836 US**, **14.004 India**, and **16.128 France**, with country P95 26/25/27. Predicted matches per anchor were 1.789/1.860/2.443, and empty-prediction rates **21.934%/23.734%/11.540%**. All **259,452 France** anchors have complete rows. Compared with the bounded fixture, the empty-rate shifts are −0.89, +0.33, and −0.20 percentage points; none breached the predeclared five-point anomaly gate. The full independent checker and official validator passed. These figures measure output distribution and integrity only; France F0.5 and true candidate recall remain **NOT MEASURABLE** without labels.

## Limitation

Neither US nor India reproduces French name, address, language, or vendor-source distributions. The test set has no supplied labels. The observed US–India gap is descriptive, not a causal transfer estimate, and the global dev threshold used both countries. This is not a leave-one-country-out threshold experiment; no country was entirely withheld from dev threshold selection.

## Implication

Keep France coverage as an explicit full-output gate, retain Unicode scripts, and avoid claims of unseen-country accuracy. The US/India holdout showed similar improved scores under one frozen 0.65 threshold (US 0.581115, India 0.532503), but their gap and the different France candidate/prediction rates show that country transfer remains uncertain. Use the unlabeled France counts only to flag possible instability, not to tune on France labels that do not exist.
