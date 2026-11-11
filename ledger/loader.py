import csv
import io
import zipfile


_COLUMN_MAP = (
    ("event_id", "event_id"),
    ("mission_id", "satellite_id"),
    ("time_to_tca", "time_to_tca"),
    ("miss_distance", "miss_distance_m"),
    ("relative_speed", "relative_speed_mps"),
    ("c_object_type", "chaser_object_type"),
)
_NUMERIC_FIELDS = ("time_to_tca", "miss_distance_m", "relative_speed_mps")


def load_archive(zip_path, member="train_data.csv"):
    """Load mapped raw rows and report fields that cannot be parsed numerically."""
    rows = []
    failures = []

    with zipfile.ZipFile(zip_path) as archive:
        try:
            member_stream = archive.open(member)
        except KeyError as error:
            raise FileNotFoundError(
                f"Archive member not found: {member}"
            ) from error

        with member_stream:
            with io.TextIOWrapper(
                member_stream, encoding="utf-8-sig", newline=""
            ) as text_stream:
                reader = csv.DictReader(text_stream)
                missing_headers = [
                    source
                    for source, _ in _COLUMN_MAP
                    if source not in (reader.fieldnames or ())
                ]
                if missing_headers:
                    raise ValueError(
                        "CSV is missing required headers: "
                        + ", ".join(missing_headers)
                    )

                for source_row in reader:
                    line_number = reader.line_num
                    row = {
                        target: source_row[source]
                        for source, target in _COLUMN_MAP
                    }
                    row["source"] = member
                    rows.append(row)

                    for field in _NUMERIC_FIELDS:
                        value = row[field]
                        try:
                            float(value)
                        except (TypeError, ValueError, OverflowError):
                            failures.append(
                                (
                                    line_number,
                                    field,
                                    "value is missing or non-numeric",
                                )
                            )

    return rows, failures
