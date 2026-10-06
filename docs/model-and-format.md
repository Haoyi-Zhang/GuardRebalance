# Model, object, and certificate contract

## Finite semantic table

A model is a strict JSON object with `input_bits`, `actions`, and one complete
row for each input integer from `0` through `2^input_bits-1`. Action identifiers
are consecutive nonnegative JSON integers; Booleans and floating-point values
are not accepted as identifiers. Every row supplies a full source permutation,
an inherited Boolean guard, and a raw outcome for every action.

A raw outcome is exactly one of:

* `{"guard":g,"kind":"silent"}`;
* `{"guard":g,"kind":"emit","value":...}`; or
* `{"guard":g,"kind":"fault","value":...}`.

`value` ranges over strict finite JSON: null, Boolean, integer, finite number,
string, array, or object with string keys. The semantic equality relation is
type preserving, so `{}` differs from `[]`, an object differs from an array of
key/value pairs, and `false` differs from `0`. For an emission, `value` is the
payload and the observed event is `(action_id,value)`. For a fault, `value` is
the complete terminal signature declared visible by the client. The word
*signature* is semantic terminology, not a second JSON field.

A false guard annuls the raw outcome before evaluation. An enabled fault
terminates the region. Guards and raw outcomes are immutable functions of the
entry input. There are no mutable reads, handlers, loops, concurrency, timing
observations, or production-ISA effects.

The source is a full permutation. A target leaf is a nonrepeating ordered
subset of inherited action identities. Omission and reordering are the only
leaf transformations. A tree may branch only on an entry bit not already
examined on its root-to-leaf path. Leaves are private; the format has no shared
suffix, synthesized predicate, unconditional throw, or new primitive.

## Canonical PFC1 bytecode

All 16-bit integers are unsigned **little-endian**. Input integer `x` maps to
bit `x mod 8` of byte `floor(x/8)` in every guard mask; within a byte, input 0
is the least-significant bit.

| Item | Encoding | Bytes |
|---|---|---:|
| Header | ASCII `PFC1`, `input_bits`, zero reserved byte | 6 |
| Branch | ASCII `B`, tested-bit index (`u8`) | 2 |
| Leaf | ASCII `L`, action-copy count (`u16le`) | 3 |
| Action copy | action id (`u16le`), flag (`u8`) | 3 |
| Guard mask | `ceil(2^b/8)` global LSB-first bytes when flag is 1 | variable |

A leaf action uses flag 0 and omits its mask exactly when its inherited guard is
true for every input in that leaf cell. Otherwise it uses flag 1 followed by
the complete global input mask, including bits outside the cell. The decoder
rejects wrong magic, width mismatch, nonzero reserved bytes, unknown tags,
invalid or repeated branch bits, unknown or duplicate action identities,
invalid flags, noncanonical masks, wrong masks, every truncation, and trailing
bytes.

The hand-calculable fixture in `fixtures/golden-pfc1/` fixes every byte. Its
single action is enabled only on input 0, so the final mask byte is `01`:

```text
50 46 43 31 01 00 4c 01 00 00 00 01 01
```

The object cost is the actual byte-string length. It is relative to the common
semantic/action table. It excludes model JSON, certificate JSON, primitive
instruction bodies, transport framing, and real ISA encoding. A reported PFC1
optimum is therefore grammar-relative, not a cache, execution-time, or machine-
code claim.

## Certificate

The certificate records the exact object size and each decoded leaf cell. Each
cell lists reached input rows and the decoded action order. For a faulting
source input it supplies one acceptable terminal-fault action identity; for a
normally returning input it supplies null.

The `input_bits` and `object_size` fields must be JSON integers, not Boolean or
floating-point values that compare equal to integers. Cells, orders, and
nonnull witnesses likewise use integer identities. Each outcome's `kind`
must be one of the three string tags specified above; other JSON types are
rejected as model errors before outcome interpretation.

The checker independently decodes the actual object and recomputes source
prefixes, enabled emissions, enabled faults, acceptable fault sets, and
barriers from the model. It checks:

1. exact model typing and complete input coverage;
2. exact PFC1 decoding and canonicality;
3. actual byte length against certificate length and external budget;
4. exact leaf/cell correspondence and one appearance of every input;
5. source emission-prefix preservation and order;
6. completion of that prefix before every selected enabled fault;
7. acceptable-fault coverage; and
8. one supplied acceptable fault before each selected extra emission or wrong-
   signature fault.

Passing proves observational equivalence for every explicitly tabulated input,
relative to the declared model and trusted checker implementation. It does not
prove correct extraction from a compiler IR, adequacy of the chosen observer,
or minimum size.

## Search modes and refusal

`optional_subset` enumerates every optional subset after the exact mandatory
set. Here the mandatory set is **exactly** the union of all source-prefix
identities and all singleton acceptable-fault sets. `representative_tuple`
chooses one representative from each distinct non-singleton acceptable-fault
set. `auto` chooses the smaller complete candidate space. Explicit modes are
never overwritten. The configured limit is tested before enumeration; an
over-limit space is `refused`, not `infeasible`.

Whole-tree optimization distinguishes:

* `optimal`: every competing leaf and branch alternative was completely
  searched and the returned tree is minimum in the private-leaf grammar;
* `infeasible`: complete search proved that no grammar object exists; and
* `incomplete`: diagnostic-only best feasible tree after at least one required
  alternative was refused. Such a tree is never reported as proven optimal.
