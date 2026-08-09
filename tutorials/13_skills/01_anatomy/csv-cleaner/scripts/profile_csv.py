from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def detect_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample)
    except csv.Error:
        return csv.excel


def profile_csv(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Input file does not exist: {path}")
    if not path.is_file():
        raise SystemExit(f"Input path is not a file: {path}")

    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    dialect = detect_dialect(sample)

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, dialect=dialect)
        if not reader.fieldnames:
            raise SystemExit("CSV has no header row")

        headers = [header or "" for header in reader.fieldnames]
        missing_counts = Counter({header: 0 for header in headers})
        duplicate_rows = 0
        seen_rows: set[tuple[tuple[str, str], ...]] = set()
        row_count = 0

        for row in reader:
            row_count += 1
            normalized_row = tuple(sorted((key, value or "") for key, value in row.items()))
            if normalized_row in seen_rows:
                duplicate_rows += 1
            seen_rows.add(normalized_row)

            for header in headers:
                if not (row.get(header) or "").strip():
                    missing_counts[header] += 1

    print(f"file: {path}")
    print(f"delimiter: {repr(dialect.delimiter)}")
    print(f"rows: {row_count}")
    print(f"columns: {len(headers)}")
    print("headers:")
    for header in headers:
        print(f"  - {header}")

    print("missing values:")
    for header, count in missing_counts.items():
        if count:
            print(f"  - {header}: {count}")

    if not any(missing_counts.values()):
        print("  - none")

    print(f"duplicate rows: {duplicate_rows}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a CSV file for a csv-cleaner skill.")
    parser.add_argument("csv_file", type=Path, help="Path to the CSV file to inspect.")
    args = parser.parse_args()
    profile_csv(args.csv_file)


if __name__ == "__main__":
    main()
