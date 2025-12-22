# Housing Affordability Stress Index

A data analysis project examining housing affordability across metropolitan areas using a comprehensive Affordability Stress Index (ASI).

## Project Structure

```
housing-affordability/
├── data/
│   ├── raw/                    # Raw data files (gitignored)
│   │   ├── .gitignore         # Excludes raw data from version control
│   │   └── README.md          # Download instructions for raw data
│   └── processed/             # Cleaned and processed data
│       ├── metros_master.csv  # Master dataset of metropolitan areas
│       └── asi_scores.csv     # Affordability Stress Index scores
├── notebooks/
│   ├── 01_ingest_clean.ipynb      # Data ingestion and cleaning
│   ├── 02_features_index.ipynb    # Feature engineering and ASI calculation
│   └── 03_clustering.ipynb        # Clustering analysis
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

1. **01_ingest_clean.ipynb**: Load raw data, perform initial exploration, clean and preprocess data
2. **02_features_index.ipynb**: Engineer features and calculate the Affordability Stress Index (ASI)
3. **03_clustering.ipynb**: Perform clustering analysis to group metros by affordability patterns

Run the notebooks in sequence:

```bash
jupyter notebook
```

## Data

- **Raw data**: Stored in `data/raw/` (not tracked by git). See download instructions in that directory.
- **Processed data**: Cleaned datasets stored in `data/processed/`
  - `metros_master.csv`: Master dataset with metropolitan area information
  - `asi_scores.csv`: Calculated Affordability Stress Index scores

## Outputs

- Analysis results and visualizations are saved to `report/figures/`
- Processed datasets are saved to `data/processed/`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]
