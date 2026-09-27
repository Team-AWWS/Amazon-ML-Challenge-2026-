# Amazon ML Challenge 2026 — approach summary

**Team:** [Team name]  
**Members:** [Team members]  
**Submission date:** September 27, 2026

## Problem and constraints

The task is to match every Source 1 business entity to zero or more entities in Source 2 and Source 3. The supplied training set contains US and India records with labels; the test set also includes France. Evaluation is entity-level macro F0.5, so false merges matter strongly. The solution uses only the supplied data and is designed for a CPU-only machine with about 16 GB RAM.

## Method

The selected primary is a disk-backed deterministic matcher. It normalizes case, punctuation, whitespace, and Latin accents while retaining Indic and other non-Latin scripts. It indexes Source 2/3 by country, normalized business name, and normalized address. Independent exact name and address routes retrieve bounded candidates from each target source. When these yield fewer than eight candidates, one rare address token and one rare name token (frequency 2–1,000 in the supplied target index) each add at most six per source. Every actual candidate is scored using name/address token overlap, character trigrams, and address-number agreement. The threshold 0.65 was selected only on a fixed Source 1 entity-level dev partition; identical normalized name/address groups remain together. The complete holdout was evaluated once at that frozen threshold.

The pipeline writes `matching_results.tsv` and `candidate_pairs.tsv`, then checks complete Source 1 coverage, valid target IDs and country, unique IDs, and `matches ⊆ candidates`. A separate strict scan confirms empty fields, candidate limits, and fresh file hashes. The supplied official validator passed against the complete test set. Large indexes stay outside the submission ZIP.

## Measured evidence and final choice

On the complete 44,098-anchor dev split, the combined primary reached macro F0.5 **0.560165** and link candidate recall **0.431252**, versus the preserved exact-route fallback's **0.497433** and **0.297894**. On all 44,212 untouched holdout anchors at dev-fixed thresholds, primary versus fallback macro F0.5 was **0.561627 versus 0.499692**, and recall **0.430373 versus 0.298817**. The primary uses more candidates (holdout mean **13.37 versus 3.63**, P99 **28 versus 13**); the official efficiency weighting is unknown. Complete primary inference covered **1,732,544** test anchors, scored **24,702,044** candidates (mean **14.26**, P99 **28**, max **31**), and passed the full independent ID/country/subset check, strict output sanity scan, and supplied validator. The original narrow outputs remain in `fallback/`; promoted files are in `best/` and `output/`. France has no labels, so no France accuracy or private-test score is claimed.

## Reproduction and deliverables

The runnable pipeline and exact commands are in `code/business_entity_resolution/README.md`. The package includes both output TSVs, source code, dependency/environment information, and the filled methodology template. The improved full outputs must pass the complete validator and separate target-ID existence check before promotion; otherwise the validated baseline is shipped.
