#!/usr/bin/env python3
"""Build engineered affordability features and a scaled feature set.

We take raw inputs (income, rent, vacancy) and compute simple ratios,
then scale them so different metros are comparable on the same scale.
Default scaling is robust (median/IQR). Use --scaler standard for mean/std.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def parse_float(value: str) -> Optional[float]:
    """Parse a numeric string and return None for blanks or NA tokens."""
    if value is None:
        return None
    value = value.strip()
    if value == "" or value.lower() in {"na", "nan", "null"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def quantile(sorted_values: List[float], q: float) -> Optional[float]:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return sorted_values[lower]
    weight = pos - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def robust_stats(values: Iterable[Optional[float]]) -> Dict[str, Optional[float]]:
    cleaned = sorted(v for v in values if v is not None)
    if not cleaned:
        return {"median": None, "iqr": None}
    q1 = quantile(cleaned, 0.25)
    q3 = quantile(cleaned, 0.75)
    median = quantile(cleaned, 0.5)
    if q1 is None or q3 is None:
        iqr = None
    else:
        iqr = q3 - q1
    return {"median": median, "iqr": iqr}


def standard_stats(values: Iterable[Optional[float]]) -> Dict[str, Optional[float]]:
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return {"mean": None, "std": None}
    mean = sum(cleaned) / len(cleaned)
    variance = sum((v - mean) ** 2 for v in cleaned) / len(cleaned)
    std = math.sqrt(variance)
    return {"mean": mean, "std": std}


def build_features(input_path: Path, scaler: str) -> List[Dict[str, Optional[float]]]:
    rows: List[Dict[str, Optional[float]]] = []
    with input_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            median_income = parse_float(row.get("statcan_median_income_after_tax", ""))
            avg_rent = parse_float(row.get("cmhc_avg_rent_2br", ""))
            rent_growth = parse_float(row.get("cmhc_rent_growth_yoy", ""))
            vacancy = parse_float(row.get("cmhc_vacancy_rate", ""))

            monthly_income = None
            if median_income is not None and median_income > 0:
                monthly_income = median_income / 12.0

            rent_to_income = None
            if monthly_income and avg_rent is not None and avg_rent >= 0:
                # Share of monthly income required for rent.
                rent_to_income = avg_rent / monthly_income

            # Invert vacancy so lower vacancy means higher stress.
            vacancy_stress = -vacancy if vacancy is not None else None

            rows.append(
                {
                    "metro_id": row.get("metro_id"),
                    "metro_name_std": row.get("metro_name_std"),
                    "province": row.get("province"),
                    "statcan_reference_year": row.get("statcan_reference_year"),
                    "cmhc_rent_year": row.get("cmhc_rent_year"),
                    "cmhc_vacancy_year": row.get("cmhc_vacancy_year"),
                    "cmhc_rent_growth_year": row.get("cmhc_rent_growth_year"),
                    "rent_to_income": rent_to_income,
                    "rent_growth_yoy": rent_growth,
                    "vacancy_rate": vacancy,
                    "vacancy_stress": vacancy_stress,
                }
            )

    feature_names = ["rent_to_income", "rent_growth_yoy", "vacancy_rate", "vacancy_stress"]
    if scaler == "robust":
        stats = {name: robust_stats([r[name] for r in rows]) for name in feature_names}
        for row in rows:
            for name in feature_names:
                median = stats[name]["median"]
                iqr = stats[name]["iqr"]
                value = row[name]
                if value is None or median is None or iqr is None:
                    row[f"{name}_scaled"] = None
                elif iqr == 0:
                    row[f"{name}_scaled"] = 0.0
                else:
                    # Scale by how far the value is from the median.
                    row[f"{name}_scaled"] = (value - median) / iqr
    else:
        stats = {name: standard_stats([r[name] for r in rows]) for name in feature_names}
        for row in rows:
            for name in feature_names:
                mean = stats[name]["mean"]
                std = stats[name]["std"]
                value = row[name]
                if value is None or mean is None or std is None:
                    row[f"{name}_scaled"] = None
                elif std == 0:
                    row[f"{name}_scaled"] = 0.0
                else:
                    # Standard z-score scaling.
                    row[f"{name}_scaled"] = (value - mean) / std

    return rows


def write_csv(output_path: Path, rows: List[Dict[str, Optional[float]]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_parquet(output_path: Path, rows: List[Dict[str, Optional[float]]]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError(
            "pyarrow is required to write parquet outputs. "
            "Install it (e.g., `pip install pyarrow`) or choose a .csv output."
        ) from exc

    table = pa.Table.from_pylist(rows)
    pq.write_table(table, output_path)


def write_output(output_path: Path, rows: List[Dict[str, Optional[float]]]) -> None:
    if output_path.suffix == ".parquet":
        write_parquet(output_path, rows)
    elif output_path.suffix == ".csv":
        write_csv(output_path, rows)
    else:
        raise ValueError("Output path must end with .parquet or .csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build engineered features and scaled set.")
    parser.add_argument(
        "--input",
        default="data/processed/metros_modeling.csv",
        help="Input modeling CSV",
    )
    parser.add_argument(
        "--output",
        default="data/processed/features_scaled.parquet",
        help="Output path (.parquet or .csv)",
    )
    parser.add_argument(
        "--scaler",
        choices=["robust", "standard"],
        default="robust",
        help="Scaling method for engineered features",
    )
    args = parser.parse_args()

    rows = build_features(Path(args.input), args.scaler)
    write_output(Path(args.output), rows)


if __name__ == "__main__":
    main()
