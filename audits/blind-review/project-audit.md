# Blind code and artifact audit

- Python: 19 files, 1915 non-comment lines
- JavaScript: 0 files
- Tests discovered: 16
- Accepted: **False**

## Evidence chains

- explicit_tree_shape_oracle: **False**
- independent_node_verifier: **False**
- restricted_ir_extractor: **False**
- search_refusal: **True**
- strict_json: **False**
- heldout_or_robustness: **True**

## Command results

- `['/opt/pyvenv/bin/python', '-m', 'compileall', '-q', '/mnt/data/pccfr-final-blind/proof-carrying-control-flow-predication-rebalancing/artifact']` → rc=0, 0.698 s
- `['/opt/pyvenv/bin/python', '-m', 'unittest', 'discover', '-s', '/mnt/data/pccfr-final-blind/proof-carrying-control-flow-predication-rebalancing/artifact/tests', '-v']` → rc=1, 0.713 s

## Static risks

- Broad exception handlers: `[('artifact/pccfr/certificate.py', [50])]`
- Bare exception handlers: `[]`
- Silent exception handlers: `[]`
- TODO/FIXME: `[]`
- Network in reproduction shell scripts: `[]`