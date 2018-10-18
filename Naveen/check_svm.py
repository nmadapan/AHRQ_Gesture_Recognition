import os, sys, time
import numpy as np
import pickle

trained_pkl_file = r'H:\AHRQ\Study_IV\Data\Data\L6_data.pickle'

with open(trained_pkl_file, 'rb') as fp:
	res = pickle.load(fp)
	fe, out = res['fe'], res['out']

print fe.svm_clf

# Train Predict
pred_output = fe.svm_clf.predict(out['data_input'])
train_acc = float(np.sum(pred_output == np.argmax(out['data_output'], axis = 1))) / pred_output.size
print 'Train Acc: ', train_acc
