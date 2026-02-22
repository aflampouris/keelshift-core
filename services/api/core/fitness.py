import pandas as pd

REQUIRED_COLUMNS = ["user_id", "timestamp", "event_name"]

def evaluate_events_fitness(df: pd.DataFrame, *, min_users: int = 50, min_events: int = 500, min_span_days: int = 30) -> dict:
    checks = []
    metrics = {}

    # Required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        checks.append({"name": "required_columns", "status": "FAIL", "detail": f"Missing: {missing}"})
        return {"verdict": "UNFIT", "checks": checks, "metrics": metrics}

    # Timestamp parse
    ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    bad_ts = int(ts.isna().sum())
    metrics["bad_timestamp_rows"] = bad_ts
    if bad_ts > 0:
        checks.append({"name": "timestamp_parse", "status": "WARN", "detail": f"{bad_ts} rows have invalid timestamps"})
    else:
        checks.append({"name": "timestamp_parse", "status": "PASS", "detail": "All timestamps parsed"})

    # Basic metrics
    n_rows = int(len(df))
    n_users = int(df["user_id"].nunique(dropna=True))
    metrics.update({"n_rows": n_rows, "n_users": n_users})

    # Time span
    span_days = int((ts.max() - ts.min()).days) if ts.notna().any() else 0
    metrics["span_days"] = span_days

    # Threshold checks
    checks.append({
        "name": "min_users",
        "status": "PASS" if n_users >= min_users else ("WARN" if n_users >= max(10, min_users // 2) else "FAIL"),
        "detail": f"{n_users} unique users (min {min_users})",
    })

    checks.append({
        "name": "min_events",
        "status": "PASS" if n_rows >= min_events else ("WARN" if n_rows >= max(100, min_events // 2) else "FAIL"),
        "detail": f"{n_rows} events (min {min_events})",
    })

    checks.append({
        "name": "time_span",
        "status": "PASS" if span_days >= min_span_days else ("WARN" if span_days >= max(7, min_span_days // 2) else "FAIL"),
        "detail": f"{span_days} days covered (min {min_span_days})",
    })

    # Deterministic verdict
    n_fail = sum(1 for c in checks if c["status"] == "FAIL")
    n_warn = sum(1 for c in checks if c["status"] == "WARN")

    if n_fail > 0:
        verdict = "UNFIT"
    elif n_warn >= 2:
        verdict = "BORDERLINE"
    else:
        verdict = "FIT"

    return {"verdict": verdict, "checks": checks, "metrics": metrics}
