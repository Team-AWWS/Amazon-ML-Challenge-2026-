# Five-agent research review

Provisional, based on the measured 10,000-anchor narrow baseline (macro F0.5 0.488891; candidate recall 0.291607; mean 3.6837 candidates; 119.2 anchors/s) and early broad-FTS runtime kill (>100 seconds before 1,000 anchors). All research agents were read-only and CPU-light. The root coordinator owns production changes and the final decision.

## Agent 1 — six distinct solution families

1. **HARDEN THE DETERMINISTIC BASELINE:** keep exact name/address blocking and add only bounded fuzzy routes for weak/unresolved anchors; low implementation risk, but present recall is low.
2. **Rare-token inverted retrieval:** use country-scoped rare name/address token postings and candidate caps; can recover reordered/partial text, but common postings may explode.
3. **Character n-gram LSH:** near-neighbor bucket retrieval for typos, followed by full scoring; script-sensitive and costly to build/tune at 10M targets.
4. **Structured address-first retrieval:** house number/postal/locality/street keys plus cautious name corroboration; helps trade-name changes but shared buildings risk false merges.
5. **Lightweight supervised pairwise ranker:** small CPU classifier on bounded candidates and hard negatives; may improve precision but cannot fix missing candidates.
6. **Cross-source consistency graph:** use Source 2–3 corroboration around bounded candidates; potential multi-match support but propagation and graph scale are high risk.

## Agents 2 and 3 — preserved disagreement

Agent 2 saw plausible score gains from rare-token/address recovery, later supervised calibration, and local cross-source support. Agent 3 marked bounded deterministic, rare-token, and address routes **conditional**; deferred the ranker until recall improves; and killed full LSH and graph propagation for this deadline. Agent 3 specifically noted that SQL `LIMIT` bounds returned rows but not FTS posting traversal—the measured broad-FTS runtime failure is consistent with that risk. Neither review proves an approach works; dev experiments decide.

## Agent 4 — red team and priority

1. Rare-token retrieval only for weak/unresolved anchors, with a measured document-frequency cutoff, per-source cap, 1k early gate, then 10k dev benchmark. Hypothesized targets: candidate recall ≥0.35 and macro F0.5 ≥0.50 without a runtime or P99 explosion. Kill on poor throughput, weak marginal recall, >2% score regression, or an infeasible full-run projection.
2. Address-number plus distinctive street-token retrieval, measured for incremental gain beyond experiment 1. Hypothesized targets: ≥0.02 absolute incremental recall or ≥0.01 macro F0.5 with acceptable precision and P99 ≤64. Kill on shared-building false merges, weak marginal gain, or index cost.
3. Optional cheap deterministic rescoring/threshold check on cached dev candidates; it cannot repair retrieval recall. Require repeatable ≥2% relative score gain to promote.

The broad FTS route is not retried unchanged. Candidate recall is kept separate from macro F0.5, and all candidate files must list exactly the scored pairs.

## Agent 5 — provisional architecture

Preferred direction: preserve the complete validated narrow baseline, then test a two-stage country-scoped matcher that activates bounded rare-token/address routes only when exact evidence is weak. Keep the narrow pipeline as fallback. Key unresolved questions are marginal recall, false merges, query fanout/runtime, France transfer, and related-record leakage. Do not build full LSH, broad FTS, graph propagation, or a trained ranker before retrieval evidence and submission safety justify them. Promote only a measured, repeatable macro F0.5 gain (or comparable score with materially fewer candidates) that passes runtime, memory, compliance, and full validation gates.

## Agent 5 — final measured decision

Select **combined rare-address + rare-name retrieval** with frozen dev threshold **0.65** as the *conditional primary*, and retain the validated narrow exact-route outputs as fallback. Complete dev: 0.560165 macro F0.5 versus narrow 0.497433 (+12.6% relative), with candidate recall 0.431252 versus 0.297894. Untouched full holdout: 0.561627 versus 0.499692 (+12.4% relative), recall 0.430373 versus 0.298817. The candidate cost is substantial: 13.37 mean and P99 28 on holdout, versus narrow 3.63 and P99 13. The official candidate-efficiency weighting is unknown, so this does not establish a public or private leaderboard gain.

Remaining mandatory gates are a representative test-side 10k runtime/memory/country benchmark, conservative full-run projection including complete validation before the reserved delivery buffer, then full output target-ID/subset/coverage/duplicate checks and official validator. If any gate fails or the run threatens the deadline, ship the already validated narrow fallback. France has no labels; favorable US/India holdout consistency is not a France performance claim. This conclusion is based on measurements rather than agent consensus.
