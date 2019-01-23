from __future__ import print_function

import numpy as np
import pickle
import sys, os
from copy import deepcopy
from glob import glob
from random import shuffle
from FeatureExtractor import FeatureExtractor
from helpers import *
from sklearn.metrics import confusion_matrix
from scipy import stats
from DST import DST
import matplotlib.pyplot as plt
plt.rcdefaults()
plt.ioff()

####################
## Initialization ##
####################

## Global constants
ENABLE_FINGERS = True
MULTIPLIER = 1 ## TODO: Verify with 8. top5 is less than top1.
DISPLAY = False
WRITE_FLAG = True
LEXICON_ID = 'L8'
TASK_ID = 2

## Paths and variables
skel_folder_path = r'G:\AHRQ\Study_IV\NewData2\\' + LEXICON_ID
pickle_base_path = r'H:\\AHRQ\\Study_IV\\Data\\Data_cpm_new\\fingers'
pickle_file_suffix = '_fingers_from_hand_base_equate_dim_subsample.pkl'
out_filename_suffix = '_data.pickle'
task_command_path = r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\Commands\commands_t' + str(TASK_ID) + '.json'
full_command_path = r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\commands.json'
pickle_path = os.path.join(pickle_base_path,os.path.basename(skel_folder_path))
fingers_pkl_fname = os.path.basename(skel_folder_path) + pickle_file_suffix

## Subject Variables
all_subject_ids = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
eliminate_subject_id = 'S6'
#######################

############################
### Ignore some comamnds ###
############################
## The command ids to ignore
all_commands = json_to_dict(full_command_path).keys()
task_commands = json_to_dict(task_command_path).keys()
ignore_command_ids_list = list(set(all_commands).difference(set(task_commands)))

## Find out pickle filename
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)
out_pkl_fname = os.path.join(dirname, fileprefix + out_filename_suffix)

## Process Skeleton Data - Generate I/O
annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
fe = FeatureExtractor(json_param_path = 'param.json')
print('Generating IO: ', end = '')
## Generate skeleton input and output for training
out = fe.generate_io(skel_folder_path, annot_folder_path)
print('DONE !!!')

## Extract some variables from fe object
num_points = fe.fixed_num_frames
num_fingers = fe.num_fingers
id_to_labels = fe.id_to_labels
skel_file_order = deepcopy(fe.skel_file_order)
dominant_types_order = deepcopy(fe.dominant_type)
try:
	assert len(dominant_types_order) == len(skel_file_order), 'ERROR! MISMATCH'
except AssertionError as error:
	print(error)
	sys.exit()

## Extract from out object
body_data_input = deepcopy(out['data_input'])
data_output = deepcopy(out['data_output'])
hand_data_input = None
combined_data_input = None

## Transforms to task specific scenario
old_to_new, new_to_old, cmd_flags = remove_some_classes(deepcopy(data_output), id_to_labels, ignore_command_ids_list)
fe.update_new_to_old_ids(new_to_old)
num_new_classes = len(new_to_old)

if(ENABLE_FINGERS):
	## Appending finger lengths with dominant_hand first
	print('Appending finger lengths: ', end = '')
	with open(os.path.join(pickle_path, fingers_pkl_fname), 'rb') as fp:
		fingers_data = pickle.load(fp)
	data_merge=[]
	for idx,txt_file in enumerate(fe.skel_file_order):
		key = os.path.splitext(txt_file)[0].split('_')[:-1]
		s='_'
		key=s.join(key)
		dom_type=fe.dominant_type[idx]
		for idx1, line in enumerate(np.round(fingers_data.get(key),4)):
			if dom_type[idx1]==1:data_merge.append(line)
			else:
				gesture_shuffle=[]
				gesture=np.array(line).reshape(num_points,int(len(line)/num_points))
				for frame in gesture:
					gesture_shuffle.append(frame[num_fingers:].tolist()+frame[:num_fingers].tolist())
				data_merge.append(np.array(gesture_shuffle).flatten().tolist())

	hand_data_input = deepcopy(np.array(data_merge))
	print('Hand Data: ', hand_data_input.shape, end = ' : ')
	combined_data_input = np.concatenate([body_data_input, hand_data_input], axis = 1)
	print('DONE !!!')
else:
	combined_data_input = body_data_input

## Plotting histogram - No. of instances per class
if(DISPLAY): plot_class_hist(fe)

## Leave One Subject Out - Create IDs
subject_name_order = np.array([fname.split('_')[2] for fname in skel_file_order])
partial_train_subject_flags = (subject_name_order != eliminate_subject_id)
subject_flags = []
for idx, dom_types_list in enumerate(dominant_types_order):
	subject_flags += [partial_train_subject_flags[idx]]*len(dom_types_list)
subject_flags = np.array(subject_flags)

def train_test(data_in, data_out, inst_var_name, display = False):
	st = time.time()
	t_data_in, t_data_out = deepcopy(data_in), deepcopy(data_out)
	train_flags = np.logical_and(cmd_flags, subject_flags)
	test_flags = np.logical_and(cmd_flags, np.logical_not(subject_flags))
	## Leave one subject out
	train_data_input = t_data_in[train_flags, :]
	train_data_output = modify_output_indices(t_data_out, old_to_new, train_flags)
	print('New no. of classes: ', train_data_output.shape[1])
	## Left out subject is the testing data
	test_data_input = t_data_in[test_flags, :]
	test_data_output = modify_output_indices(t_data_out, old_to_new, test_flags)
	X, Y = augment_data(train_data_input, train_data_output, multiplier = MULTIPLIER)
	ret = fe.run_svm(X, Y, test_data_input, test_data_output, train_per = 0.80, inst_var_name = inst_var_name, display = DISPLAY)
	prob = fe.__dict__[inst_var_name].predict_proba(test_data_input)
	ret['prob'] = prob
	pred_output = np.argmax(prob, axis = 1)
	true_output = np.argmax(test_data_output, axis = 1)
	print('Time taken: %.04f seconds'%(time.time()-st))
	return ret, pred_output, true_output

## Only Body
print('\nBody ====> SVM')
body_ret, body_pred_output, true_test_output = train_test(body_data_input, data_output, 'svm_clf', DISPLAY)
print('DONE !!! Storing variable in svm_clf')

if(ENABLE_FINGERS):
	## Only Hand
	print('\nHand ====> SVM')
	hand_ret, hand_pred_output, _ = train_test(hand_data_input, data_output, 'svm_clf_hand', DISPLAY)
	print('DONE !!! Storing variable in svm_clf_hand')

	## Body + Hands
	print('\nBody + Hand ====> SVM')
	full_ret, full_pred_output, _ = train_test(combined_data_input, data_output, 'svm_clf_both', DISPLAY)
	print('DONE !!! Storing variable in svm_clf_both')

	print('\nJOINT Prediction ====> Predicted label is one ATLEAST one of the models')
	joint_predictions = np.concatenate((body_pred_output.reshape(1,-1), full_pred_output.reshape(1,-1), hand_pred_output.reshape(1,-1)), axis = 0).T ##

	# temp = np.sum(joint_predictions.T == true_test_output, axis = 0) > 0
	# print('Top 1 - Combined Acc of three classifiers - %.04f'%np.mean(temp))
	# print('Note. True label is predicted correctly by one of the three classifiers. This is INCORRECT!!')

	print('\nJOINT Prediction ====> ARG MODE is the final predicted label')
	joint_predictions = np.concatenate((body_pred_output.reshape(1,-1), full_pred_output.reshape(1,-1), hand_pred_output.reshape(1,-1)), axis = 0).T ##
	temp = (stats.mode(joint_predictions, axis = 1)[0].flatten() == true_test_output)
	print('Top 1 - Combined Acc of three classifiers - %.04f'%np.mean(temp))
	print('Note. Arg Mode is the final class lablel. This is CORRECT!!')

	#### Using DST for predictions ####
	print('\nDST =========> Prediction')
	dst = DST(num_models = 3, num_classes = num_new_classes)
	prob_mat = np.zeros((full_ret['prob'].shape[0], full_ret['prob'].shape[1], 3))
	prob_mat[:,:,0] = full_ret['prob']
	prob_mat[:,:,1] = body_ret['prob']
	prob_mat[:,:,2] = hand_ret['prob']
	pred_output = dst.batch_predict(prob_mat)
	temp = (pred_output == true_test_output)
	print('Top 1 - DST - Combined Acc of three classifiers - %.04f'%np.mean(temp))

if(WRITE_FLAG):
	print('\nSaving in: ', out_pkl_fname)
	with open(out_pkl_fname, 'wb') as fp:
		pickle.dump({'fe': fe, 'out': out}, fp)
