#!/usr/bin/env python3
"""Compute an Affordability Stress Index (ASI) and optional PC1 comparison."""

from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np


FEATURES = [
    "rent_to_income_scaled",
    "rent_growth_yoy_scaled",
    "vacancy_stress_scaled",
]


def parse_float(value: Optional[str]) -> Optional[float]:
    """Parse a numeric cell value, returning None for blanks/NA tokens."""
    if value is None:
        return None
    value = value.strip()
    if value == "" or value.lower() in {"na", "nan", "null"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_rows(path: Path) -> List[Dict[str, Optional[str]]]:
    """Load a CSV into a list of dict rows, keeping raw string values."""
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def compute_asi(
    rows: List[Dict[str, Optional[str]]],
    weights: Dict[str, float],
) -> Tuple[List[Dict[str, Optional[str]]], Dict[str, float]]:
    """Compute ASI as a weighted mean of standardized feature signals.

    - Weights are normalized to sum to 1 for transparency.
    - Missing feature values are skipped, and weights are re-normalized per row.
    - Outputs: asi_score (stringified float) and asi_components_used (count).
    """
    weight_sum = sum(weights.values())
    if weight_sum <= 0:
        raise ValueError("Weights must sum to a positive value.")
    normalized = {key: val / weight_sum for key, val in weights.items()}

    for row in rows:
        weighted_sum = 0.0
        used_weight = 0.0
        used_features: List[str] = []
        for feature, weight in normalized.items():
            value = parse_float(row.get(feature))
            if value is None:
                continue
            weighted_sum += value * weight
            used_weight += weight
            used_features.append(feature)
        if used_weight == 0:
            row["asi_score"] = None
            row["asi_components_used"] = "0"
        else:
            row["asi_score"] = f"{weighted_sum / used_weight:.6f}"
            row["asi_components_used"] = str(len(used_features))
    return rows, normalized


def compute_pc1_scores(rows: List[Dict[str, Optional[str]]]) -> None:
    """Compute a standardized PC1 score for comparison (optional diagnostic).

    Uses only rows with complete FEATURES. The PC1 direction is aligned to ASI
    so that higher values indicate more stress when correlation is negative.
    """
    data = []
    row_indices = []
    for idx, row in enumerate(rows):
        values = [parse_float(row.get(feature)) for feature in FEATURES]
        if any(v is None for v in values):
            continue
        data.append(values)
        row_indices.append(idx)

    if len(data) < 2:
        for row in rows:
            row["asi_score_pc1"] = None
        return

    matrix = np.array(data, dtype=float)
    mean = matrix.mean(axis=0)
    centered = matrix - mean
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    pc1 = vt[0]
    scores = centered @ pc1

    score_mean = scores.mean()
    score_std = scores.std()
    if score_std == 0:
        standardized = np.zeros_like(scores)
    else:
        standardized = (scores - score_mean) / score_std

    row_pos = {row_idx: pos for pos, row_idx in enumerate(row_indices)}
    asi_values = []
    pc1_values = []
    for idx in row_indices:
        asi_value = parse_float(rows[idx].get("asi_score"))
        if asi_value is None:
            continue
        asi_values.append(asi_value)
        pc1_values.append(standardized[row_pos[idx]])

    if asi_values:
        asi_array = np.array(asi_values)
        pc1_array = np.array(pc1_values)
        if asi_array.std() > 0 and pc1_array.std() > 0:
            corr = np.corrcoef(asi_array, pc1_array)[0, 1]
            if corr < 0:
                standardized = -standardized

    for idx, score in zip(row_indices, standardized):
        rows[idx]["asi_score_pc1"] = f"{score:.6f}"
    for idx, row in enumerate(rows):
        if idx not in row_indices:
            row["asi_score_pc1"] = None


def write_csv(path: Path, rows: List[Dict[str, Optional[str]]]) -> None:
    """Write rows to CSV, preserving key order from the first row."""
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def create_top15_plot(
    rows: List[Dict[str, Optional[str]]],
    output_path: Path,
) -> None:
    """Save a horizontal bar chart ranking the top 15 metros by ASI."""
    os.environ.setdefault("MPLBACKEND", "Agg")
    cache_dir = output_path.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_dir))
    mpl_config_dir = output_path.parent / ".mplconfig"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    import matplotlib.pyplot as plt

    scored = []
    for row in rows:
        score = parse_float(row.get("asi_score"))
        if score is None:
            continue
        name = row.get("metro_name_std") or row.get("metro_id") or "Unknown"
        scored.append((name, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    top = scored[:15]
    if not top:
        raise ValueError("No ASI scores available for plotting.")

    names = [item[0] for item in top][::-1]
    scores = [item[1] for item in top][::-1]

    plt.figure(figsize=(10, 7))
    plt.barh(names, scores, color="#3b6ea8")
    plt.xlabel("Affordability Stress Index (higher = more stress)")
    plt.title("Top 15 Metros by ASI")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the Affordability Stress Index.")
    parser.add_argument(
        "--input",
        default="data/processed/features_scaled.csv",
        help="Input features CSV (scaled).",
    )
    parser.add_argument(
        "--output",
        default="data/processed/asi_scores.csv",
        help="Output ASI CSV.",
    )
    parser.add_argument(
        "--plot-output",
        default="data/processed/asi_top15.png",
        help="Output PNG plot for top-15 metros.",
    )
    args = parser.parse_args()

    rows = read_rows(Path(args.input))
    weights = {feature: 1.0 for feature in FEATURES}
    rows, normalized = compute_asi(rows, weights)

    compute_pc1_scores(rows)

    rows_out = []
    for row in rows:
        output_row = dict(row)
        output_row["asi_weighting"] = ";".join(
            f"{feat}={normalized[feat]:.3f}" for feat in FEATURES
        )
        rows_out.append(output_row)

    write_csv(Path(args.output), rows_out)
    create_top15_plot(rows_out, Path(args.plot_output))


if __name__ == "__main__":
    main()
