# Remodel Baseline

## Repository state

`git status --short` printed no entries.

`git log --oneline -5` printed:

```text
033ad3e Publish all research artifacts
e32b8b0 Initial research release: calibrated SAC baseline and shield feasibility audit
```

Commit: `033ad3e`

`git lfs ls-files` listed 5 entries:

```text
68362fe562 * data/external/esa_cdm/train_data.zip
aace1fb962 * results/rerun_primary_20261014/stability_log.csv
0072302b75 * results/shield_comparison_20261014/shield_comparison_steps.csv
89e42cf44f * results/shield_comparison_cw_vs_j2_20261014/shield_comparison_steps.csv
a60e222c34 * results/stability_log.csv
```

The data archive `train_data.zip` has length 87,718,091 bytes, a real-sized file rather than a pointer. The largest `.pt` file is `results/rerun_primary_20261014/policies/sac_primary_seed4_step180000.pt`; it has length 286,643 bytes, a real-sized file rather than a pointer.

## Environment

`.venv\Scripts\python.exe --version` printed:

```text
Python 3.14.6
```

Versions from `.venv\Scripts\python.exe -m pip list`:

| Package | Version |
|---|---|
| numpy | 2.5.4 |
| torch | 2.14.1 |
| scipy | 1.18.1 |
| pytest | 9.1.1 |
| PyYAML | 6.0.3 |

The following `.gitignore` entries were present:

```text
.venv/
__pycache__/
.pytest_cache/
*.pt
```

## Test baseline

Fast suite, `.venv\Scripts\python.exe -m pytest -m "not slow" -q`:

```text
93 passed, 7 deselected in 18.18s
```

Slow suite, `.venv\Scripts\python.exe -m pytest -m slow -q`:

```text
1 failed, 6 passed, 93 deselected in 116.65s (0:01:56)
```

Failing test: `tests/test_runner_smoke.py::test_runner_writes_all_artifacts_only_to_configured_output`

First error line:

```text
E       assert "oracle_avoidable_subset,label=oracle finite-search ceiling, not a policy result" in output
```

This is a baseline record before the ADRV planning remodel. It makes no claim about performance.

## Slow suite failure diagnosis

Captured full pytest output: `%TEMP%\slow_suite_20261107_190025.log`

Failing test node id:

```text
tests/test_runner_smoke.py::test_runner_writes_all_artifacts_only_to_configured_output
```

First error line, verbatim:

```text
E   assert 'oracle_avoidable_subset,label=oracle finite-search ceiling, not a policy result' in '[0.0s] oracle pre-flight passed passive_collision_count=69 oracle_avoidable_count=69 minimum_margin_m=0.426314 prefli...t_min_distance_m\r\noracle_avoidable_subset,"oracle finite-search ceiling, not a policy result",2,2,1.0000,10.9235\r\n'
```

Classification: **oracle or pre-flight**. The test file is [`tests/test_runner_smoke.py`](../tests/test_runner_smoke.py); the failing assertion checks the emitted `oracle_avoidable_subset` output line.

The slow run reported `1 failed, 6 passed, 93 deselected in 117.74s (0:01:57)`. The failure does not involve a time limit, missing file, or missing LFS file.

The fast suite passed. The slow suite did not pass; these are the failing tests. No fix has been applied in this record.

## Addendum: slow-suite correction

The stale assertion in `tests/test_runner_smoke.py` was an unquoted-string check that no longer matched the quoted CSV output from the CSV-format fix. It was replaced with a parsed-field check on `oracle_summary.csv`.

After the correction: fast suite 93 passed, 7 deselected; slow suite 7 passed, 93 deselected (136.83 s); smoke tests 2 passed.

The earlier slow-suite failure is resolved by a test correction. No runner, config, physics, or result file was changed.
