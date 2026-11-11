import pytest

from ledger.ranking import compare_by_signal, compare_to_baseline, rank_events


def event(event_id, time_to_tca, miss_distance_m, satellite_id=None):
    return {
        "event_id": event_id,
        "satellite_id": satellite_id or f"sat-{event_id}",
        "time_to_tca": time_to_tca,
        "miss_distance_m": miss_distance_m,
        "relative_speed_mps": 7.5,
        "source": "synthetic.csv",
    }


def test_rank_events_sorts_by_distance_then_event_id_and_shapes_output():
    rows = [
        event("event-c", 2.0, 100.0),
        event("event-b", 2.0, 100.0),
        event("event-a", 2.0, 50.0),
    ]

    ranked = rank_events(rows)

    assert [row["event_id"] for row in ranked] == [
        "event-a",
        "event-b",
        "event-c",
    ]
    assert ranked == [
        {
            "event_id": "event-a",
            "satellite_id": "sat-event-a",
            "miss_distance_m": 50.0,
            "time_to_tca": 2.0,
            "rank": 1,
        },
        {
            "event_id": "event-b",
            "satellite_id": "sat-event-b",
            "miss_distance_m": 100.0,
            "time_to_tca": 2.0,
            "rank": 2,
        },
        {
            "event_id": "event-c",
            "satellite_id": "sat-event-c",
            "miss_distance_m": 100.0,
            "time_to_tca": 2.0,
            "rank": 3,
        },
    ]


def test_rank_events_filters_window_and_deduplicates_before_ranking():
    rows = [
        event("event-a", 2.5, 400.0),
        event("event-a", 1.5, 300.0),
        event("event-b", 0.5, 1.0),
        event("event-c", 3.0, 200.0),
    ]

    ranked = rank_events(rows)

    assert [(row["event_id"], row["time_to_tca"]) for row in ranked] == [
        ("event-c", 3.0),
        ("event-a", 1.5),
    ]
    assert len({row["event_id"] for row in ranked}) == len(ranked)


def test_compare_to_baseline_returns_no_differences_when_orders_agree():
    rows = [
        event("event-a", 1.0, 10.0),
        event("event-b", 2.0, 20.0),
        event("event-c", 3.0, 30.0),
    ]

    difference_count, differing_event_ids = compare_to_baseline(rows)

    assert difference_count == 0
    assert differing_event_ids == []


def test_compare_to_baseline_reports_differing_positions_and_event_ids():
    rows = [
        event("event-b", 2.0, 10.0),
        event("event-a", 2.0, 10.0),
        event("event-c", 2.0, 30.0),
    ]

    difference_count, differing_event_ids = compare_to_baseline(rows)

    assert difference_count == 2
    assert differing_event_ids == ["event-a", "event-b"]


def test_baseline_differences_are_tie_only():
    rows = [
        event("event-c", 2.0, 20.0),
        event("event-a", 2.0, 10.0),
        event("event-b", 2.0, 10.0),
        event("event-d", 2.0, 30.0),
    ]
    ledger_order = rank_events(rows)
    baseline_order = sorted(rows, key=lambda row: row["miss_distance_m"])

    differing_positions = [
        (ledger_row, baseline_row)
        for ledger_row, baseline_row in zip(ledger_order, baseline_order)
        if ledger_row["event_id"] != baseline_row["event_id"]
    ]
    difference_count, _ = compare_to_baseline(rows)

    assert all(
        ledger_row["miss_distance_m"] == baseline_row["miss_distance_m"]
        for ledger_row, baseline_row in differing_positions
    )
    assert difference_count == len(differing_positions)


def test_compare_by_signal_returns_zero_differences_for_identical_orders():
    rows = [
        {**event("event-a", 1.0, 10.0), "relative_speed_mps": 1.0},
        {**event("event-b", 2.0, 20.0), "relative_speed_mps": 2.0},
        {**event("event-c", 3.0, 30.0), "relative_speed_mps": 3.0},
    ]

    result = compare_by_signal(rows, signal="relative_speed_mps", top_n=3)

    assert result == {
        "positions_differing": 0,
        "top_n_overlap": 3,
        "top_n_size": 3,
    }


def test_compare_by_signal_counts_differences_and_top_n_overlap():
    rows = [
        {**event("event-a", 2.0, 10.0), "relative_speed_mps": 3.0},
        {**event("event-b", 2.0, 20.0), "relative_speed_mps": 1.0},
        {**event("event-c", 2.0, 30.0), "relative_speed_mps": 2.0},
        {**event("event-d", 2.0, 40.0), "relative_speed_mps": 4.0},
    ]
    distance_order = sorted(rows, key=lambda row: row["miss_distance_m"])
    signal_order = sorted(
        rows, key=lambda row: (row["relative_speed_mps"], row["event_id"])
    )
    expected_differences = sum(
        left["event_id"] != right["event_id"]
        for left, right in zip(distance_order, signal_order)
    )
    expected_overlap = len(
        {row["event_id"] for row in distance_order[:2]}
        & {row["event_id"] for row in signal_order[:2]}
    )

    result = compare_by_signal(rows, signal="relative_speed_mps", top_n=2)

    assert result == {
        "positions_differing": expected_differences,
        "top_n_overlap": expected_overlap,
        "top_n_size": 2,
    }


def test_compare_by_signal_filters_window_and_deduplicates_first():
    rows = [
        {**event("event-a", 2.5, 40.0), "relative_speed_mps": 4.0},
        {**event("event-a", 1.5, 10.0), "relative_speed_mps": 1.0},
        {**event("event-b", 0.5, 1.0), "relative_speed_mps": 0.0},
        {**event("event-c", 3.0, 20.0), "relative_speed_mps": 2.0},
    ]

    result = compare_by_signal(rows, signal="relative_speed_mps", top_n=2)

    assert result == {
        "positions_differing": 0,
        "top_n_overlap": 2,
        "top_n_size": 2,
    }


def test_compare_by_signal_rejects_unknown_signal():
    rows = [event("event-a", 2.0, 10.0)]

    with pytest.raises(ValueError, match="unknown_signal"):
        compare_by_signal(rows, signal="unknown_signal")
