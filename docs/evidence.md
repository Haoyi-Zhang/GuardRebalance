# Evidence reconciliation

## Confirmed campaign

`results/confirmed/` is the retained scientific record. The aggregate summary reports twelve serial phases, 17.303812678 cumulative phase-body CPU seconds, a maximum process high-water mark of 97,324 KiB, one worker, and zero mismatches. Aggregate driver wall/CPU timings are deliberately null because the interactive execution host split the original driver at its own wall boundary; individual phase measurements and all deterministic scientific outputs are retained. This omission is not replaced by an estimate.

| Phase | Claim attacked | Exact retained result |
|---|---|---|
| `exhaustive` | frontier theorem and certificate replay on all bounded one-state profiles/orders | 1,061,510 semantic and 45,885 certificate comparisons; 0 mismatches |
| `two-state` | interaction across two rows rather than duplicated one-state checks | 12,500 comparisons; 0 mismatches |
| `trees` | private-tree dynamic program vs independently enumerated direct-leaf oracle | 130 instances; every object cost equal |
| `and-or` | representation of all three-node waiting systems | 512 families; 0 mismatches |
| `graphs` | two-representative selection vs minimum vertex cover | all 1,094 nonempty simple graphs on 2--5 vertices; 0 mismatches |
| `observer-gap` | exact coarse/refined byte formula | `12` vs `8*2^b+4` for b=0,1,2,3 |
| `baselines` | meaning of the declared byte objective | 64 paired models, retained raw records |
| `controls` | semantic, object, certificate, and budget rejection | 3 expected accepts, 27 expected rejects; all classified correctly |
| `search` | optional-subset, representative-tuple, and automatic exact search | 384 optimum comparisons and 4,686 completion/sparsification checks; 0 mismatches |
| `padding` | irrelevance of latent silent/disabled actions | 64 instances, including 128/512/2048-action strata; 0 mismatches |
| `many-relevant` | explicit complete-search admission/refusal | 11 admitted methods and 4 pre-search refusals; 0 mismatches |
| `retained-input-replay` | independence from pseudorandom regeneration | 391 exact JSON tables loaded; 0 mismatches |

The separate top-level `results/input-replay.json` was produced by reading those 391 retained inputs directly. It records 130 tree instances, 64 baseline models, 128 joint leaf models, 64 padding models, five many-relevant models, 384 method/optimum matches, 11 admitted many-relevant runs, four explicit candidate-space refusals, and zero mismatches.

## Claim-to-result reconciliation

* Theorems 1--7 and Lemmas 8--9/Theorem 10 are handwritten general arguments in `proofs/core.md`. No executable count is offered as their proof.
* The executable campaign is a falsification/conformance layer. Direct semantics, frontier constraints, object decoding, certificate replay, exact search, and negative controls are implemented through separate functions and compared where practical.
* The tree oracle shares the semantic model but independently enumerates direct leaf sequences rather than using frontier constraints. It is independent enough to attack the optimizer logic, not independent software verification.
* The graph phase checks the reduction on every small graph but does not establish NP-completeness; the reduction proof does.
* The observer-gap phase confirms four representable instances; the formula follows from the proof and fixed byte grammar.
* Resource measurements establish that the declared bounded campaign fits the stated CPU/RAM envelope. They do not compare compiler speed, certificate efficiency, or hardware performance.

## Negative controls

The seven semantic rejects cover deleting a live emission, deleting the only required fault, reversing visible emissions, faulting before the required prefix, changing a fault signature, exposing a suppressed suffix event, and exchanging fault origins when the observer exposes origin. The three benign accepts cover equal complete signatures, a disabled fault, and deletion of a silent action. The remaining twenty controls attack cell coverage, input coverage, witness identity, length declarations, external budgets, headers, truncation, trailing bytes, opcodes, duplicate identities, guard masks, canonical mask omission, and repeated branch tests.

## Limitations that remain true

There is no production compiler pass, source/IR extractor, real exception ABI model, processor benchmark, instruction-cache measurement, liveness reconstruction, mutable memory, handler/resumption semantics, irreducible control flow, loops, concurrency, or undefined-behavior semantics. The private-leaf object grammar excludes shared suffixes and synthesized predicates. The bibliography comparison supports a precise combination-of-features claim, not a universal priority claim. External submission requires accountable human review of the proofs, code, related-work conclusions, authorship, and AI-use disclosure.
