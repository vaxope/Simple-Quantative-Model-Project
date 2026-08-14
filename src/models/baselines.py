import pandas as pd
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

def train_xgb_baseline(X_train: pd.Dataframe, y_train: pd.Series, n_estimators=100, learning_rate=0.03, max_depth=3, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1):
    model = XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        random_state=random_state,
        n_jobs=n_jobs
    )

    model.fit(X_train, y_train)
    return model

def train_linear_baseline(X_train: pd.DataFrame, y_train: pd.Series):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model