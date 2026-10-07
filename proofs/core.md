# Fault-frontier arguments

These are handwritten mathematical proofs, not proof-assistant output. The Python programs implement finite semantics and test these arguments on declared bounded families. No test count is a general proof. The compiler-to-model extraction boundary is assumed, not implemented.

## 1. Objects and observation

Let A be a finite set of action identities and X a nonempty finite input set. For each (x,a), a fixed guard g(x,a) is Boolean, and the raw outcome is silent τ, an emission (a,v), or a terminal fault κ. Emission identities are unique: executing different actions cannot produce the same tagged event. Payloads and fault signatures are immutable functions of the entry input. A disabled action is annulled before evaluating its raw outcome. Executing an enabled fault terminates the whole region. There is no handler or resumption within the region. Normal termination has no additional payload. Any live output, external side effect, or observed control event must appear as a tagged emission.

The source specifies a full permutation σ_x of A for every input. Its latent suffix after the first enabled fault is not executed. For an ordered subset π of A, Obs_x(π) is the tagged emission word followed by either normal return or the first fault's complete observer-visible signature. A leaf valid on cell C⊆X has Obs_x(π)=Obs_x(σ_x) for every x∈C.

For each input define P_x as the ordered action identities in the source emission word, F_x as all enabled fault actions, M_x as all enabled emission actions, and, for a faulting source with signature κ_x, G_x={a∈F_x : κ(x,a)=κ_x}. For a normally returning source G_x=∅. Since the source is a full permutation, it returns normally iff F_x=∅. This fact is essential. All sets include latent suffix actions as appropriate.

## 2. Exact frontier characterization

**Theorem 1.** Let S be the identities in π, with strict order <π. The leaf is valid on C iff, for every x∈C:

1. every action in P_x is in S;
2. the adjacent actions of P_x occur in that order in π;
3. if the source faults, S∩G_x is nonempty;
4. if the source faults and P_x is nonempty, its last action precedes every member of S∩F_x;
5. if the source faults, every selected barrier v in ((M_x\P_x)∪(F_x\G_x))∩S has some g∈G_x∩S preceding v.

Set subtraction by P_x means subtraction of its identities.

*Necessity.* Fix x. Equal tagged words force every source-prefix identity to be retained, executed, and in the same order: no different action can replace its tag. If the source faults, the target must also fault with κ_x. Let f be its first enabled fault. It is selected and belongs to G_x, establishing coverage. All source-prefix actions execute before f. No other selected fault can precede the final prefix action: the earliest such fault would terminate too soon. A selected extra emission cannot precede f, since it would add a different tag to the observed word. A selected wrong-signature fault cannot precede f, by definition of f and equality of terminal signatures. Thus f precedes every barrier and witnesses condition 5. Normal source execution has no enabled fault; conditions 3–5 do not apply.

*Sufficiency.* Fix x. For a normal source, F_x is empty and M_x is exactly the set of P_x identities. Conditions 1–2 execute exactly this ordered word; all other selected actions are silent or disabled, so return agrees. For a faulting source, coverage gives at least one selected enabled fault. Let f be the earliest selected enabled fault. If f∉G_x, it is a barrier, so condition 5 gives an earlier selected good fault, contradicting minimality. Hence f∈G_x. Conditions 1, 2, and 4 place every required emission, in source order, before f. If a selected extra emission v preceded f, condition 5 would give a selected good fault before v, contradicting minimality of f again. Thus the word before f is exactly the source word and the terminal signature is κ_x. Input-wise equality proves the theorem. ∎

**Corollary 1 (one witness per input).** Conditions 3 and 5 can equivalently be checked by supplying one g_x∈S∩G_x that precedes all selected barriers. Every valid order admits such a witness: choose its first enabled fault. Conversely the single witness supplies every required existential predecessor. The supplied witness need not itself be the first fault or execute; an earlier good fault can cancel it. Conditions 1, 2, and 4 still have to be checked.

**Boundary counterexamples.** Without identity-tagged emissions, two equal emissions could substitute for each other and condition 1 would no longer be necessary. With guard evaluation that can fault, a false guard cannot simply erase an action. With state-dependent reads after writes, precomputed raw outcomes are not invariant under reordering. With a handler, emissions after a caught fault may become visible. None of these models is covered.

## 3. Waiting-condition languages

A canonical waiting condition (Y,j) has nonempty Y⊆A\{j}; it requires some y∈Y to occur before j. A family of conditions is conjunctive across conditions and disjunctive within Y. These are the established AND/OR precedence constraints of Möhring, Skutella, and Stork (SIAM Journal on Computing 33(2), 2004, 393–415; DOI 10.1137/S009753970037727X). The ready algorithm and residual obstruction below are known scheduling facts, not new algorithms.

**Theorem 2 (representation).** On full permutations, the legality languages of snapshot-action models are exactly the languages defined by finite families of canonical waiting conditions.

*Forward direction.* With S=A, coverage is automatic: the source itself contains every prefix identity and a good first fault at every faulting input. Conditions 2 and 4 become singleton waiting conditions. Condition 5 is (G_x,v) for each barrier v. Good sets are nonempty and do not contain their barriers. Theorem 1 gives equality of languages.

*Reverse direction.* For each condition (Y,j), allocate one input. At that input, every action of Y faults with the same complete signature κ, j emits its own tag, and every remaining action is silent. Guards are true. Choose any source permutation beginning with an action of Y. Its observation is the empty word followed by κ. A target full permutation agrees exactly when some Y action precedes j, which is precisely the condition. Conjoin inputs. Repeated identical rows can pad the number of inputs to a power of two without changing legality. The empty condition family is represented by a single all-silent input. Each row specifies a valid source permutation even when the combined family has no valid branchless permutation. ∎

**Proposition 1 (smallest nonempty non-poset language).** With three actions a,b,z, where a and b fault with the same signature and z emits, source order abz admits exactly abz, azb, baz, bza. No directed acyclic graph on these identities has exactly these topological orders. For every ordered pair, one of these four permutations reverses the pair. Hence an exact graph could contain no precedence edge, but its six topological orders would then include zab and zba, which expose z. With zero or one identity there is only one permutation. With two identities, every nonempty permutation family is either a singleton or both permutations, represented by one edge or no edge. Thus three is minimal under the stated nonempty-family/full-permutation criterion. ∎

**Known ready algorithm.** Start with no emitted identities. A node is ready when each condition targeting it already has an emitted predecessor. Emit any ready node and satisfy all waiting conditions containing it as an alternative predecessor. If all nodes are emitted, their order satisfies every condition. If a nonempty set R remains and no node is ready, each j∈R has an unmet condition (Y,j) with Y⊆R. Every alleged valid continuation has an earliest R member; that member's unmet condition requires an earlier R member, a contradiction. This also proves that arbitrary ready choices cannot destroy feasibility. With reverse incidence lists the work is linear in node/condition/incidence count; deterministic sorting in this implementation is additional overhead. A nonempty R with the stated property is a replayable infeasibility witness. This proof restates the known method to make its use self-contained.

## 4. Unique representatives and action selection

Action costs c_C(a)>0 are additive and independent of order within the fixed cell C. The leaf has an additional fixed charge.

**Theorem 3 (least mandatory set).** Suppose every faulting input in C has exactly one acceptable representative, |G_x|=1. Define Q as the union of all source-prefix identities and all these unique representatives. If any valid leaf exists, restricting its order to Q is valid. Consequently Q is the unique inclusion-least feasible identity set. Feasibility and minimum positive additive cost reduce to acyclicity and topological ordering of ordinary precedence constraints on Q.

*Proof.* Every valid leaf contains Q by Theorem 1. Fix a valid order π and an input x. If the source returns, all required emissions are in Q and there is no enabled fault. Deleting S\Q leaves exactly the same observed word. If the source faults, the target's first enabled fault must be the unique member g_x of G_x. It is in Q. Every required prefix emission is also in Q. Deleting other actions leaves the prefix unchanged, keeps g_x at its relative position after the prefix, and cannot introduce an emission or earlier fault. The shortened trace thus has the same terminal observation. This holds for all inputs. By Theorem 1, the constraints on Q have only singleton predecessors: the prefix edges, prefix-to-fault edges, and unique-good-to-barrier edges. A directed cycle makes every Q order impossible; adding optional actions cannot help, because a valid superset would restrict to Q. An acyclic graph supplies a topological order of Q. Strictly positive additive costs make every strict superset more expensive. Polynomial construction in the explicit input table plus graph traversal proves the complexity statement. ∎

The uniqueness condition concerns complete observed signatures, not merely exception class. Distinct origins may be observationally equal only if the declared semantics really makes them indistinguishable. Preserving origin by fiat is a conservative baseline, not evidence that a real ABI permits origin erasure.

**Theorem 4 (selection hardness with two representatives).** For the unbounded mathematical family, deciding whether a valid branchless leaf with at most k selected actions exists is NP-complete, even with all guards true, no emissions, unit positive action costs, one observed fault signature, and exactly two acceptable representatives at every input.

*Proof.* The problem is in NP: provide a non-repeating order of at most k action identities and directly evaluate it against the source for every explicitly listed input. This is polynomial in the encoded model and witness lengths, including payload comparisons.

Reduce Vertex Cover on a simple graph (V,E) with at least one edge. Use one action per vertex and one input per edge e={u,v}. At that input, actions u and v fault with the same signature κ and all other actions are silent. Put one endpoint first in the source order. The source observation is always the empty word followed by κ. A selected order has this observation exactly when its selected set intersects {u,v}; order does not matter. Therefore a size-at-most-k valid leaf exists exactly when the graph has a vertex cover of size at most k. Constructing all rows and source orders takes polynomial space. Padding edge rows to a power of two preserves the equivalence and increases their count by less than a factor of two. Every row has two good representatives. ∎

This is a reduction using a standard NP-complete problem, not a new hardness result about Vertex Cover. The implementation's fixed limits (at most eight input bits and a configurable complete-candidate-space limit) cannot themselves define an asymptotically NP-complete family. The candidate limit is not an action-count bound: representative search can admit models with more than twelve actions.

## 5. Object grammar and exact optimization

For b entry bits let q=2^b and w=ceil(q/8). A target is a binary prefix tree. A branch tests one entry bit not previously tested on that path; leaves are private rather than shared. A leaf contains an ordered subset of action identities. An action retains its complete original guard. Its guard may be omitted only when true at every input in that leaf's cell. New guard strengthening, primitive synthesis, and shared suffixes are not productions of this grammar.

The executable format charges a six-byte header, two bytes per branch, three bytes per leaf, and three bytes per action copy plus w bytes when its guard must be retained. It is a region bytecode relative to the common immutable action table. Primitive bodies, model JSON, and certificate JSON are not region-object bytes. No hardware ISA interpretation or instruction-cache/runtime claim follows.

Let L(C) be the minimum leaf charge among all valid selected orders on cell C, or infinity if none exists. The subset algorithm examines every S⊆A, rejects coverage failures, runs the known AND/OR ready test, and minimizes the positive additive leaf cost. Since cost is order independent, one successful schedule per subset suffices. Theorem 3 supplies a faster exact path when all good sets are singletons. Cost pruning discards only a subset whose already known charge cannot improve the incumbent, not a semantic possibility needed by another subset.

For a cell whose fixed bits are d and values v define

D(C) = min( L(C), min over free bits i of [2 + D(C∩{x_i=0}) + D(C∩{x_i=1})] ).

**Theorem 5 (grammar-relative optimum).** The minimum whole-object charge is 6+D(X), and the reconstructed object is valid. Every object in the grammar is represented by the recurrence.

*Proof.* Induct on the number of free bits of C. With no free bits, a source order is a valid leaf, and no branch is permitted; L(C) is exact by exhaustive subset selection and schedule feasibility. At a general cell, any object is either a leaf, charged at least L(C), or a branch on an unused bit i with two private child objects. Its cost is exactly two plus the sum of its child costs. By the induction hypothesis each child cost is at least its D value, so every object costs at least the displayed minimum. Conversely choose an attaining leaf or branch and attaining child objects. The leaf is valid by Theorem 1; a branch partitions inputs, so valid children make the parent valid. Because the grammar has finitely many read-once tree shapes and subset orders, the minimum is attained. Singleton source leaves also show feasibility of a fully split tree. Adding the one common header completes the proof. ∎

There are 3^b canonical cells. Counting memberships of inputs in cells gives 4^b: each bit contributes four (cell description,input bit) possibilities, namely fixed zero/zero, fixed one/one, free/zero, free/one. With straightforward O(|C| n²) constraint construction per subset and incidence-based scheduling, an upper bound for the abstract search is O(2^n 4^b n² + b 3^b), plus payload and sorting/encoding costs. The Python scheduler builds reverse incidences and marks each waiting condition satisfied once; a min-heap preserves the smallest-ready order with logarithmic node-ordering overhead. This is an exponential bounded method, not a scalable general compiler optimizer. The precise-origin fast path makes a fixed cell polynomial, but not the complete bit-partition dynamic program polynomial in b.

## 6. Certificate replay and trust

An object decoder enforces the header/action-table arity, exact binary grammar, unused branch bits, action uniqueness, inherited guard masks, canonical omission of all-true guards, and consumption of every byte. The externally supplied budget is compared with the actual byte-string length. Declared size in the certificate must match the same length.

The certificate lists every decoded leaf cell and every input in that cell, with one good representative for a faulting input and a null marker for normal return. The checker recomputes source summaries from the supplied model; it does not accept summaries, prefixes, guards, or observation classes from the optimizer. It checks Theorem 1's coverage/order/last-prefix conditions and Corollary 1's single-witness conditions. Missing/extra cells or input rows, wrong witnesses, and type mismatches are rejected.

**Theorem 6 (abstract checker soundness and relative completeness).** If a well-formed model, a decoded object, and a certificate pass these rules at budget B, the object has at most B bytes and is observationally equivalent to the source for every input. Conversely every valid canonical object of at most B bytes admits a passing certificate.

*Proof.* The decoder's cells form a partition, by induction on the read-once tree. The checker covers every input in every cell exactly once. The per-input checks imply Theorem 1, so every reached leaf is valid. The byte comparison is on the actual object, not a claimed cost. Conversely for each valid leaf and input choose its first enabled fault as witness, or null for normal return, and list the exact decoded cells and actual size. Corollary 1 proves all checks pass. ∎

This theorem is about the specified rules. The Python implementation is not mechanically verified. Its tests provide finite evidence of conformance. The checker depends on the Python runtime, the object parser, the supplied immutable semantic table, and the completeness of the declared observation. It does not authenticate the model, verify the extraction of a source program into that table, or certify that the optimizer's output is smallest. Object size excludes transport of the semantic table and certificate; these are separate artifacts.

## 7. Refinement and a representation-dependent gap

An observer refinement replaces a fault signature by a more informative signature with a deterministic projection back to the old one. Emission tagging, guards, actions, target grammar, and byte charges stay fixed.

**Proposition 2 (monotonicity).** Every target valid under the refined observer is valid under the coarser one, by projecting the terminal observation. Therefore the refined minimum size is no smaller. This assertion does not permit changing the actual observer contract to obtain an improvement.

**Theorem 7 (exact private-leaf gap).** For b≥0 let m=2^b. There is a family whose coarse optimum is 12 bytes and whose precise-origin optimum is 8m+4 bytes in the specified bytecode, for all parameters representable in that bytecode.

*Construction and proof.* Use m always-enabled actions, all of which immediately fault. On input x the source permutation starts with action a_x. Under the coarse observer every action produces the same complete signature κ. A leaf containing any single action is valid. Every valid object must contain at least one leaf and one action, so its cost is at least 6+3+3=12, attained by that leaf.

Under the precise observer action a produces signature (κ,a). A leaf containing two inputs x≠y would have one fixed first selected action, but correctness requires it to be both a_x and a_y. Hence every valid leaf cell contains only one input. The tree therefore has exactly m singleton leaves and m−1 branches. Each leaf requires at least one action and one suffices, giving cost 6+2(m−1)+m(3+3)=8m+4. This is attained by a fully split tree with one appropriate action per leaf. ∎

The byte formula uses the fixed action-index/header widths, so an unbounded asymptotic interpretation must explicitly idealize those fixed charges or generalize the format. For the mathematical grammar, the structural gap is one versus m action copies and zero versus m−1 branches; this is exponential in b but only linear in the explicitly tabulated q=m inputs. The executable confirms b=0,1,2,3. Predicate strengthening (for example guard a_x by x), synthesized unconditional throws, or shared control/data representation changes the search space; the same lower bound cannot be transferred to such representations.

## 8. Evidence map and unresolved external claims

The finite comparison families, exact inputs, seeds, raw object/certificate example, and negative controls are in results/confirmed. The additional two-state campaign covers 625 profiles × four source-order pairs × five partial target orders = 12,500 joint comparisons of direct observations, frontier validity, and row-level witness existence. It does not encode objects or replay serialized certificates. The two-state unit test checks both rows separately on the same family. These are boundary checks rather than practical benchmarks.

These arguments establish statements within the declared snapshot-action and observer model. They do not establish novelty over every existing compiler or scheduling formulation, practical applicability of observer quotients to a real exception ABI, or TACO acceptance/readiness. The original historical source and the broader twelve-plus-five-plus-five calibration set were substantively reviewed; the resulting contribution boundary is recorded in `docs/literature.md`. This calibration does not prove universal priority or acceptance readiness.

## 9. Completion, sparsification, and exact representative search

These arguments strengthen the leaf-search implementation without changing the action model, observer, or byte grammar.

**Lemma 8 (completion).** If π is a valid leaf on C, appending any ordering of any omitted action identities preserves validity. Consequently a valid selected leaf exists exactly when a valid full permutation exists.

*Proof.* At a faulting input the valid leaf already terminates with the required signature; its appended suffix is not executed. At a normally returning input, the full source has no enabled fault and every enabled emission is in its required prefix. Validity and unique tags imply that all these emission identities are already in π. An omitted action is therefore silent or disabled on such an input. Appending it does not change the observed word or termination. The assertion holds for any number of appended identities. The converse implication, from a valid full permutation to a selected leaf, is immediate. ∎

Combining the lemma with Theorem 2 and the known ready algorithm gives polynomial-time branchless feasibility in the explicit model even when minimum-size branchless selection is NP-complete. A closed residual of the full-system waiting constraints disproves all selected leaves, not merely the particular order attempted by the optimizer. This is a restatement and use of established AND/OR feasibility, not a new scheduling algorithm.

**Lemma 9 (frontier sparsification).** Let P be the union of the source-prefix identities over a cell. In any valid leaf π, let f_x be its first enabled fault on each faulting input. Restricting π to Q=P∪{f_x : x faults} preserves validity. If two faulting inputs have the same good set G_x=G_y, their f_x and f_y are equal. Therefore every inclusion-minimal valid leaf retains at most |P|+d actions, where d is the number of distinct good sets in the cell.

*Proof.* All required emissions and each input's actual terminal action remain in Q. Deletion cannot introduce an event or change relative order, and it cannot remove the retained first fault. Thus each faulting input has its original observed prefix and terminal fault, and a normally returning input retains exactly its required emissions. For equality of representatives, a valid leaf's first enabled fault is in G_x; it must therefore also be the earliest selected member of G_x. The earliest selected member of the same set is the same action under the same leaf order, so G_x=G_y implies f_x=f_y. If a valid selected set were inclusion-minimal but had more than |P|+d actions, the valid restriction Q would be a proper subset, contradicting minimality. ∎

It follows in particular that actions outside R=P∪⋃_x G_x can be removed without excluding any positive-cost optimum. Feasibility on R is equivalent to feasibility on all actions: restrict a valid leaf to Q⊆R and use completion to append R\Q. This justifies running the full-set obstruction test on R rather than on all latent primitives.

**Theorem 10 (exact representative enumeration).** For each distinct good set G choose one representative f_G∈G, and form Q_f=P∪{f_G}. The minimum positive additive cost of a valid leaf equals the minimum feasible cost among these selected sets, with feasibility decided by the frontier constraints and the known ready algorithm. Define the mandatory set exactly as M=P∪⋃_{G:|G|=1}G. Complete search may enumerate either all subsets of R\M added to this exact M, or all tuples over the non-singleton good sets. The smaller candidate-space bound is

    min(2^|R\M|, product over distinct non-singleton G of |G|).

*Proof.* Every feasible enumerated set supplies a valid leaf, so its cost cannot be below the true optimum. Conversely take an optimal leaf. Positive costs imply that its valid restriction from Lemma 9 cannot be strictly cheaper; choose f_G as the common first selected good member of G. Its restricted selected set is Q_f and appears in the representative enumeration. A feasible ordering of that same set has the same additive cost, independent of ordering. Hence the representative minimum attains the true optimum. Every optimal selected set is contained in R and contains this exact M, so the optional-subset enumeration is exact as well. An arbitrary strict superset of M is not mandatory and could exclude an optimum. Taking the smaller complete search space changes only execution cost. Duplicate representative tuples yielding the same selected set may be discarded because its feasibility is decided afresh using the full AND/OR constraints, not using the tuple as an additional order requirement. ∎

For fixed numbers and sizes of distinct good sets, the expensive search is bounded independently of the number of irrelevant actions. Reading and checking the complete input table still costs at least its size. For fixed q input states, representative enumeration gives a polynomial n^q bound in action count, up to table, payload, sorting, and waiting-condition construction costs; this is not a polynomial bound when q grows. A configured candidate-space limit rejects an instance before incomplete search and does not constitute an infeasibility certificate. These are exact finite-model algorithms, not learned-model or hardware observations.
