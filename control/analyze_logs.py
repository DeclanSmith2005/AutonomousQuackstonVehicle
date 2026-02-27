import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import List, Optional

LOG_PATTERN = "pid_log_*.csv"
TIME_FORMAT = "%Y%m%d_%H%M%S"

@dataclass
class LogEntry:
    index: int
    path: Path
    timestamp: Optional[datetime]


def parse_timestamp_from_name(path: Path) -> Optional[datetime]:
    stem = path.stem  # pid_log_YYYYMMDD_HHMMSS
    if not stem.startswith("pid_log_"):
        return None

    raw = stem.replace("pid_log_", "", 1)
    try:
        return datetime.strptime(raw, TIME_FORMAT)
    except ValueError:
        return None


def list_log_files(log_dir: Path) -> List[LogEntry]:
    files = list(log_dir.glob(LOG_PATTERN))

    def sort_key(p: Path):
        ts = parse_timestamp_from_name(p)
        if ts is not None:
            return (0, ts)
        return 1, datetime.fromtimestamp(p.stat().st_mtime)

    files.sort(key=sort_key, reverse=True)

    entries = []
    for idx, path in enumerate(files, start=1):
        entries.append(LogEntry(index=idx, path=path, timestamp=parse_timestamp_from_name(path)))
    return entries


def read_rows(path: Path):
    rows = []
    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append({
                "time_s": float(row["time_s"]),
                "error": float(row["error"]),
                "steering_angle": float(row["steering_angle"]),
                "speed": float(row["speed"]),
            })
    return rows


def summarize(path: Path):
    rows = read_rows(path)
    if not rows:
        print("No data rows found.")
        return

    errors = [r["error"] for r in rows]
    steering = [r["steering_angle"] for r in rows]
    speeds = [r["speed"] for r in rows]

    total = len(rows)
    span_s = rows[-1]["time_s"] - rows[0]["time_s"]

    sat_pos = sum(1 for x in steering if x >= 24.9)
    sat_neg = sum(1 for x in steering if x <= -24.9)
    zero_error = sum(1 for x in errors if abs(x) < 1e-9)
    large_error = sum(1 for x in errors if abs(x) >= 70)

    top_errors = Counter(errors).most_common(6)

    print(f"\nAnalyzing: {path.name}")
    print("-" * (12 + len(path.name)))
    print(f"Rows: {total}")
    print(f"Time span: {span_s:.2f}s")
    print(f"Mean |error|: {mean(abs(x) for x in errors):.2f}")
    print(f"Median |error|: {median(abs(x) for x in errors):.2f}")
    print(f"Zero-error samples: {100.0 * zero_error / total:.1f}%")
    print(f"Large-error samples (|error| >= 70): {100.0 * large_error / total:.1f}%")
    print(f"Steer saturation (+25): {100.0 * sat_pos / total:.1f}%")
    print(f"Steer saturation (-25): {100.0 * sat_neg / total:.1f}%")
    print(f"Speed min/max: {min(speeds):.1f} / {max(speeds):.1f}")
    print("Most common error values:")
    for value, count in top_errors:
        print(f"  {value:>8.3f} -> {count}")


def choose_entry(entries: List[LogEntry]) -> Optional[LogEntry]:
    print("\nAvailable log files (newest first):")
    for entry in entries:
        if entry.timestamp is not None:
            label = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            label = datetime.fromtimestamp(entry.path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{entry.index}. {entry.path.name}   [{label}]")

    while True:
        raw = input("\nPick a file number to analyze (q to quit): ").strip().lower()
        if raw in {"q", "quit", "exit"}:
            return None
        if not raw.isdigit():
            print("Enter a valid number, or 'q' to quit.")
            continue

        pick = int(raw)
        for entry in entries:
            if entry.index == pick:
                return entry

        print("Selection out of range. Try again.")


def main():
    parser = argparse.ArgumentParser(description="Analyze PID CSV logs from the logs folder.")
    parser.add_argument("--logs", default="logs", help="Path to logs folder (default: logs)")
    parser.add_argument("--index", type=int, help="Analyze this menu index directly (newest is 1)")
    parser.add_argument("--list", action="store_true", help="Only list files, do not analyze")
    args = parser.parse_args()

    log_dir = Path(args.logs).expanduser().resolve()
    if not log_dir.exists() or not log_dir.is_dir():
        print(f"Logs directory not found: {log_dir}")
        return

    entries = list_log_files(log_dir)
    if not entries:
        print(f"No log files matching '{LOG_PATTERN}' in {log_dir}")
        return

    if args.list:
        print("Available log files (newest first):")
        for entry in entries:
            if entry.timestamp is not None:
                label = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                label = datetime.fromtimestamp(entry.path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{entry.index}. {entry.path.name}   [{label}]")
        return

    selected = None
    if args.index is not None:
        selected = next((entry for entry in entries if entry.index == args.index), None)
        if selected is None:
            print(f"Index out of range: {args.index}")
            return
    else:
        selected = choose_entry(entries)

    if selected is None:
        print("No file selected.")
        return

    summarize(selected.path)


if __name__ == "__main__":
    main()
