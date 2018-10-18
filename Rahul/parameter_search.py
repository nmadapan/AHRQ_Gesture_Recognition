import numpy as np 
import sklearn
from sklearn.svm import SVC
from sklearn.model_selection import RandomizedSearchCV


X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
y = np.array([1, 1, 2, 2])

def fit(X,y):

	clf = SVC(decision_function_shape='ova')

	parameter_candidates = {'C': range(1,200,10), 'gamma': [0.1, 0.01, 0.001, 0.0001], 'kernel': ['rbf','linear','poly','sigmoid']}

	# for AHRQ data cv shoould atleast be 4
	clf_rv = RandomizedSearchCV(estimator=clf, param_distributions=parameter_candidates,\
			 random_state=1, n_iter=10
			 ,cv=2, verbose=0, n_jobs=-1)

	clf_rv.fit(X, y)
	print(clf_rv.best_params_)

if __name__ == "__main__":
	fit(X,y)
	
