import math
from collections.abc import Iterable, Mapping

from planning.greedy import leg_delta_v


def _vector3(value, field, target_index):
    try:
        vector = tuple(value)
    except TypeError as exc:
        raise ValueError(f"targets[{target_index}].{field} must be a 3-vector") from exc

    if len(vector) != 3:
        raise ValueError(f"targets[{target_index}].{field} must be a 3-vector")
    if any(
        isinstance(component, bool)
        or not isinstance(component, (int, float))
        or not math.isfinite(component)
        for component in vector
    ):
        raise ValueError(
            f"targets[{target_index}].{field} must contain finite numbers"
        )
    return vector


def _target_parts(targets):
    if isinstance(targets, (str, bytes, Mapping)):
        raise ValueError("targets must be an iterable of target objects")
    try:
        items = list(targets)
    except TypeError as exc:
        raise ValueError("targets must be an iterable of target objects") from exc

    parsed = []
    for index, target in enumerate(items):
        if not isinstance(target, Mapping):
            raise ValueError(f"targets[{index}] must be an object")
        if "object_id" not in target:
            raise ValueError(f"targets[{index}].object_id is required")
        object_id = target["object_id"]
        if not isinstance(object_id, str) or not object_id:
            raise ValueError(f"targets[{index}].object_id must be a non-empty string")
        if "r0" not in target:
            raise ValueError(f"targets[{index}].r0 is required")
        if "v0" not in target:
            raise ValueError(f"targets[{index}].v0 is required")
        r0 = _vector3(target["r0"], "r0", index)
        v0 = _vector3(target["v0"], "v0", index)
        parsed.append((object_id, r0, v0))
    return parsed


def plan_order(targets: Iterable[Mapping]) -> list[str]:
    """Sort by initial miss distance, a fixed heuristic, not an optimized plan.

    This ordering is for simulation only.
    """
    parsed = _target_parts(targets)
    return [
        object_id
        for object_id, _, _ in sorted(
            parsed,
            key=lambda item: (math.hypot(*item[1]), item[0]),
        )
    ]


def total_delta_v(targets: Iterable[Mapping]) -> float:
    """Sum instantaneous cancellations; this is not a fuel-optimal sequence.

    This total is for simulation only; no multi-leg propagation is performed.
    """
    parsed = _target_parts(targets)
    return sum(
        leg_delta_v((*r0, *v0))
        for _, r0, v0 in parsed
    )
