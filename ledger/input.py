import math
from collections.abc import Mapping


WINDOW_DAYS = (1.0, 3.0)
_REQUIRED_FIELDS = (
    "event_id",
    "satellite_id",
    "time_to_tca",
    "miss_distance_m",
    "relative_speed_mps",
    "source",
)


class InvalidRow(ValueError):
    """Raised when a ledger input row is missing or has invalid data."""


def _normalized_identifier(row, field):
    value = row[field]
    if not isinstance(value, str) or not value.strip():
        raise InvalidRow(f"{field} must be a non-empty string")
    return value.strip()


def _normalized_number(row, field, *, nonnegative=False):
    try:
        value = float(row[field])
    except (TypeError, ValueError, OverflowError) as error:
        raise InvalidRow(f"{field} must be numeric") from error
    if not math.isfinite(value):
        raise InvalidRow(f"{field} must be finite")
    if nonnegative and value < 0:
        raise InvalidRow(f"{field} must be non-negative")
    return value


def validate_row(row):
    if not isinstance(row, Mapping):
        raise InvalidRow("row must be a mapping")
    for field in _REQUIRED_FIELDS:
        if field not in row:
            raise InvalidRow(f"missing required field: {field}")

    source = row["source"]
    if not isinstance(source, str) or not source.strip():
        raise InvalidRow("source must be a non-empty string")

    return {
        "event_id": _normalized_identifier(row, "event_id"),
        "satellite_id": _normalized_identifier(row, "satellite_id"),
        "time_to_tca": _normalized_number(row, "time_to_tca"),
        "miss_distance_m": _normalized_number(
            row, "miss_distance_m", nonnegative=True
        ),
        "relative_speed_mps": _normalized_number(
            row, "relative_speed_mps", nonnegative=True
        ),
        "source": source.strip(),
    }


def window_filter(rows):
    lower, upper = WINDOW_DAYS
    included = []
    excluded_count = 0
    for row in rows:
        normalized = validate_row(row)
        if lower <= normalized["time_to_tca"] <= upper:
            included.append(normalized)
        else:
            excluded_count += 1
    return included, excluded_count


def dedupe_latest(rows):
    in_window, _ = window_filter(rows)
    latest_by_event = {}
    collapsed_count = 0
    for row in in_window:
        event_id = row["event_id"]
        previous = latest_by_event.get(event_id)
        if previous is None:
            latest_by_event[event_id] = row
        else:
            collapsed_count += 1
            if row["time_to_tca"] < previous["time_to_tca"]:
                latest_by_event[event_id] = row
    return list(latest_by_event.values()), collapsed_count
