from __future__ import print_function

import numpy as np
from glob import glob
import os, sys
from scipy import stats
from helpers import print_dict, custom_bar
import pickle
from matplotlib import pyplot as plt
import cv2

####################
## Initialization ##
####################
out_base_dir = 'Backup\\test'
out_res_pkl_fname = 'H:\AHRQ\Study_IV\NewData\L8_result.pickle'

######################
## Global Variables ##
######################
subject_keys = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
clf_keys = ['body', 'hand', 'body_plus_hand']
overall_acc_keys = ['arg_mode', 'atleast_one', 'dst']
clf_dict_keys = ['train_acc', 'test_acc_top4', 'test_acc_top3', 'test_acc_top1', 'valid_acc']

## Find lexicon ID from pickle name
lexicon_id = os.path.splitext(os.path.basename(out_res_pkl_fname))[0].split('_')[0]

## Read the pickle file
with open(out_res_pkl_fname, 'rb') as fp:
	result = pickle.load(fp)['result']

print_dict(result)

#################################
###### OVERALL ACCURACIES #######
#################################
subject_values = []
acc_values = []
for key, value in result.items():
	subject_values.append(key)
	temp = []
	for overall_acc_key in overall_acc_keys:
		temp.append(value[overall_acc_key])
	acc_values.append(temp)
acc_values = np.array(acc_values).T.tolist()
## Writing to the file
dir_path = os.path.join(out_base_dir, lexicon_id)
if(not os.path.isdir(dir_path)): os.makedirs(dir_path)
fname = os.path.join(out_base_dir, os.path.join(lexicon_id, 'overall_accuracies' + '.jpg'))
custom_bar(acc_values, ylim = [0, 1.05], xticks = subject_values, legends = overall_acc_keys, title = 'Overall Accuracies', write_path = fname)


#################################
#### CLF SPECIFIC ACCURACIES ####
#################################
for clf_key in clf_keys:
	acc_values = []
	subject_values = []
	for key, value in result.items():
		subject_values.append(key)
		temp = []
		for clf_dict_key in clf_dict_keys:
			temp.append(value[clf_key][clf_dict_key])
		acc_values.append(temp)
	acc_values = np.array(acc_values).T.tolist()
	## Writing to the file
	fname = os.path.join(out_base_dir, os.path.join(lexicon_id, clf_key + '.jpg'))
	custom_bar(acc_values, ylim = [0, 1.05], xticks = subject_values, legends = clf_dict_keys, title = 'Classifier Specific Accuracies', write_path = fname)