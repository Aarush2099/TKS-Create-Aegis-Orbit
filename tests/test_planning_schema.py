import pytest

from planning.schema import validate_plan, validate_target, validate_vehicle


def _valid_target():
    return {
        "object_id": "debris-001",
        "object_id_source": "catalog",
        "mass_kg": 120.0,
        "mass_kg_source": "user assumption",
        "altitude_km": 800.0,
        "altitude_km_source": "catalog",
        "inclination_deg": 98.0,
        "inclination_deg_source": "catalog",
        "tumble_rate_deg_s": None,
        "tumble_rate_deg_s_source": "unknown",
    }


def _valid_vehicle():
    return {
        "vehicle_id": "servicer-001",
        "vehicle_id_source": "scenario",
        "dry_mass_kg": 500.0,
        "dry_mass_kg_source": "vehicle specification",
        "delta_v_budget_mps": 1200.0,
        "delta_v_budget_mps_source": "user assumption",
        "u_max_mps2": 0.001,
        "u_max_mps2_source": "user assumption",
    }


def _valid_plan():
    return {
        "sequence": ["debris-001"],
        "legs": [{"delta_v_mps": 100.0}],
        "feasible": True,
        "assumptions": [],
        "config_sha256": "a" * 64,
        "seed": 7,
    }


def test_validate_target_accepts_all_fields_and_sources():
    target = _valid_target()

    assert validate_target(target) == target


def test_validate_target_rejects_missing_mass_with_field_name():
    target = _valid_target()
    del target["mass_kg"]

    with pytest.raises(ValueError, match="mass_kg"):
        validate_target(target)


@pytest.mark.parametrize(
    "field",
    [
        "object_id",
        "mass_kg",
        "altitude_km",
        "inclination_deg",
        "tumble_rate_deg_s",
    ],
)
def test_validate_target_requires_source_for_each_value(field):
    target = _valid_target()
    del target[f"{field}_source"]

    with pytest.raises(ValueError, match=f"{field}_source"):
        validate_target(target)


def test_validate_target_accepts_unknown_tumble_rate():
    target = _valid_target()
    target["tumble_rate_deg_s"] = None

    assert validate_target(target) == target


def test_validate_target_rejects_string_tumble_rate():
    target = _valid_target()
    target["tumble_rate_deg_s"] = "unknown"

    with pytest.raises(ValueError, match="tumble_rate_deg_s"):
        validate_target(target)


def test_validate_target_rejects_negative_mass():
    target = _valid_target()
    target["mass_kg"] = -1.0

    with pytest.raises(ValueError, match="mass_kg"):
        validate_target(target)


@pytest.mark.parametrize("altitude_km", [199.9, 2000.1])
def test_validate_target_rejects_altitude_outside_source_labelled_adrv_range(
    altitude_km,
):
    target = _valid_target()
    target["altitude_km"] = altitude_km
    target["altitude_km_source"] = "ADRV range assumption: 200-2000 km"

    with pytest.raises(ValueError, match="altitude_km"):
        validate_target(target)


def test_validate_vehicle_accepts_valid_vehicle():
    vehicle = _valid_vehicle()

    assert validate_vehicle(vehicle) == vehicle


@pytest.mark.parametrize("u_max_mps2", [0.0, -0.001])
def test_validate_vehicle_rejects_nonpositive_acceleration_limit(u_max_mps2):
    vehicle = _valid_vehicle()
    vehicle["u_max_mps2"] = u_max_mps2

    with pytest.raises(ValueError, match="u_max_mps2"):
        validate_vehicle(vehicle)


@pytest.mark.parametrize("field", ["config_sha256", "seed"])
def test_validate_plan_rejects_missing_required_field(field):
    plan = _valid_plan()
    del plan[field]

    with pytest.raises(ValueError, match=field):
        validate_plan(plan)
