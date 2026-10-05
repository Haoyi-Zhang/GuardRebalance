# Evidence reconciliation

## Evidence classes

The artifact separates general proof, bounded direct comparison, row-level witness checking, serialized object replay, exact optimization comparison, malformed-input controls, and retained-input reproduction. Counts from different classes must not be added together or relabeled as one another.

| Phase | Question attacked | Retained result |
|---|---|---|
| `exhaustive` | direct semantics versus the fault-frontier theorem, plus witness and serialized-certificate coverage | 1,061,510 direct comparisons; 45,885 witness checks; 45,885 encode/decode/check replays; 24,813 frontier rows and 24,813 direct rows; 0 mismatches |
| `two-state` | cross-row interaction rather than duplicated one-row checks | 12,500 comparisons; 0 mismatches |
| `trees` | production DP versus independent enumeration of every read-once tree shape and direct leaf order | 130 instances; equal optimum/status in every instance; 130 retained PFC1 objects |
| `and-or` | semantic realization of every three-node waiting-condition family | 512 models, 2,978 rows, 3,072 permutation comparisons, 121 feasible families; 0 mismatches |
| `graphs` | two-representative selection versus minimum vertex cover at the small boundary | all 1,094 nonempty simple graphs on 2--5 vertices; 0 mismatches |
| `observer-gap` | fixed-grammar formula under coarse versus origin-refined faults | four representable widths, matching 12 versus `8*2^b+4` |
| `baselines` | exact private tree, fully split, branchless status/cost, and refined-observer cost | 64 retained models |
| `controls` | semantic, object-format, certificate, and external-budget rejection | 3 expected accepts and 27 expected rejects; exact outcome, stage, and reason matched in all 30 |
| `search` | optional-subset, representative-tuple, and automatic leaf search | 384 cost/infeasibility comparisons and 4,686 completion/sparsification checks; actual modes retained for 57 feasible models and null for 71 infeasible models; 0 mismatches |
| `padding` | independence from latent silent/disabled actions after semantic sparsification | 64 models including 128/512/2,048-action strata; 0 mismatches |
| `many-relevant` | complete-space admission and refusal | 11 admitted method/instance pairs and 4 explicit refusals; 0 mismatches |
| `retained-input-replay` | stable-ID loading rather than pseudorandom regeneration | exactly 391 inputs present and parsed; no missing or unexpected ID |

The `n=4` one-row certificate protocol covers every ordered subset for every enumerated profile. For `n=5`, the direct semantic/frontier phase still examines all ordered subsets, while serialized certificate replay covers the source order of every profile. The 45,885 witness checks and 45,885 serialized object replays are separate activities, even though their totals happen to coincide after the repaired protocol.

## Independent paths and shared trust

The tree oracle in `pccfr/oracle.py` does not import the frontier module, production optimizer, or its dynamic-programming recurrence. It enumerates every tree shape and every ordered leaf subset directly at the configured small boundary. The direct semantic path serializes strict finite JSON canonically and does not use the frontier's type-tagged `freeze` representation. This specifically protects the `{}` versus `[]`, object-versus-array, and Boolean-versus-number distinctions that motivated the signature repair.

These paths still share the Python runtime, the finite model contract, and utility code. They are an implementation cross-check, not independently verified software or a mechanized proof.

## Search status discipline

A complete admitted leaf search yields `optimal` or `infeasible`. A space above the declared candidate limit yields `refused`. Tree search raises `SearchRefusal` in strict mode if any alternative needed for a global optimum was not completed. Diagnostic mode may retain the best feasible tree seen, but labels it `incomplete` with `optimality_proven=false`. `branchless_cost` uses the same three-way status discipline rather than representing refusal and infeasibility as `None`.

The retained two-input microexample has acceptable fault sets `{0,1}` and `{1,2}`. Its direct one-leaf optimum is action `[1]`, 12 object bytes. At candidate limit 2, strict tree search refuses; diagnostic search finds a 20-byte branch tree but does not call it optimal; branchless search reports `refused`.

## Parser, schema, and golden object

The PFC1 decoder rejects a magic-only object, every strict truncation of the golden object, negative cursor reads, nonzero reserved fields, duplicate/repeated tests, malformed masks, unknown opcodes, and trailing bytes through structured `invalid-object` results. Strict model loading rejects duplicate JSON keys, nonfinite numbers, unsupported Python values, nonstring object keys, Boolean identities, and nonintegral source actions. `source=[0.0]` is rejected by model validation, the certificate checker, and the CLI check entry point.

`fixtures/golden-pfc1/region.pfc` has the independently hand-computable bytes:

```text
50 46 43 31 01 00 4c 01 00 00 00 01 01
```

PFC1 uses little-endian `u16` fields. Guard masks are LSB first: input `x` is bit `x mod 8` of byte `floor(x/8)`. Emit/fault model payloads use the JSON field `value`; “signature” is the semantic name for the complete observer-visible fault value, not a second wire field.

## Directed controls

A control counts as successful only if its accept/reject outcome **and** stage/reason match the frozen expectation. The 30 controls include deletion/reordering/signature semantic errors; wrong witness identity; object truncation, trailing bytes, unknown opcode, repeated branch bit, noncanonical implicit and explicit guard masks, duplicate action identities, and malformed length; and exact/under budget checks. Rejection for the wrong reason is recorded as a mismatch.

## Input loading and separate retained-result comparison

The campaign's `retained-input-replay` phase checks and parses the stable-ID set: 130 `exact`, 64 `baseline`, 128 `joint`, 64 `padding`, and 5 `many` inputs. It calls an optimizer path for each input without comparing that return value to a retained result. Its mismatch count checks the inventory, not numerical or byte reproduction.

The standalone `replay_inputs.py` comparator requires this same stable-ID set and rejects duplicates in the retained record indices. It separately reports:

1. loading and stable-ID coverage;
2. numerical/status comparison and the recorded mode fields: joint-search actual modes are informative only for feasible cases; infeasible null fields do not verify mode selection;
3. byte equality for all 130 retained `.pfc` objects; and
4. the scientific source plus exact-input binding.

`verify_results.py` compares every deterministic JSON file after excluding only host-dependent resource/timing fields and byte-compares every `.pfc` file. It fails when the reference has no retained inputs or no PFC objects.

## Interpretation and remaining limits

The general theorems have supplied mathematical proofs, not mechanized derivations. The executable campaign is bounded falsification and implementation-conformance evidence. There is no production compiler pass, compiler-to-table extractor, real exception ABI, real instruction encoding, workload benchmark, hardware measurement, mutable memory, effectful guard, handler/resumption semantics, loops, concurrency, undefined behavior, or asynchronous fault model. The private-leaf grammar excludes shared suffixes, strengthened predicates, and synthesized actions. No finite count is presented as proof of those excluded cases or as evidence of production performance.
