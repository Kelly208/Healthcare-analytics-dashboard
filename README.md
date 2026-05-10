# Healthcare Operational Analytics Dashboard

**End-to-end healthcare analytics pipeline for operational efficiency and patient trend analysis.**

This project demonstrates a comprehensive data engineering and analysis pipeline, starting from raw data generation to interactive visualization. It focuses on deriving actionable business insights from clinic operations, such as identifying peak periods, analyzing service duration, and tracking cancellation impacts.

## Architecture & Data Flow

1.  **Data Generation & Simulation (`src/generate_data.py`)**: 
    Uses the `Faker` library to build realistic clinical data (~50,000 records). It simulates:
    *   Operational timestamps (`check_in_time`, `service_start_time`, `completion_time`) for duration analysis.
    *   Realistic No-Show and Cancellation rates.
    *   Intentional anomalies (missing values, unnormalized text, duplicates) to simulate real-world data ingestion challenges.
2.  **ETL & Data Cleaning (`src/clean_and_load.py`)**: 
    A Pandas-based pipeline that ingests raw CSVs, standardizes schemas, handles null values (imputation), removes duplicates, and standardizes text formats.
3.  **Relational Database (SQLite)**: 
    Cleaned data is loaded into `clinic.db`, forming a robust SQL layer equipped with proper indexing for fast querying.
4.  **Operational Dashboard (`app.py`)**: 
    A modern, minimalist Dark Mode dashboard built with Streamlit and Plotly. Powered by SQLAlchemy queries (`src/queries.py`), it visualizes:
    *   Operational KPIs (Patient Volume, Wait Times, Satisfaction, Monthly Growth).
    *   Appointments by Hour vs Day Heatmap.
    *   Psychologist Workload and Cancellation Rate analysis.

## Dashboard Screenshots

Visualizing the data is a crucial part of this project. Here are some views of the Streamlit dashboard:

### Full Dashboard
![Dashboard Completo](assets/dashboard_completo.png)

### Operational KPIs
![KPIs](assets/kpis.png)

### Peak Periods Heatmap
![Heatmap](assets/heatmap.png)

### Analytics Charts
![Charts](assets/charts.png)

## Sample Business Insights

- Peak appointment activity occurs between 10 AM and 1 PM.
- Cancellation rates increase significantly on Fridays.
- Average wait times are 22% higher during peak periods.

## Setup Instructions

### 1. Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Data Pipeline

First, generate the synthetic data:
```bash
python src/generate_data.py
```

Next, run the cleaning and loading script:
```bash
python src/clean_and_load.py
```

### 3. Launch Dashboard

Run the Streamlit application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

## Technologies

| Area | Technology |
| :--- | :--- |
| **Data Generation** | Python, Faker |
| **Data Processing** | Pandas, Numpy |
| **Database** | SQLite |
| **SQL Layer** | SQLAlchemy |
| **Dashboard** | Streamlit |
| **Visualizations** | Plotly |
