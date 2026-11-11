import csv

import pytest

from ledger.export import write_ranked_csv


def ranked_entries():
    return [
        {
            "rank": 1,
            "event_id": "event-2",
            "satellite_id": "sat-2",
            "miss_distance_m": 100.5,
            "time_to_tca": 2.0,
        },
        {
            "rank": 2,
            "event_id": "event-1",
            "satellite_id": "sat-1",
            "miss_distance_m": 200.0,
            "time_to_tca": 1.5,
        },
    ]


def test_write_ranked_csv_writes_expected_header_rows_and_order(tmp_path):
    output_path = tmp_path / "ranked.csv"

    write_ranked_csv(ranked_entries(), output_path)

    with output_path.open(newline="", encoding="utf-8") as output_file:
        rows = list(csv.reader(output_file))
    assert rows == [
        ["rank", "event_id", "satellite_id", "miss_distance_m", "time_to_tca"],
        ["1", "event-2", "sat-2", "100.5", "2.0"],
        ["2", "event-1", "sat-1", "200.0", "1.5"],
    ]


def test_write_ranked_csv_refuses_to_overwrite_and_names_path(tmp_path):
    output_path = tmp_path / "ranked.csv"
    output_path.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError) as error:
        write_ranked_csv(ranked_entries(), output_path)

    assert error.value.filename == str(output_path)
    assert output_path.read_text(encoding="utf-8") == "existing"


def test_write_ranked_csv_creates_no_other_files(tmp_path):
    output_path = tmp_path / "ranked.csv"

    write_ranked_csv(ranked_entries(), output_path)

    assert [path.name for path in tmp_path.iterdir()] == ["ranked.csv"]
