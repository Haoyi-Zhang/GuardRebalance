"""Finite schema regressions for scalar certificate fields and outcome kinds."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from pccfr.bytecode import encode_object
from pccfr.certificate import check_certificate, make_certificate
from pccfr.generate import observer_gap_model
from pccfr.model import ModelError, validate_model
from pccfr.provenance import _aggregate


class ContractBoundaryTests(unittest.TestCase):
    def test_source_binding_uses_case_sensitive_posix_name_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            names = ("README.md", "model.json", "region.pfc")
            expected = hashlib.sha256()
            paths = []
            for name in names:
                data = name.encode("ascii")
                path = root / name
                path.write_bytes(data)
                paths.append(path)
                expected.update(name.encode("utf-8"))
                expected.update(b"\0")
                expected.update(len(data).to_bytes(8, "big"))
                expected.update(data)
            actual = _aggregate(root, reversed(paths))
            self.assertEqual(actual["aggregate"], expected.hexdigest())
            self.assertEqual(actual["files"], 3)

    def test_certificate_metadata_requires_json_integers(self):
        for bits in (0, 1):
            model = observer_gap_model(bits)
            obj = encode_object(model, {"type": "leaf", "order": [0]})
            cert = make_certificate(model, obj)
            self.assertTrue(check_certificate(model, obj, cert, len(obj))["accepted"])
            for field, value in (
                ("input_bits", bool(bits)),
                ("input_bits", float(bits)),
                ("object_size", float(len(obj))),
            ):
                with self.subTest(bits=bits, field=field, value=value):
                    supplied = copy.deepcopy(cert)
                    supplied[field] = value
                    result = check_certificate(model, obj, supplied, len(obj))
                    self.assertEqual(result["reason"], "invalid-certificate")
                    self.assertEqual(result["stage"], "certificate")

    def test_nonstring_outcome_kind_is_a_model_error(self):
        for kind in ([], {}, None, False, 0, 0.0):
            with self.subTest(kind=kind):
                model = observer_gap_model(0)
                obj = encode_object(model, {"type": "leaf", "order": [0]})
                cert = make_certificate(model, obj)
                model["rows"][0]["outcomes"][0]["kind"] = kind
                with self.assertRaises(ModelError):
                    validate_model(model)
                result = check_certificate(model, obj, cert, len(obj))
                self.assertEqual(result["reason"], "invalid-model")
                self.assertEqual(result["stage"], "model")
