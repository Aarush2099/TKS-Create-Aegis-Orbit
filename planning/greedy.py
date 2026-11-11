import math
from collections.abc import Iterable


def leg_delta_v(initial_state: Iterable[float]) -> float:
    """Return delta-v for impulsive, instantaneous velocity cancellation.

    This assumes no thrust limit and is for simulation only.
    """
    try:
        state = tuple(initial_state)
    except TypeError as exc:
        raise ValueError("initial_state must contain six finite numbers") from exc

    if len(state) != 6:
        raise ValueError("initial_state must contain six finite numbers")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in state
    ):
        raise ValueError("initial_state must contain six finite numbers")

    return math.hypot(*state[3:])
