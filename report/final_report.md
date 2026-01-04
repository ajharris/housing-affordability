# Housing Affordability Stress Index – Portfolio Summary

## Motivation & Framing

Housing stress is a public-health and migration issue: renters who spend most of their paycheque on shelter defer medical care, while employers struggle to attract talent into high-cost metros. This project builds an Affordability Stress Index (ASI) to compare Canadian CMAs on three renter-facing signals—rent-to-income pressure, rent growth, and vacancy stress—so regional planners can identify which markets most urgently need supply, subsidies, or mobility support.

![Top ASI metros](figures/asi_top15.png)

*Figure 1. Halifax, Moncton, Kelowna, and other mid-sized metros top the ASI leaderboard, reflecting simultaneous rent spikes and lagging incomes.*

## Data & Methods

- **Sources** – Statistics Canada tables (income, CPI, labour force, population) and CMHC Rental Market Survey / Housing Starts feed the engineered feature set (details in `data_sources.md`).
- **Indexing** – `src/compute_asi.py` combines standardized stress signals into the ASI and publishes `data/processed/asi_scores.csv` plus Figure 1.
- **Dimensionality reduction** – `05_pca.ipynb` reprojects the signals into orthogonal PCs, documenting explained variance for transparency.
- **Segmentation** – `06_clustering.ipynb` runs both centroid-based (KMeans) and density-based (HDBSCAN) clustering to surface personas and noise metros, then exports labeled tables and profile heatmaps.

![PCA explained variance](figures/pca_explained_variance.png)

*Figure 2. PC1 captures the shared rent-to-income/vacancy pressure axis, while PC2 isolates high rent-growth metros.*

![KMeans diagnostics](figures/kmeans_k_sweep.png)

*Figure 3. Silhouette and inertia curves justify the selected K; the elbow occurs where silhouette remains high but inertia’s marginal gains flatten.*

## Cluster Narratives

KMeans personas reveal three broad metro types:

1. **"High heat" renters** – CMAs with extreme rent-to-income and low vacancy (e.g., Halifax, Kelowna) show up in the most stressed cluster.
2. **"Momentum markets"** – Fast rent growth but moderate vacancy (e.g., Calgary, Ottawa) demands monitoring before stress spills over into health/migration outcomes.
3. **"Relief hubs"** – Higher vacancy or lower rent-to-income metros (e.g., Winnipeg, Regina) where migration inflows can be encouraged.

![KMeans clusters](figures/pca_clusters_kmeans.png)

*Figure 4. PC1/PC2 scatter colored by KMeans cluster, aligning with the personas above.*

![HDBSCAN clusters](figures/pca_clusters_hdbscan.png)

*Figure 5. HDBSCAN highlights sparse metros (gray) that defy dense grouping—many are tourism or resource towns needing bespoke policies.*

![Cluster profiles](figures/cluster_profiles_kmeans.png)

*Figure 6. Persona heatmap summarizing median stress-signal loadings per cluster plus exemplar metros.*

## Limitations & Next Steps

- **Data lags** – StatCan/CMHC releases trail real time, so ASI should be regenerated each quarter; automation via Prefect/Airflow is on the backlog.
- **Scope** – Current signals focus on renters. Extending to ownership, evictions, or health outcomes will deepen the decision lens.
- **Sensitivity** – RobustScaler and leave-one-feature-out tests show most personas are stable, but single-feature metros can flip; future work should extend robustness checks to HDBSCAN and explore fuzzy clustering.
- **Causal links** – The ASI surfaces hotspots but does not estimate causal impacts on health or migration; integrating net-migration dashboards and health admin data is a natural next step.
