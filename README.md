# Housing Affordability Stress Index

A data analysis project examining housing affordability across metropolitan areas using a comprehensive Affordability Stress Index (ASI).

## StatCan WDS status

The WDS API endpoints have been updated to use the correct `/rest/` path as documented in the [StatCan WDS User Guide](https://www.statcan.gc.ca/en/developers/wds/user-guide).

Previous 404 errors were due to using incorrect endpoint paths (`/en/grp/wds/fn/` instead of `/rest/`). The endpoints are now configured correctly:
- `getAllCubesListLite`: `https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite`
- `getFullTableDownloadCSV`: `https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{PID}/en`

## Project Structure

```
├── data/
│   ├── raw/                    # Raw data files (gitignored)
│   │   ├── .gitignore         # Excludes raw data from version control
│   │   └── README.md          # Download instructions for raw data
│   └── processed/             # Cleaned and processed data
│       ├── metros_master.csv  # Master dataset of metropolitan areas
│       └── asi_scores.csv     # Affordability Stress Index scores
├── notebooks/
│   ├── 01_ingest_statcan.ipynb    # StatCan metro ingest
│   ├── 02_ingest_cmhc.ipynb       # CMHC metro ingest
│   ├── 03_ingest_clean.ipynb      # Data ingestion and cleaning
│   ├── 04_features_index.ipynb    # Feature engineering and ASI calculation
│   └── 05_clustering.ipynb        # Clustering analysis
├── src/                       # Source code (optional for refactored functions)
├── report/
│   └── figures/              # Generated visualizations and figures
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ajharris/housing-affordability.git
   cd housing-affordability
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Download raw data:
   - See `data/raw/README.md` for detailed download instructions
   - Place downloaded files in the `data/raw/` directory

## Usage

The analysis is organized into three main notebooks:

1. **01_ingest_statcan.ipynb**: Build StatCan metro variables from raw CSVs
2. **02_ingest_cmhc.ipynb**: Build CMHC metro variables from the Rental Market Survey workbook
3. **03_ingest_clean.ipynb**: Load raw data, perform initial exploration, clean and preprocess data
4. **04_features_index.ipynb**: Engineer features and calculate the Affordability Stress Index (ASI)
5. **05_clustering.ipynb**: Perform clustering analysis to group metros by affordability patterns

Run the notebooks in sequence:

```bash
jupyter notebook
```

## Data

- **Raw data**: Stored in `data/raw/` (not tracked by git). See download instructions in that directory.
- **Processed data**: Cleaned datasets stored in `data/processed/`
  - `metros_master.csv`: Master dataset with metropolitan area information
  - `asi_scores.csv`: Calculated Affordability Stress Index scores

## Metro Crosswalk and Join Keys

- Run the reproducible builder in [src/build_metros_master.py](src/build_metros_master.py) to regenerate the master metro table and refresh coverage diagnostics: `python src/build_metros_master.py`.
- `metro_id` is the four-digit StatCan CMA code (last four digits of the 2021 DGUID) and is the canonical join key across sources.
- `metro_name_std` keeps the human-readable CMA label, while `metro_slug` is an ASCII-safe slug used to standardize joins from verbose `GEO` strings (e.g., "Ottawa-Gatineau, Ontario/Quebec"). Provinces follow the same pattern via `province` and `province_slug`.
- The builder also emits a missingness summary at [data/processed/metro_join_missingness_summary.csv](data/processed/metro_join_missingness_summary.csv) and the unmatched records at [data/processed/metro_join_missingness_unmatched.csv](data/processed/metro_join_missingness_unmatched.csv). As of this run, only the Ontario/Quebec split parts of Ottawa-Gatineau lack a direct CMA-level match and are flagged for manual handling.

## Outputs

- Analysis results and visualizations are saved to `report/figures/`
- Processed datasets are saved to `data/processed/`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]
