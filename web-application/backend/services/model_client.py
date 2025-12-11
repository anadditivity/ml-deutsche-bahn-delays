# The following code was re-made with help from Copilot
# based on the code created by Emile
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb

class ModelClient:
    THRESHOLDS = [5, 10, 15, 20, 25, 30]

    def __init__(self):
        base = Path(__file__).parent.parent.parent.parent
        self.data_path = base / "data" / "connections_v3.csv"
        self.model_dir = base / "web-application" / "backend" / "services"

        self.boosters = {}
        for t in self.THRESHOLDS:
            model_path = self.model_dir / f"model{t}.json"
            bst = xgb.Booster()
            bst.load_model(str(model_path))
            self.boosters[t] = bst

        # Build expected columns from full dataset
        self.category_map, self.expected_columns, self.numeric_cols = self._build_expected_columns()

    def _build_expected_columns(self):
        print('Loading OHE data, this will take some time.')
        data = pd.read_csv(self.data_path)

        # Create target and drop original delay column
        data["delayed"] = (data["dst_arrival_delay"] > 0).astype(int)
        data = data.drop(columns=list(data.filter(regex="dst_arrival_delay")))

        # Extract time features from full dataset
        time_features = ["start_timestamp", "src_arrival_plan", "dst_arrival_plan"]
        for col in time_features:
            data[col] = pd.to_datetime(data[col])
            data[f"{col}_sec"] = data[col].dt.second
            data[f"{col}_minute"] = data[col].dt.minute
            data[f"{col}_hour"] = data[col].dt.hour
            data[f"{col}_day"] = data[col].dt.dayofweek
        data = data.drop(columns=time_features)

        numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col]) and col != "delayed"]
        # Collect unique categories for each categorical column
        categorical_cols = [col for col in data.columns if not pd.api.types.is_numeric_dtype(data[col]) and col != "delayed"]
        category_map = {col: data[col].astype("category").cat.categories.tolist() for col in categorical_cols}

        # Build expected columns list
        expected_columns = numeric_cols.copy()
        for col, cats in category_map.items():
            expected_columns.extend([f"{col}_{cat}" for cat in cats])

        return category_map, expected_columns, numeric_cols

    def _apply_ohe(self, df):
        # Apply OHE using category_map without exploding memory
        df = df.copy()
        dummies = pd.get_dummies(df[self.category_map.keys()], prefix_sep="_", dtype="int")
        df = pd.concat([df[self.numeric_cols], dummies], axis=1)
        return df.reindex(columns=self.expected_columns, fill_value=0)

    def _preprocess_payload(self, features):
        X = pd.DataFrame([features])

        # Extract time features
        for col in ["start_timestamp", "src_arrival_plan", "dst_arrival_plan"]:
            X[col] = pd.to_datetime(X[col])
            X[f"{col}_sec"] = X[col].dt.second
            X[f"{col}_minute"] = X[col].dt.minute
            X[f"{col}_hour"] = X[col].dt.hour
            X[f"{col}_day"] = X[col].dt.dayofweek
        X = X.drop(columns=["start_timestamp", "src_arrival_plan", "dst_arrival_plan"])

        # Apply OHE and align columns
        X = self._apply_ohe(X)
        X = X.astype(np.float32)

        return X

    def predict(self, features):
        X = self._preprocess_payload(features)
        dmat = xgb.DMatrix(X)

        results = {"model_versions": {t: f"model{t}.json" for t in self.THRESHOLDS}}
        for t, bst in self.boosters.items():
            prob = float(bst.predict(dmat)[0])
            results[f"dst_arrival_delay_over_{t}_minutes_prob"] = prob
        return results

model_client = ModelClient()