import os
import re
import math
import random
import warnings
from datetime import datetime
from itertools import combinations
from collections import Counter
from typing import List, Tuple, Dict, Optional
import numpy as np
import pandas as pd
from scipy import stats

# --- VISUALIZATION ---
import matplotlib.pyplot as plt
import seaborn as sns
import missingno
import mplcursors
from matplotlib.colors import LinearSegmentedColormap

# --- PROGESS & OPTIMIZATION ---
from tqdm.notebook import tqdm
tqdm.pandas()
import optuna

# --- DATA PREPROCESSING ---
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, PowerTransformer,
    OneHotEncoder, LabelEncoder, OrdinalEncoder
)
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.feature_selection import SelectFromModel

# --- TRAIN/TEST SPLITS & CROSS VALIDATION ---
from sklearn.model_selection import (
    train_test_split, KFold, StratifiedKFold,
    cross_val_score, cross_val_predict,
    GridSearchCV, RandomizedSearchCV, ParameterGrid
)

# --- METRICS & EVALUATION --- 
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, auc, roc_curve,
    confusion_matrix, classification_report,
    precision_recall_curve, make_scorer
)

# --- MACHINE LEARNING MODELS ---
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import xgboost as xgb
from lightgbm import LGBMClassifier
import lightgbm as lgb
from catboost import CatBoostClassifier, CatBoostRegressor, Pool, cv


def evaluate_model(y_true, y_pred, y_proba=None, dataset_name=''):
    """
    Đánh giá mô hình phân loại dựa trên các chỉ số phổ biến.

    Tham số:
        y_true (array-like): Nhãn thực tế (ground truth).
        y_pred (array-like): Nhãn dự đoán (dạng nhị phân 0/1).
        y_proba (array-like, optional): Xác suất dự đoán (nếu có), dùng để tính ROC AUC.
        dataset_name (str, optional): Tên tập dữ liệu (ví dụ: "Train", "Test", "Validation") để hiển thị.

    Chức năng:
        - In ra Accuracy, Precision, Recall, F1-score.
        - Nếu có xác suất (`y_proba`), tính thêm ROC AUC.
        - In bảng phân loại (classification report).
        - Vẽ confusion matrix bằng seaborn heatmap.

    Ghi chú:
        - Phù hợp với bài toán phân loại nhị phân.
        - Sử dụng tốt cho cả train/test/dev set để so sánh hiệu suất mô hình.
    """
    
    print(f"Evaluation on {dataset_name} set:")

    # Các chỉ số cơ bản
    print("Accuracy :", round(accuracy_score(y_true, y_pred), 4))
    print("Precision:", round(precision_score(y_true, y_pred), 4))
    print("Recall   :", round(recall_score(y_true, y_pred), 4))
    print("F1-score :", round(f1_score(y_true, y_pred), 4))

    # ROC AUC nếu có xác suất
    if y_proba is not None:
        auc = roc_auc_score(y_true, y_proba)
        print(f"ROC AUC  : {auc:.4f}")

        # Vẽ ROC Curve
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {dataset_name}')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    # Classification report
    print("Classification Report:")
    print(classification_report(y_true, y_pred))

    # Confusion Matrix (vẽ đẹp)
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Pred 0', 'Pred 1'], yticklabels=['True 0', 'True 1'])
    plt.title(f'Confusion Matrix - {dataset_name}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.show()
    
# def preprocess_features(
#     X, numerical_features, 
#     categorical_features, 
#     use_pca=False, 
#     n_components=None
# ):
#     """
#     Xử lý dữ liệu đầu vào gồm các biến numerical và categorical.

#     Tham số:
#         X (pd.DataFrame): DataFrame đầu vào.
#         numerical_features (list): Danh sách tên các cột numerical.
#         categorical_features (list): Danh sách tên các cột categorical.
#         use_pca (bool): Có dùng PCA cho numerical features không (mặc định: False).
#         n_components (int | None): Số thành phần PCA (nếu dùng PCA).

#     Trả về:
#         X_processed (np.ndarray): Ma trận đặc trưng sau khi xử lý.
#         preprocessor (ColumnTransformer): Bộ xử lý đã fit, dùng cho transform sau này.
#     """
#     # --- Numeric pipeline ---
#     steps_num = [
#         ('imputer', SimpleImputer(strategy='median')),
#         ('scaler', StandardScaler())
#     ]
#     if use_pca:
#         from sklearn.decomposition import PCA
#         steps_num.append(('pca', PCA(n_components=n_components)))

#     numeric_transformer = Pipeline(steps=steps_num)

#     # --- Categorical pipeline ---
#     categorical_transformer = Pipeline(steps=[
#         ('imputer', SimpleImputer(strategy='most_frequent')),
#         ('onehot', OneHotEncoder(handle_unknown='ignore'))
#     ])

#     # --- Combine ---
#     preprocessor = ColumnTransformer(
#         transformers=[
#             ('num', numeric_transformer, numerical_features),
#             ('cat', categorical_transformer, categorical_features)
#         ],
#         remainder='drop'
#     )

#     # --- Fit & transform ---
#     X_processed = preprocessor.fit_transform(X)
#     print(f"Đã xử lý X thành công. Kích thước mới: {X_processed.shape}")

#     return X_processed, preprocessor


def optimize_threshold_by_f1(model, X_test, y_test, start=0.05, end=0.95, step=0.01, plot=True):
    """
    Tối ưu ngưỡng phân loại để đạt F1-score cao nhất.

    Parameters:
        model: Mô hình đã huấn luyện, phải có phương thức `predict_proba`.
        X_test (DataFrame or array): Dữ liệu kiểm tra.
        y_test (Series or array): Nhãn thật.
        start (float): Ngưỡng bắt đầu thử.
        end (float): Ngưỡng kết thúc thử.
        step (float): Bước nhảy của ngưỡng.
        plot (bool): Có hiển thị biểu đồ không.

    Returns:
        best_thresh (float): Ngưỡng phân loại tốt nhất.
        best_f1 (float): F1-score cao nhất tương ứng.
    """
    # Lấy xác suất của lớp 1
    y_proba = model.predict_proba(X_test)[:, 1]

    thresholds = np.arange(start, end, step)
    f1_scores = []

    for thresh in thresholds:
        y_pred = (y_proba >= thresh).astype(int)
        f1 = f1_score(y_test, y_pred)
        f1_scores.append(f1)

    best_idx = np.argmax(f1_scores)
    best_thresh = thresholds[best_idx]
    best_f1 = f1_scores[best_idx]

    print(f"Best threshold: {best_thresh:.2f} with F1-score: {best_f1:.4f}")

    if plot:
        plt.figure(figsize=(10,6))
        plt.plot(thresholds, f1_scores, marker='o')
        plt.xlabel("Threshold")
        plt.ylabel("F1-score")
        plt.title("Tối ưu threshold phân loại")
        plt.grid(True)
        plt.axvline(best_thresh, color='red', linestyle='--', label=f'Best: {best_thresh:.2f}')
        plt.legend()
        plt.tight_layout()
        plt.show()

    return best_thresh, best_f1