# Data sources — housing-affordability

This document lists the prioritized StatCan and CMHC datasets used for the project's housing affordability indicators, the geography and time coverage, key variables, and how each dataset will be downloaded.

Scope: 6 indicators (CMA-level) kept small and actionable.

1) Median household (total) income (Census)
- Provider: Statistics Canada
- Geography level: Census Metropolitan Area (CMA)
- Time range: Census years (e.g., 2016, 2021). Use the latest census release.
- Key variables: `CMA name` (GEO_NAME or GEO), `REF_DATE` (year), `Median total income` (label differs by table)
- Download method: StatCan Census table page (use the table viewer's "Download" → CSV). Recommended table: "Median total income of economic families and census families" (search StatCan census profile tables). Programmatic option: use StatCan Web Data Service `getFullTableDownloadCSV` with the table Product ID (PID) found on the table page. See: https://www.statcan.gc.ca/en/developers/wds

2) Annual population estimates (mid-year)
- Provider: Statistics Canada
- Geography level: CMA
- Time range: annual (e.g., 2000–present)
- Key variables: `CMA name`, `REF_DATE` (date/year), `Population`
- Download method: StatCan table viewer or WDS. Example table pages: search "Population and dwelling counts" or "Estimates of population" on StatCan and use the CSV download or the WDS `getFullTableDownloadCSV` endpoint.

3) Unemployment rate (Labour Force Survey)
- Provider: Statistics Canada
- Geography level: CMA (monthly)
- Time range: monthly, last ~10–20 years (or as available)
- Key variables: `CMA name`, `REF_DATE` (YYYY-MM), `Unemployment rate`, `Labour force`, `Employed`, `Unemployed`
- Download method: StatCan table viewer (Labour Force Survey by CMA) or WDS. Search for "Labour Force Survey CMA unemployment rate" on StatCan and download CSV from the table page or use WDS.

4) Consumer Price Index (CPI) — All-items (for real adjustments)
- Provider: Statistics Canada
- Geography level: Canada / province (use national CPI to deflate incomes)
- Time range: monthly (long series)
- Key variables: `REF_DATE`, `CPI_all_items`, `index_value`
- Download method: StatCan time series pages or WDS. Example product: Consumer Price Index (CPI) — All-items (search StatCan for "CPI, all-items, Canada"). Download CSV from table page or use WDS endpoints.

5) Rental Market Survey — median rents and vacancy rates
- Provider: Canada Mortgage and Housing Corporation (CMHC)
- Geography level: CMA (primary rental market)
- Time range: annual / quarterly (as published)
- Key variables: `CMA name`, `Period`, `Median rent` (by bedroom), `Vacancy rate`
- Download method: CMHC Rental Market Data tables. Page: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market — open the specific RMS table for "median rents" or "vacancy rates" and click CSV / Excel download. CMHC often provides direct CSV/Excel links per table.

6) Housing starts (by type)
- Provider: Canada Mortgage and Housing Corporation (CMHC)
- Geography level: CMA (monthly/annual)
- Time range: monthly/annual (use 10+ years where available)
- Key variables: `CMA name`, `Period`, `Starts_total`, `Starts_by_type` (single-detached, multi-unit)
- Download method: CMHC Housing Market Data tables. Page: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/housing-market-data — select "Housing starts" and download CSV/Excel for CMA-level series.

Notes on provider access and choosing exact tables:
- Statistics Canada: most useful programmatic entry point is the StatCan Open Data portal (https://www.statcan.gc.ca/en/developers/wds) and the table download endpoints. Each table page provides a CSV download link and an API-friendly endpoint. When automating, identify the table ID on StatCan and use the table's CSV export URL or the StatCan REST endpoints.
- CMHC: data are published in the CMHC Housing Market Information Portal and often include direct CSV downloads or Excel files per report. Identify the RMS and Housing Starts pages for CMA-level exports and use the CSV links or download programmatically.
- If an exact table ID is required for StatCan, locate the table on statcan.gc.ca and copy the CSV export URL; the ingest script below accepts direct CSV URLs or local filenames.

Minimal local storage layout (used by ingest plan):
- `data/raw/` — raw CSVs downloaded from StatCan/CMHC (store original filenames)
- `data/processed/` — cleaned, standardised indicator tables (CMA, date, variable, value, unit)

Acceptable download methods (ranked):
1. Programmatic CSV download (preferred): direct CSV link or StatCan API
2. API JSON endpoints (if available) parsed into tabular form
3. Manual download (last resort) — store CSV/Excel into `data/raw/` with descriptive filenames

---

Ingest plan (script or notebook cell plan): see `notebooks/00_ingest_plan.ipynb` for a cell-by-cell plan and code skeleton. The notebook contains:
- Setup: create folders, imports
- Source list: mapping dataset name → provider → download URL (CSV) or instructions
- Download cell: `download_csv(url, path)` function and loop to fetch and save raw files
- Load & standardize: read raw CSVs, select and rename key columns to canonical column set (`cma`, `date`, `variable`, `value`, `unit`)
- Save processed: write per-indicator CSVs to `data/processed/`
- Simple QA: row counts, date ranges, sample values

Exact download examples and programmatic snippets

- StatCan full-table CSV (programmatic):

	Use the WDS `getFullTableDownloadCSV` endpoint with the table PID (product id). Example (replace PID):

	https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/98-10-0009-01/en

	To find the PID for a table: open the StatCan table viewer page for the table and note the PID in the URL (pid=...). You can also use the WDS methods to list cubes and find PIDs. See: https://www.statcan.gc.ca/en/developers/wds

- CMHC direct CSV (example):

	CMHC table pages include CSV/Excel download links. Example landing pages:

	- Rental Market Data: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market
	- Housing Market Data (starts): https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/housing-market-data

	On each CMHC table page click the relevant table and use the CSV/Excel download action (the ingest notebook accepts direct CSV URLs or saved local files).
