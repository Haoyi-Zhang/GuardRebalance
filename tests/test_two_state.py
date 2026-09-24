from __future__ import annotations

import itertools
import unittest

from pccfr.frontier import frontier_valid, witness_valid
from pccfr.generate import two_row_profiles
from pccfr.model import observe, source_observation


class TwoStateBoundaryTests(unittest.TestCase):
    def test_all_effective_two_action_profiles(self):
        orders = [(), (0,), (1,), (0,1), (1,0)]
        sources = [([0,1],[0,1]),([0,1],[1,0]),([1,0],[0,1]),([1,0],[1,0])]
        for p0 in itertools.product(range(5), repeat=2):
            for p1 in itertools.product(range(5), repeat=2):
                for s0, s1 in sources:
                    model = two_row_profiles(p0,p1,s0,s1)
                    for order in orders:
                        for row in model["rows"]:
                            direct = observe(row, order) == source_observation(row)
                            front = frontier_valid(row, order)
                            cert = any(witness_valid(row, order, w) for w in [None,0,1])
                            self.assertEqual(direct, front)
                            self.assertEqual(front, cert)


if __name__ == "__main__":
    unittest.main()
