import math

import pytest

from ledger.input import (
    WINDOW_DAYS,
    InvalidRow,
    dedupe_latest,
    validate_row,
    window_filter,
)


def valid_row(**overrides):
    row = {
        "event_id": "event-1",
        "satellite_id": "sat-1",
        "time_to_tca": "2",
        "miss_distance_m": "1200.5",
        "relative_speed_mps": "7.25",
        "source": "train_data.csv",
    }
    row.update(overrides)
    return row


def test_validate_row_returns_normalized_dict():
    assert validate_row(valid_row()) == {
        "event_id": "event-1",
        "satellite_id": "sat-1",
        "time_to_tca": 2.0,
        "miss_distance_m": 1200.5,
        "relative_speed_mps": 7.25,
        "source": "train_data.csv",
    }


@pytest.mark.parametrize(
    "field",
    [
        "event_id",
        "satellite_id",
        "time_to_tca",
        "miss_distance_m",
        "relative_speed_mps",
        "source",
    ],
)
def test_validate_row_rejects_missing_required_field(field):
    row = valid_row()
    del row[field]

    with pytest.raises(InvalidRow, match=field):
        validate_row(row)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("miss_distance_m", math.nan),
        ("miss_distance_m", math.inf),
        ("miss_distance_m", "not-a-number"),
        ("miss_distance_m", -1),
        ("relative_speed_mps", math.nan),
        ("relative_speed_mps", math.inf),
        ("relative_speed_mps", "not-a-number"),
        ("relative_speed_mps", -1),
    ],
)
def test_validate_row_rejects_invalid_nonnegative_measurements(field, value):
    with pytest.raises(InvalidRow, match=field):
        validate_row(valid_row(**{field: value}))


@pytest.mark.parametrize("value", [math.nan, math.inf, "not-a-number"])
def test_validate_row_rejects_invalid_time_to_tca(value):
    with pytest.raises(InvalidRow, match="time_to_tca"):
        validate_row(valid_row(time_to_tca=value))


@pytest.mark.parametrize("source", ["", " \t\n"])
def test_validate_row_rejects_empty_source(source):
    with pytest.raises(InvalidRow, match="source"):
        validate_row(valid_row(source=source))


def test_window_filter_keeps_inclusive_bounds_and_returns_excluded_count():
    rows = [
        valid_row(event_id="below", time_to_tca=0.5),
        valid_row(event_id="lower", time_to_tca=1.0),
        valid_row(event_id="middle", time_to_tca=2.0),
        valid_row(event_id="upper", time_to_tca=3.0),
        valid_row(event_id="above", time_to_tca=3.5),
    ]

    kept, excluded_count = window_filter(rows)

    assert [row["event_id"] for row in kept] == ["lower", "middle", "upper"]
    assert excluded_count == 2


def test_dedupe_latest_keeps_smallest_in_window_time_and_returns_collapsed_count():
    rows = [
        valid_row(event_id="event-1", time_to_tca=2.5),
        valid_row(event_id="event-2", time_to_tca=1.5),
        valid_row(event_id="event-1", time_to_tca=1.2),
        valid_row(event_id="event-1", time_to_tca=0.5),
    ]

    deduped, collapsed_count = dedupe_latest(rows)

    assert [(row["event_id"], row["time_to_tca"]) for row in deduped] == [
        ("event-1", 1.2),
        ("event-2", 1.5),
    ]
    assert collapsed_count == 1
    assert WINDOW_DAYS == (1.0, 3.0)
