import argparse
import csv
from pathlib import Path

from ledger.loader import load_archive
from ledger.ranking import rank_events


_FIELDNAMES = (
    "rank",
    "event_id",
    "satellite_id",
    "miss_distance_m",
    "time_to_tca",
)


def write_ranked_csv(ranked, path):
    """Write ranked ledger entries to a new CSV file, refusing to overwrite."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(ranked)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export the ranked ledger as CSV.")
    parser.add_argument(
        "--out",
        default="ledger_output/ranked_events.csv",
        help="new output CSV path (default: ledger_output/ranked_events.csv)",
    )
    arguments = parser.parse_args(argv)

    rows, failures = load_archive("data/external/esa_cdm/train_data.zip")
    if failures:
        details = "; ".join(
            f"line {line_number} {field}: {reason}"
            for line_number, field, reason in failures
        )
        raise ValueError(f"Archive contains unparseable fields: {details}")

    ranked = rank_events(rows)
    write_ranked_csv(ranked, arguments.out)


if __name__ == "__main__":
    main()
