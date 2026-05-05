def drop_unnecessary_cols(
    df: 'pd.DataFrame',
    cols: list
) -> 'pd.DataFrame':
    """
    Xoá các cột không cần thiết trước khi merge data
    """
    return df.drop(columns=cols)

def transform_merge_dfs(
    df_left: 'pd.DataFrame',
    left_cols: list,
    df_right: 'pd.DataFrame',
    right_cols: list,
    on=None,
    left_on=None,
    right_on=None,
    how='inner',
    suffix='_dep'
 ) -> 'pd.DataFrame':
    """
    Merge hai DataFrame theo các tham số giống pd.merge.

    Args:
        df_left (pd.DataFrame): DataFrame bên trái.
        df_right (pd.DataFrame): DataFrame bên phải.
        on (str or list, optional): cột chung để join.
        left_on (str or list, optional): cột bên trái để join.
        right_on (str or list, optional): cột bên phải để join.
        how (str): kiểu merge ['left', 'right', 'inner', 'outer'], mặc định 'inner'.
        suffixes (tuple): hậu tố thêm vào cột trùng tên.

    Returns:
        pd.DataFrame: DataFrame đã merge.
    """
    import pandas as pd
    # Xoá các cột không cần thiết
    df_left = drop_unnecessary_cols(df_left, left_cols)
    df_right = drop_unnecessary_cols(df_right, right_cols)
    
    df_right = df_right.add_suffix(suffix)
    merged_df = pd.merge(
        df_left, df_right,
        how=how,
        on=on,
        left_on=left_on,
        right_on=right_on
    )
    return merged_df