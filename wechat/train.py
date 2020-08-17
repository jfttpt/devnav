# -*- coding: utf-8 -*-


from .utils import *
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score, classification_report
from sklearn.model_selection import cross_val_score
import joblib

filename = "devnav/wechat/dataset_v7.csv"
columns = ['application_num', 'destination_num', 'sent_sum', 'sent_avg', 'recv_sum', 'recv_avg',
           'flows_sum', 'flows_avg', 'protocol_num', 'port_num', 'activeSeconds_sum', 'activeSeconds_avg',
           'label']
X_train, X_test, y_train, y_test = load_dataset(filename, columns)
print(X_train)
print(y_train)
print(X_test)
print(y_test)
ss = StandardScaler()
X_train_scaled = ss.fit_transform(X_train)
X_test_scaled = ss.transform(X_test)
print(X_train_scaled.shape, X_test_scaled.shape)
y_train = np.array(y_train)
y_test = np.array(y_test)

rfc = RandomForestClassifier(oob_score=True, random_state=10, n_estimators=100)
rfc.fit(X_train_scaled, y_train)

print(rfc.score(X_train_scaled, y_train))
print(rfc.score(X_test_scaled, y_test))
scores = cross_val_score(rfc, X_test_scaled, y_test, cv=5)
print(scores)

y_pred_test = rfc.predict(X_test_scaled)
print(classification_report(y_test, y_pred_test))

joblib.dump(rfc, 'devnav/wechat/save/rfc9.pkl')
