import zipfile

import pytest

from ledger.loader import load_archive


CSV_HEADER = (
    "event_id,mission_id,time_to_tca,miss_distance,relative_speed,"
    "c_object_type\n"
)


def write_archive(path, csv_text, member="train_data.csv"):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, csv_text)
    return path


def test_load_archive_maps_headers_and_sets_source(tmp_path):
    archive_path = write_archive(
        tmp_path / "events.zip",
        CSV_HEADER + "event-1,sat-1,2.0,1200,7.5,DEBRIS\n",
    )

    rows, failures = load_archive(archive_path)

    assert rows == [
        {
            "event_id": "event-1",
            "satellite_id": "sat-1",
            "time_to_tca": "2.0",
            "miss_distance_m": "1200",
            "relative_speed_mps": "7.5",
            "chaser_object_type": "DEBRIS",
            "source": "train_data.csv",
        }
    ]
    assert failures == []


def test_load_archive_reports_unparseable_field_without_dropping_row(tmp_path):
    archive_path = write_archive(
        tmp_path / "events.zip",
        CSV_HEADER + "event-1,sat-1,not-a-number,1200,7.5,DEBRIS\n",
    )

    rows, failures = load_archive(archive_path)

    assert len(rows) == 1
    assert rows[0]["event_id"] == "event-1"
    assert rows[0]["time_to_tca"] == "not-a-number"
    assert len(failures) == 1
    line_number, field, reason = failures[0]
    assert line_number == 2
    assert field == "time_to_tca"
    assert reason


def test_load_archive_missing_member_names_requested_member(tmp_path):
    archive_path = write_archive(
        tmp_path / "events.zip",
        CSV_HEADER,
        member="other.csv",
    )

    with pytest.raises(FileNotFoundError, match="train_data.csv"):
        load_archive(archive_path)


def test_load_archive_parses_bom_prefixed_header(tmp_path):
    archive_path = write_archive(
        tmp_path / "events.zip",
        "\ufeff" + CSV_HEADER + "event-1,sat-1,2.0,1200,7.5,DEBRIS\n",
    )

    rows, failures = load_archive(archive_path)

    assert rows[0]["event_id"] == "event-1"
    assert failures == []


def test_load_archive_does_not_extract_files(tmp_path):
    archive_path = write_archive(
        tmp_path / "events.zip",
        CSV_HEADER + "event-1,sat-1,2.0,1200,7.5,DEBRIS\n",
    )

    load_archive(archive_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == ["events.zip"]
