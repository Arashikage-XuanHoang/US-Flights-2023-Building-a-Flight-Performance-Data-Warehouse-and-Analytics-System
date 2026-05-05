import warnings
from collections import Counter
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from sklearn.preprocessing import OneHotEncoder


def remove_unnecessary_cols (df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """
    Drop the column that is unnecessary
    """
    df.drop (columns=cols, inplace=True)
    print (f"Deleted {len (cols)} columns.")
    return df

def time_transform (df: pd.DataFrame, date_col: str):
    """
    Transform 'Date' column from object to datetime
    """
    df [date_col] = pd.to_datetime (df[date_col])
    print (f"Transform {date_col} to datetime")
    return df
    
def date_time_extract (df: pd.DataFrame, org_col: str, types: list):
    """
    Create day, month, quarter, or year columns
    Return (a) new columns from a datetime column (org_col)
    """
    for type in types:
        if type == "day":
            df ["day"] = df [org_col].dt.day
            print (f"Create {type} column.")
        elif type == "month":
            df ["month"] = df [org_col].dt.month
            print (f"Create {type} column.")
        elif type == "year":
            df ["year"] = df [org_col].dt.year
            print (f"Create {type} column.")
        elif type == "quarter":
            df ["quarter"] = df [org_col].dt.quarter
            print (f"Create {type} column.")
        elif type == "is_weekend":
            df ["is_weekend"] = df [org_col].dt.dayofweek
            print (f"Create {type} column.")
        else:
            print (f"Unvalid column: {type}")
    print ("Done") 
    return df

def calc_woe_iv_single(data, feature, target, bins=10, alpha=1):
    """
    Tính WoE và IV cho 1 feature duy nhất, tối ưu cho dữ liệu imbalance.
    """
    df = data[[feature, target]].copy().dropna()
    
    if not df[target].isin([0, 1]).all():
        raise ValueError(f"Target column {target} must be binary (0,1)")
    
    # Phân bin
    if pd.api.types.is_numeric_dtype(df[feature]) and df[feature].nunique() > bins:
        try:
            df['bin'] = pd.qcut(df[feature], q=bins, duplicates='drop')
        except:
            df['bin'] = pd.cut(df[feature], bins=bins, duplicates='drop')
    else:
        df['bin'] = df[feature].astype(str)
    
    grouped = df.groupby('bin')[target].agg(['count', 'sum'])
    grouped.columns = ['total', 'bad']
    grouped['good'] = grouped['total'] - grouped['bad']
    
    # Laplace smoothing
    grouped['%good'] = (grouped['good'] + alpha) / (grouped['good'].sum() + alpha * len(grouped))
    grouped['%bad'] = (grouped['bad'] + alpha) / (grouped['bad'].sum() + alpha * len(grouped))
    
    # Tính WOE và IV
    grouped['WOE'] = np.log(grouped['%good'] / grouped['%bad']).replace([np.inf, -np.inf], 0)
    grouped['IV'] = (grouped['%good'] - grouped['%bad']) * grouped['WOE']
    grouped = grouped.reset_index()
    grouped.insert(0, 'Feature', feature)
    
    iv = grouped['IV'].sum()
    return iv, grouped

def iv_woe_all(data, target, bins=10, show_woe=False, plot_iv=True, alpha=1, iv_threshold=0.3):
    """
    Tính IV & WOE cho toàn bộ các feature, tối ưu cho dữ liệu lớn và imbalance.
    """
    warnings.filterwarnings("ignore", category=FutureWarning)
    
    if len(data) < bins * 2:
        bins = max(2, len(data) // 2)
    
    iv_summary = []
    woe_details = []
    strong_features = []
    
    features = [col for col in data.columns if col != target]
    
    for feature in features:
        try:
            iv, detail = calc_woe_iv_single(data, feature, target, bins, alpha)
            iv_summary.append((feature, iv))
            woe_details.append(detail)
            
            if iv >= iv_threshold:
                strong_features.append(feature)
            
            if show_woe:
                print(detail)
        except Exception as e:
            print(f"Lỗi khi xử lý '{feature}': {e}")
    
    iv_df = pd.DataFrame(iv_summary, columns=['Feature', 'IV']).sort_values(by='IV', ascending=False)
    woe_df = pd.concat(woe_details, axis=0).reset_index(drop=True)
    
    if plot_iv:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=iv_df.head(10), x='IV', y='Feature', palette='viridis')  # Top 10
        for i, bar in enumerate(plt.gca().patches):
            width = bar.get_width()
            percentage = (iv_df.iloc[i]['IV'] / iv_df['IV'].sum() * 100) if iv_df['IV'].sum() > 0 else 0
            plt.text(width * 1.01, bar.get_y() + bar.get_height()/2, 
                     f'{width:.4f} ({percentage:.1f}%)', ha='left', va='center')
        plt.title("Top 10 Features by Information Value (IV)")
        plt.tight_layout()
        plt.savefig('iv_plot.png')
        plt.show()
    
    if strong_features:
        print("Strong predictive features (IV >= {:.2f}):".format(iv_threshold))
        for feat in strong_features:
            print(f" - {feat}")
    else:
        print("No strong features found (IV >= {:.2f})".format(iv_threshold))
    
    return iv_df, woe_df

def plot_corr_heatmap(df: pd.DataFrame, selected_features: list, numerical_features: list, label_col: str = 'label'):
    """
    Vẽ heatmap tương quan giữa các numerical features đã chọn và cột nhãn.
    
    Args:
        df (pd.DataFrame): DataFrame đầu vào.
        selected_features (list): Danh sách các features đã chọn.
        numerical_features (list): Danh sách các cột dạng số.
        label_col (str): Tên cột nhãn (default: 'label').
    """
    # Chọn các cột vừa được chọn vừa là numerical
    corr_features = [f for f in selected_features if f in numerical_features]

    # Thêm label để xem tương quan với nhãn
    if label_col not in corr_features:
        corr_features.append(label_col)

    # Tính ma trận tương quan
    corr_matrix = df[corr_features].apply(pd.to_numeric, errors='coerce').corr(method="spearman")
    print("Đường chéo:", np.diag(corr_matrix))

    # Tạo mask tam giác trên để không vẽ đối xứng
    # mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

    # Tạo colormap pastel nhẹ nhàng
    pastel = LinearSegmentedColormap.from_list("pastel_sang", ["#f2f2f2", "#8f81dd", "#122d63"])

    # Vẽ heatmap
    plt.figure(figsize=(15, 12))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap=pastel,
        square=True,
        mask=mask,
        linewidths=0.5,
        cbar_kws={"shrink": 0.7}
    )
    plt.title("Correlation Matrix of Selected Numerical Features", fontsize=14)
    plt.tight_layout()
    plt.show()