from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task

# Import functions from each DAG module
from CurrenlyExchangeRates_ingestion import (
    extract_exchange_rates as extract_currency_rates,
    transform_exchange_rates as transform_currency_rates,
    update_currency_names
)
from ExchangeRate_ingestion import (
    extract_exchange_rates as extract_api_rates,
    transform_exchange_rates as transform_api_rates  # This transform overwrites all rates
)
from Gold_Exchangeingestion import (
    extract_gold_prices,
    transform_gold_prices
)
from load_mongo import merge_final_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    "financial_data_pipeline",
    default_args=default_args,
    description="Orchestrates complete financial data pipeline including currency names, exchange rates, and gold prices",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["financial", "pipeline"]
) as dag:

    # 1. Currency Names Extraction and Transformation
    @task(task_id="extract_currency_names")
    def extract_currency_names_task(ti=None):
        extract_currency_rates(ti=ti)

    @task(task_id="transform_currency_names")
    def transform_currency_names_task(ti=None):
        transform_currency_rates(ti=ti)

    # 2. Update full currency names dictionary task
    @task(task_id="update_currency_names")
    def update_currency_names_task():
        update_currency_names()

    # 3. Exchange Rates Extraction and Transformation (full currencies, overwrite)
    @task(task_id="extract_exchange_rates")
    def extract_exchange_rates_task(ti=None):
        extract_api_rates(ti=ti)

    @task(task_id="transform_exchange_rates")
    def transform_exchange_rates_task(ti=None):
        transform_api_rates(ti=ti)  # This transform overwrites the full rates document

    # 4. Gold Prices Extraction and Transformation
    @task(task_id="extract_gold_prices")
    def extract_gold_prices_task(ti=None):
        extract_gold_prices(ti=ti)

    @task(task_id="transform_gold_prices")
    def transform_gold_prices_task(ti=None):
        transform_gold_prices(ti=ti)

    # 5. Final consolidation of all financial data
    @task(task_id="consolidate_financial_data")
    def consolidate_financial_data_task():
        merge_final_data()

    # Task instances
    t1 = extract_currency_names_task()
    t2 = transform_currency_names_task()
    t3 = update_currency_names_task()
    t4 = extract_exchange_rates_task()
    t5 = transform_exchange_rates_task()
    t6 = extract_gold_prices_task()
    t7 = transform_gold_prices_task()
    t8 = consolidate_financial_data_task()

    # Task dependencies / orchestration
    t1 >> t2 >> t3  # Currency names extraction -> transform -> update dictionary
    t4 >> t5        # Exchange rates extraction -> transform (overwrite all rates)
    t6 >> t7        # Gold prices extraction -> transform
    [t3, t5, t7] >> t8  # Consolidate after all processed data
