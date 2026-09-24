# Literature calibration and contribution boundary

This matrix records substantive calibration sources used to shape the paper. “Read” means the accessible full article/PDF/eReader or an author/institutional full-text copy was inspected beyond its abstract, including its method and evaluation or proof sections. The matrix is a research note, not a citation substitute; bibliographic entries appear in the paper.

## Twelve TACO articles

| Article | Problem / mechanism | Decisive evidence and narrative pattern | Boundary for this work |
|---|---|---|---|
| Han, Ahn, and Choi, *Power-Efficient Predication Techniques for Acceleration of Control Flow Execution on CGRA* (2013) | architectural predication mechanisms for divergent CGRA control | gate-level simulation, energy-delay evaluation, architecture then mechanisms then experiments | demonstrates that practical predication claims require architecture-level evidence; our byte grammar makes no power claim |
| Shobaki, Wilken, and Heffernan, *Optimal Trace Scheduling Using Enumeration* (2009) | exact global trace scheduling by branch-and-bound | formal objective, pruning, optimality checks, benchmark comparison | enumeration and optimal scheduling are established; novelty cannot rest on exact search alone |
| Shobaki, Shawabkeh, and Abu Rmaileh, *Preallocation Instruction Scheduling...* (2013) | exact balance of ILP and register pressure in LLVM | branch-and-bound, SPEC CPU2006, real x86-64 effects | TACO expects production integration for performance claims; our result is instead a semantic/complexity boundary |
| Shobaki et al., *Exploring an Alternative Cost Function...* (2019) | SLIL objective for register-pressure-aware scheduling | algorithm, LLVM implementation, SPEC/MediaBench on x86 and ARM | objective choice changes solutions; analogous to our insistence on fixing the observer and byte grammar |
| Shobaki et al., *Register-Pressure-Aware Instruction Scheduling Using Ant Colony Optimization* (2022) | heuristic/exact scheduling trade-off | LLVM, x86/ARM/AMD GPU, exact B&B comparison | established comparison style separates quality, timeout, and real execution; we do not report such performance |
| Pompougnac et al., *Weaving Synchronous Reactions into the Fabric of SSA-form Compilers* (2022) | extends SSA/MLIR for synchronous reactive semantics | semantic exposition, compiler embedding, generated-code evaluation | shows how exact semantic assumptions and implementation claims are separated; its stateful reactions differ from terminal snapshots |
| Zhou and Xue, *A Compiler Approach for Exploiting Partial SIMD Parallelism* (2016) | partial vectorization with masking and exception safety | LLVM implementation and x86/ARM application experiments | inserted/melded operations and numeric/memory exception safety are outside inherited-action grammar |
| Cherubin et al., *Dynamic Precision Autotuning with TAFFO* (2020) | compiler analyses and autotuning for fixed-point precision | LLVM toolchain, error/performance trade-offs, applications | illustrates TACO’s expectation that practical compiler claims connect analysis to real transformed programs |
| Ashouri et al., *MiCOMP* (2017) | phase ordering through subsequences and learned prediction | LLVM/cBench exploration and baseline comparisons | learned phase-ordering is unrelated to proof certificates; it calibrates empirical breadth and claim discipline |
| Ashouri et al., *COBAYN* (2016) | Bayesian-network compiler autotuning | learned model, compiler integration, application evaluation | further evidence that “optimizer” in TACO normally implies production workloads unless scope is explicitly theoretical |
| Martins et al., *Clustering-Based Selection for the Exploration of Compiler Optimization Sequences* (2016) | reduces phase-order search by clustering | ReflectC/LLVM, MicroBlaze/LEON3, exploration-time and speedup measures | search-space reduction is established; our representative sparsification must be justified semantically, not presented as generic DSE novelty |
| Na, Kim, and Han, *JavaScript Parallelizing Compiler for Exploiting Parallelism from Data-Parallel HTML5 Applications* (2016) | source/compiler transformation for data-parallel web applications | end-to-end compiler and application evaluation | calibrates venue structure: concrete workload, transformation, correctness constraints, implementation, then evaluation |

## Five influential correctness/IR papers

| Article | Why influential here | Boundary learned |
|---|---|---|
| Ferrante, Ottenstein, and Warren, *The Program Dependence Graph and Its Use in Optimization* | canonical control/data dependence representation | a finite action table is not a replacement for general dependence semantics |
| Cytron et al., *Efficiently Computing Static Single Assignment Form and the Control Dependence Graph* | foundational SSA construction | our source orders and guards assume an already extracted region |
| Pnueli, Siegel, and Singerman, *Translation Validation* | validates each translation rather than a compiler implementation | our checker is a fragment-specific translation validator with a much smaller semantics |
| Tristan and Leroy, *A Simple, Verified Validator for Software Pipelining* | mechanized validator architecture and proof decomposition | handwritten checker soundness plus tests must not be called a mechanically verified compiler validator |
| Lopes et al., *Alive2: Bounded Translation Validation for LLVM* | production-facing bounded LLVM validation | our explicit table avoids LLVM undefined behavior and memory, so it is neither stronger nor a substitute |

## Five adjacent-venue closest papers

| Article | Closest aspect | Delta retained after reading |
|---|---|---|
| August, Hwu, and Mahlke, *A Framework for Balancing Control Flow and Predication* (MICRO 1997) | aggressive if-conversion followed by scheduling-time partial reverse if-conversion; liveness, duplication, code size | historical framework uses a processor/scheduler model and nontrapping operation variants; it does not give terminal-observation frontier certificates or grammar-relative exact bytes |
| Moll and Hack, *Partial Control-Flow Linearization* (PLDI 2018) | preserves selected control while linearizing other paths | broader reducible-CFG/vectorization transformation assumes correctness of predication/masking; our narrow model makes first-fault obligations explicit |
| Li et al., *Eliminate Branches by Melding IR Instructions (MERIT)* (2025) | branch-path melding and safe inserted operands | it synthesizes/melds operations outside our inherited-action grammar; its practical transformation cannot be judged by our byte objective |
| Zhang et al., *CF-GKAT: Efficient Validation of Control-Flow Transformations* (POPL 2025) | efficient algebraic validation of nonlocal control flow | general trace-equivalence machinery precedes this work; our contribution is an explicit first-fault selected-action characterization |
| Zhang et al., *Outrunning Big KATs* (2026) | symbolic decision procedures for guarded-algebra variants | reinforces that finite replay is not a new general validation framework; our theorem exposes a specialized, checkable frontier and selection boundary |

## Additional comparison set

The paper also compares classic if-conversion and hyperblock work, precise exceptions/speculation, AND/OR precedence scheduling, optimal/basic-block scheduling, Unison-style combinatorial code generation, CompCert/Alive/LLVM formalization, Csmith/EMI compiler testing, CORELS-style certified sparse search, CompilerGym/BaCO autotuning, and decision-tree complexity. These papers are cited where their specific result constrains a claim; they are not counted as extra “full reads” merely to inflate a total.

## Synthesis

TACO compiler papers commonly move from a concrete architecture/code-generation problem to a clearly delimited mechanism, then connect it to production compiler infrastructure and broad application evidence. Exact scheduling papers additionally specify their objective, pruning, optimality oracle, and timeout accounting. Formal-validation papers distinguish the source/target semantics, trusted base, mechanized theorems, executable checks, and extraction boundary.

The defensible contribution here is therefore narrow: an exact first-terminal-fault characterization for selected immutable guarded actions; a unique-versus-shared representative complexity boundary; a canonical private-leaf byte object and replay certificate; and a bounded conformance campaign. The work does **not** claim a new general scheduling algorithm, a new concept of translation validation, a production if-converter, an ISA code-size result, or practical speedup. The most important remaining external-use risk is not missing finite tests but whether reviewers judge this precisely delimited semantics/complexity result sufficiently important without a production extraction case study.
