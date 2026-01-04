#!/usr/bin/env bash
set -euo pipefail

# Creates GitHub issues for the "Housing Affordability Stress Index" project.
# Requirements:
#   - GitHub CLI installed: https://cli.github.com/
#   - Authenticated: gh auth login
#
# Usage:
#   ./scripts/create_issues_housing_asi.sh OWNER/REPO
# Example:
#   ./scripts/create_issues_housing_asi.sh ajharris/housing-affordability

REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Usage: $0 OWNER/REPO"
  exit 1
fi

# Optional: set to "true" to create a milestone
CREATE_MILESTONE="${CREATE_MILESTONE:-true}"
MILESTONE_TITLE="${MILESTONE_TITLE:-Housing Affordability Stress Index MVP}"
MILESTONE_DUE_ON="${MILESTONE_DUE_ON:-}" # ISO date, e.g. 2026-01-05T00:00:00Z (optional)

ensure_label () {
  local name="$1"
  local color="$2"
  local desc="$3"
  if gh label list -R "$REPO" --limit 200 | awk '{print $1}' | grep -qx "$name"; then
    echo "Label exists: $name"
  else
    echo "Creating label: $name"
    gh label create "$name" -R "$REPO" --color "$color" --description "$desc"
  fi
}

ensure_milestone_exists () {
  # Ensures the milestone exists (by title). Creates it if missing.
  local existing
  existing="$(gh api -X GET "repos/${REPO}/milestones?state=all" --paginate \
    | jq -r ".[] | select(.title==\"${MILESTONE_TITLE}\") | .number" | head -n 1 || true)"

  if [[ -n "$existing" ]]; then
    return 0
  fi

  if [[ -n "$MILESTONE_DUE_ON" ]]; then
    gh api -X POST "repos/${REPO}/milestones" \
      -f title="$MILESTONE_TITLE" \
      -f due_on="$MILESTONE_DUE_ON" >/dev/null
  else
    gh api -X POST "repos/${REPO}/milestones" \
      -f title="$MILESTONE_TITLE" >/dev/null
  fi
}

create_issue () {
  local title="$1"
  local body="$2"
  local labels_csv="$3"      # comma-separated
  local milestone_ref="${4:-}" # milestone title (not number)

  local args=(issue create -R "$REPO" --title "$title" --body "$body")
  IFS=',' read -ra labels_arr <<< "$labels_csv"
  for lbl in "${labels_arr[@]}"; do
    [[ -n "$lbl" ]] && args+=(--label "$lbl")
  done
  [[ -n "$milestone_ref" ]] && args+=(--milestone "$milestone_ref")

  gh "${args[@]}" >/dev/null
  echo "Created: $title"
}

command -v gh >/dev/null 2>&1 || { echo "gh is required but not installed."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required but not installed."; exit 1; }

echo "Target repo: $REPO"

# Labels
ensure_label "type:data"       "0E8A16" "Data acquisition, cleaning, crosswalks"
ensure_label "type:features"   "1D76DB" "Feature engineering and index construction"
ensure_label "type:modeling"   "5319E7" "PCA and clustering work"
ensure_label "type:viz"        "FBCA04" "Visualization and reporting figures"
ensure_label "type:docs"       "006B75" "README, report, project documentation"
ensure_label "type:quality"    "D93F0B" "Robustness checks, testing, reproducibility"
ensure_label "priority:high"   "B60205" "High priority"
ensure_label "priority:medium" "FF9F1C" "Medium priority"
ensure_label "priority:low"    "C2E0C6" "Low priority"

# Optional milestone
MILESTONE_REF=""
if [[ "$CREATE_MILESTONE" == "true" ]]; then
  ensure_milestone_exists
  MILESTONE_REF="$MILESTONE_TITLE"   # IMPORTANT: gh issue create expects milestone title
  echo "Using milestone: $MILESTONE_REF"
else
  echo "Skipping milestone creation (CREATE_MILESTONE=false)"
fi

# Issues
create_issue \
  "Project scaffolding: repo structure, env, and conventions" \
  "Create the initial project structure and reproducibility setup.\n\nAcceptance criteria:\n- Repo has folders: data/raw (gitignored), data/processed, notebooks, report/figures, scripts, src (optional)\n- requirements.txt (or pyproject.toml) created\n- README has project overview stub + how to run\n- Pre-commit hooks or basic formatting guidance documented\n\nNotes:\n- Prefer CMA/CA unit of analysis; decide and document.\n" \
  "type:docs,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Data inventory: identify StatCan and CMHC tables and download plan" \
  "List the exact StatCan and CMHC datasets needed and how they will be downloaded.\n\nAcceptance criteria:\n- A data_sources.md (or README section) listing:\n  - Dataset name\n  - Provider (StatCan/CMHC)\n  - Geography level (CMA/CA)\n  - Time range\n  - Key variables\n  - Download method (manual file, API, etc.)\n- A script or notebook cell plan for ingest steps\n\nNotes:\n- Keep scope small: 5–8 indicators maximum.\n" \
  "type:data,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Build metro crosswalk: standardize CMA/CA identifiers and names" \
  "Create a master metro table with stable identifiers for joining across sources.\n\nAcceptance criteria:\n- metros_master table with columns like: metro_id (CMA code), metro_name_std, province\n- Join keys documented\n- A missingness report after initial joins\n\nNotes:\n- This is the critical integration step. Keep it explicit and versioned.\n" \
  "type:data,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Ingest StatCan indicators: income and context variables" \
  "Pull StatCan variables for each metro.\n\nAcceptance criteria:\n- Notebook: 01_ingest_statcan.ipynb (or similar)\n- Output: data/processed/statcan_metro.csv\n- Variables include at minimum: median household income (prefer after-tax if available)\n- If added: unemployment rate, population growth, migration proxy, document rationale\n\nNotes:\n- Ensure consistent time alignment (same year or closest available).\n" \
  "type:data,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Ingest CMHC indicators: rent, vacancy, supply proxies" \
  "Pull CMHC variables for each metro.\n\nAcceptance criteria:\n- Notebook: 02_ingest_cmhc.ipynb (or similar)\n- Output: data/processed/cmhc_metro.csv\n- Variables include at minimum: avg rent (1BR or 2BR), vacancy rate, rent growth YoY if derivable\n\nNotes:\n- Document measurement definitions (e.g., what rent series is used).\n" \
  "type:data,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Assemble modeling table: one row per metro with aligned time window" \
  "Join StatCan and CMHC into a single modeling dataset.\n\nAcceptance criteria:\n- Output: data/processed/metros_modeling.csv\n- Clear policy for missing values (drop metro, impute, or partial)\n- A short table in notebook showing number of metros retained and missingness by feature\n" \
  "type:data,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Feature engineering: affordability stress features" \
  "Create engineered features and finalize the feature set.\n\nAcceptance criteria:\n- Features computed (as available):\n  - rent_to_income (monthly rent / monthly income)\n  - rent_growth_yoy\n  - vacancy_rate (and optionally stress direction as -vacancy)\n  - optional: price_to_income if reliable\n- Scaling choice documented (robust or standard)\n- Output: data/processed/features_scaled.csv (or parquet)\n" \
  "type:features,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Define and compute Affordability Stress Index (ASI)" \
  "Compute an interpretable index.\n\nAcceptance criteria:\n- ASI computed as weighted sum of standardized stress signals OR documented alternative\n- Optional: PC1-based index computed for comparison\n- Output: data/processed/asi_scores.csv\n- A figure ranking metros by ASI (top 15)\n\nNotes:\n- Keep the index transparent. Avoid complicated weighting without justification.\n" \
  "type:features,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "PCA diagnostics: explained variance and loadings for interpretability" \
  "Run PCA and generate interpretability artifacts.\n\nAcceptance criteria:\n- Explained variance plot\n- Loadings table for first 2–3 PCs\n- Short written interpretation: what each PC represents\n- Saved outputs to report/figures and/or data/processed/pca_loadings.csv\n" \
  "type:modeling,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "KMeans clustering in PCA space: choose K and assign clusters" \
  "Cluster metros using KMeans and justify K.\n\nAcceptance criteria:\n- K sweep (2..10) with silhouette and inertia\n- Final K chosen with brief rationale\n- Cluster assignments saved: data/processed/clusters_kmeans.csv\n- PCA scatter plot PC1 vs PC2 colored by cluster\n" \
  "type:modeling,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "HDBSCAN clustering: parameter sweep and outlier handling" \
  "Cluster metros using HDBSCAN and compare behavior to KMeans.\n\nAcceptance criteria:\n- Parameter sweep for min_cluster_size and min_samples\n- Final run selected and documented\n- Cluster assignments saved: data/processed/clusters_hdbscan.csv\n- Note which metros are labeled as noise/outliers and why that is acceptable\n" \
  "type:modeling,priority:medium" \
  "$MILESTONE_REF"

create_issue \
  "Cluster profiling: medians/IQR and narrative interpretations" \
  "Turn clusters into interpretable profiles.\n\nAcceptance criteria:\n- For each method (KMeans and HDBSCAN):\n  - Table of cluster size and representative metros\n  - Median of each original feature per cluster\n  - A list of exemplar metros per cluster\n- 2–3 sentence story per cluster\n- Output: report/figures/cluster_profiles_*.png and/or data/processed/cluster_profiles.csv\n" \
  "type:viz,priority:high" \
  "$MILESTONE_REF"

create_issue \
  "Robustness checks: sensitivity to features and scaling" \
  "Evaluate stability of clusters and index.\n\nAcceptance criteria:\n- At least two sensitivity checks:\n  - Swap scaler (standard vs robust)\n  - Drop one feature at a time\n- Report how cluster assignments change (simple agreement rate or ARI if implemented)\n- Write a brief limitations section\n" \
  "type:quality,priority:medium" \
  "$MILESTONE_REF"

create_issue \
  "Final report: README + short narrative write-up with figures" \
  "Produce portfolio-ready documentation.\n\nAcceptance criteria:\n- README includes:\n  - Motivation (health and migration relevance)\n  - Data sources (StatCan, CMHC) and definitions\n  - Methods (ASI, PCA, KMeans, HDBSCAN)\n  - Results (key plots and cluster interpretations)\n  - Limitations and next steps\n- A short report (markdown or PDF) in report/ with 4–6 figures\n" \
  "type:docs,priority:high" \
  "$MILESTONE_REF"

echo "Done. Issues created in $REPO."
