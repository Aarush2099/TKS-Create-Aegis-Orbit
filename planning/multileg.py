import math
from numbers import Real
from collections.abc import Iterable

from aegis_orbit.envs.cw_relative_dynamics import propagate_relative


def _vector3(value: Iterable[Real], field: str) -> tuple[Real, Real, Real]:
    try:
        vector = tuple(value)
    except TypeError as exc:
        raise ValueError(f"{field} must be a 3-vector of finite numbers") from exc

    if len(vector) != 3:
        raise ValueError(f"{field} must be a 3-vector of finite numbers")
    if any(
        isinstance(component, bool)
        or not isinstance(component, Real)
        or not math.isfinite(component)
        for component in vector
    ):
        raise ValueError(f"{field} must be a 3-vector of finite numbers")
    return vector


def coast_then_cancel_delta_v(
    r0: Iterable[Real],
    v0: Iterable[Real],
    n: Real,
    T: Real,
) -> float:
    """Return one-leg delta-v for impulsive instantaneous cancellation at end of coast.

    Assumes no thrust limit, no fuel model, no drag or J2 perturbation, and
    covers a single leg for simulation only.
    """
    position = _vector3(r0, "r0")
    velocity = _vector3(v0, "v0")

    if isinstance(n, bool) or not isinstance(n, Real) or not math.isfinite(n) or n <= 0:
        raise ValueError("n must be a finite number greater than zero")
    if isinstance(T, bool) or not isinstance(T, Real) or not math.isfinite(T) or T < 0:
        raise ValueError("T must be a finite number greater than or equal to zero")

    initial_state = (*position, *velocity)
    propagated_state = propagate_relative(initial_state, float(n), float(T))
    return math.hypot(
        float(propagated_state[3]),
        float(propagated_state[4]),
        float(propagated_state[5]),
    )
