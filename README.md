````markdown
# 🚀 ETL Pipeline: Airflow + MongoDB + Streamlit

A fully dockerized batch ETL pipeline that:
- ⬇️ **Ingests** data from multiple public APIs via Apache Airflow
- 🗃️ **Stores** both raw and processed data in MongoDB
- 📊 **Visualizes** results using interactive Streamlit dashboards

## 📌 Project Overview

This project demonstrates a modular, scalable data pipeline architecture using Airflow for orchestration, MongoDB for data persistence, and Streamlit for visualization. It is ideal for educational and production-ready use cases where asynchronous data ingestion and fast dashboarding are required.

---

## 🌐 APIs Used

- 💱 **Exchange Rate API (Fawaz Ahmed)**  

  Provides exchange rates for hundreds of currencies in JSON format.

- 🪙 **Gold Price API (Metals API clone)**  
  ↪ Simulated API for retrieving historical gold prices.

---

## 🆚 Why MongoDB over PostgreSQL?

MongoDB was chosen for its schema flexibility and native support for nested JSON documents — making it ideal for storing hierarchical data from external APIs without the need for schema migrations. It also allows rapid prototyping and dynamic visualizations in Streamlit.

---

## 🐳 How to Launch Services

From the project root:

```bash
docker-compose up --build
````

This will launch the following services:

| Service       | URL                                            |
| ------------- | ---------------------------------------------- |
| Airflow UI    | [http://localhost:8080](http://localhost:8080) |
| Streamlit App | [http://localhost:8501](http://localhost:8501) |
| MongoDB       | localhost:27017 (internal)                     |

---

## 📅 How to Trigger DAGs

1. Open the Airflow UI at:
   → [http://localhost:8080](http://localhost:8080)

2. Use the toggle switch to **enable DAGs** like:

   * `CurrenlyExchangeRates_ingestion`
   * `Gold_Exchangeingestion`
   * `main_pipeline`

3. Click the ▶️ **Trigger DAG** button.

4. Navigate to the "Graph View" or "Tree View" to check execution flow.

---

## 🪵 How to View Airflow Logs

* In the Airflow UI, select a DAG run.
* Click on any task (e.g., `extract_exchange_rates`).
* Then click **"View Log"** to inspect output, errors, or XComs.

---

## 📈 Open the Streamlit Dashboard

Once services are running:

→ Visit [http://localhost:8501](http://localhost:8501)

You’ll see multiple dashboards for:

* 📉 **Exchange Rate Trends**
* 🪙 **Gold Price Visualizations**
* 🌍 **Currency Metadata**

Each dashboard allows interactive filtering and plot generation in real-time.

---

## 🔄 How XCom is Used

Apache Airflow’s **XCom** (cross-communication) mechanism is used to:

* Pass processed exchange rate results between tasks.
* Share MongoDB insertion results across tasks for logging and conditional logic.
* Track DAG execution metadata that can be surfaced in dashboards.

---

## 📂 Folder Structure

```bash
pipeline_chaos_to_insights/
├── dags/                       # All Airflow DAG definitions
├── utils/                      # Shared ETL helpers (Mongo, APIs, transforms)
├── streamlit_app/             # Dashboards, pages, styling
│   ├── pages/
│   ├── utils/
│   ├── styles/
│   └── app.py
├── Documentation-Initialization/
│   └── README.md               # DAG-level doc with images (if needed)
├── docker-compose.yml         # Defines all services
├── Dockerfile                 # Airflow base Docker image
└── .env                       # Your local secrets (excluded by .gitignore)
```

---

## ✅ To-Do / Coming Soon

* [ ] Add unit tests for pipeline components
* [ ] Include screenshots of dashboards
* [ ] Add support for PostgreSQL as optional DB backend
* [ ] CI/CD with GitHub Actions

---

Built with ❤️ by [Russel Ku](https://github.com/RusselKu)

