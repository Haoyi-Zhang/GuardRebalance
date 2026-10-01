# Hand-calculable PFC1 golden object

This fixture fixes one input bit and one inherited action.  Action 0 is enabled
only for input 0; when enabled it terminates with the complete JSON fault value
`"F"`.  The root is a single leaf that copies action 0.

The 13 bytes are calculated without the encoder:

| Offset | Bytes | Meaning |
|---:|---|---|
| 0 | `50 46 43 31` | ASCII `PFC1` |
| 4 | `01` | one input bit |
| 5 | `00` | reserved zero |
| 6 | `4c` | leaf tag `L` |
| 7 | `01 00` | one action copy, unsigned 16-bit little-endian |
| 9 | `00 00` | action id 0, unsigned 16-bit little-endian |
| 11 | `01` | explicit inherited guard mask follows |
| 12 | `01` | LSB-first mask: bit 0 is input 0 (true), bit 1 is input 1 (false) |

`region.hex` is the human-readable authority; `region.pfc` is the exact binary
copy used by the regression test.  The semantic JSON schema uses `value` for
both emissions and faults.  For a fault, that value is the complete declared
observer-visible fault signature.
