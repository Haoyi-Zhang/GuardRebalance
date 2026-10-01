# Artifact inspection checklist

1. Run `python -m unittest discover -s tests -v` and inspect the named regression cases.
2. Read `results/confirmed/repair-validation.json` for the requested search-mode, typed-signature, refusal-state, parser, golden-byte, source-type, and action-domain microexamples.
3. Inspect `results/confirmed/exhaustive.json`; do not merge direct comparisons, witness checks, and serialized object/certificate replays.
4. Inspect `results/confirmed/trees.json` and `pccfr/oracle.py` to confirm that the 130 comparison path enumerates tree shapes and direct leaf orders rather than reusing the production DP.
5. Inspect `results/confirmed/and-or.json` and `pccfr/generate.py::waiting_family_model` for the real snapshot constructions and per-permutation semantic comparisons.
6. Inspect every record in `results/confirmed/controls.json`; success requires the expected outcome and exact reason/stage.
7. Run `python replay_inputs.py --reference results/confirmed --out results/reproduced-review-input-replay.json`; verify stable-ID loading, numerical/status/mode results, PFC bytes, and binding separately.
8. Run `./reproduce-clean.sh` from a clean extraction. It must refuse existing, linked, retained, or outside output paths and must not delete anything.
9. Read `docs/model-and-format.md` and the golden fixture before interpreting PFC1 bytes.
10. Read the paper's validity section and `CURRENT-STATE.md` for the non-claims. The artifact does not supply a compiler extractor, real-ISA size result, hardware evaluation, mechanized proof, or independent review.
