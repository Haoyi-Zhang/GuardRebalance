# Proof-Carrying Control-Flow Rebalancing

This repository is the anonymous executable supplement for **Fault-Frontier Certificates for Budgeted Guarded Rebalancing**. It implements the finite snapshot-action semantics, exact bounded optimizer, canonical region bytecode, proof-certificate generator, independent safety checker, deterministic campaign, retained input replay, and manuscript-data derivation.

## What is and is not proved

The handwritten argument in `proofs/core.md` proves the stated mathematical results for a finite snapshot-action model: guards and primitive outcomes are fixed by the entry input; a false guard annuls an action before its raw outcome is evaluated; emissions carry action identities; faults terminate the region; and the target may only retain inherited actions in a read-once entry-bit decision tree with private leaves. The Python implementation is **not** proof-assistant verified. Its tests and campaigns are finite conformance evidence, not a general proof.

The checker certifies observational equivalence of a supplied canonical object to a supplied finite semantic table and enforces an external byte budget. It does not authenticate compiler-to-model extraction, establish that the table is complete for a real exception ABI, verify Python itself, or certify object optimality. The optimizer is complete only for the declared grammar and configured admitted search space. Candidate spaces above the configured limit are rejected before search; rejection is not an infeasibility result.

## Requirements

* Python 3.11 or later; standard library only.
* One process is sufficient. The retained campaign was run serially with one worker.
* No GPU, network service, private data, or model API is used.

## Fast checks

From this directory:

```bash
python -m unittest discover -s tests -v
python replay_inputs.py \
  --results results/confirmed \
  --out results/input-replay.json
python verify_results.py \
  --reference results/confirmed \
  --candidate results/confirmed
```

The last command is a structural self-comparison smoke check. For an actual clean reproduction, use a new output directory as shown below.

## Complete clean reproduction

The one-command route is:

```bash
./reproduce-clean.sh
```

The equivalent explicit commands are:

```bash
rm -rf results/reproduced
mkdir -p results/reproduced
python reproduce.py --out results/reproduced
python verify_results.py \
  --reference results/confirmed \
  --candidate results/reproduced
python replay_inputs.py \
  --results results/reproduced \
  --out results/reproduced-input-replay.json
python paper_data.py \
  --results results/reproduced \
  --out results/reproduced-presentation
```

`reproduce.py` runs twelve deterministic phases sequentially. The one-command driver runs all phases sequentially in one single-threaded process under a 3.5 GiB virtual-address and 30-minute CPU ceiling. Each phase is also independently runnable through `experiment.py`, which applies the same ceilings. This avoids `preexec_fn` and fixed-CPU pinning while preserving resumable chunks. The complete campaign is far below these ceilings on the retained run. If an interactive host imposes a shorter wall-time than the documented command, every phase is independently resumable:

```bash
for phase in exhaustive two-state trees and-or graphs observer-gap \
             baselines controls search padding many-relevant retained-input-replay; do
  python experiment.py "$phase" --out results/reproduced
done
```

After split execution, run `python reproduce.py --out results/reproduced` only when the host permits a single uninterrupted command; otherwise compare the twelve phase files and retained inputs with `verify_results.py`. The supplied `results/confirmed/summary.json` records the retained phase-body resource totals and explicitly marks unavailable aggregate-driver timings rather than inventing them.

## Optimize and check one model

```bash
python run.py optimize results/confirmed/example/model.json --out /tmp/pccfr-example
python run.py check \
  results/confirmed/example/model.json \
  /tmp/pccfr-example/region.pfc \
  /tmp/pccfr-example/certificate.json \
  --budget "$(wc -c < /tmp/pccfr-example/region.pfc)"
```

Exit status 0 means the object/certificate passed; status 2 means either the checker rejected or the optimizer explicitly refused an over-limit search. See `docs/model-and-format.md` for the exact JSON and bytecode contracts.

## Retained evidence

The confirmed campaign contains 391 exact JSON semantic tables and twelve result phases. Its material counts are:

* 1,061,510 direct semantic comparisons and 45,885 certificate comparisons in the one-state exhaustive family;
* 12,500 complete two-state/two-action boundary comparisons;
* 130 private-tree optima compared with an independently enumerated direct-leaf oracle;
* 512 three-node AND/OR systems and all 1,094 nonempty simple graphs on two through five vertices;
* 384 exact optimum comparisons across three leaf-search modes and 4,686 completion/sparsification checks;
* 30 directed semantic/format/budget controls (three expected accepts and 27 expected rejects);
* 391 retained-input tables reloaded without pseudorandom regeneration; and
* zero recorded disagreement in the declared campaign.

These counts are bounded checks, not claims of production-workload breadth. Raw JSON, object/certificate bytes, manuscript-facing CSV files, and exact fixed seeds are retained under `results/`.

## Repository map

* `pccfr/`: semantics, frontier constraints, known AND/OR scheduling, exact search, bytecode, certificates, generators, and campaign phases.
* `tests/`: boundary and regression tests.
* `proofs/core.md`: handwritten theorems and proofs.
* `results/confirmed/`: exact retained inputs and raw confirmation results.
* `results/presentation/`: tables/macros derived from raw results.
* `docs/model-and-format.md`: model, object, budget, and certificate formats.
* `docs/evidence.md`: result reconciliation and limitations.
* `docs/literature.md`: research calibration and novelty boundary.
* `claim_evidence_ledger.csv`: manuscript claims mapped to proofs and raw evidence.
* `external_resources.csv`: external scholarly/software resources and integration status.

## Research provenance and external use

Generative AI was used substantively in the research lifecycle, including formulation, literature retrieval and synthesis, handwritten proof construction, code and test generation, experiment execution, analysis, manuscript preparation, and internal validation. No external model API or learned-model experiment was used. Any external use must be reviewed by accountable human authors and must satisfy the then-current venue rules for authorship, AI-use disclosure, originality, and artifact claims. This repository does not assert independent blind review, submission, acceptance, or compiler production readiness.

## License

The original repository code and documentation are released under the MIT License in `LICENSE`. The copied ACM class, bibliography style, and template license belong to the paper package and retain their upstream notices; they are not relicensed by this repository.

## Reviewer-oriented audit

Run the offline audit after the normal reproduction:

```sh
./artifact/audits/run-reviewer-audit.sh
```

The audit checks bibliography closure and cached identity evidence, test and implementation structure, theorem/proof traceability, experiment-result provenance, paper-number provenance, and PDF integrity.  These checks are internal evidence, not external peer review or an acceptance guarantee.

