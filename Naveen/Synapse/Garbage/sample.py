import cv2
import numpy as np
import os, sys, time
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import math

"""
	Input Arguments:
		before, after: path to the image before right click, and after right click OR
		before, after: numpy image before right click, and after right click
		thresholds: tuple (x_thresh, y_thresh). thresholds in both x and y directions
		draw: True, display the bounding box. False, do not display
	Output Arguments:
		(x1, y1, x2, y2): where x1, y1 are top left corner and x2, y2 are bottom right corner
"""
def get_bbox(before, after, thresholds = None, draw = False, num_bins=20):
	if (type(before) != type(after)):
		return ValueError('before and after should have same type')
	if (isinstance(before, str)):
		if (not os.path.isfile(before)):
			sys.exit(before + ' does NOT exist')
		if (not os.path.isfile(after)):
			sys.exit(after + ' does NOT exist')
		before = cv2.imread(before)
		after = cv2.imread(after)
	elif (isinstance(before, np.ndarray)):
		assert before.ndim == 3 and after.ndim == 3, 'before and after needs to be rgb arrays'
		assert (before.shape[0] == after.shape[0]) and (before.shape[1] == after.shape[1]),\
			 'before and after arrays should be of same dimension'
	###########################
	#### Tuning Params ########
	noise_percentage = 0.25
	percentage_bins_for_mean = 0.5
	##########################

	noise_index = int(num_bins*noise_percentage)
	remaining_mean = int(math.ceil((num_bins - noise_index)*percentage_bins_for_mean))
	dif = cv2.cvtColor(np.uint8(np.abs(after - before)), cv2.COLOR_BGR2GRAY)
	# _, dif = cv2.threshold(dif,127,255,0)

	x_sum = np.mean(dif, axis = 0)
	y_sum = np.mean(dif, axis = 1)

	x_sum = medfilt(x_sum, 211)
	y_sum = medfilt(y_sum, 211)

	if (thresholds == None):
		frequencies, avg_hist_values = np.histogram(x_sum, bins = num_bins)
		sort_ids = np.argsort(frequencies[noise_index:])
		x_thresh = np.mean(avg_hist_values[noise_index+sort_ids[:remaining_mean]])

		# x_thresh = avg_hist_values[10]# np.argmin(frequencies)

		frequencies, avg_hist_values = np.histogram(y_sum, bins = num_bins)
		sort_ids = np.argsort(frequencies[noise_index:])
		y_thresh = np.mean(avg_hist_values[noise_index+sort_ids[:remaining_mean]])
	else:
		x_thresh = thresholds[0]
		y_thresh = thresholds[1]

	print x_thresh, y_thresh
	# plt.hist(y_sum, bins = 20)
	plt.plot(y_sum)
	plt.show()	
	# sys.exit(0)
	x_sum, y_sum = x_sum > x_thresh, y_sum > y_thresh

	x1, x2 = np.argmax(x_sum), x_sum.size - np.argmax(np.flip(x_sum, 0)) - 1
	y1, y2 = np.argmax(y_sum), y_sum.size - np.argmax(np.flip(y_sum, 0)) - 1

	if (draw):
		after = cv2.rectangle(after,(x1,y1),(x2,y2),(0,255,0),4)
		cv2.imshow('Frame', cv2.resize(after, None, fx=0.5, fy=0.5))
		cv2.waitKey(0)

	return (x1, y1, x2, y2)

after = 'after.png'
before = 'before.png'
x1, y1, x2, y2 = get_bbox(before, after, thresholds = None, draw = True)

# from __future__ import print_function
# import numpy as np
# import os, sys
# import random

# from sklearn import datasets
# from sklearn.cross_validation import train_test_split
# from sklearn.grid_search import GridSearchCV
# from sklearn.svm import SVC

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
