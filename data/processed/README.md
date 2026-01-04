# Processed data directory

This folder holds cleaned and derived files created by the notebooks and scripts.
They are outputs, not raw data, and are not committed to version control.

Common files you will see here:

- `metros_master.csv`: standard list of metros and join keys.
- `metros_modeling.csv`: modeling-ready version of the master table.
- `features_scaled.parquet` or `.csv`: engineered affordability features.
- `asi_scores.csv`: the Affordability Stress Index results.
- `metro_join_missingness_summary.csv`: join coverage checks across sources.
