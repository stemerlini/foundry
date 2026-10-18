import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from counters import Counters  # noqa: E402


def test_counts_and_clears():
    c = Counters(3)
    c.hit(0)
    c.hit(2)
    c.hit(2)
    assert c.read_and_clear() == [1, 0, 2]
    assert c.read_and_clear() == [0, 0, 0]
