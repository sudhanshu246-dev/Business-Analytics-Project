# Sales & Profit Analytics Dashboard

MCA Business Analytics project: Sales and Profit Analysis using Excel, SQL (MySQL) and a Python (Streamlit) dashboard.

## Features
- Excel workbook: data cleaning checks, formula-based KPIs, summary tables (PivotTable equivalents) and charts
- MySQL: normalized schema (customers, products, orders, order_details), import script and 10 analysis queries
- Dashboard: KPI cards, monthly trend, category/region analysis, top 10 products and customers, filters (date, region, category), data table with CSV download, data quality summary and auto insights
- Data source: MySQL first, automatic fallback to `data/sample_sales.csv`

## Project Structure
```
Sales & Profit Analytics Dashboard/
├── app.py                         # Streamlit dashboard
├── config/db_config.py            # MySQL connection (reads .env)
├── utils/data_loader.py           # MySQL/CSV loading and cleaning
├── utils/insights.py              # Automatic business insights
├── data/sample_sales.csv          # Dataset (1000 orders)
├── data/Sales_Profit_Analysis.xlsx  # Excel analysis workbook
├── sql/create_db.sql              # Database and tables
├── sql/load_data.sql              # Import CSV and fill tables
├── sql/analysis_queries.sql       # Business analysis queries
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1) Virtual environment and dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2) MySQL database (MySQL 8.0+)
1. Run `sql/create_db.sql`.
2. Open `sql/load_data.sql`, import `data/sample_sales.csv` into `sales_staging` (Workbench import wizard or the LOAD DATA option in the script), then run the rest of the script.
3. The last query of `load_data.sql` should show: 1000 orders, 150 customers, 25 products, total sales 1124204.49, total profit 585082.25.
4. Run queries from `sql/analysis_queries.sql` as needed.

### 3) Environment variables
Copy `.env.example` to `.env` and set `DB_USER`, `DB_PASSWORD` (and host/port/name if different). Never share or commit `.env`.

### 4) Run the dashboard
```bash
streamlit run app.py
```
Opens at http://localhost:8501. The sidebar shows the active data source (MySQL database or CSV file). Without MySQL, the dashboard works from the CSV.

## Excel workbook
`data/Sales_Profit_Analysis.xlsx` sheets: Charts, Sales_Data (with formula columns), Data_Cleaning, KPI_Summary, Summary_Tables. To add a native PivotTable: select `Sales_Data!A1:R1001` > Insert > PivotTable.

## Data notes
- Totals (all data): Sales 1,124,204.49, Profit 585,082.25, Margin 52.04%, 1000 orders, 150 customers. Excel, SQL and dashboard use the same figures.
- In the raw CSV, most CustomerIDs have several different names. One name per ID is used everywhere (most frequent name, ties alphabetical).
- `products.unit_cost` is derived as (SalesAmount - Profit) / Quantity because the CSV has no cost column.
- The dataset is synthetic; the 52% margin is higher than typical real businesses.
