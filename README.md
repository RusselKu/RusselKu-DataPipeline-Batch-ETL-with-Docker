````markdown
# 🧠 PIPELINE_CHAOS_TO_INSIGHTS

A full-stack data pipeline project that extracts, transforms, and visualizes financial data from multiple APIs (e.g., exchange rates, gold prices), using **Airflow**, **MongoDB**, and **Streamlit** — all containerized with **Docker**.

---

## 📁 Project Structure

```bash
PIPELINE_CHAOS_TO_INSIGHTS/
├── dags/
│   ├── exchange_rate_ingestion.py           # ETL for currency exchange rates
│   ├── currency_names_processing.py         # Normalize currency names
│   ├── gold_price_ingestion.py              # ETL for gold prices
│   ├── main_pipeline.py                     # Master DAG orchestration
│   └── utils/
│       ├── api_helpers.py                   # API request handler
│       ├── mongo_utils.py                   # MongoDB helpers
│       └── transform_helpers.py             # Transformation logic (if needed)
│
├── streamlit_app/
│   ├── app.py                               # Main dashboard entry
│   ├── Dockerfile                           # Streamlit container config
│   ├── styles/
│   │   └── custom.css                       # Global CSS styling
│   ├── pages/
│   │   ├── exchange_rates.py               # Visualizes top 10 exchange rates
│   │   ├── currency_names.py               # Currency names + rate mapping
│   │   └── gold_prices.py                  # Gold price visualization
│   └── utils/
│       ├── db.py                           # MongoDB connection for Streamlit
│       └── charts.py                       # Reusable Plotly chart components
│
├── docker-compose.yml                       # Docker orchestration
├── requirements.txt                         # Python dependencies
├── .env                                     # Optional env variables
└── README.md                                # You are here 📄
````

---

## 🚀 How to Run the Project

### 1. ✅ Clone the Repository

```bash
git clone https://github.com/RusselKu/RusselKu-DataPipeline-Batch-ETL-with-Docker.git
cd RusselKu-DataPipeline-Batch-ETL-with-Docker/pipeline_chaos_to_insights/
```

### 2. 👤 Create Airflow Admin User

#### MacOS/Linux:

```bash
docker compose run --rm webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow
```

#### Windows (PowerShell):

```bash
docker-compose run --rm webserver airflow users create `
    --username airflow `
    --firstname Admin `
    --lastname User `
    --role Admin `
    --email admin@example.com `
    --password airflow
```

### 3. 🧱 Build and Run the Services

```bash
docker-compose up --build
```

### 4. 🧭 Connect to MongoDB with Compass

In **MongoDB Compass**, create a new connection using the following URI:

```text
mongodb://root:example@localhost:27019/admin
```

---

## 🌐 Service Access (Default Ports)

| Service       | URL                                            | Notes                 |
| ------------- | ---------------------------------------------- | --------------------- |
| **Airflow**   | [http://localhost:8080](http://localhost:8080) | DAG management UI     |
| **Streamlit** | [http://localhost:8501](http://localhost:8501) | Frontend dashboard    |
| **MongoDB**   | mongodb://localhost:27017                      | Used as main database |

### Airflow Credentials:

* **Username:** `airflow`
* **Password:** `airflow`

---

## 📂 MongoDB Collections

**Database:** `project_db`

| Collection                                 | Description                              |
| ------------------------------------------ | ---------------------------------------- |
| `raw_exchange_rates_api`                   | Raw API data from er-api                 |
| `processed_exchange_rates_api`             | Cleaned latest rates (one document only) |
| `processed_processed_exchange_rates_names` | Currency names (code → full name)        |
| `raw_gold_prices`                          | Raw gold price records                   |
| `processed_gold_prices`                    | Cleaned gold price data                  |

You can connect using:

```bash
docker exec -it pipeline_chaos_to_insights-mongodb-1 mongosh -u root -p example --authenticationDatabase admin
use project_db
show collections
```

---

## 📊 Streamlit Pages Overview

| Page               | Features                                                             |
| ------------------ | -------------------------------------------------------------------- |
| **Exchange Rates** | Top 10 currencies by value, styled table, bar/line/pie charts        |
| **Currency Names** | Full name per currency code + current rate matching                  |
| **Gold Prices**    | Historical and latest gold price trends (optional or in development) |

---

## 🧪 Airflow DAGs Overview

| DAG File                       | Task Description                               |
| ------------------------------ | ---------------------------------------------- |
| `exchange_rate_ingestion.py`   | Extract + transform exchange rates from ER-API |
| `currency_names_processing.py` | Fetch and map currency codes to full names     |
| `gold_price_ingestion.py`      | Extract gold price data                        |
| `main_pipeline.py`             | Master DAG that runs all the above in sequence |

---

## 📌 Requirements

Make sure Docker + Docker Compose is installed.

If you want to install Python dependencies locally:

```bash
pip install -r requirements.txt
```

## 🤝 Credits

Developed by **Russel Ku** and enhanced with a custom multi-service pipeline for data visualization and orchestration.

---

## 🧠 License

MIT License — feel free to use, fork, and contribute!

```
