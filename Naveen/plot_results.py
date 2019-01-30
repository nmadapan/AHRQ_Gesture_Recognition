from __future__ import print_function

import numpy as np
from glob import glob
import os, sys
from scipy import stats
from helpers import *
import pickle
import argparse
from matplotlib import pyplot as plt
import cv2

####################
## Initialization ##
####################
LEXICON_ID = 'L2'
TASK_ID = 1
NUM_SUBJECTS = 12

##########################
#####   PARSING       ####
##########################
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--task_id",
					default=TASK_ID,
					help=("Task ID. Should be 1 or 2."))
parser.add_argument("-l", "--lexicon_id",
					default=LEXICON_ID,
					help=("Lexicon ID string. Format: 'L2'."))
args = vars(parser.parse_args())
TASK_ID = args['task_id']
LEXICON_ID = args['lexicon_id']

out_base_dir = 'Backup\\test\\all_commands'
res_pkl_name = LEXICON_ID + '_' + str(TASK_ID) + '_result.pickle'
out_res_pkl_fname = os.path.join('G:\\AHRQ\\Study_IV\\NewData2\\', res_pkl_name)
print(out_res_pkl_fname)

######################
## Global Variables ##
######################
subject_keys = map(lambda x: 'S' + x, map(str, range(1, NUM_SUBJECTS + 1)))
clf_keys = ['body', 'hand', 'body_plus_hand']
overall_acc_keys = ['arg_mode', 'dst']
# clf_dict_keys = ['train_acc', 'test_acc_top5', 'test_acc_top3', 'test_acc_top1', 'valid_acc']
clf_dict_keys = ['test_acc_top3', 'test_acc_top1']

## Find lexicon ID from pickle name
lexicon_id = os.path.splitext(os.path.basename(out_res_pkl_fname))[0].split('_')[0]

## Read the pickle file
with open(out_res_pkl_fname, 'rb') as fp:
	result = pickle.load(fp)['result']

# print_dict(result)

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
dir_path = os.path.join(out_base_dir, lexicon_id + '_T'+str(TASK_ID))
if(not os.path.isdir(dir_path)): os.makedirs(dir_path)
fname = os.path.join(out_base_dir, os.path.join(lexicon_id + '_T'+str(TASK_ID), 'overall_accuracies' + '.jpg'))
custom_bar(acc_values, ylim = [0, 1.05], xticks = subject_values, legends = overall_acc_keys,\
	title = 'Overall Accuracies', write_path = fname)

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
	fname = os.path.join(out_base_dir, os.path.join(lexicon_id + '_T'+str(TASK_ID), clf_key + '.jpg'))
	custom_bar(acc_values, ylim = [0, 1.05], xticks = subject_values, legends = clf_dict_keys, \
		title = 'Classifier Specific Accuracies', write_path = fname)

##################################
###### AVERAGE ACCURACIES ########
##################################
dt = {}
for subject_id in subject_keys:
	for clf_key in clf_keys:
		dt[clf_key] = {}
		for clf_dict_key in clf_dict_keys:
			dt[clf_key][clf_dict_key] = []

for subject_id in subject_keys:
	res = result[subject_id]
	for clf_key in clf_keys:
		for clf_dict_key in clf_dict_keys:
			dt[clf_key][clf_dict_key].append(res[clf_key][clf_dict_key])

avg_res = {}
for clf_key, clf_res in dt.items():
	avg_res[clf_key] = {}
	for clf_dict_key in clf_dict_keys:
		avg_res[clf_key][clf_dict_key] = [np.mean(clf_res[clf_dict_key]), np.std(clf_res[clf_dict_key])]
print_dict(avg_res)
