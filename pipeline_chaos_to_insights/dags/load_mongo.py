from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from utils.mongo_utils import get_processed_collection, get_final_collection

@task
def merge_final_data(ti):
    try:
        final_output = get_final_collection("project_db", "combined_data")
        
        exchange_rates = get_processed_collection("project_db", "exchange_rates").find_one(sort=[("_id", -1)])
        exchange_rates_api = get_processed_collection("project_db", "exchange_rates_api").find_one(sort=[("_id", -1)])
        gold_prices = get_processed_collection("project_db", "gold_prices").find_one(sort=[("_id", -1)])

        missing_sources = []
        if not exchange_rates: missing_sources.append("exchange_rates")
        if not exchange_rates_api: missing_sources.append("exchange_rates_api")
        if not gold_prices: missing_sources.append("gold_prices")

        if missing_sources:
            raise ValueError(f"Datos faltantes de las fuentes: {', '.join(missing_sources)}")

        merged_data = {
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "sources": ["exchange_rates", "exchange_rates_api", "gold_prices"],
                "update_frequency": "daily",
                "processing_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "financial_data": {
                "currency_data": {
                    "names": exchange_rates.get("currencies", {}),
                    "rates": exchange_rates_api.get("rates", {}),
                    "base_currency": exchange_rates_api.get("base_currency", "USD")
                },
                "commodity_data": {
                    "gold": {
                        "prices": gold_prices.get("time_series", [])[-30:], 
                        "currency": "PLN",
                        "stats": gold_prices.get("metadata", {}).get("stats", {})
                    }
                }
            },
            "stats": {
                "num_currencies": len(exchange_rates.get("currencies", {})),
                "num_gold_records": len(gold_prices.get("time_series", []))
            }
        }

        result = final_output.replace_one(
            {"metadata.sources": merged_data["metadata"]["sources"]},
            merged_data,
            upsert=True
        )

        ti.xcom_push(key="merged_record_id", value=str(result.upserted_id if result.upserted_id else merged_data.get("_id", "unknown")))
        return "Datos combinados exitosamente"
        
    except Exception as e:
        raise ValueError(f"Error al combinar datos: {str(e)}")

with DAG(
    "load_combined_data",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["load", "combined"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=15),
        "depends_on_past": True  
    }
) as dag:
    merge_task = merge_final_data()
