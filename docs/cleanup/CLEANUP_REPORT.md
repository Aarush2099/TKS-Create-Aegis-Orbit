# AegisOrbit Public-Release Hygiene Report

**Scope:** inventory, hygiene, defect scan, module entry points, dependency metadata,
and an editable install check. No physics, training parameters/band, rewards,
collision definitions, shield mathematics, official config, `data/`, or
`results/` files were changed. Git was initialized solely for the requested
dry-run add inspection. No files are staged, committed, or pushed.
The per-file repository path/size/disposition listing is in
[CLEANUP_TREE.csv](CLEANUP_TREE.csv); large local virtualenv/cache internals
are summarized separately rather than expanded into the listing.

## Inventory and Release Size

Top-level source tree after cleanup (counts exclude generated cache directories
where stated):

| Path | Files | Size or contents |
|---|---:|---:|
| `aegis_orbit/` | 18 source files | 49,454 bytes, excluding bytecode |
| `benchmarks/` | 12 source files | 126,900 bytes, excluding bytecode |
| `configs/` | 2 | 5,839 bytes |
| `data/` | 1 | ESA archive only, 87,718,091 bytes |
| `docs/` | 10 | 45,693 bytes |
| `results/` | 197 | 855,043,880 bytes |
| `scripts/` | 6 source/PowerShell scripts | 47,224 bytes, excluding bytecode |
| `tests/` | 30 source files | 82,707 bytes, excluding bytecode |
| Root metadata/docs | README, setup, pyproject, requirements, ignore rules, cleanup audit files | See release-size totals below |

There are 62 Python files across the package, benchmarks, scripts, tests, and
`setup.py`. The final on-disk tree totals 26,113 files / 1,805,195,600 bytes,
including Git metadata, the local virtual environment, and historical
result/data artifacts.
The main excluded groups, counted once, are:

| Excluded group | Files | Bytes |
|---|---:|---:|
| `.venv/` | 25,733 | 861,243,116 |
| `.git/` metadata | 18 | 27,252 |
| `results/` | 197 | 855,043,880 |
| `data/external/esa_cdm/` | 1 | 87,718,091 |
| Python bytecode caches | 68 | 689,597 |
| `.pytest_cache/` | 5 | 9,248 |
| **Unique excluded total** | **26,022** | **1,804,731,184** |

There are 25 checkpoint `*.pt` files and 13 result log/error files; these are
already inside the excluded `results/` total and are not double-counted. There
are 80 CSVs in the workspace; 9 under `results/` exceed 1 MiB, totaling
841,594,081 bytes. No `.DS_Store` or `Thumbs.db` was present. The
pre-exclusion release-candidate filesystem estimate was **91 files /
464,416 bytes**, including the README, license, report, and audit ledgers. The
five internal reports and ledgers are now excluded from the public add set;
the current dry-run Git list is authoritative for the included-file count.

`.gitignore` was updated to ignore virtualenvs, Python/pytest caches, egg-info,
checkpoints, `/results/`, the downloaded dataset directory, logs/errors, and
OS metadata files. The blanket `*.csv` rule was removed, so future source/test
CSVs are not hidden. I verified the patterns in a disposable Git repository:
result/data/cache/checkpoint/log/OS files were ignored and a test CSV remained
visible.

## Defect Scan

- Full fast suite before cleanup: **90 passed, 7 deselected**. Final post-cleanup
  result is recorded below.
- Ruff and Pyflakes are not installed. `py_compile` succeeded for all 62 Python
  files with no syntax failures; VS Code diagnostics reported no errors.
  `py_compile` does not detect unused imports or unreachable code, and no
  dedicated linter was available, so those checks are not claimed as complete.
  No undefined-name diagnostics were reported by the available editor
  diagnostics.
- No `TODO`, `FIXME`, or `XXX` markers were found in source/docs. No
  code-like commented-out blocks were found.
- Active source/docs contain no hard-coded absolute paths. Seven absolute
  Windows-path matches remain in two immutable historical files under
  `results/` (`seed4_logging_rerun_20261016/launcher_attempt1.err` and
  `shield_comparison_cw_vs_j2_20261014/RESULTS_HASHES.txt`); they are not
  runtime references and were not edited.
- Five test-only debug prints were removed, including an unused `capsys`
  parameter. The remaining 34 `print()` calls are intentional CLI/progress or
  numerical-test output, listed in [CLEANUP_OUTPUTS.csv](CLEANUP_OUTPUTS.csv).
- The scan found 73 policy-sensitive wording lines in Markdown and Python
  docstrings. The line-by-line ledger is [CLEANUP_CLAIMS.csv](CLEANUP_CLAIMS.csv):
  66 are qualified parameter/model terminology (including explicitly labeled
  parameter sweeps and mathematical “safe set” definitions); 7 are explicit
  limitations or negations. No `realistic`, `flight-grade`, or `100%` claim
  was found. Two ambiguous phrases were corrected: “validated CW
  environment” is now “CW base environment,” and “production comparison grid”
  is now “default comparison grid.” No real-world safety claim was promoted.
- Existing stale/superseded snapshot:
  `results/superseded/20261011_143208/` contains a CSV and PNG. It remains in
  place: moving it would modify `results/`, which is explicitly prohibited by
  the hash-preservation requirement. No result was deleted, moved, or archived.

## Entry Points and Dependencies

All 11 argparse-based CLI modules passed `python -m <module> --help` from the
repository root: `benchmarks.check_gates`, `benchmarks.check_shield_gates`,
`benchmarks.run_seed4_logging_rerun`, `benchmarks.run_shield_comparison`,
`benchmarks.run_unshielded_benchmark`, `benchmarks.shield_grid`,
`benchmarks.verify_policies`, `benchmarks.perturbation_sensitivity`,
`scripts.run_cbf_root_cause`, `scripts.run_sigma_miss_baseline`, and
`scripts.trace_original_scenario`.
`benchmarks.oracle_reference` ran successfully with its finite five-seed
output. `benchmarks.check_safe_set` ran and returned its expected blocked exit
code 2 because `sigma_miss_m` remains null. The perturbation smoke ran from the
repository root with a temporary `--output-dir`, refused overwrite semantics,
and produced the CSV/PNG there. Its five mean minimum distances were 91.103800 m
(CW), 91.140664 m (CW+J2), 91.099918 m (CW+drag nominal), 91.096165 m
(CW+drag storm peak), and 91.133030 m (CW+J2+drag+storm). These are historical
sensitivity outputs from hypothetical perturbation settings, not physical
validation.
`benchmarks.baselines` is a helper module without a `__main__` entry point,
not a command-line script.

External imports found in source are NumPy, SciPy, Torch, PyYAML, and pytest.
The runtime requirements cover NumPy (`>=1.24`), SciPy (`>=1.10`), Torch
(`>=2.0`), and PyYAML (`>=6.0`). Developer requirements include pytest
(`>=7.0`) and setuptools (`>=64`) for editable-build support. `setup.py` now
reads runtime dependencies from `requirements.txt` into package metadata.

`pip install -e .` succeeded in a fresh temporary virtual environment; imports
of `aegis_orbit`, NumPy, SciPy, Torch, and PyYAML succeeded. Installed versions
were NumPy 2.5.4, SciPy 1.18.1, Torch 2.14.1+cpu, and PyYAML 6.0.3; `pip check`
reported no broken requirements. Generated egg-info and the temporary audit
artifact were removed from the workspace after verification.

## Changes Made

- `.gitignore`: scoped generated-artifact exclusions; removed global CSV hiding;
  added logs, OS files, results/data, and egg-info rules.
- `setup.py`: include the existing runtime requirements in package metadata.
- `requirements-dev.txt`: declare `setuptools>=64` for editable builds.
- `benchmarks/perturbation_sensitivity.py`: require `--output-dir` and refuse
  to overwrite existing artifacts.
- `README.md`: document installation, tests, missing reproduction artifacts,
  and the perturbation command with explicit output destination.
- `LICENSE`: add the MIT License with Aarush Amit Mahajan as copyright holder;
  contributors should confirm they have authority to license their work.
- `aegis_orbit/envs/perturbed_conjunction.py` and
  `benchmarks/run_shield_comparison.py`: qualify two ambiguous docstrings.
- `tests/test_env_reference.py`, `tests/test_j2_relative.py`,
  `tests/test_perturbed_conjunction.py`, and `tests/test_cbf_shield.py`: remove
  test-only diagnostic prints; remove unused `capsys` fixture parameter.
- `CLEANUP_REPORT.md`, `CLEANUP_TREE.csv`, `CLEANUP_RESULTS_HASHES.csv`,
  `CLEANUP_CLAIMS.csv`, and `CLEANUP_OUTPUTS.csv`: retain these internal
  reports and ledgers locally; they are excluded from the public release.

No source logic, physical/model parameters, reward weights, collision radius,
training band, shield equations, configs, dataset files, or historical results
were changed.

## Results Preservation

Before editing, SHA-256 and size were captured for every file under `results/`.
After cleanup: **197/197 paths are identical, 0 added, 0 removed, 0 changed**;
total size remains **855,043,880 bytes**. The per-file before/after digest and
size are in [CLEANUP_RESULTS_HASHES.csv](CLEANUP_RESULTS_HASHES.csv).

The protected config hash is unchanged:
`098391214ac211765190e2c84b81f60a51ee5c8d9d5ce4cf3aa5eae5c2ec6426`.
The ESA archive was not changed: 87,718,091 bytes,
SHA-256 `68362fe5629cc80f17291f2d73f733bf4e922675e37b91a8ee79afadb46f3edc`.
Git was initialized solely for the requested dry-run add inspection. No files
are staged, and no commit or push was performed.

## Git Dry Run

`git init -b main` was run, followed by `git add -n .`. The original dry run
listed **91 paths**. The subsequent public-release decision excludes the five internal reports and
ledgers listed above and personal `.vscode/settings.json`, leaving **85
paths**. Their prior release-candidate markings in `CLEANUP_TREE.csv` are not
the final public scope. Git ignores all six paths; the index remains empty. No
files were staged, and no commit or push was performed.

## Final Validation

- `python -m pytest -m "not slow" -q`: **90 passed, 7 deselected**.
- `py_compile`: **62 files compiled, 0 failures**.
- VS Code diagnostics: **no errors**.
- Module help/entry-point checks: passed as listed above; `check_safe_set` is
  intentionally blocked by unresolved `sigma_miss_m`.
- Fresh editable install and `pip check`: passed.
- Results hashes and protected config hash: unchanged.
