import io
import logging
import psycopg2

def list_tables_in_schema(schema: str):
    conn = psycopg2.connect(
        host="localhost",
        port=5440,
        user="minhphu",
        password="minhphu123",
        dbname="usflights_psql1"
    )
    cursor = conn.cursor()
    try:
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        cursor.execute(query, (schema,))
        tables = cursor.fetchall()
        table_list = [t[0] for t in tables]
        return table_list
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
        
        
def load_to_silver(
    df: 'pd.DataFrame',
    table_name: str
):
    """
    Load pandas DataFrame vào PostgreSQL table trong Silver layer với chunksize.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần load.
        table_name (str): Tên bảng trong Postgres.
        schema (str): Tên schema, mặc định 'silver'.
        if_exists (str): 'fail', 'replace', 'append'.
        chunksize (int): số dòng load một lần (để tránh tốn RAM).
    """
    import pandas as pd
    conn = psycopg2.connect(
        host="localhost",
        port=5440,
        user="minhphu",
        password="minhphu123",
        dbname="usflights_psql1"
    )
    df.drop(columns='COUNTRY_arr', inplace=True)
    print(df.columns)
    cursor = conn.cursor()
    # Ví dụ gọi hàm
    tables = list_tables_in_schema('silver')
    print("Danh sách bảng trong schema 'silver':")
    for tbl in tables:
        print(tbl)
    cursor.execute("SHOW search_path;")
    print("search_path =", cursor.fetchone()[0])
    cursor.execute("SET search_path TO silver, public;")
    cursor.execute("SHOW search_path;")
    print("search_path =", cursor.fetchone()[0])
    try:
        # buffer = io.StringIO()
        # df.to_csv(buffer, index=False, header=False)
        # buffer.seek(0)
        
        # cursor.copy_from(buffer, table_name, sep=",")
        buffer = io.StringIO()
        # Xuất CSV có header, pandas tự quote trường có dấu phẩy
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
        cursor.copy_expert(sql, buffer)
        # sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
        # with io.StringIO() as buffer:
        #     df.to_csv(buffer, index=False)  # header=True mặc định
        #     buffer.seek(0)
        #     cursor.copy_expert(sql, buffer)
            
        conn.commit()
        logging.info(f"Successfully loaded {len(df)} rows to silver.{table_name}")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error loading data to silver.{table_name}: {e}")
        print(f"Error loading data to silver.{table_name}: {e}")
    finally:
        cursor.close()
        conn.close()

