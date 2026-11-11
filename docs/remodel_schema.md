# ADRV Planning Schema Contract

This document defines the input and output data shapes for the planning layer.
It does not specify a planner implementation.

## Target input

Each target is a JSON object with the following fields. Every value has a
corresponding `_source` field that identifies its provenance.

| Field | Type | Units / meaning |
|---|---|---|
| `object_id` | string | Identifier; no physical units |
| `object_id_source` | string | Provenance for `object_id`; no physical units |
| `mass_kg` | number | Kilograms (kg) |
| `mass_kg_source` | string | Provenance for `mass_kg`; no physical units |
| `altitude_km` | number | Kilometers (km) |
| `altitude_km_source` | string | Provenance for `altitude_km`; no physical units |
| `inclination_deg` | number | Degrees (deg) |
| `inclination_deg_source` | string | Provenance for `inclination_deg`; no physical units |
| `tumble_rate_deg_s` | number or null; optional, defaults to null | Degrees per second (deg/s); null means unknown |
| `tumble_rate_deg_s_source` | string | Provenance for `tumble_rate_deg_s`, including the basis for an unknown value; no physical units |

## Vehicle input

Each vehicle is a JSON object with the following fields and a corresponding
source field for each value.

| Field | Type | Units / meaning |
|---|---|---|
| `vehicle_id` | string | Identifier; no physical units |
| `vehicle_id_source` | string | Provenance for `vehicle_id`; no physical units |
| `dry_mass_kg` | number | Kilograms (kg) |
| `dry_mass_kg_source` | string | Provenance for `dry_mass_kg`; no physical units |
| `delta_v_budget_mps` | number | Meters per second (m/s) |
| `delta_v_budget_mps_source` | string | Provenance for `delta_v_budget_mps`; no physical units |
| `u_max_mps2` | number | Meters per second squared (m/s^2) |
| `u_max_mps2_source` | string | Provenance for `u_max_mps2`; no physical units |

`delta_v_budget_mps` and `u_max_mps2` are user-supplied scenario inputs. They are not validated propulsion values. Each must carry a `_source` entry stating where the user obtained it, or the literal text `user assumption`.

## `plan.json` output

The output is a JSON object with these fields:

| Field | Type | Units / meaning |
|---|---|---|
| `sequence` | array of strings | Ordered target `object_id` values; identifiers have no physical units |
| `legs` | array of objects | One object per transfer leg |
| `legs[].delta_v_mps` | number | Per-leg delta-v in meters per second (m/s) |
| `feasible` | boolean | Planning feasibility flag; no physical units |
| `assumptions` | array of strings | Assumption descriptions; no physical units |
| `config_sha256` | string | SHA-256 digest of the configuration; hexadecimal, no physical units |
| `seed` | integer | Random seed; no physical units |

## `trajectory.csv` output

The CSV header is:

```csv
step,time_s,sat_x_m,sat_y_m,sat_z_m,deb_x_m,deb_y_m,deb_z_m,rel_distance_m,thrust_x_mps2,thrust_y_mps2,thrust_z_mps2,shield_mode,collided
```

| Field | Units / meaning |
|---|---|
| `step` | Simulation step index; no physical units |
| `time_s` | Seconds (s) |
| `sat_x_m`, `sat_y_m`, `sat_z_m` | Satellite position components in meters (m) |
| `deb_x_m`, `deb_y_m`, `deb_z_m` | Debris position components in meters (m) |
| `rel_distance_m` | Relative distance in meters (m) |
| `thrust_x_mps2`, `thrust_y_mps2`, `thrust_z_mps2` | Thrust/acceleration components in meters per second squared (m/s^2) |
| `shield_mode` | Shield mode identifier; no physical units |
| `collided` | Boolean collision indicator; no physical units |

## Limits

- Simulation only.
- The shield is a documented infeasible-regime finding.
- `sigma_miss` and safe radius are unresolved.
- No propulsion values are validated.
