# Proof-Carrying Control-Flow Rebalancing

This directory is the standalone executable supplement for **Fault-Frontier Certificates for Budgeted Guarded Rebalancing**. It implements the paper's finite snapshot-action semantics, exact admitted search for the private-leaf PFC1 grammar, canonical object encoding, certificate generation/checking, independent small-boundary tree-shape enumeration, deterministic bounded experiments, and stable-ID retained-input replay.

## Scope and trusted boundary

The model is intentionally finite and table based. For every entry input, each inherited action has an immutable Boolean guard and immutable silent, emission, or terminal-fault outcome. A false guard annuls the action before its outcome is evaluated. Emissions carry action identity. A fault terminates the region. A target uses inherited actions only, in a read-once entry-bit tree with private leaves.

The mathematical arguments in `proofs/core.md` establish the claims under those assumptions. The Python programs supply finite conformance checks, not proof-assistant output. The checker validates a PFC1 object against a supplied complete finite table and an external byte budget. It does not authenticate extraction from LLVM, MLIR, source code, or an exception ABI; verify Python; establish real instruction size; or provide processor-performance evidence.

Exactness is claimed only when the declared complete search is admitted. A candidate-space refusal is reported as `refused`, not as infeasibility. Tree search separately reports `optimal`, `infeasible`, or `incomplete`; diagnostic incomplete trees never carry an optimality claim.

## Requirements

- Python 3.11 or later, standard library only.
- A POSIX shell for the one-command reproduction.
- One worker; no GPU, network service, private data, model API, or external compute.

## Fast checks

Run from this directory:

```sh
python -m unittest discover -s tests -v
python -B -m unittest discover -s tests -p incidence_regression.py -v
python replay_inputs.py \
  --reference results/confirmed \
  --out results/reproduced-fast-input-replay.json
python verify_results.py \
  --reference results/confirmed \
  --candidate results/confirmed
```

The replay output must be a new path. The self-comparison is only a parser/comparison smoke check; the clean reproduction below is the scientific reproduction.

The scheduler builds reverse predecessor incidences once per selected set.
Each waiting condition is satisfied once, even when several alternatives emit;
a min-heap retains the smallest-ready order and the sorted closed residual.
The six additional pure incidence regressions use a bounded legal-prefix
enumerator and a direct two-row observation reference. They have an explicit
CI step; they do not replace the historical 38-test receipt or the full campaign.

## Clean reproduction

```sh
./reproduce-clean.sh
```

The script deliberately performs **no deletion**. Its four outputs must be new direct children of `results/`, must begin with `reproduced-`, and must not be symlinks, ancestors, retained results, or paths in another project. The defaults are:

```text
results/reproduced-clean/
results/reproduced-clean-presentation/
results/reproduced-clean-input-replay.json
results/reproduced-clean-verification.json
```

If those names already exist, select four fresh names explicitly:

```sh
./reproduce-clean.sh \
  results/reproduced-second \
  results/reproduced-second-presentation \
  results/reproduced-second-input-replay.json \
  results/reproduced-second-verification.json
```

The command runs the unit/regression suite, regenerates all twelve scientific phases in one bounded serial process, regenerates the targeted repair-validation report, compares deterministic JSON and every retained `.pfc` byte sequence with `results/confirmed/`, reloads all retained inputs by stable ID, and derives manuscript-facing tables/macros. Missing inputs, an empty corpus, unexpected IDs, a source/input binding mismatch, or an object-byte mismatch causes failure.

The checked-in `results/confirmed/` preserves an earlier source snapshot and its
original source/input binding. The strict historical comparison therefore does
not establish source-closed reproduction of the current implementation: source
changes cause a binding failure even when costs, statuses, and object bytes
agree. Do not rewrite the historical binding by hand or disable this gate.
For a source-closed current run on a POSIX host, use two fresh outputs:

```sh
python -B reproduce.py --out /tmp/pccfr-first
python -B reproduce.py --out /tmp/pccfr-second
python -B verify_results.py --reference /tmp/pccfr-first --candidate /tmp/pccfr-second
python -B replay_inputs.py --reference /tmp/pccfr-first --out /tmp/pccfr-input-replay.json
```

All four paths must be fresh. The prepared `scientific-checks.yml` workflow runs
this current-source protocol, the unit tests, and data derivation on Ubuntu
24.04 with a whole-run timeout and raw-output upload on failure. This is separate
from comparison with the historical snapshot; neither protocol certifies the
mathematical proofs.

## Evidence layers

The retained campaign keeps distinct evidence classes instead of combining them under one label:

- **1,061,510 direct semantic/frontier comparisons** in the bounded one-row family;
- **45,885 row-level witness-existence checks**;
- **45,885 actual PFC1 encode/decode/check-certificate replays**;
- **24,813 frontier rows and 24,813 direct-trace rows** reported by accepted object replays; rejected replays do not return these counters;
- **12,500 two-row boundary comparisons**;
- **130 optimizer comparisons against independent enumeration of every tree shape and direct leaf order** at the configured small boundary;
- **512 realized three-action waiting systems**, 2,978 semantic rows, and 3,072 per-permutation semantic comparisons;
- **1,094 nonempty simple graphs** on two through five vertices for the two-representative reduction check;
- **384 cross-mode leaf-optimum comparisons** and **4,686 completion/sparsification checks**;
- **30 directed controls**, accepted or rejected only when the expected outcome, checker stage, and rejection reason all match; and
- **391 retained exact input tables**, loaded and parsed by the campaign phase; its zero mismatch count concerns the identifier inventory. The standalone comparator checks retained costs/statuses and 130 PFC1 object byte sequences. Joint-search mode fields exist for the 57 feasible models, but are null for the 71 infeasible models; null-to-null comparison does not verify a selected mode.

These are bounded checks around mathematical proofs. They do not establish workload breadth, a production compiler result, or hardware benefit.

The current Ubuntu replay runs all 38 tests and the complete twelve-phase campaign twice. The two runs agree on 409 deterministic JSON files and 131 PFC byte objects. Replaying all 391 input tables independently reproduces 1,909 numeric checks and 130 emitted objects. The first campaign took 35.268 seconds wall time and 35.252 seconds driver-and-child CPU time, with a 28,172 KiB maximum process RSS. The run-matched records are in `results/measurements/current-linux/`; these host observations do not replace the historical campaign measurements.

`results/confirmed/provenance.json` binds the scientific source aggregate and exact retained input aggregate. `results/confirmed/repair-validation.json` preserves the requested search-mode, typed-signature, refusal-state, parser, golden-byte, source-type, and duplicate-action microexamples. Both files are generated by `reproduce.py`; they are not manually edited result summaries.

## Optimize and check one model

```sh
python run.py optimize results/confirmed/example/model.json --out /tmp/pccfr-example
python run.py check \
  results/confirmed/example/model.json \
  /tmp/pccfr-example/region.pfc \
  /tmp/pccfr-example/certificate.json \
  --budget "$(wc -c < /tmp/pccfr-example/region.pfc)"
```

Exit status 0 means acceptance. Exit status 2 is a structured rejection or explicit search refusal. See `docs/model-and-format.md` for the strict JSON, PFC1, bit-order, certificate, and budget contracts.

## Repository map

- `pccfr/`: semantics, frontier conditions, scheduling, exact search, independent small oracle, bytecode, certificates, provenance, and campaign phases.
- `tests/`: theorem-boundary, parser, refusal-state, stable-mode, and regression tests.
- `fixtures/golden-pfc1/`: independently hand-computable model, tree, and golden PFC1 bytes.
- `proofs/core.md`: mathematical theorem statements and proofs.
- `results/confirmed/`: historical retained inputs, objects, certificates, raw phase results, provenance, and repair validation, bound to their original source snapshot.
- `results/presentation/`: tables and TeX macros derived from confirmed JSON.
- `docs/model-and-format.md`: normative finite-model and PFC1 contract.
- `docs/evidence.md`: exact evidence reconciliation and remaining limitations.
- `docs/literature.md`: literature calibration and contribution boundary.
- `claim_evidence_ledger.csv`: material manuscript claims mapped to proofs and raw evidence.
- `external_resources.csv`: scholarly/software resources and their role.

## License

Original artifact code and documentation are under the MIT License in `LICENSE`. The ACM class and bibliography style are in the separate paper package under their upstream notices.
