# Novelty and scope dossier

This dossier records the comparison used to keep the paper's novelty claim narrow.  It is not a proof that no related result exists, and it must not be cited as an external peer review.

## Claim being defended

The paper does **not** claim to invent predication, if-conversion, trace scheduling, speculative code motion, precise exceptions, partial-order scheduling, proof-carrying code, translation validation, or guarded control-flow algebra.  The claim is the combination, within the finite model stated in the paper, of:

1. a necessary-and-sufficient *fault-frontier* certificate for observational equivalence when enabled actions may synchronously fault and action identity is observable;
2. a separation between permutation-only legality and observer-dependent action selection, including the stated easy case and the two-representative hardness boundary;
3. an exact optimizer for the explicitly delimited private-leaf/read-once byte grammar, with a serialized object whose legality and budget can be checked independently; and
4. finite exhaustive, cross-implementation, negative-control, and extraction-bridge evidence tied to those claims.

Every item above is conditional on the paper's entry-state guards, pure action results, immediate synchronous faults, finite input domain, and fixed observer.  The paper makes no production compiler, machine-code, hardware-performance, or general program-equivalence claim.

## Closest families and non-overlap

| Literature family | Established contribution used by this paper | What is *not* claimed as new | Residual distinction tested in the paper |
|---|---|---|---|
| If-conversion, predication, hyperblocks, trace scheduling | Convert/control speculative execution and expose instruction-level parallelism | Predicated execution or code motion itself | Fault identity and the source first-fault frontier are explicit observables, and legality is certified per finite input region |
| Precise exceptions and speculative scheduling | Architectural/compiler conditions for preserving precise state | Precise exceptions or speculative scheduling | The paper studies a finite observer-relative equivalence and a checkable rebalancing object, not a microarchitectural recovery mechanism |
| Partial-order and AND/OR scheduling | Compact legality constraints and scheduling algorithms | AND/OR precedence or scheduling algorithms | The paper characterizes the legality language induced by its fault-frontier semantics and supplies a non-poset witness |
| Proof-carrying code and translation validation | Small checkers validate untrusted transformations | Proof-carrying validation or translation validation | The certificate fields and byte budget are specialized to the declared finite guarded-rebalancing model and PFC1 grammar |
| Guarded/algebraic control-flow equivalence | Equational reasoning about guarded control flow | Guarded Kleene algebra or general CFG equivalence | The result is a finite, fault-sensitive, action-identity observer characterization with explicit selection complexity |
| Exact decision-tree and branching-program optimization | Dynamic programming and exhaustive small-instance oracles | Decision-tree dynamic programming | Exactness is claimed only for the declared private-leaf/read-once grammar and is checked against explicit small tree-shape enumeration |

## Search and falsification protocol

The reference registry and citation-context audit in `artifact/audits/reference/` records the exact bibliography identities and where each item is used.  Searches should cover at least the following conjunctions in ACM DL, DBLP, Crossref, IEEE Xplore, SpringerLink, and arXiv, with citation chasing from the closest results:

- exception-preserving instruction scheduling + predication;
- precise exceptions + if-conversion / hyperblock;
- fault-preserving control-flow restructuring;
- proof-carrying / translation validation + instruction scheduling;
- AND/OR precedence + guarded scheduling;
- decision-tree optimization + exception semantics;
- guarded control flow + faults / exceptions;
- observer-relative compiler transformation equivalence.

A result that provides the same necessary-and-sufficient frontier conditions, the same selection boundary, or a strictly more general certified optimizer would invalidate or require narrowing the corresponding claim.  Accordingly, the paper uses “within the stated model” and “to our knowledge” where priority is asserted.

## Reviewer-facing falsifiers

The contribution should be judged unsupported if any of the following occurs:

- a retained citation is not identifiable from authoritative metadata;
- the paper cites a source for a proposition that the source does not establish;
- the explicit small-tree oracle disagrees with the optimizer;
- the independent direct interpreter accepts an object rejected by the primary semantics, or conversely;
- search truncation can return a result labeled globally optimal;
- the restricted extraction bridge maps two operationally different guarded regions to the same finite table without recording the lost distinction;
- the claimed complexity reduction fails under the exact representation used in the theorem;
- any result depends on a hidden random seed or on generated inputs not included in the archive.
