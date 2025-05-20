import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib

class ChurnPredictor:
    def __init__(self, model_path=None):
        if model_path:
            self.model, self.scaler = joblib.load(model_path)
        else:
            self.model = LogisticRegression(solver='lbfgs', max_iter=200)
            self.scaler = StandardScaler()

    def train(self, usage_data: pd.DataFrame, feature_cols: list, target_col: str):
        X = usage_data[feature_cols]
        y = usage_data[target_col]
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        joblib.dump((self.model, self.scaler), "churn_model.pkl")

    def predict(self, member_features: pd.DataFrame) -> pd.Series:
        X_scaled = self.scaler.transform(member_features)
        return pd.Series(self.model.predict_proba(X_scaled)[:, 1], index=member_features.index)
