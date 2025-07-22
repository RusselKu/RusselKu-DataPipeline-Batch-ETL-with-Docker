from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from utils.mongo_utils import get_raw_collection, get_processed_collection
from utils.api_helpers import fetch_api_data
import bson


DB_NAME = "project_db"
SOURCE_NAME = "exchange_rates"
TARGET_CURRENCIES = ["usd", "eur", "mxn", "jpy", "gbp"]

def extract_exchange_rates(ti):
    """Extrae tasas de cambio y guarda en MongoDB (raw)"""
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json"
    
    try:
        data = fetch_api_data(url)
        collection = get_raw_collection(DB_NAME, SOURCE_NAME)
        record = {
            "data": data,
            "timestamp": datetime.now(),
            "source": "currency-api",
            "metadata": {
                "num_currencies": len(data),
                "status": "raw"
            }
        }
        collection.insert_one(record)
        ti.xcom_push(key="num_currencies", value=len(data))

    except Exception as e:
        raise ValueError(f"Error en extracción: {str(e)}")

def clean_object_ids(obj):
    if isinstance(obj, dict):
        return {k: clean_object_ids(v) for k, v in obj.items() if not isinstance(v, bson.ObjectId)}
    elif isinstance(obj, list):
        return [clean_object_ids(v) for v in obj]
    else:
        return obj

def transform_exchange_rates(ti):
    """Transforma datos y guarda en colección processed"""
    try:
        raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
        processed_collection = get_processed_collection(DB_NAME, SOURCE_NAME)

        latest = raw_collection.find_one(sort=[("_id", -1)])
        if not latest:
            raise ValueError("No hay datos crudos para transformar")

        transformed = {
            "currencies": {
                code: {
                    "name": latest["data"][code],
                    "code": code.upper()
                }
                for code in TARGET_CURRENCIES
                if code in latest["data"]
            },
            "stats": {
                "total_currencies": len(latest["data"]),
                "processed_at": datetime.now().isoformat(),
                "source": latest["source"]
            }
        }

        processed_collection.insert_one(transformed)

        cleaned = clean_object_ids(transformed)
        ti.xcom_push(key="transformed_data", value=cleaned)

    except Exception as e:
        raise ValueError(f"Error en transformación: {str(e)}")

def update_currency_names():
    raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
    processed_names_col = get_processed_collection(DB_NAME, "processed_exchange_rates_names")

    latest = raw_collection.find_one(sort=[("_id", -1)])
    if not latest:
        raise ValueError("No hay datos crudos para nombres")

    full_names_dict = latest["data"] 

    processed_names_col.replace_one(
        {"_id": "currency_names"},
        {"_id": "currency_names", "currencies": full_names_dict, "updated_at": datetime.utcnow()},
        upsert=True
    )
    print("Nombres de monedas actualizados correctamente")

with DAG(
    "exchange_rates_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "currency"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5)
    }
) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_exchange_rates,
        doc_md="""Extrae tasas de cambio actuales:
        - Usa API pública de currencies
        - Guarda en raw_exchange_rates"""
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_exchange_rates,
        doc_md="""Filtra monedas clave:
        - Procesa solo USD, EUR, MXN, JPY, GBP
        - Estructura datos para dashboard"""
    )

    update_names = PythonOperator(
        task_id="update_currency_names",
        python_callable=update_currency_names,
        doc_md="Actualiza diccionario completo de nombres de monedas en processed_exchange_rates_names"
    )

    extract >> transform >> update_names
