# Data sources (plain language)

This project uses a small set of public Canadian datasets. Each source is listed with the table ID, what it measures, and how to download it. These are the inputs used to build the Affordability Stress Index (ASI).

If you are not a data specialist, you can treat this file as a shopping list: each item is something we need in `data/raw/` before the notebooks will run.

## 1) Median household income (Census)
- Provider: Statistics Canada
- Table ID (PID): 98-10-0009-01
- Geography: Census Metropolitan Area (CMA)
- What it tells us: typical household income for each metro.
- Download: https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/98-10-0009-01/en

## 2) Population estimates (mid-year)
- Provider: Statistics Canada
- Table ID (PID): 17-10-0135-01
- Geography: CMA
- What it tells us: how many people live in each metro over time.
- Download: https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/17-10-0135-01/en

## 3) Unemployment rate (Labour Force Survey)
- Provider: Statistics Canada
- Table ID (PID): 14-10-0294-01
- Geography: CMA (monthly)
- What it tells us: local job market conditions.
- Download: https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/14-10-0294-01/en

## 4) Consumer Price Index (CPI), all-items
- Provider: Statistics Canada
- Table ID (PID): 18-10-0004-01
- Geography: Canada (national CPI)
- What it tells us: inflation over time so we can compare dollars across years.
- Download: https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/18-10-0004-01/en

## 5) Rental Market Survey (rents and vacancies)
- Provider: Canada Mortgage and Housing Corporation (CMHC)
- Geography: CMA
- What it tells us: median rents by bedroom size and vacancy rates.
- Landing page: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market
- Download notes: CMHC often posts tables as Excel files. Save them to `data/raw/` with descriptive names.

## 6) Housing starts
- Provider: CMHC
- Geography: CMA
- What it tells us: how much new housing supply is being built.
- Landing page: https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/housing-market-data
- Download notes: select the CMA-level housing starts table and save the CSV/Excel to `data/raw/`.

## How to download (simple options)

Ranked by convenience:

1. Direct CSV download from StatCan using the links above.
2. StatCan WDS API if you want to automate downloads.
3. Manual download from CMHC landing pages (still required for some tables).

## Where files go

- Raw files: `data/raw/`
- Cleaned outputs: `data/processed/`

If a download is missing, the ingest notebooks will stop and tell you which file to add.

## Notes on reliability

- StatCan WDS sometimes changes, so we keep the table IDs in one place here.
- CMHC file URLs can change each release, so the landing pages are the safest reference.

For the step-by-step ingest plan, see `notebooks/00_ingest_plan.ipynb`.
