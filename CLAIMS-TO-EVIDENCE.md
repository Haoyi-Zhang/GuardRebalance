# Claims-to-evidence matrix

“Proved” below means a handwritten mathematical proof under the stated finite model. “Checked” means deterministic bounded executable evidence. No entry denotes proof-assistant verification or a production compiler evaluation.

| Claim | Maturity | Principal evidence | Independent failure mode attacked | Boundary |
|---|---|---|---|---|
| Fault-frontier conditions are necessary and sufficient | proved; finite-checked | paper and `proofs/core.md`; `exhaustive.json`; `two-state.json` | direct observations use canonical strict JSON, while frontier summaries use type-tagged structural signatures | finite entry-snapshot guards/outcomes, immediate terminal faults, declared complete observer |
| One acceptable witness per faulting input suffices for checking | proved; finite-checked | corollary proof; witness layer in `exhaustive.json`; controls | witness identity and barrier obligations are checked separately from direct traces | witness count is not serialized-object count |
| Full-permutation legality is an AND/OR waiting language | proved; semantically checked | representation proof; `and-or.json` | 512 actual snapshot models and every permutation are compared, not only the ready algorithm | no claim of inventing the known scheduler |
| Unique representatives give a least set; two representatives encode Vertex Cover | proved; small-boundary checked | proofs; `search.json`; `graphs.json` | exhaustive small graphs and direct leaf optimum | exact representation and positive additive costs only |
| Private-leaf/read-once tree optimization is exact when search is complete | proved; checked | DP proof; `trees.json`; `pccfr/oracle.py` | oracle enumerates all tree shapes/direct leaf orders without the DP/frontier modules | fixed PFC1 grammar and admitted complete leaf spaces |
| Search truncation never becomes an optimality claim | implementation invariant; regression-checked | `repair-validation.json`; regression tests | strict refusal, diagnostic incomplete, and infeasible states are distinct | does not remove exponential worst-case search |
| A passing PFC1 object/certificate preserves the supplied table and budget | proved-relative; checked | checker proof; object replay layer; directed controls; golden bytes | direct trace and frontier witness both replayed; malformed bytes and schemas rejected | trusts finite table, Python runtime, parser, and observer adequacy |
| Reported counts and retained optima are reproducible | measured | bound `results/confirmed/`; stable-ID replay; `.pfc` byte comparison | fresh regeneration, source/input binding, missing/extra-ID failure | resource timings remain host dependent |
| Production compiler or hardware benefit | not claimed | explicit model/validity boundaries | n/a | would require extraction, real code generation, workloads, and hardware evidence |
