import os
import sqlalchemy
import psycopg2
import logging, io

def ensure_table_exists(conn, df, schema, table_name):
    """
    Tạo bảng nếu chưa có (các cột đều là TEXT để phù hợp raw data).
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        );
    """, (schema, table_name))
    exists = cursor.fetchone()[0]

    if not exists:
        columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
        create_sql = f'CREATE TABLE IF NOT EXISTS "{schema}"."{table_name}" ({columns});'
        cursor.execute(create_sql)
        conn.commit()
        logging.info(f"Created table {schema}.{table_name} with {len(df.columns)} TEXT columns.")
    cursor.close()

def load_to_bronze(
    df: 'pd.DataFrame',
    table_name: str,
    schema: str,
    if_exists='replace'
):
    """
    Load pandas DataFrame into PostgreSQL table (bronze layer) với chunksize.

    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu cần load.
        table_name (str): Tên bảng trong Postgres.
        db_uri (str): Chuỗi kết nối database.
        if_exists (str): 'fail', 'replace', 'append'
        chunksize (int): số dòng load 1 lần (để tránh dùng quá nhiều RAM)
    """
    conn = psycopg2.connect(
        host="localhost",
        port=5440,
        user="minhphu",
        password="minhphu123",
        dbname="usflights_psql1"
    )
    cursor = conn.cursor()
    try:
        # Tạo schema nếu chưa có
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
        conn.commit()

        # Nếu replace thì drop bảng cũ
        if if_exists == 'replace':
            cursor.execute(f'DROP TABLE IF EXISTS "{schema}"."{table_name}" CASCADE;')
            conn.commit()

        # Đảm bảo bảng tồn tại
        ensure_table_exists(conn, df, schema, table_name)

        # Ghi DataFrame vào buffer CSV
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        # Dùng COPY để load vào bảng
        cursor.copy_expert(
            f"""
            COPY "{schema}"."{table_name}" FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL '', QUOTE '"');
            """,
            buffer
        )

        conn.commit()
        logging.info(f"Successfully loaded data to {schema}.{table_name}")
        print(f"Loaded {len(df)} rows into {schema}.{table_name}")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error loading data to {schema}.{table_name}: {e}")
        print(f"Error loading data to {schema}.{table_name}: {e}")
        
    finally:
        cursor.close()
        conn.close()

def load_csv_files_as_tables(folder_path: str, schema: str = 'bronze'):
    """
    Đọc tất cả file CSV trong folder, load mỗi file vào bảng riêng (tên bảng lấy từ tên file).

    Args:
        folder_path (str): thư mục chứa các file CSV.
        db_uri (str): chuỗi kết nối DB.
        schema (str): schema trong Postgres, mặc định 'bronze'.
    """
    import pandas as pd
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files in {folder_path}")
    print(pd.__version__)
    print(sqlalchemy.__version__)
    for i, file in enumerate(csv_files, 1):
        file_path = os.path.join(folder_path, file)
        table_name = os.path.splitext(file)[0]  # lấy tên file không có .csv làm tên bảng
        # full_table_name = f"{schema}.{table_name}"

        print(f"[{i}/{len(csv_files)}] Loading file {file_path} into table {table_name} ...")
        try:
            # df = pd.read_csv(file_path)
            for i, chunk in enumerate(pd.read_csv(file_path, chunksize=3000000)):
                if i == 0:
                    # chunk đầu tiên, tạo bảng mới hoặc replace bảng cũ
                    load_to_bronze(chunk, table_name, schema, if_exists='replace')
                else:
                    # các chunk sau, thêm dữ liệu vào bảng
                    load_to_bronze(chunk, table_name, schema, if_exists='append')
            # load_to_bronze(df, table_name, schema, if_exists='replace')
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")