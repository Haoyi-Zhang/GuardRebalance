# Claims-to-evidence matrix

This matrix limits each paper claim to the evidence actually present in the archive.  “Checked” means finite executable evidence; “proved” means a hand-written mathematical proof unless explicitly stated otherwise.

| Claim class | Evidence | Independent failure mode addressed | Boundary |
|---|---|---|---|
| Source/candidate observational equivalence iff the fault-frontier conditions hold | Formal definitions and hand-written necessity/sufficiency proof in the paper and `artifact/proofs/` | General argument, not sample agreement | Finite entry-state guards, pure action outcomes, synchronous immediate faults, declared observer |
| Permutation-only legality has the stated AND/OR waiting form and need not be a poset | Characterization proof, non-poset witness, exhaustive finite language checks | Guards against an unjustified ordinary-DAG reduction | Does not claim a new general AND/OR scheduling algorithm |
| Unique representative selection is easy; two acceptable representatives encode the stated hard problem | Constructive proof and reduction | Guards against extrapolating the easy case | Complexity is for the exact finite representation in the theorem |
| The private-leaf/read-once optimizer is exact | Dynamic-programming proof plus explicit small tree-shape enumeration | Oracle does not reuse the DP recurrence | No exactness claim outside that grammar or beyond completed search |
| Search limits never become an optimality claim | Failure-closed exception path and targeted regression test | Addresses truncation masquerading as proof | Diagnostic partial search is labeled not proven optimal |
| A PFC1 object preserves semantics and meets its budget | Primary checker, separately implemented direct interpreter, parser/schema negative controls, and byte reserialization | Reduces shared optimizer/checker defects | Both implementations share the published model and are not proof assistants |
| Restricted guarded IR extraction preserves the modeled behavior | Executable extraction bridge and positive/negative operational controls | Tests the hand-authored-table boundary | No claim for full LLVM/MLIR or arbitrary side effects |
| Reported finite counts are reproducible | Preserved input tables, deterministic seeds, machine-readable summaries, and claim-provenance audit | Guards against hand-entered headline numbers | Finite checking does not prove the general theorems |
| Robustness is not an artifact of one hand-written example | Exhaustive small domains, structural corpus audit, guaranteed-changing mutations, and distinct verifier implementation | Addresses example and implementation overfitting | Post-hoc structural checks are not called preregistered holdouts |
| Production compiler benefit | **Not claimed** | — | Requires real extraction, profitability, machine-code, and hardware evaluation |
