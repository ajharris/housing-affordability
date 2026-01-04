"""Build the metro master table and surface join coverage across StatCan sources."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

POPULATION_FILE = RAW_DIR / "population_estimates_17100148.csv"
UNEMPLOYMENT_FILE = RAW_DIR / "unemployment_rate_14100459.csv"
INCOME_FILE = RAW_DIR / "median_household_income_11100035.csv"


def slugify(value: str) -> str:
    """Return a lowercase ASCII slug that is consistent across sources."""

    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_text = ascii_text.lower().replace("&", " and ")
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    ascii_text = re.sub(r"_+", "_", ascii_text).strip("_")
    return ascii_text


def clean_city_label(label: str) -> str:
    """Strip StatCan qualifiers down to the city/metro label."""

    if not isinstance(label, str):
        return ""
    text = label.strip()
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    text = text.split(",")[0]
    text = re.sub(r"\((?:CMA|CA)\)", "", text, flags=re.I)
    text = text.replace(" - ", "-")
    return text.strip(" ,")


def extract_province(label: str) -> str:
    if not isinstance(label, str) or "," not in label:
        return ""
    return label.split(",")[-1].strip()


def build_master_from_population() -> pd.DataFrame:
    cols = ["GEO", "DGUID", "Gender", "Age group"]
    df = pd.read_csv(POPULATION_FILE, usecols=cols, dtype={"DGUID": "string"})
    mask = (df["Age group"] == "All ages") & (df["Gender"] == "Total - gender")
    df = df.loc[mask]
    df = df[df["GEO"].str.contains("(CMA)", regex=False, na=False)]
    df = df[~df["GEO"].str.contains("part", case=False, na=False)]
    df = df.drop_duplicates(subset=["GEO", "DGUID"])

    master = pd.DataFrame(
        {
            "metro_id": df["DGUID"].str[-4:],
            "metro_name_std": df["GEO"].apply(clean_city_label),
            "province": df["GEO"].apply(extract_province),
            "dguid_2021": df["DGUID"],
            "boundary_year": 2021,
        }
    )
    master["metro_slug"] = master["metro_name_std"].apply(slugify)
    master["province_slug"] = master["province"].apply(slugify)
    master = master[
        [
            "metro_id",
            "metro_name_std",
            "metro_slug",
            "province",
            "province_slug",
            "dguid_2021",
            "boundary_year",
        ]
    ]
    master = master.drop_duplicates(subset=["metro_id"]).sort_values("metro_name_std").reset_index(drop=True)

    if master["metro_id"].duplicated().any():
        dupes = master.loc[master["metro_id"].duplicated(), "metro_id"].tolist()
        raise ValueError(f"Duplicate metro_id values detected: {dupes}")
    return master


def load_geo_labels(path: Path, *, require_cma_tag: bool = False) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["GEO"])
    df = df.dropna(subset=["GEO"])
    if require_cma_tag:
        df = df[df["GEO"].str.contains("(CMA)", regex=False, na=False)]
    df = df[df["GEO"].str.contains(",", na=False)]
    df = df[~df["GEO"].str.contains("Total", case=False, na=False)]
    df = df[~df["GEO"].str.contains("All other", case=False, na=False)]

    geo_df = df.rename(columns={"GEO": "geo_label"}).copy()
    geo_df["metro_name_source"] = geo_df["geo_label"].apply(clean_city_label)
    geo_df["province_source"] = geo_df["geo_label"].apply(extract_province)
    geo_df["metro_slug"] = geo_df["metro_name_source"].apply(slugify)
    geo_df["is_partial"] = geo_df["geo_label"].str.contains("part", case=False, na=False)
    geo_df = geo_df.drop_duplicates(subset=["geo_label"])
    return geo_df


def summarize_missingness(master: pd.DataFrame, geo_df: pd.DataFrame, source: str) -> tuple[dict[str, object], pd.DataFrame]:
    merged = geo_df.merge(master[["metro_slug", "metro_id"]], on="metro_slug", how="left", indicator=True)
    merged["matched"] = merged["_merge"] == "both"
    merged.drop(columns="_merge", inplace=True)
    partial_mask = merged["is_partial"].fillna(False)
    merged.loc[partial_mask, "metro_id"] = pd.NA
    merged.loc[partial_mask, "matched"] = False
    merged["source"] = source

    summary = {
        "source": source,
        "unique_geo_labels": int(len(geo_df)),
        "matched_geos": int(merged["matched"].sum()),
        "unmatched_geos": int((~merged["matched"]).sum()),
        "partial_geos": int(partial_mask.sum()),
        "sample_unmatched": "; ".join(merged.loc[~merged["matched"], "geo_label"].head(5).tolist()),
    }
    return summary, merged


def ensure_processed_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ensure_processed_dir()
    master = build_master_from_population()
    master_path = PROCESSED_DIR / "metros_master.csv"
    master.to_csv(master_path, index=False)

    coverage_summary: list[dict[str, object]] = []
    coverage_details: list[pd.DataFrame] = []

    for name, dataset_path, require_cma in (
        ("statcan_unemployment", UNEMPLOYMENT_FILE, False),
        ("statcan_income", INCOME_FILE, False),
    ):
        geo_df = load_geo_labels(dataset_path, require_cma_tag=require_cma)
        summary, detail = summarize_missingness(master, geo_df, name)
        coverage_summary.append(summary)
        coverage_details.append(detail)

    summary_df = pd.DataFrame(coverage_summary)
    summary_path = PROCESSED_DIR / "metro_join_missingness_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    unmatched_df = pd.concat(coverage_details, ignore_index=True)
    unmatched_df = unmatched_df[~unmatched_df["matched"]].sort_values(["source", "geo_label"])
    unmatched_path = PROCESSED_DIR / "metro_join_missingness_unmatched.csv"
    unmatched_df.to_csv(unmatched_path, index=False)

    print(f"Wrote {master_path.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {summary_path.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {unmatched_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()