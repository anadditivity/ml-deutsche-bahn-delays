import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# This file will contain test runs for xgboost
# we try this out since it was presented in homework 5 and it might give some better results

data = pd.read_csv('connections_v3.csv')
print(data.shape)

# For the first tests we will just try to make the boolean decision whether the train was delayed or not
# So we will create a new column from dst_arrival_delay that just checks if the value is larger than 0 or not
data['delayed'] = (data['dst_arrival_delay'] > 0). astype(int)
data = data[data.columns.drop(list(data.filter(regex='dst_arrival_delay')))]

# Here I will select 1000 datapoints that were delayed and 10000 datapoints that were on time
positive_sample = data[data['delayed'] == 1].sample(n=1000, frac=None, axis=0, random_state=13)
negative_sample = data[data['delayed'] == 0].sample(n=1000, frac=None, axis=0, random_state=13)
train_sub = pd.concat([positive_sample, negative_sample], axis=0)
train_sub.sort_index(inplace=True)

X_train = train_sub.drop('delayed', axis=1)
y_train = train_sub['delayed']

time_features = ['start_timestamp', 'src_arrival_plan', 'dst_arrival_plan']

for col in time_features:
  X_train[col] = pd.to_datetime(X_train[col])

  X_train[col + '_sec'] = X_train[col].dt.second
  X_train[col + '_minute'] = X_train[col].dt.minute
  X_train[col + '_hour'] = X_train[col].dt.hour
  X_train[col + '_day'] = X_train[col].dt.dayofweek
  X_train = X_train.drop(col, axis=1)

for col in X_train.columns:
  if not pd.api.types.is_numeric_dtype(X_train[col]):
    # turn all non numeric features into categorical features 
    X_train[col] = X_train[col].astype('category')

    # use one-hot-encoding for these categorical features
    data_dum = pd.get_dummies(X_train[col], col, dtype='int')
    X_train = pd.concat([X_train, data_dum], axis=1)
    X_train = X_train.drop(col, axis=1)

X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, random_state = 13, test_size = 0.10)
X_train_small, X_val, y_train_small, y_val = train_test_split(X_train, y_train, random_state = 13, test_size = 0.20)
# Since this is just some basic testing we won't use any cross validation

print(X_train_small.shape)
print(X_val.shape)
print(X_test.shape)
print(y_train_small.shape)
print(y_val.shape)
print(y_test.shape)

dtrain = xgb.DMatrix(X_train, label=y_train)
dtrain_small = xgb.DMatrix(X_train_small, label=y_train_small)
dval = xgb.DMatrix(X_val, label=y_val)
dtest = xgb.DMatrix(X_test, label=y_test)

def xgb_f1(preds, labels, threshold=0.5):
  # This function will be used so the model actually optimizes the f-score and not the accuracy, as our real data set is heavily imbalanced
  label_list = labels.get_label()
  pred_list = (preds > threshold).astype(int)
  return 'f1', f1_score(label_list, pred_list, pos_label = 1)

optimal_params = 0
best_f_score = 0

for learning_rate in np.linspace(0.1,1.0,10):
  for max_depth in range(3,10):
    for child_weight in np.linspace(0.5,2,15):
      learning_rate = np.float32(learning_rate)
      params = {
        "booster": 'gbtree', 
        "eta": learning_rate,
        "objective": 'binary:logistic',
        "seed":111,
        "max_depth": max_depth,
        "min_child_weight": child_weight,
        "sub_sampling": 0.9
      }

      eval_list = [(dtrain_small, 'train'), (dval, 'eval')]

      bst = xgb.train(params, dtrain_small, 50, evals=eval_list, custom_metric=xgb_f1, maximize=True)

      preds = (bst.predict(dtest) > 0.5).astype(int) # We could also experiment with different cutoff points
      current_score = f1_score(y_test, preds, pos_label=1) 
      print(current_score)
      if current_score > best_f_score:
        optimal_params = params
        best_f_score = current_score


bst = xgb.train(optimal_params, dtrain, 50, evals=eval_list, custom_metric=xgb_f1, maximize=True)
bst.save_model('model.json')
print(f1_score(y_test, preds, pos_label=1))
