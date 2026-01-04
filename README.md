# Housing Affordability Stress Index (ASI)

This project builds a plain-language score called the Affordability Stress Index (ASI). The score combines a few housing and income signals into one number so you can quickly compare Canadian metro areas. Higher ASI means more pressure on renters.

## What this project is for

- Compare metros using a consistent, repeatable score.
- Highlight places where rent is rising faster than incomes or vacancies are tight.
- Support policy, planning, and research discussions with transparent inputs.

## What this project is not

- It does not prove cause and effect. It shows patterns, not why they happen.
- It does not replace local analysis or on-the-ground context.
- It does not measure homeownership affordability (mortgages and prices are not included yet).

## Data sources in plain language

We combine two trusted public sources:

- Statistics Canada (StatCan): income, population, unemployment, and inflation data.
- Canada Mortgage and Housing Corporation (CMHC): rents, vacancy rates, and housing starts.

See `data_sources.md` for exact table IDs, links, and download notes.

## How the ASI is built (simple version)

We take three stress signals, scale them so they can be compared, and then average them:

1. Rent-to-income pressure: how much of a typical household's income goes to rent.
2. Rent growth: how quickly rent is rising year over year.
3. Vacancy stress: low vacancy means tight supply, so we invert the vacancy rate.

A higher combined score means more housing stress for renters. The score is meant to be compared across metros in the same run.

## Project structure

```
├── data/
│   ├── raw/                    # Raw data files (gitignored)
│   │   ├── .gitignore         # Excludes raw data from version control
│   │   └── README.md          # Download instructions for raw data
│   └── processed/             # Cleaned and processed data
│       ├── metros_master.csv  # Master dataset of metropolitan areas
│       └── asi_scores.csv     # Affordability Stress Index scores
├── notebooks/
│   ├── 00_ingest_plan.ipynb       # Download inventory + ingestion checklist
│   ├── 01_ingest_statcan.ipynb    # StatCan metro ingest
│   ├── 02_ingest_cmhc.ipynb       # CMHC metro ingest
│   ├── 03_ingest_clean.ipynb      # Data ingestion and cleaning
│   ├── 04_features_index.ipynb    # Feature engineering and ASI calculation
│   ├── 05_pca.ipynb               # PCA diagnostics + interpretability artifacts
│   └── 06_clustering.ipynb        # KMeans + HDBSCAN clustering, personas, and checks
├── src/                       # Source code (reusable functions)
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
   - See `data/raw/README.md` for download instructions.
   - Place downloaded files in `data/raw/`.

## Run the analysis (notebook order)

1. `notebooks/00_ingest_plan.ipynb` - list sources and check what is missing.
2. `notebooks/01_ingest_statcan.ipynb` - bring in StatCan data.
3. `notebooks/02_ingest_cmhc.ipynb` - bring in CMHC data.
4. `notebooks/03_ingest_clean.ipynb` - clean and merge sources into a master file.
5. `notebooks/04_features_index.ipynb` - build features and calculate ASI.
6. `notebooks/05_pca.ipynb` - explain the features with PCA.
7. `notebooks/06_clustering.ipynb` - group metros into similar profiles.

Start Jupyter and run each notebook:

```bash
jupyter notebook
```

## Outputs and how to read them

- `data/processed/asi_scores.csv`: the main ASI results per metro.
- `report/figures/asi_top15.png`: quick view of the 15 most stressed metros.
- `report/figures/pca_explained_variance.png`: how much each feature contributes.
- `report/figures/pca_clusters_kmeans.png` and `report/figures/pca_clusters_hdbscan.png`: grouping maps.
- `report/figures/kmeans_k_sweep.png`: shows how the chosen number of clusters was selected.
- `report/final_report_1_4_26.md`: short narrative write-up with the headline figures for sharing (as run on 1/4/26).

## What you can infer (and what you cannot)

You can infer:
- Which metros are under relatively higher renter pressure right now.
- Whether that pressure is driven more by rent growth, low vacancy, or rent-to-income.
- Which metros look similar to each other based on those signals.

You should not infer:
- Why a metro is stressed (this needs local context and deeper analysis).
- That the score predicts future migration or health outcomes.
- That small differences in the score are meaningful on their own.

## Limitations and next steps

- Data releases lag by months, so the score should be refreshed each cycle.
- The current focus is renters, not owners.
- Some metros have partial data or special cases (see the missingness summary).

Next steps include adding ownership metrics, automating refreshes, and pairing the ASI with migration outcomes.

## Contributing

Contributions are welcome. Please open a pull request with a clear description.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
