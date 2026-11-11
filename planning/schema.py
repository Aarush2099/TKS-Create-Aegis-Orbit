import math
import re
from collections.abc import Mapping


_TARGET_FIELDS = ("object_id", "mass_kg", "altitude_km", "inclination_deg")
_VEHICLE_FIELDS = (
    "vehicle_id",
    "dry_mass_kg",
    "delta_v_budget_mps",
    "u_max_mps2",
)


def _require_object(value, name):
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")


def _require_source(value, field):
    source_field = f"{field}_source"
    if source_field not in value:
        raise ValueError(f"{source_field} is required")
    source = value[source_field]
    if not isinstance(source, str) or not source.strip():
        raise ValueError(f"{source_field} must be a non-empty string")


def _require_string(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _require_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    if not math.isfinite(value):
        raise ValueError(f"{field} must be finite")


def validate_target(target):
    """Validate a target input and return a normalized copy."""
    _require_object(target, "target")
    normalized = dict(target)
    for field in _TARGET_FIELDS:
        if field not in normalized:
            raise ValueError(f"{field} is required")

    normalized.setdefault("tumble_rate_deg_s", None)
    for field in (*_TARGET_FIELDS, "tumble_rate_deg_s"):
        _require_source(normalized, field)

    _require_string(normalized["object_id"], "object_id")
    for field in ("mass_kg", "altitude_km", "inclination_deg"):
        _require_number(normalized[field], field)

    if normalized["mass_kg"] <= 0:
        raise ValueError("mass_kg must be greater than zero")
    if not 200 <= normalized["altitude_km"] <= 2000:
        raise ValueError("altitude_km must be between 200 and 2000 km")

    tumble_rate = normalized["tumble_rate_deg_s"]
    if tumble_rate is not None:
        _require_number(tumble_rate, "tumble_rate_deg_s")

    return normalized


def validate_vehicle(vehicle):
    """Validate a vehicle input and return it."""
    _require_object(vehicle, "vehicle")
    for field in _VEHICLE_FIELDS:
        if field not in vehicle:
            raise ValueError(f"{field} is required")
        _require_source(vehicle, field)

    _require_string(vehicle["vehicle_id"], "vehicle_id")
    for field in ("dry_mass_kg", "delta_v_budget_mps", "u_max_mps2"):
        _require_number(vehicle[field], field)

    if vehicle["dry_mass_kg"] <= 0:
        raise ValueError("dry_mass_kg must be greater than zero")
    if vehicle["delta_v_budget_mps"] < 0:
        raise ValueError("delta_v_budget_mps must be non-negative")
    if vehicle["u_max_mps2"] <= 0:
        raise ValueError("u_max_mps2 must be greater than zero")

    return vehicle


def validate_plan(plan):
    """Validate a plan.json object and return it."""
    _require_object(plan, "plan")
    required_fields = (
        "sequence",
        "legs",
        "feasible",
        "assumptions",
        "config_sha256",
        "seed",
    )
    for field in required_fields:
        if field not in plan:
            raise ValueError(f"{field} is required")

    sequence = plan["sequence"]
    if not isinstance(sequence, list) or any(
        not isinstance(item, str) or not item.strip() for item in sequence
    ):
        raise ValueError("sequence must be a list of non-empty strings")

    legs = plan["legs"]
    if not isinstance(legs, list):
        raise ValueError("legs must be a list")
    for index, leg in enumerate(legs):
        field = f"legs[{index}].delta_v_mps"
        _require_object(leg, f"legs[{index}]")
        if "delta_v_mps" not in leg:
            raise ValueError(f"{field} is required")
        _require_number(leg["delta_v_mps"], field)
        if leg["delta_v_mps"] < 0:
            raise ValueError(f"{field} must be non-negative")

    if not isinstance(plan["feasible"], bool):
        raise ValueError("feasible must be a boolean")
    assumptions = plan["assumptions"]
    if not isinstance(assumptions, list) or any(
        not isinstance(item, str) for item in assumptions
    ):
        raise ValueError("assumptions must be a list of strings")

    config_sha256 = plan["config_sha256"]
    if not isinstance(config_sha256, str) or re.fullmatch(
        r"[0-9a-fA-F]{64}", config_sha256
    ) is None:
        raise ValueError("config_sha256 must be a 64-character hexadecimal SHA-256")

    seed = plan["seed"]
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    return plan
