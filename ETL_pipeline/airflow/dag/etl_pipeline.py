import pendulum
import datetime
# from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.providers.standard.operators.python import PythonOperator
from airflow.decorators import task_group
from airflow.decorators import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# NOTE: avoid importing heavy native libraries (pandas, numpy, etc.) or
# local ETL modules at module import (DAG parse) time. Import them inside
# task callables so Airflow's DAG parser doesn't load native extensions
# and risk fork-related crashes on macOS.

# Silver Layer: Transform tables and merge data prepraring for gold layer
@task
def task_read(table_name, **kwargs):
    # Import DB reader inside the task to avoid importing at DAG-parse time
    from etl_pipeline.read_data_from_db import read_sql_table

    chunk_files = []
    for i, chunk_df in enumerate(read_sql_table(table_name, schema='bronze')):
        print(f"Chunk {i+1} with {len(chunk_df)} rows")
        file_path = f"/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/data/silver_data/{table_name}_part{i+1}.parquet"
        chunk_df.to_parquet(file_path)
        chunk_files.append(file_path)
    return chunk_files

@task
def task_drop_nulls(chunk_files, **kwargs):
    # Import heavy libs and transforms inside the task
    import pandas as pd
    from etl_pipeline.silver_layer.cleaning_data import transform_drop_nulls

    new_file_paths = []
    for file_path in chunk_files:
        df = pd.read_parquet(file_path)
        df = transform_drop_nulls(df)
        df.to_parquet(file_path)
        new_file_paths.append(file_path)
    return new_file_paths

@task
def task_time_cols(file_paths, **kwargs):
    import pandas as pd
    from etl_pipeline.silver_layer.cleaning_data import transform_cols

    new_file_paths = []
    for file_path in file_paths:
        df = pd.read_parquet(file_path)
        df = transform_cols(df)
        df.to_parquet(file_path)
        new_file_paths.append(file_path)
    return new_file_paths

@task
def task_remove_duplicates(file_paths, **kwargs):
    import pandas as pd
    from etl_pipeline.silver_layer.cleaning_data import transform_remove_duplicates

    new_file_paths = []
    for file_path in file_paths:
        df = pd.read_parquet(file_path)
        df = transform_remove_duplicates(df)
        df.to_parquet(file_path)
        new_file_paths.append(file_path)
    return new_file_paths

@task
def task_merging(chunk_files):
    """
    """
    import pandas as pd
    from etl_pipeline.silver_layer.merging import transform_merge_dfs
    from etl_pipeline.silver_layer.load_to_silver import load_to_silver

    df2 = pd.read_parquet("/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/data/silver_data/airports_geolocation_part1.parquet")
    right_cols = ["COUNTRY"]
    left_cols = [
            "Delay_Carrier", "Delay_Weather",
            "Delay_NAS", "Delay_Security",
            "Delay_LastAircraft"
        ]
    
    for idx, file_path in enumerate(chunk_files):
        df1 = pd.read_parquet(file_path)
        
        # Merge lần 1: Merge bảng Us_Flights_2023 và Airports_Geolocation_Dep
        df = transform_merge_dfs(
            df_left=df1,
            left_cols=left_cols,
            df_right=df2,
            right_cols=right_cols,
            on=None,
            left_on='Dep_Airport',
            right_on='IATA_CODE_dep',
            how='left',
            suffix='_dep'
        )
        # Merge lần 2: Merge bảng Us_Flights_2023 và Airports_Geolocation_Arr
        df = transform_merge_dfs(
            df_left=df,
            left_cols=[],
            df_right=df2,
            right_cols=[],
            on=None,
            left_on='Arr_Airport',
            right_on='IATA_CODE_arr',
            how='left',
            suffix='_arr'
        )
        df.to_parquet(f"/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/data/silver_data/us_flights_clean_part{idx+1}.parquet")
        load_to_silver(df, table_name='us_flights_clean')
    
def load_sql_file(path):
    with open(path, 'r') as f:
        return f.read()
    
def atoti_task():
    from etl_pipeline.ssas_process.ssas import ssas_pipeline
    return ssas_pipeline()

def create_transform_group(table_name):
    with TaskGroup(group_id=f"transform_table_{table_name}") as tg:
        chunk_files = task_read(table_name)
        chunk_files = task_drop_nulls(chunk_files)
        chunk_files = task_time_cols(chunk_files)
        chunk_files = task_remove_duplicates(chunk_files)
    if table_name == "US_flights_2023":
        return tg, chunk_files
    else:
        return tg

@dag (
    dag_id="ETL_Pipeline",
    # schedule="0 0 * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def etl_pipeline():
    # Database Setup
    create_schema = SQLExecuteQueryOperator(
        task_id="create_schema",
        conn_id="usflights_connection",
        sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/sql/create_schema.sql')
    )
    
    @task_group(group_id="create_tables")
    def create_tables_group():
        create_silver_tables = SQLExecuteQueryOperator(
            task_id='create_silver_tables',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/sql/ddl_silver.sql'),
        )
        create_gold_tables = SQLExecuteQueryOperator(
            task_id='create_gold_tables',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/sql/ddl_gold.sql'),
        )
        [create_silver_tables, create_gold_tables]

    # Bronze Layer: Load raw data to bronze layer
    @task
    def load_bronze_task (**kwargs):
        print("Loading data to Bronze layer...")
        folder = '/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/data/bronze_data'
        # import the bronze loader here so we don't load native libs at parse time
        from etl_pipeline.bronze_layer.load_to_bronze import load_csv_files_as_tables
        load_csv_files_as_tables(folder, schema='bronze')
    
    # Silver Layer: Transform tables and merge data prepraring for gold layer
    with TaskGroup("transform_per_table") as transform_tables:
        tgs = []
        table_names = [
            # 'Cancelled_Diverted_2023', 
            'US_flights_2023', 
            'airports_geolocation', 
            # 'maj_us_flight_january_2024', # Not use
            # 'weather_meteo_by_airport'
        ]
        for tbl in table_names:
            if tbl == "US_flights_2023":
                tg, chunk_paths = create_transform_group(tbl)
            else:
                tg = create_transform_group(tbl)
            tgs.append(tg)
    
    # Gold Layer: Load to Data Warehouse
    load_fact_flights = SQLExecuteQueryOperator(
            task_id='load_fact_flights',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/etl_pipeline/gold_layer/load_fact_flights.sql'),
        )
    
    @task_group(group_id="load_to_dim_tables")
    def load_to_dim():
        load_dim_date = SQLExecuteQueryOperator(
            task_id='load_dim_date',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/etl_pipeline/gold_layer/load_dim_date.sql'),
        )

        load_dim_airline = SQLExecuteQueryOperator(
            task_id='load_dim_airline',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/etl_pipeline/gold_layer/load_dim_airline.sql'),
        )

        load_dim_airport = SQLExecuteQueryOperator(
            task_id='load_dim_airport',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/etl_pipeline/gold_layer/load_dim_airport.sql'),
        )
        
        load_dim_plane = SQLExecuteQueryOperator(
            task_id='load_dim_plane',
            conn_id='usflights_connection',
            sql=load_sql_file('/Users/kittnguyen/Documents/Project/IS217_Us_Flights_Project/DE_DA/Airflow_Without_Docker/etl_pipeline/gold_layer/load_dim_plane.sql'),
        )
        [load_dim_date, load_dim_airline, load_dim_airport, load_dim_plane]
        
    atoti_ssas = PythonOperator(
        task_id="ssas",
        python_callable=atoti_task
    )
    
    tables_group = create_tables_group()
    load_bronze = load_bronze_task()
    merging_task = task_merging(chunk_paths)
    load_dim_tables = load_to_dim()
    
    create_schema >> tables_group >> load_bronze >> transform_tables >> merging_task >> load_dim_tables >> load_fact_flights >> atoti_ssas
    
dag = etl_pipeline()