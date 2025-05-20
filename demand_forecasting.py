import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

class DemandForecaster:
    def __init__(self, model_path=None):
        if model_path:
            self.model, self.scaler = joblib.load(model_path)
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()

    def train(self, booking_history: pd.DataFrame, feature_cols: list, target_col: str):
        X = booking_history[feature_cols]
        y = booking_history[target_col]
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        joblib.dump((self.model, self.scaler), "demand_forecaster.pkl")

    def predict(self, upcoming_features: pd.DataFrame) -> pd.Series:
        X_scaled = self.scaler.transform(upcoming_features)
        return pd.Series(self.model.predict(X_scaled), index=upcoming_features.index)
