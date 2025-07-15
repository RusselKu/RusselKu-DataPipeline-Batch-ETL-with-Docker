# ETL Pipeline: Airflow + MongoDB + Streamlit

Dockerized batch pipeline that:

1. **Ingests** data from public APIs (Airflow)  
2. **Stores** raw/processed data in MongoDB  
3. **Visualizes** insights via Streamlit  

▶ **Services**:  
- Airflow @ `localhost:8080`  
- MongoDB @ `27017`  
- Streamlit @ `localhost:8501`  

`docker-compose up -build` to start.  