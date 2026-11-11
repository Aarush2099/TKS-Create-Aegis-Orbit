# Aegis Orbit

Aegis Orbit is a research project with two parts: a verified conjunction screening ledger for ESA collision-avoidance data, and a documented simulator study of a control-barrier shield.

This is research code. It is not a collision probability model, is not validated against real outcomes, and is not an operational avoidance screen or a removal design.

## 1. Screening ledger

The ledger ranks ESA Collision Avoidance Challenge conjunction events by miss distance.

- Keeps CDM rows with `time_to_tca` in [1, 3] days (inclusive).
- Produces one row per event, taken from the latest CDM inside the window.
- Ranks events by ascending `miss_distance_m`, with `event_id` as tie-break. Ranks are 1-based.

Verified numbers from recorded runs:

| Measure | Value |
|---|---|
| Archive rows | 162,634 |
| Distinct event_id values | 13,154 |
| Events with a row in [1, 3] days | 9,890 |
| Rows in [1, 3] days | 48,383 |
| Ranked events in export | 9,890 |
| Duplicate event_id values in export | 0 |
| Loader failures | 0 |

Baseline check: 1,051 positions differ between the ledger and a plain miss-distance sort. All of them have equal `miss_distance_m`, so the differences are tie-order only. This is a consistency check, not a performance claim.

Second-signal comparison: ranking the same 9,890 events by `relative_speed_mps` gives a top-20 overlap of 0 and a top-100 overlap of 1 with the miss-distance ranking. This is descriptive only; neither ordering is claimed to be better.

### Limits

- The archive is the unfiltered training set, not the competition test set.
- No comparison has been made to ground truth or to the competition's risk score.
- The data's redistribution terms are not confirmed beyond the competition's release, so the archive is not included here.

### Reproduce

Place the archive at `data/external/esa_cdm/train_data.zip`, obtained from the competition Data page. Then:

```powershell
python -m pip install -r requirements-dev.txt
python -m ledger.export --out ledger_output/ranked_events.csv
python -m pytest -m "not slow" -q
```

See `ledger/README.md` for details. Citation: Uriot et al., 2020, arXiv:2008.03069.

## 2. Shield feasibility study

The `aegis_orbit/` package contains an orbital relative-motion simulator, a soft actor-critic agent, and a control-barrier-function action filter. The study found that the shield was infeasible in every shield-on episode, so it did not demonstrate safe operation in the tested setting. Results are simulator results only. See `docs/shield_comparison.md` and `docs/unshielded_baseline.md`.

The physical `sigma_miss` estimate and derived safe radius remain unresolved placeholders.

## Repository layout

| Path | Contents |
|---|---|
| `ledger/` | Screening ledger: loader, validation, window filter, ranking, export |
| `aegis_orbit/`, `planning/`, `benchmarks/`, `configs/`, `scripts/` | Simulator and shield feasibility work |
| `results/` | Historical research outputs referenced by the docs |
| `docs/` | Research record and rules; `docs/cleanup/` holds internal audit files |
| `tests/` | Pytest suite |
| `data/` | Local external data, not tracked |

## License

MIT for this repository's code and documents (see `LICENSE`). The ESA archive is not covered by this license and is not included.
