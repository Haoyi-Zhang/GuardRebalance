# Model, object, and certificate contract

## Finite semantic table

A model is a JSON object with `input_bits`, `actions`, and one complete row for each input integer from `0` through `2^input_bits-1`. Action identifiers are consecutive nonnegative integers and every row supplies a source permutation, guard value, and raw outcome for every action.

A raw outcome is one of:

* `{"kind":"silent"}`;
* `{"kind":"emit","value":...}`; or
* `{"kind":"fault","signature":...}`.

An emitted event is observed as the pair `(action_id, value)`, so equal payloads from different actions do not substitute for one another. The signature contains the complete terminal information declared visible by the model. A false guard annuls the raw outcome before evaluation. An enabled fault terminates the region. Guards and raw outcomes are immutable functions of the entry input; there are no mutable reads, handlers, loops, concurrency, or timing observations.

The source row gives a full permutation. A target leaf gives a nonrepeating ordered subset of inherited action identities. Omission and reordering are the only leaf transformations. A tree may branch only on an entry bit not already tested on its root-to-leaf path. Leaves are private; the format has no shared suffix, synthesized predicate, unconditional throw, or new primitive.

## Canonical bytecode

All multibyte integers are unsigned and big-endian.

| Item | Encoding | Bytes |
|---|---|---:|
| Header | ASCII `PFC1`, `input_bits`, zero reserved byte | 6 |
| Branch | ASCII `B`, tested bit | 2 |
| Leaf | ASCII `L`, action-copy count (`u16`) | 3 |
| Action copy | action id (`u16`), flags | 3 |
| Guard mask | `ceil(2^b/8)` bytes, when required | variable |

A leaf action omits its mask exactly when its inherited guard is true for every input in that leaf cell. Otherwise the global input mask is encoded, with bits outside the cell still representing the immutable global guard. The decoder rejects wrong headers, reserved flags, truncation, trailing bytes, repeated branch bits, duplicate action identities in a leaf, unknown actions, noncanonical all-true masks, and masks that disagree with the supplied model.

The object cost is the actual byte-string length. It is a compact region object relative to the common semantic/action table. It does not include the model JSON, certificate JSON, primitive instruction bodies, transport framing, or a real ISA encoding. Consequently the reported byte optimum is grammar-relative and is not a hardware cache or runtime claim.

## Certificate

The certificate records the exact object size and every decoded leaf cell. Each cell lists the reached input rows and the decoded action order. For a faulting source input it supplies one acceptable terminal-fault representative; for a normally returning input it supplies null.

The checker independently decodes the object and recomputes source prefixes, enabled emissions, enabled faults, acceptable fault sets, and barriers from the model. It checks:

1. exact model typing and complete input coverage;
2. exact object decoding and canonicality;
3. actual byte length against both the declared certificate length and the external budget;
4. exact leaf/cell correspondence and one appearance of every input;
5. preservation and order of the source emission prefix;
6. completion of that prefix before every selected enabled fault;
7. acceptable-fault coverage; and
8. one supplied acceptable fault before every selected extra emission or wrong-signature fault.

Passing therefore proves observational equivalence for every explicitly tabulated input, relative to the abstract checker rules and trusted implementation. It does not prove that a real compiler region was extracted correctly, that the model's observation is adequate for an ABI, or that the object is minimum size.

## Search modes and refusal

`optional_subset` enumerates every optional subset after mandatory identities. `representative_tuple` chooses one representative from each distinct non-singleton acceptable-fault set. `auto` chooses the smaller complete candidate space. The exact sparsification theorem justifies both spaces for positive additive leaf costs. The configured candidate limit is checked before incomplete enumeration. Exceeding it raises `SearchRefusal` and produces status `refused`; this is neither a timeout nor a semantic infeasibility certificate.

The whole-tree dynamic program enumerates read-once private-leaf entry-bit trees. For each canonical cell it compares the exact admitted leaf cost with every unused-bit split. The optimizer is complete only for this grammar, finite input table, positive costs, and admitted leaf search.
