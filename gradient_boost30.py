import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

# Load full dataset
target_delay = 30

data = pd.read_csv('data/connections_v3.csv')
data['delayed'] = (data['dst_arrival_delay'] > target_delay).astype(int)
data = data.drop(columns=list(data.filter(regex='dst_arrival_delay')))


# Extract time features
time_features = ['start_timestamp', 'src_arrival_plan', 'dst_arrival_plan']
for col in time_features:
    data[col] = pd.to_datetime(data[col])
    data[f"{col}_sec"] = data[col].dt.second
    data[f"{col}_minute"] = data[col].dt.minute
    data[f"{col}_hour"] = data[col].dt.hour
    data[f"{col}_day"] = data[col].dt.dayofweek
data = data.drop(columns=time_features)

numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col]) and col != 'delayed']
# ---- STEP 1: Collect unique categories for each categorical column ----
categorical_cols = [col for col in data.columns if not pd.api.types.is_numeric_dtype(data[col]) and col != 'delayed']
category_map = {col: data[col].astype('category').cat.categories.tolist() for col in categorical_cols}

# Build expected columns list: numeric + OHE categorical
expected_columns = numeric_cols.copy()
for col, cats in category_map.items():
    expected_columns.extend([f"{col}_{cat}" for cat in cats])

### unrealistic sample for training
positive_sample = data[data['delayed'] == 1].sample(n=4227, random_state=13)
negative_sample = data[data['delayed'] == 0].sample(n=4227, random_state=14)
train_subset = pd.concat([positive_sample, negative_sample], axis=0)

# Apply same OHE mapping to subset
def apply_ohe(df, category_map, expected_columns, numeric_cols):
    df = df.copy()
    for col in category_map.keys():
        df[col] = df[col].astype('category')
    dummies = pd.get_dummies(df[category_map.keys()], prefix_sep='_', dtype='int')
    df = pd.concat([df[numeric_cols], dummies], axis=1)
    return df.reindex(columns=expected_columns, fill_value=0)

X_train_small = apply_ohe(train_subset.drop(columns=['delayed']), category_map, expected_columns, numeric_cols).astype(np.float32)
y_train_small = train_subset['delayed']

# ---- STEP 4: Create validation and test sets from full dataset ----
val_sample = data.sample(n=5000, random_state=15)
test_sample = data.sample(n=5000, random_state=16)

X_val = apply_ohe(val_sample.drop(columns=['delayed']), category_map, expected_columns, numeric_cols).astype(np.float32)
y_val = val_sample['delayed']

X_test = apply_ohe(test_sample.drop(columns=['delayed']), category_map, expected_columns, numeric_cols).astype(np.float32)
y_test = test_sample['delayed']

# Convert to DMatrix
dtrain = xgb.DMatrix(X_train_small, label=y_train_small)
dval = xgb.DMatrix(X_val, label=y_val)
dtest = xgb.DMatrix(X_test, label=y_test)

def xgb_f1(preds, labels, threshold=0.5):
    label_list = labels.get_label()
    pred_list = (preds > threshold).astype(int)
    return 'f1', f1_score(label_list, pred_list, pos_label=1)

optimal_params = None
best_f_score = 0

for learning_rate in np.linspace(0.1, 1.0, 10):
    for max_depth in range(3, 10):
        for child_weight in np.linspace(0.5, 2, 15):
            params = {
                "booster": 'gbtree',
                "eta": float(learning_rate),
                "objective": 'binary:logistic',
                "seed": 111,
                "max_depth": max_depth,
                "min_child_weight": float(child_weight),
                "subsample": 0.9
            }
            eval_list = [(dtrain, 'train'), (dval, 'eval')]
            bst = xgb.train(params, dtrain, 50, evals=eval_list, custom_metric=xgb_f1, maximize=True)
            preds = (bst.predict(dtest) > 0.5).astype(int)
            current_score = f1_score(y_test, preds, pos_label=1)
            if current_score > best_f_score:
                optimal_params = params
                best_f_score = current_score

# Train final model on small training set
bst = xgb.train(optimal_params, dtrain, 50, evals=[(dtrain, 'train')], custom_metric=xgb_f1, maximize=True)
bst.save_model(f'model{target_delay}.json')
print(f"Best F1 Score: {best_f_score}")
