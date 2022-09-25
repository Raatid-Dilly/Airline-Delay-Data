import os
import pandas as pd
import zipfile
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq
from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import  BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", '/opt/airflow/')
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "flight_delay_dataset")
zip_name = 'all_year_flights.zip'
parquet_name = "all_years_flights.parquet"
dest_path = f"{AIRFLOW_HOME}/{parquet_name}"
url = 'https://www.transtats.bts.gov/OT_Delay/ot_delaycause1_DL.aspx?8n4=9ur4r%20Brn4z106u%20or69rr0%20FHDHF%20NaQ%20FHFJK'

def preclean_and_format_to_parquet(src_file, dest_path):
    with zipfile.ZipFile(src_file, 'r') as file:
        file.extractall()
        file_name = file.namelist()[0]

    flights_df = pd.read_csv(file_name)
    date =  pd.to_datetime(flights_df[['year', 'month']].assign(DAY=1))
    flights_df['year'] = date.dt.to_period('Y')
    flights_df['month'] = date.dt.month
    flights_df['city'] = flights_df['airport_name'].apply(lambda x: x.split(',')[0])
    flights_df['state'] = flights_df["airport_name"].apply(lambda x: x.split(',')[1].split(':')[0].strip())
    flights_df['airport_name'] = flights_df['airport_name'].apply(lambda x: x.split(':')[1])
    cols = flights_df.columns.tolist()
    cols = cols[:2] + cols[-2:] + cols[2:-2]
    flights_df = flights_df[cols]
    flights_df.to_csv(f"./{file_name}", index=False)
    table = pv.read_csv(f"./{file_name}")
    pq.write_table(table, dest_path)

def upload_pq_file_to_gcs(bucket_name, source_file_name, destination_blob_name):

    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

default_args={
    'owner': 'airflow',
    'depends_on_past': 'False',
    'retries': 1
}

with DAG(
    dag_id='airplane_flight_delays_dag',
    start_date=days_ago(1),
    schedule_interval="@once",
    catchup=False,
    tags=['flight_delays']

) as dag:
    download_flight_data_task = BashOperator(
        task_id="download_flight_data_task",
        bash_command=f"wget -q -O {AIRFLOW_HOME}/{zip_name} {url} --no-check-certificate"
    )

    format_csv_file_to_parquet_task = PythonOperator(
        task_id='format_csv_file_to_parquet_task',
        python_callable=preclean_and_format_to_parquet,
        op_kwargs={
            "src_file": f"{AIRFLOW_HOME}/{zip_name}",
            "dest_path": dest_path
        }
    )

    upload_pq_file_to_gcs_task = PythonOperator(
        task_id="upload_pq_file_to_gcs_task",
        python_callable=upload_pq_file_to_gcs,
        op_kwargs={
            'bucket_name': BUCKET,
            "source_file_name": dest_path,
            "destination_blob_name": f"raw/flights/{parquet_name}"
        }
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource = {
            "tableReference":{
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "flights_delay_external_table"
            },
            "externalDataConfiguration":{
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/*"]
            }
        }
    )

    remove_files_task = BashOperator(
        task_id="remove_files_task",
        bash_command=f"cd {AIRFLOW_HOME} && rm *.csv *.parquet"
    )

    download_flight_data_task >> format_csv_file_to_parquet_task >> upload_pq_file_to_gcs_task >> bigquery_external_table_task >> remove_files_task