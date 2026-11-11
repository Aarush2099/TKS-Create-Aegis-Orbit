# Conjunction screening ledger

## What it is

A screening ledger that ranks ESA CDM conjunction events by miss distance within `time_to_tca` in `[1, 3]` days. It produces one row per event, using the latest in-window CDM.

## What it is not

It is not a collision probability, a prediction of the competition's final risk, a result validated against real outcomes, an operational avoidance screen, or a removal design.

## Data

The archive `data/external/esa_cdm/train_data.zip` is not included in Git. Obtain it from the competition Data page and place it at that path. The source is the ESA Advanced Concepts Team collision avoidance challenge; the citation is Uriot et al. 2020 (arXiv:2008.03069). See [the ledger rules](../docs/ledger_rules.md#2-data-source).

## Reproduce

Run `python -m ledger.export --out ledger_output/ranked_events.csv`.

Expected output: 9,890 rows, 0 duplicate `event_id` values, and 0 loader failures. The export refuses to overwrite an existing output file.

## Tests

Run `python -m pytest -m "not slow" -q`.

## Limits

The window is inclusive. The archive is the unfiltered training set, not the competition test set. The baseline check reports tie-order differences only and is a consistency check, not a performance claim.
