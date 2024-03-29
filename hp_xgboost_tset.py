import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
from random import shuffle
from xgboost.sklearn import XGBClassifier
from sklearn.model_selection import cross_val_score
import pickle
import time
from hyperopt import  fmin, tpe, hp, space_eval, rand, Trials, partial, STATUS_OK

def loadFile(fileName):
    data = pd.read_csv(fileName, header=None)
    data = data.values
    return data

data_file_name = '/Users/mac/code/data/iris.csv'
data = loadFile(data_file_name)
label = data[:, -1]
attrs = data[:, :-1]
labels = label.reshape((1, -1))
label = labels.tolist()[0]

minmaxscaler = MinMaxScaler()
attrs = minmaxscaler.fit_transform(attrs)
print(attrs)

index = list(range(0, len(label)))
shuffle(index)

trainIndex = index[:int(len(label)*0.7)]
print(len(trainIndex))
testIndex = index[int(len(label) * 0.7):]
print(len(testIndex))

attr_train = attrs[trainIndex, :]
attr_test = attrs[testIndex, :]
print(attr_train.shape)
print(attr_train)
print(attr_test.shape)

label_train = labels[:, trainIndex].tolist()[0]
label_test = labels[:, testIndex].tolist()[0]
print(len(label_train))
print(label_train)
print(len(label_test))

print(np.mat(label_train).reshape((-1, 1)).shape)


def GBM(argsDict):
    max_depth = argsDict['max_depth'] + 5
    n_estimators = argsDict['n_estimators'] * 5 + 50
    learning_rate = argsDict['learning_rate'] * 0.02 + 0.05
    subsample = argsDict['subsample'] * 0.1 + 0.7
    min_child_weight = argsDict['min_child_weight'] + 1

    print('max_depth:' + str(max_depth))
    print('n_estimator:' + str(n_estimators))
    print('learning_rate:' + str(learning_rate))
    print('subsample:' + str(subsample))
    print('min_child_weight:' + str(min_child_weight))


    global attr_train, label_train

    gbm = xgb.XGBClassifier(nthread=4,  #进程数
                            max_depth=max_depth,  # 最大深度
                            n_estimators=n_estimators,  # 树的数量
                            learning_rate= learning_rate, #cai'an
                            subsample=subsample,    #采样率
                            min_child_weight=min_child_weight,  # 孩子数
                            max_delta_step=10,      # 10步不降则停止
                            objective='binary:logistic')

    metric = cross_val_score(gbm, attr_train, label_train, cv=5, scoring='roc_auc').mean()
    print('metric:' + metric)
    print(-metric)



space = {'max_depth':hp.randint('max_depth', 15),
         'n_estimators':hp.randint('n_estimators', 10),
         'learning_rate':hp.randint('learning_rate', 6),
         'subsample':hp.randint('subsample', 4),
         'min_child_weight':hp.randint('min_child_weight', 5)}

algo = partial(tpe.suggest, n_startup_jobs=1)
best = fmin(GBM, space, algo=algo, max_evals=4)

print(best)
print(GBM(best))

