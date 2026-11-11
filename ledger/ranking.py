from ledger.input import dedupe_latest, window_filter


def _rankable_events(rows):
    in_window, _ = window_filter(rows)
    deduped, _ = dedupe_latest(in_window)
    return deduped


def rank_events(rows):
    """Return one ranked ledger entry per event in the screening window."""
    events = sorted(
        _rankable_events(rows),
        key=lambda row: (row["miss_distance_m"], row["event_id"]),
    )
    return [
        {
            "event_id": row["event_id"],
            "satellite_id": row["satellite_id"],
            "miss_distance_m": row["miss_distance_m"],
            "time_to_tca": row["time_to_tca"],
            "rank": rank,
        }
        for rank, row in enumerate(events, start=1)
    ]


def compare_to_baseline(rows):
    """Count position differences from stable plain miss-distance ordering."""
    events = _rankable_events(rows)
    ledger_order = [
        row["event_id"]
        for row in sorted(
            events, key=lambda row: (row["miss_distance_m"], row["event_id"])
        )
    ]
    baseline_order = [
        row["event_id"]
        for row in sorted(events, key=lambda row: row["miss_distance_m"])
    ]
    differing_event_ids = [
        ledger_id
        for ledger_id, baseline_id in zip(ledger_order, baseline_order)
        if ledger_id != baseline_id
    ]
    return len(differing_event_ids), differing_event_ids


def compare_by_signal(rows, signal="relative_speed_mps", top_n=20):
    """Compare miss-distance and alternate-signal orderings descriptively."""
    events = _rankable_events(rows)
    if not events:
        return {
            "positions_differing": 0,
            "top_n_overlap": 0,
            "top_n_size": 0,
        }
    if signal not in events[0]:
        raise ValueError(f"Unknown signal: {signal}")
    if isinstance(top_n, bool) or not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("top_n must be a positive integer")

    distance_order = sorted(
        events, key=lambda row: (row["miss_distance_m"], row["event_id"])
    )
    signal_order = sorted(events, key=lambda row: (row[signal], row["event_id"]))
    differing_positions = sum(
        distance_row["event_id"] != signal_row["event_id"]
        for distance_row, signal_row in zip(distance_order, signal_order)
    )
    top_n_size = min(top_n, len(events))
    distance_top_ids = {row["event_id"] for row in distance_order[:top_n_size]}
    signal_top_ids = {row["event_id"] for row in signal_order[:top_n_size]}

    return {
        "positions_differing": differing_positions,
        "top_n_overlap": len(distance_top_ids & signal_top_ids),
        "top_n_size": top_n_size,
    }
