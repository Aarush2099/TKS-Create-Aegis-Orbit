# Conjunction screening ledger rules

## 1. Purpose and non-claims

The ledger is a screening tool that ranks conjunction events by miss distance within a stated window. It is not a collision probability, has not been validated against real outcomes, and is not a removal design.
The archive's test split is filtered to CDMs within 1 day of TCA. This ledger uses the unfiltered training archive, so its results do not describe the competition's test set.

## 2. Data source

The planned data source is `data/external/esa_cdm/train_data.zip`, using its `train_data.csv` member, from the ESA Kelvins collision-avoidance archive.

Citation (requested by the competition organizers): Uriot, T., Izzo, D., Simoes, L., Abay, R., Einecke, N., Rebhan, S., Martinez-Heras, J., Letizia, F., Siminski, J. and Merz, K., 2020. Spacecraft Collision Avoidance Challenge: design and results of a machine learning competition. arXiv preprint arXiv:2008.03069. [https://arxiv.org/abs/2008.03069](https://arxiv.org/abs/2008.03069). The paper is described as under review in Astrodynamics; the journal version may differ from the preprint.

License: not stated on the competition pages checked on 2026-11-10. Use is pending confirmation from ESA’s Advanced Concepts Team.

## 3. Unit of analysis

Output unit: one row per event_id, taken from the CDM with the smallest time_to_tca inside the window. This is the latest CDM inside the window, not necessarily the latest CDM overall. Archive rows are CDMs, not events; counting CDMs would double-count events.

## 4. Window

The screening window is `time_to_tca` in `[1, 3]`, inclusive. time_to_tca is in days, per the dataset description.

The window includes 2 to 3 days before TCA, where the competition's test data has no CDMs. The ledger is a research screen, not an operational avoidance screen.

Rows with time_to_tca below 1 are excluded, including negative values (closest approach already passed). The archive contains negative values, so this exclusion is active.

## 5. Column mapping

| Archive header | Ledger field | Notes |
|---|---|---|
| `event_id` | `event_id` | Event identifier |
| `mission_id` | `satellite_id` | Protected object, not debris |
| `time_to_tca` | `time_to_tca` | Days, per dataset description |
| `miss_distance` | `miss_distance_m` | Meters, per dataset description |
| `relative_speed` | `relative_speed_mps` | m/s, per dataset description |
| `c_object_type` | `chaser_object_type` | Stratification only |

`risk` and `max_risk_estimate` are not used for ranking and are not reported as probability.

## 6. Ranking rule

Before any run, the ranking rule is ascending `miss_distance_m`, with `event_id` as the tie-break. A benchmark against a plain miss-distance ordering is planned but has not been run.

## 7. Gates for later steps

The window filter must report its excluded count. No `event_id` may appear twice in the output. Any row that fails validation must be reported by name, not silently dropped.

## 8. Observed archive totals (evidence, not documentation)

The archive contains 162,634 data rows and 13,154 distinct `event_id` values. There are 9,890 `event_id` values with at least one row in `[1, 3]`, 48,383 rows in `[1, 3]`, and 12,929 `event_id` values with more than one row.

The ledger output cannot exceed 9,890 events under the current window.

## 9. Open items before release

1. Confirm data-redistribution terms with ESA’s Advanced Concepts Team.
2. Confirm the upstream license terms.

## 10. Loader

The loader reads `train_data.csv` from the zip in memory and writes no files. It maps the headers as described in section 5 and reports unparseable fields as failures rather than dropping them.

## 11. Ranking output

Ranking is ascending `miss_distance_m` with `event_id` as the tie-break, and rank is 1-based. The export is written by `ledger.export` and refuses to overwrite an existing file. The baseline comparison reports tie-order differences only.

## 12. Second-signal comparison

The comparison uses `relative_speed_mps` with the same `event_id` tie-break. Results are descriptive overlap counts; neither ordering is claimed to be better. This comparison makes no performance claim.
