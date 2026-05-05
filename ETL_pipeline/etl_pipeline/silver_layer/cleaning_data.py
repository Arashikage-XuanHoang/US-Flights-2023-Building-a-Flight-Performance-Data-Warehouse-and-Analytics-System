import logging

def transform_drop_nulls(df: 'pd.DataFrame', subset=None) -> 'pd.DataFrame':
    """
    Xóa các dòng có giá trị NULL (NaN) trong DataFrame.

    Args:
        df (pd.DataFrame): DataFrame đầu vào.
        subset (list hoặc None): Danh sách tên cột cần kiểm tra NULL.
                                Nếu None, kiểm tra tất cả các cột.

    Returns:
        pd.DataFrame: DataFrame sau khi xóa các dòng NULL.
    """
    import pandas as pd
    logging.info("Dropping nulls")
    return df.dropna(subset=subset)

def transform_cols(df: 'pd.DataFrame') -> 'pd.DataFrame':
    """
    Convert các cột có tên 'FlightDate' hoặc chứa 'time' (case-insensitive)
    sang kiểu datetime trong pandas.
    """
    import pandas as pd
    logging.info("Transforming time columns")
    # time_columns = ['FlightDate', 'DepTime']
    for col in df.columns:
        col_lower = col.lower()
        # Chỉ convert cột có tên đúng là flightdate hoặc tên có 'time' nhưng không phải label
        if col_lower == 'flightdate' or ('time' in col_lower and 'label' not in col_lower):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                print(f"Đã transform cột {col} sang datetime")
            except Exception as e:
                print(f"Warning: Không thể convert cột {col} sang datetime: {e}")
    
    return df

def transform_remove_duplicates(
    df: 'pd.DataFrame',
    subset=None,
    keep='first'
 ) -> 'pd.DataFrame':
    """
    Loại bỏ các dòng trùng lặp trong DataFrame.

    Args:
        df (pd.DataFrame): DataFrame đầu vào.
        subset (list hoặc None): Danh sách cột để kiểm tra trùng lặp. Nếu None thì kiểm tra toàn bộ cột.
        keep (str): 'first', 'last', hoặc False - giữ dòng đầu, cuối hoặc bỏ hết các dòng trùng.

    Returns:
        pd.DataFrame: DataFrame đã loại bỏ duplicate.
    """
    import pandas as pd
    logging.info("Removing duplicates")
    return df.drop_duplicates(subset=subset, keep=keep)


