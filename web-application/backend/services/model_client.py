# The following code was re-made with help from Copilot
# based on the code created by Emile

from typing import Dict, Any, List
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb


class ModelClient:
    THRESHOLDS = [5, 6, 10, 15, 20, 25, 30]

    def __init__(self):
        base = Path(__file__).parent.parent.parent.parent
        self.data_path = base / "data" / "connections_v3.csv"
        self.model_dir = base / "web-application" / "backend" / "services"

        # Load all trained boosters once
        self.boosters: Dict[int, xgb.Booster] = {}
        for t in self.THRESHOLDS:
            model_path = self.model_dir / f"model{t}.json"
            bst = xgb.Booster()
            bst.load_model(str(model_path))
            self.boosters[t] = bst

        # Build the exact feature space used during training (once)
        self.expected_columns = self._build_expected_columns()

    def _build_expected_columns(self) -> List[str]:
        """
        Reproduce the preprocessing from gradient_boost.py on the same sampled training
        subset to get the exact set and order of feature columns the model was trained on.
        """
        input(f'Reading data for the models, might crash your computer (RAM).\nPress ENTER to continue.')
        data = pd.read_csv(self.data_path)

        # Create binary target and drop original dst_arrival_delay columns
        data["delayed"] = (data["dst_arrival_delay"] > 0).astype(int)
        data = data[data.columns.drop(list(data.filter(regex="dst_arrival_delay")))]

        # Sample using the same parameters as in gradient_boost.py
        positive_sample = data[data["delayed"] == 1].sample(n=1000, random_state=13)
        negative_sample = data[data["delayed"] == 0].sample(n=1000, random_state=13)
        train_sub = pd.concat([positive_sample, negative_sample], axis=0)
        train_sub.sort_index(inplace=True)

        X_train = train_sub.drop("delayed", axis=1)

        # Time feature engineering
        time_features = ["start_timestamp", "src_arrival_plan", "dst_arrival_plan"]
        for col in time_features:
            X_train[col] = pd.to_datetime(X_train[col])
            X_train[f"{col}_sec"] = X_train[col].dt.second
            X_train[f"{col}_minute"] = X_train[col].dt.minute
            X_train[f"{col}_hour"] = X_train[col].dt.hour
            X_train[f"{col}_day"] = X_train[col].dt.dayofweek
            X_train = X_train.drop(col, axis=1)

        # One-hot encoding for non-numeric features (exactly as in gradient_boost.py)
        for col in list(X_train.columns):
            if not pd.api.types.is_numeric_dtype(X_train[col]):
                X_train[col] = X_train[col].astype("category")
                data_dum = pd.get_dummies(X_train[col], prefix=col, dtype="int")
                X_train = pd.concat([X_train.drop(columns=[col]), data_dum], axis=1)

        return list(X_train.columns)

    def _preprocess_payload(self, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply the same preprocessing to the incoming payload and align
        the resulting matrix to the expected training columns.
        """
        X = pd.DataFrame([features])

        # Time feature engineering
        for col in ["start_timestamp", "src_arrival_plan", "dst_arrival_plan"]:
            X[col] = pd.to_datetime(X[col])
            X[f"{col}_sec"] = X[col].dt.second
            X[f"{col}_minute"] = X[col].dt.minute
            X[f"{col}_hour"] = X[col].dt.hour
            X[f"{col}_day"] = X[col].dt.dayofweek
            X = X.drop(columns=[col])

        # One-hot encode non-numeric features
        for col in list(X.columns):
            if not pd.api.types.is_numeric_dtype(X[col]):
                X[col] = X[col].astype("category")
                dummies = pd.get_dummies(X[col], prefix=col, dtype="int")
                X = pd.concat([X.drop(columns=[col]), dummies], axis=1)

        # Align with training feature space (missing columns -> 0)
        X = X.reindex(columns=self.expected_columns, fill_value=0)

        # XGBoost prefers float32
        X = X.astype(np.float32)

        return X

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess the payload once, then run inference across all threshold-specific models.
        """
        X = self._preprocess_payload(features)
        dmat = xgb.DMatrix(X)

        results: Dict[str, Any] = {
            "model_versions": {t: f"model{t}.json" for t in self.THRESHOLDS},
        }

        # Predict with each model{t}.json and populate corresponding keys
        for t, bst in self.boosters.items():
            prob = float(bst.predict(dmat)[0])
            results[f"dst_arrival_delay_over_{t}_minutes_prob"] = prob

        return results


model_client = ModelClient()