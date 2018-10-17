from __future__ import print_function
import numpy as np
import os, sys
import random

from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC

# print(__doc__)

# Loading the digits dataset
# digits = datasets.load_digits()

# n_samples = len(digits.images)

# X = digits.images.reshape((n_samples, -1))
# y = digits.target

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.5, random_state = 0)

# ## Set the parameters by cross-validation
# param1 = {'kernel': ['rbf'], 'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]}
# param2 = {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}
# tuned_parameters = [param1, param2]

# scores = ['precision', 'recall']

# print(y_train)

# for score in scores:
#     print('# Tuning hyper parameters for %s \n'%score)
#     clf = GridSearchCV(SVC(C=1), tuned_parameters, cv = 5, scoring = score)
#     clf.fit(X_train, y_train)

#     print('Best parameters set found on development set: \n')
#     print(clf.best_estimator_)
#     print('Grud scores on development set: \n')
#     for params, mean_score, t_scores in clf.grid_scores_:
#         print("%0.3f (+/-%0.03f) for %r" \
#               % (mean_score, t_scores.std() / 2, params))
#     print('\n')

#     print("Detailed classification report:")
#     print()
#     print("The model is trained on the full development set.")
#     print("The scores are computed on the full evaluation set.")
#     print()

#     y_true, y_pred = y_test, clf.predict(X_test)
#     print(classification_report(y_true, y_pred))
#     print()
