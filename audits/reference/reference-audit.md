# Reference audit

- Entries: **60**
- Distinct cited keys: **68**
- Registry status: `{'unverified': 60}`
- Accepted: **False**

## Closure problems

- Undefined: `['agakov2006', 'ansel2014', 'ashouri2016', 'ashouri2017', 'chen2018', 'cummins2022', 'fursin2011', 'martins2016']`
- Uncited: `[]`
- Duplicate DOI: `{}`
- Duplicate title: `{}`
- Mismatch/unverified: `['angelino2018', 'august1997', 'allen1983', 'mahlke1992', 'mahlke1994', 'tyson1994', 'chuang2003', 'park1991', 'johnson1996', 'gillies1996', 'mahlke1994branch', 'eichenberger1996', 'hsu1986', 'dehnert1989', 'rau1989', 'fisher1981', 'han2013', 'moll2018', 'li2025', 'ferrante1987', 'cytron1991', 'kildall1973', 'lattner2004', 'lattner2021', 'muchnick1997', 'aho2006', 'appel1998', 'pnueli1998', 'necula2000', 'tristan2010', 'leroy2009', 'leroy2006', 'lopes2021', 'lopes2015', 'zhao2012', 'le2014', 'yang2011', 'zuck2003', 'zhang2025', 'zhang2026', 'kozen1997', 'smolka2020', 'mohring2004', 'karp1972', 'shobaki2009', 'shobaki2013', 'shobaki2019', 'shobaki2022', 'wilken2000', 'castaneda2019', 'pompougnac2022', 'zhou2016', 'cherubin2020', 'na2016', 'hyafil1976', 'quinlan1986', 'bryant1986', 'debray2000', 'ball1994', 'bala2000']`
- Metadata review: `[]`

## Per-entry evidence

### `angelino2018` — unverified
- Bibliography: Learning Certifiably Optimal Rule Lists for Categorical Data (2018); first author `angelino`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - The same caution applies to exact sparse search. CORELS supplies certified optimal rule lists for a classification objective \cite{angelino2018}; decision-tree optimization is classically hard \cite{hyafil1976}; binary decision diagrams and learned decision trees use different sharing and objective choices \cite{bryant1986,quinlan1986}. The present private-leaf grammar and exact semantic loss are distinct, but exact search alone is not a novelty claim. The semantic frontier, the representative boundary, and the grammar-relative replay are the joint result.
  - Optimal decision trees are NP-hard in general \cite{hyafil1976}; induction algorithms and reduced decision diagrams optimize different predictive or Boolean objectives and often permit sharing absent from private leaves \cite{quinlan1986,bryant1986}. CORELS produces certifiably optimal rule lists for an empirical-risk objective \cite{angelino2018}. These analogies are important negative novelty evidence: enumeration, dynamic programming, and a small certificate are not by themselves new. Theorems~\ref{thm:frontier}, \ref{thm:unique}, \ref{thm:hard}, and \ref{thm:representatives} supply the semantics-specific reason that the chosen search space is complete.

### `august1997` — unverified
- Bibliography: A Framework for Balancing Control Flow and Predication (1997); first author `august`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Park and Schlansker's predicated-execution analysis and phi-predication study compiler representations that retain more control structure or introduce selective predication \cite{park1991,chuang2003}. August, Hwu, and Mahlke's framework is the most direct historical anchor: it performs aggressive early if-conversion and then partial reverse if-conversion while scheduling, accounting for predicate flow, liveness, duplication, resources, performance, and static code growth \cite{august1997}. Its modeled machine provides nontrapping variants for most potentially excepting instructions. Our result does not replace that framework. It removes machine scheduling and mutable dataflow to prove an exact terminal-observation condition and a fragment-relative byte theorem.

### `allen1983` — unverified
- Bibliography: Conversion of Control Dependence to Data Dependence (1983); first author `allen`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `mahlke1992` — unverified
- Bibliography: Effective Compiler Support for Predicated Execution Using the Hyperblock (1992); first author `mahlke`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `mahlke1994` — unverified
- Bibliography: A Comparison of Full and Partial Predicated Execution Support for {ILP} Processors (1995); first author `mahlke`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `tyson1994` — unverified
- Bibliography: The Effects of Predicated Execution on Branch Prediction (1994); first author `tyson`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `chuang2003` — unverified
- Bibliography: Phi-Predication for Light-Weight If-Conversion (2003); first author `chuang`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Park and Schlansker's predicated-execution analysis and phi-predication study compiler representations that retain more control structure or introduce selective predication \cite{park1991,chuang2003}. August, Hwu, and Mahlke's framework is the most direct historical anchor: it performs aggressive early if-conversion and then partial reverse if-conversion while scheduling, accounting for predicate flow, liveness, duplication, resources, performance, and static code growth \cite{august1997}. Its modeled machine provides nontrapping variants for most potentially excepting instructions. Our result does not replace that framework. It removes machine scheduling and mutable dataflow to prove an exact terminal-observation condition and a fragment-relative byte theorem.

### `park1991` — unverified
- Bibliography: On Predicated Execution (1991); first author `park`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Park and Schlansker's predicated-execution analysis and phi-predication study compiler representations that retain more control structure or introduce selective predication \cite{park1991,chuang2003}. August, Hwu, and Mahlke's framework is the most direct historical anchor: it performs aggressive early if-conversion and then partial reverse if-conversion while scheduling, accounting for predicate flow, liveness, duplication, resources, performance, and static code growth \cite{august1997}. Its modeled machine provides nontrapping variants for most potentially excepting instructions. Our result does not replace that framework. It removes machine scheduling and mutable dataflow to prove an exact terminal-observation condition and a fragment-relative byte theorem.

### `johnson1996` — unverified
- Bibliography: Analysis Techniques for Predicated Code (1996); first author `johnson`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `gillies1996` — unverified
- Bibliography: Global Predicate Analysis and Its Application to Register Allocation (1996); first author `gillies`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `mahlke1994branch` — unverified
- Bibliography: Characterizing the Impact of Predicated Execution on Branch Prediction (1994); first author `mahlke`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `eichenberger1996` — unverified
- Bibliography: Speculative Execution Using Guarded Predicates (1996); first author `eichenberger`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Predicated execution and if-conversion have a long compiler and architecture lineage. Hyperblocks, predicate analysis, speculative guarded execution, partial reverse if-conversion, and branch-prediction trade-offs establish that control-to-data conversion interacts with liveness, code growth, processor support, and scheduling \cite{allen1983,mahlke1992,mahlke1994,tyson1994,mahlke1994branch,eichenberger1996}. In particular, August, Hwu, and Mahlke combine early aggressive if-conversion with scheduling-time partial reverse if-conversion and evaluate a modeled architecture with nontrapping instruction variants \cite{august1997}. That framework motivates the problem but does not provide the finite terminal-observation theorem, selected-action complexity boundary, or actual-byte certificate studied here.
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `hsu1986` — unverified
- Bibliography: Highly Concurrent Scalar Processing (1986); first author `hsu`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `dehnert1989` — unverified
- Bibliography: Overlapped Loop Support in the {Cydra 5} (1989); first author `dehnert`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `rau1989` — unverified
- Bibliography: The {Cydra 5} Departmental Supercomputer: Design Philosophies, Decisions, and Trade-Offs (1989); first author `rau`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `fisher1981` — unverified
- Bibliography: Trace Scheduling: A Technique for Global Microcode Compaction (1981); first author `fisher`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Trace scheduling moved global compaction across basic-block boundaries and made likely paths a compiler object \cite{fisher1981}. Early highly concurrent and VLIW designs exposed architectural support that motivated speculative and predicated compilation \cite{hsu1986,dehnert1989,rau1989}. If-conversion formalized the replacement of control dependences by data dependences \cite{allen1983}; hyperblocks provided an influential compiler structure for predicated execution \cite{mahlke1992}. Subsequent work analyzed partial versus full predication, branch-prediction effects, guarded speculation, predicate analysis, and predicate-aware allocation \cite{mahlke1994,mahlke1994branch,tyson1994,eichenberger1996,johnson1996,gillies1996}.

### `han2013` — unverified
- Bibliography: Power-Efficient Predication Techniques for Acceleration of Control Flow Execution on {CGRA} (2013); first author `han`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Real predication mechanisms expose similar trade-offs at a different level. Architectural predicates, hyperblocks, partial SIMD masks, and branch-path melding can trade control transfers for predicated work, duplication, or target-specific support \cite{han2013,zhou2016,moll2018,li2025}. Those systems evaluate execution, code generation, or hardware effects. Figure~\ref{fig:observer-gap} instead isolates how an observation contract and one abstract grammar determine an exact representational optimum.
  - Architectural predication work also evaluates concerns that the abstract byte object cannot address. Han, Ahn, and Choi analyze power-efficient CGRA predication with gate-level and energy-delay evidence \cite{han2013}. Real architectures must account for execution resources, speculation, exception deferral, code placement, and branch behavior. The present study intentionally reports none of those quantities.

### `moll2018` — unverified
- Bibliography: Partial Control-Flow Linearization (2018); first author `moll`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Real predication mechanisms expose similar trade-offs at a different level. Architectural predicates, hyperblocks, partial SIMD masks, and branch-path melding can trade control transfers for predicated work, duplication, or target-specific support \cite{han2013,zhou2016,moll2018,li2025}. Those systems evaluate execution, code generation, or hardware effects. Figure~\ref{fig:observer-gap} instead isolates how an observation contract and one abstract grammar determine an exact representational optimum.
  - More recent control transformations broaden the operational scope. Partial control-flow linearization preserves selected control while linearizing paths for vectorization \cite{moll2018}. PAVER exploits partial SIMD parallelism with compiler transformations and masked execution \cite{zhou2016}. MERIT melds instructions from alternative paths and must make synthesized operations safe \cite{li2025}. These systems can insert, combine, or retarget operations beyond our inherited-action grammar. Their practical correctness questions therefore cannot be answered solely by a \PFC certificate, while their transformation power can evade our private-leaf lower bounds.

### `li2025` — unverified
- Bibliography: Eliminate Branches by Melding {IR} Instructions (2025); first author `li`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Real predication mechanisms expose similar trade-offs at a different level. Architectural predicates, hyperblocks, partial SIMD masks, and branch-path melding can trade control transfers for predicated work, duplication, or target-specific support \cite{han2013,zhou2016,moll2018,li2025}. Those systems evaluate execution, code generation, or hardware effects. Figure~\ref{fig:observer-gap} instead isolates how an observation contract and one abstract grammar determine an exact representational optimum.
  - More recent control transformations broaden the operational scope. Partial control-flow linearization preserves selected control while linearizing paths for vectorization \cite{moll2018}. PAVER exploits partial SIMD parallelism with compiler transformations and masked execution \cite{zhou2016}. MERIT melds instructions from alternative paths and must make synthesized operations safe \cite{li2025}. These systems can insert, combine, or retarget operations beyond our inherited-action grammar. Their practical correctness questions therefore cannot be answered solely by a \PFC certificate, while their transformation power can evade our private-leaf lower bounds.

### `ferrante1987` — unverified
- Bibliography: The Program Dependence Graph and Its Use in Optimization (1987); first author `ferrante`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Theorem~\ref{thm:frontier} is relative to the supplied finite table. A checker can recompute all five conditions and direct observations without trusting optimizer summaries. It cannot determine whether a compiler correctly extracted the table from LLVM, MLIR, a source language, or an exception ABI. General compiler representations contain control/data dependences \cite{ferrante1987,cytron1991}, iterative dataflow facts \cite{kildall1973}, and semantics for memory, poison, undefined behavior, or dialect-specific operations \cite{lattner2004,lattner2021}. Those obligations are intentionally not hidden inside the certificate.
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `cytron1991` — unverified
- Bibliography: Efficiently Computing Static Single Assignment Form and the Control Dependence Graph (1991); first author `cytron`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Theorem~\ref{thm:frontier} is relative to the supplied finite table. A checker can recompute all five conditions and direct observations without trusting optimizer summaries. It cannot determine whether a compiler correctly extracted the table from LLVM, MLIR, a source language, or an exception ABI. General compiler representations contain control/data dependences \cite{ferrante1987,cytron1991}, iterative dataflow facts \cite{kildall1973}, and semantics for memory, poison, undefined behavior, or dialect-specific operations \cite{lattner2004,lattner2021}. Those obligations are intentionally not hidden inside the certificate.
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `kildall1973` — unverified
- Bibliography: A Unified Approach to Global Program Optimization (1973); first author `kildall`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Theorem~\ref{thm:frontier} is relative to the supplied finite table. A checker can recompute all five conditions and direct observations without trusting optimizer summaries. It cannot determine whether a compiler correctly extracted the table from LLVM, MLIR, a source language, or an exception ABI. General compiler representations contain control/data dependences \cite{ferrante1987,cytron1991}, iterative dataflow facts \cite{kildall1973}, and semantics for memory, poison, undefined behavior, or dialect-specific operations \cite{lattner2004,lattner2021}. Those obligations are intentionally not hidden inside the certificate.
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `lattner2004` — unverified
- Bibliography: {LLVM}: A Compilation Framework for Lifelong Program Analysis and Transformation (2004); first author `lattner`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Theorem~\ref{thm:frontier} is relative to the supplied finite table. A checker can recompute all five conditions and direct observations without trusting optimizer summaries. It cannot determine whether a compiler correctly extracted the table from LLVM, MLIR, a source language, or an exception ABI. General compiler representations contain control/data dependences \cite{ferrante1987,cytron1991}, iterative dataflow facts \cite{kildall1973}, and semantics for memory, poison, undefined behavior, or dialect-specific operations \cite{lattner2004,lattner2021}. Those obligations are intentionally not hidden inside the certificate.
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `lattner2021` — unverified
- Bibliography: {MLIR}: Scaling Compiler Infrastructure for Domain Specific Computation (2021); first author `lattner`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - Theorem~\ref{thm:frontier} is relative to the supplied finite table. A checker can recompute all five conditions and direct observations without trusting optimizer summaries. It cannot determine whether a compiler correctly extracted the table from LLVM, MLIR, a source language, or an exception ABI. General compiler representations contain control/data dependences \cite{ferrante1987,cytron1991}, iterative dataflow facts \cite{kildall1973}, and semantics for memory, poison, undefined behavior, or dialect-specific operations \cite{lattner2004,lattner2021}. Those obligations are intentionally not hidden inside the certificate.
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `muchnick1997` — unverified
- Bibliography: Advanced Compiler Design and Implementation (1997); first author `muchnick`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `aho2006` — unverified
- Bibliography: Compilers: Principles, Techniques, and Tools (2006); first author `aho`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `appel1998` — unverified
- Bibliography: {SSA} Is Functional Programming (1998); first author `appel`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Program dependence graphs and SSA make control/data relationships explicit and support broad optimization frameworks \cite{ferrante1987,cytron1991}. Classical dataflow theory and compiler texts explain the fixed-point, alias, liveness, and code-generation machinery omitted from the snapshot interface \cite{kildall1973,aho2006,muchnick1997}. The functional interpretation of SSA clarifies why values and joins can be reasoned about compositionally \cite{appel1998}, while LLVM and MLIR provide extensible industrial intermediate representations with much richer operation semantics \cite{lattner2004,lattner2021}. Our finite table is an input to analysis, not a substitute for those representations or an extraction algorithm from them.

### `pnueli1998` — unverified
- Bibliography: Translation Validation (1998); first author `pnueli`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - The distinction parallels translation validation: validate a particular transformation under explicit source and target semantics rather than trust the optimizer implementation \cite{pnueli1998,necula2000}. However, the present semantics is far smaller than production validators. Its advantage is that the exact first-fault obligation can be isolated and independently enumerated; its limitation is that a real compiler front end remains a separate proof or engineering task.
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `necula2000` — unverified
- Bibliography: Translation Validation for an Optimizing Compiler (2000); first author `necula`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - The distinction parallels translation validation: validate a particular transformation under explicit source and target semantics rather than trust the optimizer implementation \cite{pnueli1998,necula2000}. However, the present semantics is far smaller than production validators. Its advantage is that the exact first-fault obligation can be isolated and independently enumerated; its limitation is that a real compiler front end remains a separate proof or engineering task.
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `tristan2010` — unverified
- Bibliography: A Simple, Verified Validator for Software Pipelining (2010); first author `tristan`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `leroy2009` — unverified
- Bibliography: Formal Verification of a Realistic Compiler (2009); first author `leroy`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - These are not defects that can be repaired by adding another frontier edge. They change the semantic object. A production instantiation would need a source-language and IR-specific extraction theorem analogous to the semantic foundations used in verified or bounded translation validators \cite{leroy2006,leroy2009,zhao2012,lopes2015,lopes2021}. The present work begins after that extraction boundary.
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `leroy2006` — unverified
- Bibliography: Formal Certification of a Compiler Back-End or: Programming a Compiler with a Proof Assistant (2006); first author `leroy`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - These are not defects that can be repaired by adding another frontier edge. They change the semantic object. A production instantiation would need a source-language and IR-specific extraction theorem analogous to the semantic foundations used in verified or bounded translation validators \cite{leroy2006,leroy2009,zhao2012,lopes2015,lopes2021}. The present work begins after that extraction boundary.
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `lopes2021` — unverified
- Bibliography: {Alive2}: Bounded Translation Validation for {LLVM} (2021); first author `lopes`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - These are not defects that can be repaired by adding another frontier edge. They change the semantic object. A production instantiation would need a source-language and IR-specific extraction theorem analogous to the semantic foundations used in verified or bounded translation validators \cite{leroy2006,leroy2009,zhao2012,lopes2015,lopes2021}. The present work begins after that extraction boundary.
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `lopes2015` — unverified
- Bibliography: Provably Correct Peephole Optimizations with {Alive} (2015); first author `lopes`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - These are not defects that can be repaired by adding another frontier edge. They change the semantic object. A production instantiation would need a source-language and IR-specific extraction theorem analogous to the semantic foundations used in verified or bounded translation validators \cite{leroy2006,leroy2009,zhao2012,lopes2015,lopes2021}. The present work begins after that extraction boundary.
  - This separation follows the architecture of translation validation and verified validators while retaining a much smaller trusted semantics. Pnueli et al. and Necula validate individual compiler runs \cite{pnueli1998,necula2000}; Tristan and Leroy prove a validator for software pipelining \cite{tristan2010}; CompCert proves compiler passes against formal semantics \cite{leroy2006,leroy2009}; Alive and Alive2 reason about LLVM transformations and undefined-behavior-sensitive semantics \cite{lopes2015,lopes2021}. The present checker is not comparable in production coverage or mechanization. Its contribution is the fragment-specific frontier certificate and exact byte replay.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `zhao2012` — unverified
- Bibliography: Formalizing the {LLVM} Intermediate Representation for Verified Program Transformations (2012); first author `zhao`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - These are not defects that can be repaired by adding another frontier edge. They change the semantic object. A production instantiation would need a source-language and IR-specific extraction theorem analogous to the semantic foundations used in verified or bounded translation validators \cite{leroy2006,leroy2009,zhao2012,lopes2015,lopes2021}. The present work begins after that extraction boundary.
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `le2014` — unverified
- Bibliography: Compiler Validation via Equivalence Modulo Inputs (2014); first author `le`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `yang2011` — unverified
- Bibliography: Finding and Understanding Bugs in {C} Compilers (2011); first author `yang`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `zuck2003` — unverified
- Bibliography: Translation and Run-Time Validation of Loop Transformations (2003); first author `zuck`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Translation validation shifts trust from an optimizer implementation to a validator for each produced transformation \cite{pnueli1998,necula2000}. Loop-transformation and run-time validation work develops proof obligations for structured optimizations \cite{zuck2003}; CompCert mechanizes compiler correctness and validator components in a proof assistant \cite{leroy2006,leroy2009,tristan2010}. Vellvm formalizes LLVM IR for verified transformations \cite{zhao2012}. Alive and Alive2 validate peephole and bounded LLVM transformations while handling semantic features far beyond our model \cite{lopes2015,lopes2021}. Equivalence-modulo-inputs and Csmith attack compilers by generating or reducing tests rather than proving a specific transformation \cite{le2014,yang2011}. The artifact borrows their discipline of independent semantic comparison, but its bounded tables do not become a production validator through testing.

### `zhang2025` — unverified
- Bibliography: {CF-GKAT}: Efficient Validation of Control-Flow Transformations (2025); first author `zhang`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Algebraic approaches validate control-flow transformations at a different abstraction. Kleene algebra with tests supplies an equational foundation \cite{kozen1997}; guarded KAT obtains efficient reasoning for uninterpreted guarded programs \cite{smolka2020}. CF-GKAT targets efficient validation of nonlocal control-flow transformations, and later work studies decision procedures for broader GKAT variants \cite{zhang2025,zhang2026}. These results prevent a claim that finite replay or guarded decision procedures are new in general. Our theorem instead specializes the observation to tagged prefixes plus a first terminal fault, permits action deletion, and derives a representative-selection boundary not stated by those general trace-equivalence frameworks.

### `zhang2026` — unverified
- Bibliography: Outrunning Big {KATs}: Efficient Decision Procedures for Variants of {GKAT} (2026); first author `zhang`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Algebraic approaches validate control-flow transformations at a different abstraction. Kleene algebra with tests supplies an equational foundation \cite{kozen1997}; guarded KAT obtains efficient reasoning for uninterpreted guarded programs \cite{smolka2020}. CF-GKAT targets efficient validation of nonlocal control-flow transformations, and later work studies decision procedures for broader GKAT variants \cite{zhang2025,zhang2026}. These results prevent a claim that finite replay or guarded decision procedures are new in general. Our theorem instead specializes the observation to tagged prefixes plus a first terminal fault, permits action deletion, and derives a representative-selection boundary not stated by those general trace-equivalence frameworks.

### `kozen1997` — unverified
- Bibliography: Kleene Algebra with Tests (1997); first author `kozen`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Algebraic approaches validate control-flow transformations at a different abstraction. Kleene algebra with tests supplies an equational foundation \cite{kozen1997}; guarded KAT obtains efficient reasoning for uninterpreted guarded programs \cite{smolka2020}. CF-GKAT targets efficient validation of nonlocal control-flow transformations, and later work studies decision procedures for broader GKAT variants \cite{zhang2025,zhang2026}. These results prevent a claim that finite replay or guarded decision procedures are new in general. Our theorem instead specializes the observation to tagged prefixes plus a first terminal fault, permits action deletion, and derives a representative-selection boundary not stated by those general trace-equivalence frameworks.

### `smolka2020` — unverified
- Bibliography: Guarded Kleene Algebra with Tests: Verification of Uninterpreted Programs in Nearly Linear Time (2020); first author `smolka`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Algebraic approaches validate control-flow transformations at a different abstraction. Kleene algebra with tests supplies an equational foundation \cite{kozen1997}; guarded KAT obtains efficient reasoning for uninterpreted guarded programs \cite{smolka2020}. CF-GKAT targets efficient validation of nonlocal control-flow transformations, and later work studies decision procedures for broader GKAT variants \cite{zhang2025,zhang2026}. These results prevent a claim that finite replay or guarded decision procedures are new in general. Our theorem instead specializes the observation to tagged prefixes plus a first terminal fault, permits action deletion, and derives a representative-selection boundary not stated by those general trace-equivalence frameworks.

### `mohring2004` — unverified
- Bibliography: Scheduling with {AND/OR} Precedence Constraints (2004); first author `ohring`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 4
  - The characterization also separates established scheduling machinery from the new semantic boundary. With a fixed full action set, the derived obligations are exactly finite AND/OR precedence conditions, and the known ready algorithm decides feasibility \cite{mohring2004}. We do not claim a new scheduling algorithm. Instead, we prove how first-fault semantics induces those conditions and show what changes when the target may delete actions. If every faulting input has a unique acceptable representative, a unique least selected set exists. If each input may choose between two representatives, minimum-cardinality selection is NP-complete by reduction from Vertex Cover \cite{karp1972}.
  - A canonical waiting condition $(Y,j)$ has nonempty $Y\subseteq\Act\setminus\{j\}$ and requires at least one member of $Y$ to appear before $j$. Conditions are conjoined, while predecessor alternatives within $Y$ are disjoined. This is the AND/OR precedence formalism studied by M\"ohring, Skutella, and Stork \cite{mohring2004}.
  - \paragraph{Known ready algorithm.} Begin with no emitted identities. An action is ready when every waiting condition targeting it already has an emitted alternative predecessor. Emit any ready action and mark every condition containing it as an alternative predecessor satisfied. If all actions are emitted, the produced order satisfies every condition. If a nonempty residual $R$ remains and no action is ready, then each $j\in R$ has an unmet condition $(Y,j)$ with $Y\subseteq R$. Any alleged continuation has an earliest member of $R$, but its condition requires an earlier member of $R$, a contradiction. Reverse incidence lists give linear work in nodes, conditions, and incidences, apart from deterministic sorting. This algorithm and obstruction are established scheduling results \cite{mohring2004}; the contribution here is the semantic correspondence in Theorem~\ref{thm:waiting}.

### `karp1972` — unverified
- Bibliography: Reducibility among Combinatorial Problems (1972); first author `karp`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - The characterization also separates established scheduling machinery from the new semantic boundary. With a fixed full action set, the derived obligations are exactly finite AND/OR precedence conditions, and the known ready algorithm decides feasibility \cite{mohring2004}. We do not claim a new scheduling algorithm. Instead, we prove how first-fault semantics induces those conditions and show what changes when the target may delete actions. If every faulting input has a unique acceptable representative, a unique least selected set exists. If each input may choose between two representatives, minimum-cardinality selection is NP-complete by reduction from Vertex Cover \cite{karp1972}.
  - The reduction uses the standard NP-completeness of Vertex Cover \cite{karp1972}; it does not claim a new hardness result for graph covering. It identifies where observer-relative representative choice enters the compiler fragment. The executable's fixed small bounds are not themselves an asymptotic family, so the artifact checks the reduction on all nonempty simple graphs with two through five vertices rather than claiming that finite enumeration proves NP-completeness.

### `shobaki2009` — unverified
- Bibliography: Optimal Trace Scheduling Using Enumeration (2009); first author `shobaki`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - There are $3^b$ canonical cells because each bit is fixed zero, fixed one, or free. Summed cell membership is $4^b$. A straightforward bound with exhaustive subsets and quadratic constraint construction is \[ O\!\left(2^n4^b n^2 + b3^b\right), \] plus payload comparison, sorting, and encoding. Representative enumeration can be much smaller on sparse frontiers, but neither analysis makes the complete tree optimizer scalable in unrestricted $b$ or action count. The method is a bounded exact oracle, not a proposed production scheduling heuristic. Exact trace and instruction scheduling systems likewise distinguish optimality from scalability and use carefully defined objectives, pruning, and timeout accounting \cite{wilken2000,shobaki2009,shobaki2013,shobaki2019,castaneda2019}.
  - AND/OR precedence constraints and their ready algorithm are established scheduling theory \cite{mohring2004}. Optimal instruction scheduling has been formulated with integer programming and enumeration \cite{wilken2000,shobaki2009}. Preallocation scheduling and alternative cost functions show that register-pressure objectives can materially change generated code \cite{shobaki2013,shobaki2019}; ant-colony scheduling studies the quality/scalability trade-off against exact methods on real compiler targets \cite{shobaki2022}. Combinatorial register allocation and scheduling integrates decisions whose separation can lose quality \cite{castaneda2019}. Our action costs have no latency, resource, register, or spill semantics. We use exact scheduling only as a bounded semantic oracle after fixing a selected set.

### `shobaki2013` — unverified
- Bibliography: Preallocation Instruction Scheduling with Register Pressure Minimization Using a Combinatorial Optimization Approach (2013); first author `shobaki`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - There are $3^b$ canonical cells because each bit is fixed zero, fixed one, or free. Summed cell membership is $4^b$. A straightforward bound with exhaustive subsets and quadratic constraint construction is \[ O\!\left(2^n4^b n^2 + b3^b\right), \] plus payload comparison, sorting, and encoding. Representative enumeration can be much smaller on sparse frontiers, but neither analysis makes the complete tree optimizer scalable in unrestricted $b$ or action count. The method is a bounded exact oracle, not a proposed production scheduling heuristic. Exact trace and instruction scheduling systems likewise distinguish optimality from scalability and use carefully defined objectives, pruning, and timeout accounting \cite{wilken2000,shobaki2009,shobaki2013,shobaki2019,castaneda2019}.
  - AND/OR precedence constraints and their ready algorithm are established scheduling theory \cite{mohring2004}. Optimal instruction scheduling has been formulated with integer programming and enumeration \cite{wilken2000,shobaki2009}. Preallocation scheduling and alternative cost functions show that register-pressure objectives can materially change generated code \cite{shobaki2013,shobaki2019}; ant-colony scheduling studies the quality/scalability trade-off against exact methods on real compiler targets \cite{shobaki2022}. Combinatorial register allocation and scheduling integrates decisions whose separation can lose quality \cite{castaneda2019}. Our action costs have no latency, resource, register, or spill semantics. We use exact scheduling only as a bounded semantic oracle after fixing a selected set.

### `shobaki2019` — unverified
- Bibliography: Exploring an Alternative Cost Function for Combinatorial Register-Pressure-Aware Instruction Scheduling (2019); first author `shobaki`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - There are $3^b$ canonical cells because each bit is fixed zero, fixed one, or free. Summed cell membership is $4^b$. A straightforward bound with exhaustive subsets and quadratic constraint construction is \[ O\!\left(2^n4^b n^2 + b3^b\right), \] plus payload comparison, sorting, and encoding. Representative enumeration can be much smaller on sparse frontiers, but neither analysis makes the complete tree optimizer scalable in unrestricted $b$ or action count. The method is a bounded exact oracle, not a proposed production scheduling heuristic. Exact trace and instruction scheduling systems likewise distinguish optimality from scalability and use carefully defined objectives, pruning, and timeout accounting \cite{wilken2000,shobaki2009,shobaki2013,shobaki2019,castaneda2019}.
  - AND/OR precedence constraints and their ready algorithm are established scheduling theory \cite{mohring2004}. Optimal instruction scheduling has been formulated with integer programming and enumeration \cite{wilken2000,shobaki2009}. Preallocation scheduling and alternative cost functions show that register-pressure objectives can materially change generated code \cite{shobaki2013,shobaki2019}; ant-colony scheduling studies the quality/scalability trade-off against exact methods on real compiler targets \cite{shobaki2022}. Combinatorial register allocation and scheduling integrates decisions whose separation can lose quality \cite{castaneda2019}. Our action costs have no latency, resource, register, or spill semantics. We use exact scheduling only as a bounded semantic oracle after fixing a selected set.

### `shobaki2022` — unverified
- Bibliography: Register-Pressure-Aware Instruction Scheduling Using Ant Colony Optimization (2022); first author `shobaki`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - AND/OR precedence constraints and their ready algorithm are established scheduling theory \cite{mohring2004}. Optimal instruction scheduling has been formulated with integer programming and enumeration \cite{wilken2000,shobaki2009}. Preallocation scheduling and alternative cost functions show that register-pressure objectives can materially change generated code \cite{shobaki2013,shobaki2019}; ant-colony scheduling studies the quality/scalability trade-off against exact methods on real compiler targets \cite{shobaki2022}. Combinatorial register allocation and scheduling integrates decisions whose separation can lose quality \cite{castaneda2019}. Our action costs have no latency, resource, register, or spill semantics. We use exact scheduling only as a bounded semantic oracle after fixing a selected set.

### `wilken2000` — unverified
- Bibliography: Optimal Instruction Scheduling Using Integer Programming (2000); first author `wilken`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - There are $3^b$ canonical cells because each bit is fixed zero, fixed one, or free. Summed cell membership is $4^b$. A straightforward bound with exhaustive subsets and quadratic constraint construction is \[ O\!\left(2^n4^b n^2 + b3^b\right), \] plus payload comparison, sorting, and encoding. Representative enumeration can be much smaller on sparse frontiers, but neither analysis makes the complete tree optimizer scalable in unrestricted $b$ or action count. The method is a bounded exact oracle, not a proposed production scheduling heuristic. Exact trace and instruction scheduling systems likewise distinguish optimality from scalability and use carefully defined objectives, pruning, and timeout accounting \cite{wilken2000,shobaki2009,shobaki2013,shobaki2019,castaneda2019}.
  - AND/OR precedence constraints and their ready algorithm are established scheduling theory \cite{mohring2004}. Optimal instruction scheduling has been formulated with integer programming and enumeration \cite{wilken2000,shobaki2009}. Preallocation scheduling and alternative cost functions show that register-pressure objectives can materially change generated code \cite{shobaki2013,shobaki2019}; ant-colony scheduling studies the quality/scalability trade-off against exact methods on real compiler targets \cite{shobaki2022}. Combinatorial register allocation and scheduling integrates decisions whose separation can lose quality \cite{castaneda2019}. Our action costs have no latency, resource, register, or spill semantics. We use exact scheduling only as a bounded semantic oracle after fixing a selected set.

### `castaneda2019` — unverified
- Bibliography: Combinatorial Register Allocation and Instruction Scheduling (2019); first author `lozano`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - There are $3^b$ canonical cells because each bit is fixed zero, fixed one, or free. Summed cell membership is $4^b$. A straightforward bound with exhaustive subsets and quadratic constraint construction is \[ O\!\left(2^n4^b n^2 + b3^b\right), \] plus payload comparison, sorting, and encoding. Representative enumeration can be much smaller on sparse frontiers, but neither analysis makes the complete tree optimizer scalable in unrestricted $b$ or action count. The method is a bounded exact oracle, not a proposed production scheduling heuristic. Exact trace and instruction scheduling systems likewise distinguish optimality from scalability and use carefully defined objectives, pruning, and timeout accounting \cite{wilken2000,shobaki2009,shobaki2013,shobaki2019,castaneda2019}.
  - AND/OR precedence constraints and their ready algorithm are established scheduling theory \cite{mohring2004}. Optimal instruction scheduling has been formulated with integer programming and enumeration \cite{wilken2000,shobaki2009}. Preallocation scheduling and alternative cost functions show that register-pressure objectives can materially change generated code \cite{shobaki2013,shobaki2019}; ant-colony scheduling studies the quality/scalability trade-off against exact methods on real compiler targets \cite{shobaki2022}. Combinatorial register allocation and scheduling integrates decisions whose separation can lose quality \cite{castaneda2019}. Our action costs have no latency, resource, register, or spill semantics. We use exact scheduling only as a bounded semantic oracle after fixing a selected set.

### `pompougnac2022` — unverified
- Bibliography: Weaving Synchronous Reactions into the Fabric of {SSA}-Form Compilers (2022); first author `pompougnac`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - \paragraph{Finite breadth.} Exhaustive checks cover bounded action and input dimensions; generated models are not production workloads. The campaign is appropriate for falsifying a small semantic implementation, not for demonstrating prevalence, speedup, energy, register pressure, or practical code-size improvement. TACO compiler systems commonly support practical claims with production infrastructure and broad workloads \cite{pompougnac2022,zhou2016,cherubin2020,na2016}; this work makes no such claim.
  - TACO compiler papers connect semantic or analysis ideas to compiler infrastructure and generated-code evidence: synchronous reactions extend SSA, TAFFO couples analyses with precision tuning, and a JavaScript compiler evaluates end-to-end parallelization \cite{pompougnac2022,cherubin2020,na2016}. Phase-ordering systems such as COBAYN, MiCOMP, and clustering-based selection use workloads and compiler integration \cite{ashouri2016,ashouri2017,martins2016}; broader autotuning work includes focused iterative optimization, self-tuning compilers, OpenTuner, CompilerGym, and learned tensor schedules \cite{agakov2006,fursin2011,ansel2014,cummins2022,chen2018}. Those papers calibrate the evidence expected for production claims. Our exact finite oracle is instead evaluated against semantic constructions, and the absent compiler extractor remains a significance limitation. The defensible delta is the first-fault frontier, its representative-selection boundary, and actual-byte replay for one fixed grammar, not a universal priority claim.

### `zhou2016` — unverified
- Bibliography: A Compiler Approach for Exploiting Partial {SIMD} Parallelism (2016); first author `zhou`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 3
  - Real predication mechanisms expose similar trade-offs at a different level. Architectural predicates, hyperblocks, partial SIMD masks, and branch-path melding can trade control transfers for predicated work, duplication, or target-specific support \cite{han2013,zhou2016,moll2018,li2025}. Those systems evaluate execution, code generation, or hardware effects. Figure~\ref{fig:observer-gap} instead isolates how an observation contract and one abstract grammar determine an exact representational optimum.
  - \paragraph{Finite breadth.} Exhaustive checks cover bounded action and input dimensions; generated models are not production workloads. The campaign is appropriate for falsifying a small semantic implementation, not for demonstrating prevalence, speedup, energy, register pressure, or practical code-size improvement. TACO compiler systems commonly support practical claims with production infrastructure and broad workloads \cite{pompougnac2022,zhou2016,cherubin2020,na2016}; this work makes no such claim.
  - More recent control transformations broaden the operational scope. Partial control-flow linearization preserves selected control while linearizing paths for vectorization \cite{moll2018}. PAVER exploits partial SIMD parallelism with compiler transformations and masked execution \cite{zhou2016}. MERIT melds instructions from alternative paths and must make synthesized operations safe \cite{li2025}. These systems can insert, combine, or retarget operations beyond our inherited-action grammar. Their practical correctness questions therefore cannot be answered solely by a \PFC certificate, while their transformation power can evade our private-leaf lower bounds.

### `cherubin2020` — unverified
- Bibliography: Dynamic Precision Autotuning with {TAFFO} (2020); first author `cherubin`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - \paragraph{Finite breadth.} Exhaustive checks cover bounded action and input dimensions; generated models are not production workloads. The campaign is appropriate for falsifying a small semantic implementation, not for demonstrating prevalence, speedup, energy, register pressure, or practical code-size improvement. TACO compiler systems commonly support practical claims with production infrastructure and broad workloads \cite{pompougnac2022,zhou2016,cherubin2020,na2016}; this work makes no such claim.
  - TACO compiler papers connect semantic or analysis ideas to compiler infrastructure and generated-code evidence: synchronous reactions extend SSA, TAFFO couples analyses with precision tuning, and a JavaScript compiler evaluates end-to-end parallelization \cite{pompougnac2022,cherubin2020,na2016}. Phase-ordering systems such as COBAYN, MiCOMP, and clustering-based selection use workloads and compiler integration \cite{ashouri2016,ashouri2017,martins2016}; broader autotuning work includes focused iterative optimization, self-tuning compilers, OpenTuner, CompilerGym, and learned tensor schedules \cite{agakov2006,fursin2011,ansel2014,cummins2022,chen2018}. Those papers calibrate the evidence expected for production claims. Our exact finite oracle is instead evaluated against semantic constructions, and the absent compiler extractor remains a significance limitation. The defensible delta is the first-fault frontier, its representative-selection boundary, and actual-byte replay for one fixed grammar, not a universal priority claim.

### `na2016` — unverified
- Bibliography: A {JavaScript} Parallelizing Compiler for Exploiting Parallelism from Data-Parallel {HTML5} Applications (2016); first author `na`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - \paragraph{Finite breadth.} Exhaustive checks cover bounded action and input dimensions; generated models are not production workloads. The campaign is appropriate for falsifying a small semantic implementation, not for demonstrating prevalence, speedup, energy, register pressure, or practical code-size improvement. TACO compiler systems commonly support practical claims with production infrastructure and broad workloads \cite{pompougnac2022,zhou2016,cherubin2020,na2016}; this work makes no such claim.
  - TACO compiler papers connect semantic or analysis ideas to compiler infrastructure and generated-code evidence: synchronous reactions extend SSA, TAFFO couples analyses with precision tuning, and a JavaScript compiler evaluates end-to-end parallelization \cite{pompougnac2022,cherubin2020,na2016}. Phase-ordering systems such as COBAYN, MiCOMP, and clustering-based selection use workloads and compiler integration \cite{ashouri2016,ashouri2017,martins2016}; broader autotuning work includes focused iterative optimization, self-tuning compilers, OpenTuner, CompilerGym, and learned tensor schedules \cite{agakov2006,fursin2011,ansel2014,cummins2022,chen2018}. Those papers calibrate the evidence expected for production claims. Our exact finite oracle is instead evaluated against semantic constructions, and the absent compiler extractor remains a significance limitation. The defensible delta is the first-fault frontier, its representative-selection boundary, and actual-byte replay for one fixed grammar, not a universal priority claim.

### `hyafil1976` — unverified
- Bibliography: Constructing Optimal Binary Decision Trees Is {NP}-Complete (1976); first author `hyafil`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - The same caution applies to exact sparse search. CORELS supplies certified optimal rule lists for a classification objective \cite{angelino2018}; decision-tree optimization is classically hard \cite{hyafil1976}; binary decision diagrams and learned decision trees use different sharing and objective choices \cite{bryant1986,quinlan1986}. The present private-leaf grammar and exact semantic loss are distinct, but exact search alone is not a novelty claim. The semantic frontier, the representative boundary, and the grammar-relative replay are the joint result.
  - Optimal decision trees are NP-hard in general \cite{hyafil1976}; induction algorithms and reduced decision diagrams optimize different predictive or Boolean objectives and often permit sharing absent from private leaves \cite{quinlan1986,bryant1986}. CORELS produces certifiably optimal rule lists for an empirical-risk objective \cite{angelino2018}. These analogies are important negative novelty evidence: enumeration, dynamic programming, and a small certificate are not by themselves new. Theorems~\ref{thm:frontier}, \ref{thm:unique}, \ref{thm:hard}, and \ref{thm:representatives} supply the semantics-specific reason that the chosen search space is complete.

### `quinlan1986` — unverified
- Bibliography: Induction of Decision Trees (1986); first author `quinlan`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - The same caution applies to exact sparse search. CORELS supplies certified optimal rule lists for a classification objective \cite{angelino2018}; decision-tree optimization is classically hard \cite{hyafil1976}; binary decision diagrams and learned decision trees use different sharing and objective choices \cite{bryant1986,quinlan1986}. The present private-leaf grammar and exact semantic loss are distinct, but exact search alone is not a novelty claim. The semantic frontier, the representative boundary, and the grammar-relative replay are the joint result.
  - Optimal decision trees are NP-hard in general \cite{hyafil1976}; induction algorithms and reduced decision diagrams optimize different predictive or Boolean objectives and often permit sharing absent from private leaves \cite{quinlan1986,bryant1986}. CORELS produces certifiably optimal rule lists for an empirical-risk objective \cite{angelino2018}. These analogies are important negative novelty evidence: enumeration, dynamic programming, and a small certificate are not by themselves new. Theorems~\ref{thm:frontier}, \ref{thm:unique}, \ref{thm:hard}, and \ref{thm:representatives} supply the semantics-specific reason that the chosen search space is complete.

### `bryant1986` — unverified
- Bibliography: Graph-Based Algorithms for Boolean Function Manipulation (1986); first author `bryant`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - The same caution applies to exact sparse search. CORELS supplies certified optimal rule lists for a classification objective \cite{angelino2018}; decision-tree optimization is classically hard \cite{hyafil1976}; binary decision diagrams and learned decision trees use different sharing and objective choices \cite{bryant1986,quinlan1986}. The present private-leaf grammar and exact semantic loss are distinct, but exact search alone is not a novelty claim. The semantic frontier, the representative boundary, and the grammar-relative replay are the joint result.
  - Optimal decision trees are NP-hard in general \cite{hyafil1976}; induction algorithms and reduced decision diagrams optimize different predictive or Boolean objectives and often permit sharing absent from private leaves \cite{quinlan1986,bryant1986}. CORELS produces certifiably optimal rule lists for an empirical-risk objective \cite{angelino2018}. These analogies are important negative novelty evidence: enumeration, dynamic programming, and a small certificate are not by themselves new. Theorems~\ref{thm:frontier}, \ref{thm:unique}, \ref{thm:hard}, and \ref{thm:representatives} supply the semantics-specific reason that the chosen search space is complete.

### `debray2000` — unverified
- Bibliography: Compiler Techniques for Code Compaction (2000); first author `debray`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 2
  - The object cost is actual byte-string length. The semantic table, certificate JSON, primitive operation bodies, and transport framing are separate artifacts. Consequently, a statement such as ``12 bytes'' means 12 bytes in \PFC relative to the shared action table, not 12 bytes of machine code. Code compaction for real instruction sets has additional relocation, alignment, branch-range, and layout concerns \cite{debray2000}; none is silently imported here.
  - Real code-size optimization adds instruction selection, encoding, branch displacement, layout, and link-time effects \cite{debray2000}. Profile-guided tracing and dynamic optimization use execution frequencies and runtime behavior to choose profitable regions \cite{ball1994,bala2000}. The \PFC objective instead charges an analysis grammar exactly and has no profile. It is appropriate for testing a theorem about observer and representation declarations, but it cannot support a machine-code compaction or performance claim.

### `ball1994` — unverified
- Bibliography: Optimally Profiling and Tracing Programs (1992); first author `ball`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Real code-size optimization adds instruction selection, encoding, branch displacement, layout, and link-time effects \cite{debray2000}. Profile-guided tracing and dynamic optimization use execution frequencies and runtime behavior to choose profitable regions \cite{ball1994,bala2000}. The \PFC objective instead charges an analysis grammar exactly and has no profile. It is appropriate for testing a theorem about observer and representation declarations, but it cannot support a machine-code compaction or performance claim.

### `bala2000` — unverified
- Bibliography: {Dynamo}: A Transparent Dynamic Optimization System (2000); first author `bala`
- Registry:  (); first author ``
- Evidence: none 
- Contexts: 1
  - Real code-size optimization adds instruction selection, encoding, branch displacement, layout, and link-time effects \cite{debray2000}. Profile-guided tracing and dynamic optimization use execution frequencies and runtime behavior to choose profitable regions \cite{ball1994,bala2000}. The \PFC objective instead charges an analysis grammar exactly and has no profile. It is appropriate for testing a theorem about observer and representation declarations, but it cannot support a machine-code compaction or performance claim.
