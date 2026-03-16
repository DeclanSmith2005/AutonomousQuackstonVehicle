import argparse
import csv
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev
from typing import List, Optional, Dict, Any

LOG_PATTERNS = ["pid_log_*.csv", "run_log_*.csv"]
TIME_FORMAT = "%Y%m%d_%H%M%S"
LOG_PREFIXES = ["pid_log_", "run_log_"]

# Thresholds for anomaly detection
ANOMALY_THRESHOLDS = {
    "mean_abs_error_high": 50.0,       # Mean |error| above this is suspicious
    "large_error_pct_high": 30.0,      # >30% large errors is suspicious
    "saturation_pct_high": 40.0,       # >40% saturation is suspicious
    "zero_error_pct_high": 80.0,       # >80% zero error might mean sensor issue
    "duration_short": 2.0,             # <2 seconds is very short run
    "row_count_low": 10,               # <10 rows is too few data points
}


@dataclass
class LogEntry:
    index: int
    path: Path
    timestamp: Optional[datetime]


@dataclass
class StateStats:
    """Statistics for a specific state/mode."""
    count: int = 0
    mean_abs_error: float = 0.0
    large_error_pct: float = 0.0
    saturation_pct: float = 0.0


@dataclass
class LogStats:
    """Statistics computed from a single log file."""
    path: Path
    rows: int = 0
    duration_s: float = 0.0
    mean_abs_error: float = 0.0
    median_abs_error: float = 0.0
    zero_error_pct: float = 0.0
    large_error_pct: float = 0.0
    sat_pos_pct: float = 0.0
    sat_neg_pct: float = 0.0
    speed_min: float = 0.0
    speed_max: float = 0.0
    top_errors: List[tuple] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    state_stats: Dict[str, StateStats] = field(default_factory=dict)


def parse_timestamp_from_name(path: Path) -> Optional[datetime]:
    stem = path.stem  # pid_log_YYYYMMDD_HHMMSS or run_log_YYYYMMDD_HHMMSS
    for prefix in LOG_PREFIXES:
        if stem.startswith(prefix):
            raw = stem.replace(prefix, "", 1)
            try:
                return datetime.strptime(raw, TIME_FORMAT)
            except ValueError:
                pass
    return None


def list_log_files(log_dir: Path) -> List[LogEntry]:
    files = []
    for pattern in LOG_PATTERNS:
        files.extend(log_dir.glob(pattern))

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
            # Support both column name formats: 'steering_angle' (pid_log) and 'steer' (run_log)
            steer_value = row.get("steering_angle") or row.get("steer")
            rows.append({
                "time_s": float(row["time_s"]),
                "error": float(row["error"]),
                "steering_angle": float(steer_value),
                "speed": float(row["speed"]),
                "state": row.get("state", "unknown"),  # Capture state/mode if present
            })
    return rows


def compute_stats(path: Path) -> Optional[LogStats]:
    """Compute statistics for a single log file and detect anomalies."""
    try:
        rows = read_rows(path)
    except Exception as e:
        stats = LogStats(path=path)
        stats.anomalies.append(f"Failed to read: {e}")
        return stats

    if not rows:
        stats = LogStats(path=path)
        stats.anomalies.append("Empty file (no data rows)")
        return stats

    errors = [r["error"] for r in rows]
    steering = [r["steering_angle"] for r in rows]
    speeds = [r["speed"] for r in rows]

    total = len(rows)
    span_s = rows[-1]["time_s"] - rows[0]["time_s"]

    sat_pos = sum(1 for x in steering if x >= 24.9)
    sat_neg = sum(1 for x in steering if x <= -24.9)
    zero_error = sum(1 for x in errors if abs(x) < 1e-9)
    large_error = sum(1 for x in errors if abs(x) >= 70)

    # Compute per-state statistics
    state_data: Dict[str, List[dict]] = {}
    for r in rows:
        state = r["state"]
        if state not in state_data:
            state_data[state] = []
        state_data[state].append(r)

    state_stats_dict: Dict[str, StateStats] = {}
    for state, state_rows in state_data.items():
        state_errors = [r["error"] for r in state_rows]
        state_steering = [r["steering_angle"] for r in state_rows]
        state_count = len(state_rows)
        state_large_error = sum(1 for x in state_errors if abs(x) >= 70)
        state_sat = sum(1 for x in state_steering if abs(x) >= 24.9)
        state_stats_dict[state] = StateStats(
            count=state_count,
            mean_abs_error=mean(abs(x) for x in state_errors),
            large_error_pct=100.0 * state_large_error / state_count,
            saturation_pct=100.0 * state_sat / state_count,
        )

    stats = LogStats(
        path=path,
        rows=total,
        duration_s=span_s,
        mean_abs_error=mean(abs(x) for x in errors),
        median_abs_error=median(abs(x) for x in errors),
        zero_error_pct=100.0 * zero_error / total,
        large_error_pct=100.0 * large_error / total,
        sat_pos_pct=100.0 * sat_pos / total,
        sat_neg_pct=100.0 * sat_neg / total,
        speed_min=min(speeds),
        speed_max=max(speeds),
        top_errors=Counter(errors).most_common(6),
        state_stats=state_stats_dict,
    )

    # Detect anomalies
    if stats.rows < ANOMALY_THRESHOLDS["row_count_low"]:
        stats.anomalies.append(f"Very few data points ({stats.rows} rows)")
    if stats.duration_s < ANOMALY_THRESHOLDS["duration_short"]:
        stats.anomalies.append(f"Very short run ({stats.duration_s:.1f}s)")
    if stats.mean_abs_error > ANOMALY_THRESHOLDS["mean_abs_error_high"]:
        stats.anomalies.append(f"High mean error ({stats.mean_abs_error:.1f})")
    if stats.large_error_pct > ANOMALY_THRESHOLDS["large_error_pct_high"]:
        stats.anomalies.append(f"Many large errors ({stats.large_error_pct:.1f}%)")
    if stats.sat_pos_pct + stats.sat_neg_pct > ANOMALY_THRESHOLDS["saturation_pct_high"]:
        stats.anomalies.append(f"High steering saturation ({stats.sat_pos_pct + stats.sat_neg_pct:.1f}%)")
    if stats.zero_error_pct > ANOMALY_THRESHOLDS["zero_error_pct_high"]:
        stats.anomalies.append(f"Suspiciously high zero-error ({stats.zero_error_pct:.1f}%) - sensor issue?")

    return stats


def print_single_stats(stats: LogStats, verbose: bool = True):
    """Print statistics for a single log file."""
    print(f"\nAnalyzing: {stats.path.name}")
    print("-" * (12 + len(stats.path.name)))

    if stats.anomalies and stats.rows == 0:
        for anomaly in stats.anomalies:
            print(f"  [ANOMALY] {anomaly}")
        return

    print(f"Rows: {stats.rows}")
    print(f"Time span: {stats.duration_s:.2f}s")
    print(f"Mean |error|: {stats.mean_abs_error:.2f}")
    print(f"Median |error|: {stats.median_abs_error:.2f}")
    print(f"Zero-error samples: {stats.zero_error_pct:.1f}%")
    print(f"Large-error samples (|error| >= 70): {stats.large_error_pct:.1f}%")
    print(f"Steer saturation (+25): {stats.sat_pos_pct:.1f}%")
    print(f"Steer saturation (-25): {stats.sat_neg_pct:.1f}%")
    print(f"Speed min/max: {stats.speed_min:.1f} / {stats.speed_max:.1f}")

    if verbose:
        print("Most common error values:")
        for value, count in stats.top_errors:
            print(f"  {value:>8.3f} -> {count}")

    # Show per-state breakdown if available
    if stats.state_stats and len(stats.state_stats) > 1:
        print("\nError by State/Mode:")
        # Sort by mean error (worst first)
        sorted_states = sorted(stats.state_stats.items(), 
                               key=lambda x: x[1].mean_abs_error, reverse=True)
        for state, ss in sorted_states:
            pct_of_total = 100.0 * ss.count / stats.rows
            print(f"  {state:>8}: mean |err|={ss.mean_abs_error:6.2f}, "
                  f"large_err={ss.large_error_pct:5.1f}%, "
                  f"saturation={ss.saturation_pct:5.1f}%, "
                  f"samples={ss.count} ({pct_of_total:.1f}%)")

    if stats.anomalies:
        print("\n[!] ANOMALIES DETECTED:")
        for anomaly in stats.anomalies:
            print(f"    - {anomaly}")


def analyze_multiple(entries: List[LogEntry], verbose: bool = False):
    """Analyze multiple log files and provide aggregate statistics."""
    all_stats: List[LogStats] = []
    weird_files: List[LogStats] = []

    print(f"\n{'='*60}")
    print(f"ANALYZING {len(entries)} LOG FILES")
    print(f"{'='*60}")

    for entry in entries:
        stats = compute_stats(entry.path)
        if stats:
            all_stats.append(stats)
            if stats.anomalies:
                weird_files.append(stats)

    # Filter out files with no data for aggregate calculations
    valid_stats = [s for s in all_stats if s.rows > 0]

    if not valid_stats:
        print("\nNo valid data found in any of the selected files.")
        return

    # Aggregate statistics
    total_rows = sum(s.rows for s in valid_stats)
    total_duration = sum(s.duration_s for s in valid_stats)
    avg_mean_error = mean(s.mean_abs_error for s in valid_stats)
    avg_median_error = mean(s.median_abs_error for s in valid_stats)
    avg_zero_error_pct = mean(s.zero_error_pct for s in valid_stats)
    avg_large_error_pct = mean(s.large_error_pct for s in valid_stats)
    avg_sat_total = mean(s.sat_pos_pct + s.sat_neg_pct for s in valid_stats)

    print(f"\n--- AGGREGATE SUMMARY ({len(valid_stats)} valid files) ---")
    print(f"Total data points: {total_rows}")
    print(f"Total run time: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"Avg mean |error|: {avg_mean_error:.2f}")
    print(f"Avg median |error|: {avg_median_error:.2f}")
    print(f"Avg zero-error %: {avg_zero_error_pct:.1f}%")
    print(f"Avg large-error %: {avg_large_error_pct:.1f}%")
    print(f"Avg total saturation %: {avg_sat_total:.1f}%")

    # Aggregate state/mode statistics across all files
    aggregate_state_data: Dict[str, Dict[str, List[float]]] = {}
    for s in valid_stats:
        for state, ss in s.state_stats.items():
            if state not in aggregate_state_data:
                aggregate_state_data[state] = {"errors": [], "large_err": [], "sat": [], "counts": []}
            aggregate_state_data[state]["errors"].append(ss.mean_abs_error)
            aggregate_state_data[state]["large_err"].append(ss.large_error_pct)
            aggregate_state_data[state]["sat"].append(ss.saturation_pct)
            aggregate_state_data[state]["counts"].append(ss.count)

    if aggregate_state_data and len(aggregate_state_data) > 1:
        print(f"\n--- ERROR BY STATE/MODE (aggregated) ---")
        # Sort by average mean error across files (worst first)
        sorted_states = sorted(
            aggregate_state_data.items(),
            key=lambda x: mean(x[1]["errors"]) if x[1]["errors"] else 0,
            reverse=True
        )
        for state, data in sorted_states:
            total_samples = sum(data["counts"])
            avg_err = mean(data["errors"]) if data["errors"] else 0
            avg_large = mean(data["large_err"]) if data["large_err"] else 0
            avg_sat = mean(data["sat"]) if data["sat"] else 0
            files_with_state = len(data["errors"])
            print(f"  {state:>8}: avg mean |err|={avg_err:6.2f}, "
                  f"avg large_err={avg_large:5.1f}%, "
                  f"avg sat={avg_sat:5.1f}%, "
                  f"total samples={total_samples}, "
                  f"in {files_with_state} files")

    # Show distribution of mean errors
    if len(valid_stats) > 1:
        mean_errors = [s.mean_abs_error for s in valid_stats]
        print(f"\nMean error distribution across files:")
        print(f"  Min: {min(mean_errors):.2f}")
        print(f"  Max: {max(mean_errors):.2f}")
        if len(mean_errors) > 2:
            print(f"  Std Dev: {stdev(mean_errors):.2f}")

    # Best and worst performers
    sorted_by_error = sorted(valid_stats, key=lambda s: s.mean_abs_error)
    print(f"\n--- BEST PERFORMERS (lowest mean error) ---")
    for s in sorted_by_error[:3]:
        print(f"  {s.path.name}: mean |error| = {s.mean_abs_error:.2f}")

    print(f"\n--- WORST PERFORMERS (highest mean error) ---")
    for s in sorted_by_error[-3:][::-1]:
        print(f"  {s.path.name}: mean |error| = {s.mean_abs_error:.2f}")

    # Weird files section
    if weird_files:
        print(f"\n{'='*60}")
        print(f"[!] WEIRD/ANOMALOUS FILES ({len(weird_files)} found)")
        print(f"{'='*60}")
        for stats in weird_files:
            print(f"\n  {stats.path.name}:")
            for anomaly in stats.anomalies:
                print(f"    - {anomaly}")
    else:
        print(f"\n[OK] No anomalous files detected.")

    # Individual file details if verbose
    if verbose:
        print(f"\n{'='*60}")
        print("INDIVIDUAL FILE DETAILS")
        print(f"{'='*60}")
        for stats in all_stats:
            print_single_stats(stats, verbose=False)


def parse_range(range_str: str, max_index: int) -> Optional[List[int]]:
    """
    Parse a range string into a list of indices.
    Supports: 'all', single number '3', range '1-5', comma-separated '1,3,5', or mixed '1-3,7,9-10'
    """
    range_str = range_str.strip().lower()

    if range_str in {"all", "*"}:
        return list(range(1, max_index + 1))

    indices = set()
    parts = range_str.replace(" ", "").split(",")

    for part in parts:
        if not part:
            continue
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                start_idx = int(start)
                end_idx = int(end)
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                for i in range(start_idx, end_idx + 1):
                    if 1 <= i <= max_index:
                        indices.add(i)
            except ValueError:
                return None
        else:
            try:
                idx = int(part)
                if 1 <= idx <= max_index:
                    indices.add(idx)
            except ValueError:
                return None

    return sorted(indices) if indices else None


def choose_entries(entries: List[LogEntry], display_limit: int = 10) -> Optional[List[LogEntry]]:
    """Interactive selection supporting single file or range."""
    display_entries = entries[:display_limit]
    hidden_count = len(entries) - len(display_entries)

    print(f"\nAvailable log files (newest {len(display_entries)} shown):")
    for entry in display_entries:
        if entry.timestamp is not None:
            label = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            label = datetime.fromtimestamp(entry.path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{entry.index}. {entry.path.name}   [{label}]")

    if hidden_count > 0:
        print(f"  ... and {hidden_count} older files (use --list to see all)")

    print("\nSelection options:")
    print("  - Single file: enter a number (e.g., '3')")
    print("  - Range: '1-5' or '1,3,5' or '1-3,7'")
    print("  - All files: 'all'")

    while True:
        raw = input("\nEnter selection (q to quit): ").strip().lower()
        if raw in {"q", "quit", "exit"}:
            return None

        indices = parse_range(raw, len(entries))
        if indices is None:
            print("Invalid selection. Try again.")
            continue

        selected = [e for e in entries if e.index in indices]
        if not selected:
            print("No files matched. Try again.")
            continue

        return selected


def main():
    parser = argparse.ArgumentParser(
        description="Analyze PID CSV logs from the logs folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_logs.py                    # Interactive selection
  python analyze_logs.py --index 1          # Analyze newest file
  python analyze_logs.py --range 1-5        # Analyze files 1 through 5
  python analyze_logs.py --range 1,3,5      # Analyze specific files
  python analyze_logs.py --range all        # Analyze all files
  python analyze_logs.py --range all -v     # Analyze all with individual details
  python analyze_logs.py --list             # List available files
        """
    )
    parser.add_argument("--logs", default="logs", help="Path to logs folder (default: logs)")
    parser.add_argument("--index", type=int, help="Analyze single file by index (newest is 1)")
    parser.add_argument("--range", dest="file_range", type=str,
                        help="Analyze range of files: '1-5', '1,3,5', 'all'")
    parser.add_argument("--list", action="store_true", help="Only list files, do not analyze")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show individual file details in range analysis")
    args = parser.parse_args()

    log_dir = Path(args.logs).expanduser().resolve()
    if not log_dir.exists() or not log_dir.is_dir():
        print(f"Logs directory not found: {log_dir}")
        return

    entries = list_log_files(log_dir)
    if not entries:
        print(f"No log files matching {LOG_PATTERNS} in {log_dir}")
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

    selected_entries = None

    # Handle --index for single file (backward compatibility)
    if args.index is not None:
        entry = next((e for e in entries if e.index == args.index), None)
        if entry is None:
            print(f"Index out of range: {args.index}")
            return
        selected_entries = [entry]

    # Handle --range for multiple files
    elif args.file_range is not None:
        indices = parse_range(args.file_range, len(entries))
        if indices is None:
            print(f"Invalid range format: {args.file_range}")
            print("Use: '1-5', '1,3,5', '1-3,7', or 'all'")
            return
        selected_entries = [e for e in entries if e.index in indices]
        if not selected_entries:
            print("No files matched the specified range.")
            return

    # Interactive selection
    else:
        selected_entries = choose_entries(entries)

    if not selected_entries:
        print("No files selected.")
        return

    # Single file: detailed analysis
    if len(selected_entries) == 1:
        stats = compute_stats(selected_entries[0].path)
        if stats:
            print_single_stats(stats, verbose=True)
    # Multiple files: aggregate analysis
    else:
        analyze_multiple(selected_entries, verbose=args.verbose)


if __name__ == "__main__":
    main()
