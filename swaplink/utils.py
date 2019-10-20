import random
from collections.abc import Sequence
from typing import Any


def random_choice_safe(sequence: Sequence, default: Any = None) -> Any:
    try:
        return random.choice(sequence)
    except IndexError:
        return default
