from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from utils.mongo_utils import get_raw_collection, get_processed_collection
from utils.api_helpers import fetch_api_data
import bson  # Fix for detecting ObjectId

# Centralized config
DB_NAME = "project_db"
SOURCE_NAME = "exchange_rates_api"

def extract_exchange_rates(ti):
    """Extracts exchange rates from er-api and saves to raw collection"""
    url = "https://open.er-api.com/v6/latest/USD"
    
    try:
        data = fetch_api_data(url)
        if not data.get("rates"):
            raise ValueError("API data does not contain exchange rates")

        collection = get_raw_collection(DB_NAME, SOURCE_NAME)
        record = {
            "data": data,
            "timestamp": datetime.now(),
            "source": "er-api",
            "metadata": {
                "base_currency": data.get("base_code", "USD"),
                "num_rates": len(data.get("rates", {})),
                "status": "raw"
            }
        }
        collection.insert_one(record)
        ti.xcom_push(key="num_rates", value=len(data.get("rates", {})))

    except Exception as e:
        raise ValueError(f"Extraction error: {str(e)}")

def clean_object_ids(obj):  # Clean ObjectIds before using XCom
    if isinstance(obj, dict):
        return {k: clean_object_ids(v) for k, v in obj.items() if not isinstance(v, bson.ObjectId)}
    elif isinstance(obj, list):
        return [clean_object_ids(v) for v in obj]
    else:
        return obj

def transform_exchange_rates(ti):
    """Processes data and saves to processed collection, overwriting previous"""
    try:
        raw_collection = get_raw_collection(DB_NAME, SOURCE_NAME)
        processed_collection = get_processed_collection(DB_NAME, SOURCE_NAME)

        latest = raw_collection.find_one(sort=[("_id", -1)])
        if not latest or "data" not in latest:
            raise ValueError("No valid raw data to transform")

        rates_data = latest["data"]

        transformed = {
            "base_currency": rates_data.get("base_code", "USD"),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "rates": {
                currency: {
                    "rate": rate,
                    "last_updated": rates_data.get("time_last_update_utc")
                }
                for currency, rate in rates_data["rates"].items()  
            },
            "metadata": {
                "provider": rates_data.get("provider", "er-api"),
                "processed_at": datetime.now().isoformat(),
                "source": latest["source"]
            }
        }

        # Overwrite the document instead of insert (to avoid duplicates)
        processed_collection.replace_one(
            {"_id": "latest_rates"},
            transformed,
            upsert=True
        )

        cleaned = clean_object_ids(transformed)
        ti.xcom_push(key="transformed_data", value=cleaned)

    except Exception as e:
        raise ValueError(f"Transformation error: {str(e)}")

with DAG(
    "exchange_rate_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "currency"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False
    }
) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_exchange_rates,
        doc_md="""## Exchange Rate Extraction
        - Source: open.er-api.com
        - Base currency: USD
        - Saves data to: raw_exchange_rates_api"""
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_exchange_rates,
        doc_md="""## Data Transformation
        - Processes all currencies returned by the API
        - Saves the latest rates document, overwriting previous data
        - Saves data to: processed_exchange_rates_api"""
    )

    extract >> transform
