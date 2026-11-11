# Project summary

## What this project is

This project includes a screening ledger that ranks ESA Collision Avoidance Challenge CDM conjunction events by miss distance, using `time_to_tca` in `[1, 3]` days and one row per event (the latest in-window CDM). It also includes a separate simulator and shield feasibility study; see [docs/shield_comparison.md](docs/shield_comparison.md).

## What it is not

It is not a collision probability, a prediction of the competition's final risk, a result validated against real outcomes, an operational avoidance screen, or a removal design.

## Verified numbers

| Measure | Recorded value |
|---|---:|
| Archive rows | 162,634 |
| Distinct `event_id` values | 13,154 |
| Events with at least one row in `[1, 3]` days | 9,890 |
| Rows in `[1, 3]` days | 48,383 |
| Ranked events in export | 9,890 |
| Duplicate `event_id` values in export | 0 |
| Loader failures | 0 |
| Baseline comparison positions differing | 1,051, all with equal `miss_distance_m` (tie-order only) |

## Second-signal result

Ranking by `relative_speed_mps` versus miss distance over the same 9,890 events gives a top-20 overlap of 0 and a top-100 overlap of 1. This is descriptive only; neither ordering is claimed to be better.

## Limits

The archive is the unfiltered training set, not the competition test set. The window is inclusive. The baseline is a consistency check. The archive's data terms are unresolved, and the repository is private. The archive remains in Git history.

## Reproduce

Run:

```text
python -m ledger.export --out ledger_output/ranked_events.csv
python -m pytest -m "not slow" -q
```

Expected test result: 153 passed, 7 deselected. See [ledger/README.md](ledger/README.md).

## Repository layout

See the [Repository layout](README.md#repository-layout) section in `README.md`.
