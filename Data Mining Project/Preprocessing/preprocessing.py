from collections import Counter
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, PowerTransformer,
    OneHotEncoder, OrdinalEncoder
)
from sklearn.decomposition import PCA
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def train_dev_test(X, y, 
                   test_size=0.2, 
                   dev_size=None, 
                   stratify=True, 
                   random_state=42):
    """
    Chia dữ liệu thành các tập Train, Dev (Validation, tùy chọn) và Test.

    Tham số:
        X (pd.DataFrame): Đặc trưng đầu vào.
        y (pd.Series): Nhãn tương ứng.
        test_size (float): Tỉ lệ dữ liệu dành cho tập Test (ví dụ: 0.2 --> 20%).
        dev_size (float | None): 
            - Nếu None → chỉ chia Train/Test.
            - Nếu có giá trị (ví dụ 0.2) --> chia thêm Dev (từ phần Train).
        stratify (bool): Có dùng stratify để giữ phân phối lớp đồng đều không.
        random_state (int): Seed cố định cho việc chia dữ liệu.

    Trả về:
        Nếu dev_size là None:
            X_train, y_train, X_test, y_test
        Nếu dev_size không None:
            X_train, y_train, X_dev, y_dev, X_test, y_test
    """

    stratify_y = y if stratify else None

    # --- Bước 1: Chia Train/Test ---
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=stratify_y,
        random_state=random_state,
        shuffle=False
    )

    # --- Bước 2: Nếu có dev_size thì chia tiếp Train/Dev ---
    if dev_size is not None and 0 < dev_size < 1:
        # Dev được lấy từ phần TrainVal
        dev_ratio = dev_size / (1 - test_size)  # phần trăm so với trainval
        X_train, X_dev, y_train, y_dev = train_test_split(
            X_trainval, y_trainval,
            test_size=dev_ratio,
            stratify=y_trainval if stratify else None,
            random_state=random_state,
            shuffle=False
        )

        print("\nSố lượng mẫu mỗi lớp:")
        print("Train:", Counter(y_train))
        print("Dev:  ", Counter(y_dev))
        print("Test: ", Counter(y_test))

        return X_train, y_train, X_dev, y_dev, X_test, y_test

    else:
        # Không có tập dev
        X_train, y_train = X_trainval, y_trainval

        print("\nSố lượng mẫu mỗi lớp:")
        print("Train:", Counter(y_train))
        print("Test: ", Counter(y_test))

        return X_train, y_train, X_test, y_test
    
def preprocess_features(
    X: pd.DataFrame,
    numerical_features: list,
    categorical_features: list,
    numerical_type: str = "standard",     # None / "minmax" / "yeo-johnson" / "standard"
    categorical_type: str = "onehot",     # None / "onehot" / "ordinal"
    use_pca: bool = False,
    n_components: int | None = None
):
    """
    Tiền xử lý dữ liệu đầu vào gồm numerical và categorical features.
    Args:
        X (pd.DataFrame): Dữ liệu đầu vào.
        numerical_features (list): Danh sách cột dạng số.
        categorical_features (list): Danh sách cột dạng phân loại.
        numerical_type (str): Cách scale numerical:
            - None: Không scale
            - "minmax": MinMaxScaler
            - "yeo-johnson": PowerTransformer (Yeo-Johnson)
            - "standard": StandardScaler
        categorical_type (str): Cách encode categorical:
            - None: Bỏ qua (giữ nguyên categorical dưới dạng DataFrame)
            - "onehot": OneHotEncoder
            - "ordinal": OrdinalEncoder
        use_pca (bool): Có dùng PCA không.
        n_components (int | None): Số thành phần PCA.
    Returns:
        X_processed (pd.DataFrame hoặc np.ndarray): Dữ liệu sau xử lý (gộp numerical và categorical)
        preprocessor (ColumnTransformer hoặc None): Bộ xử lý đã fit (None nếu categorical_type=None)
    """

    # --- Numeric pipeline ---
    steps_num = [('imputer', SimpleImputer(strategy='median'))]

    if numerical_type == "standard":
        steps_num.append(('scaler', StandardScaler()))
    elif numerical_type == "minmax":
        steps_num.append(('scaler', MinMaxScaler()))
    elif numerical_type == "yeo-johnson":
        steps_num.append(('scaler', PowerTransformer(method='yeo-johnson')))
    elif numerical_type is None:
        pass  # không scale gì cả
    else:
        raise ValueError("numerical_type phải là None, 'minmax', 'yeo-johnson' hoặc 'standard'")

    if use_pca:
        steps_num.append(('pca', PCA(n_components=n_components)))

    numeric_transformer = Pipeline(steps=steps_num)

    # --- Categorical pipeline ---
    steps_cat = [('imputer', SimpleImputer(strategy='most_frequent'))]

    if categorical_type == "onehot":
        steps_cat.append(('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
    elif categorical_type == "ordinal":
        steps_cat.append(('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)))
    elif categorical_type is None:
        # Không encode categorical, giữ nguyên DataFrame
        steps_cat = None
    else:
        raise ValueError("categorical_type phải là None, 'onehot' hoặc 'ordinal'")

    if steps_cat is not None:
        categorical_transformer = Pipeline(steps=steps_cat)

    # --- Combine ---
    transformers = []
    if numerical_features and numerical_type is not None:
        transformers.append(('num', numeric_transformer, numerical_features))
    elif numerical_features:
        # nếu không scale thì vẫn impute median
        transformers.append(('num', Pipeline([('imputer', SimpleImputer(strategy='median'))]), numerical_features))

    if categorical_features and categorical_type is not None:
        transformers.append(('cat', categorical_transformer, categorical_features))

    if categorical_type is None:
        # Chỉ xử lý numerical, categorical giữ nguyên
        X_num_processed = numeric_transformer.fit_transform(X[numerical_features])
        # Biến thành DataFrame
        X_num_df = pd.DataFrame(X_num_processed, columns=numerical_features, index=X.index)

        X_cat_df = X[categorical_features].copy()  # giữ nguyên categorical dạng DataFrame

        # Gộp numerical và categorical lại thành DataFrame
        X_processed = pd.concat([X_num_df, X_cat_df], axis=1)

        preprocessor = None

    else:
        preprocessor = ColumnTransformer(transformers=transformers, remainder='drop')
        X_processed_np = preprocessor.fit_transform(X)

        # Nếu OneHotEncoder thì có thể nhiều cột mới, không giữ tên cột cũ được dễ dàng
        # Trường hợp muốn giữ tên cột, bạn có thể xử lý thêm ở ngoài hàm này

        X_processed = X_processed_np

    print(f"Kích thước mới: {X_processed.shape}")
    print("New X:")
    print(X_processed)

    return X_processed, preprocessor