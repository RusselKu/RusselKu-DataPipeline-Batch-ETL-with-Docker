from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from utils.mongo_utils import get_raw_collection, get_processed_collection  
from utils.api_helpers import fetch_api_data
import bson  # Para sanitizar ObjectId en XCom

DB_NAME = "project_db"
SOURCE_NAME = "gold_prices"
API_URL = "https://api.nbp.pl/api/cenyzlota/last/30/?format=json"

def clean_object_ids(obj):
    if isinstance(obj, dict):
        return {k: clean_object_ids(v) for k, v in obj.items() if not isinstance(v, bson.ObjectId)}
    elif isinstance(obj, list):
        return [clean_object_ids(v) for v in obj]
    else:
        return obj

def extract_gold_prices(ti):
    try:
        data = fetch_api_data(API_URL)
        if not data or not isinstance(data, list):
            raise ValueError("Datos de API no tienen el formato esperado")
        
        collection = get_raw_collection(DB_NAME, SOURCE_NAME)
        record = {
            "data": data,
            "timestamp": datetime.now(),
            "source": "nbp-api",
            "metadata": {
                "time_range": f"{data[0]['data']} to {data[-1]['data']}",
                "num_records": len(data),
                "status": "raw",
                "currency": "PLN"
            }
        }
        collection.insert_one(record)
        ti.xcom_push(key="num_records", value=len(data))
    except Exception as e:
        raise ValueError(f"Error en extracción de precios de oro: {str(e)}")

def transform_gold_prices(ti):
    try:
        raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
        processed_collection = get_processed_collection(DB_NAME, SOURCE_NAME)

        latest = raw_collection.find_one(sort=[("_id", -1)])
        if not latest or "data" not in latest:
            raise ValueError("No hay datos crudos válidos para transformar")

        raw_data = latest["data"]
        time_series = []

        for i, entry in enumerate(raw_data):
            daily_change = None
            if i > 0:
                daily_change = round(entry["cena"] - raw_data[i-1]["cena"], 4)

            time_series.append({
                "date": entry["data"],
                "price_pln": entry["cena"],
                "daily_change": daily_change,
                "day_of_week": datetime.strptime(entry["data"], "%Y-%m-%d").strftime("%A")
            })

        transformed = {
            "time_series": time_series,
            "metadata": {
                "source": latest["source"],
                "currency": "PLN",
                "processed_at": datetime.now().isoformat(),
                "stats": {
                    "initial_price": raw_data[0]["cena"],
                    "final_price": raw_data[-1]["cena"],
                    "price_change": round(raw_data[-1]["cena"] - raw_data[0]["cena"], 4),
                    "avg_price": round(sum(e["cena"] for e in raw_data) / len(raw_data), 4)
                }
            }
        }

        processed_collection.insert_one(transformed)
        ti.xcom_push(key="transformed_data", value=clean_object_ids(transformed))
    except Exception as e:
        raise ValueError(f"Error en transformación de precios de oro: {str(e)}")

with DAG(
    "gold_price_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "commodities"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False
    }
) as dag:
    extract = PythonOperator(
        task_id="extract_gold_prices",
        python_callable=extract_gold_prices,
        doc_md="""## Extracción de precios del oro
        - Fuente: Banco Nacional de Polonia (NBP)
        - Datos: Últimos 30 días
        - Moneda: PLN
        - Guardado en: raw_gold_prices"""
    )

    transform = PythonOperator(
        task_id="transform_gold_prices",
        python_callable=transform_gold_prices,
        doc_md="""## Transformación a serie temporal
        - Calcula cambios diarios
        - Añade metadatos estadísticos
        - Estructura optimizada para análisis
        - Guardado en: processed_gold_prices"""
    )

    extract >> transform
