from __future__ import print_function

import numpy as np
import pickle
import sys, os
from copy import deepcopy
from glob import glob
from random import shuffle
from FeatureExtractor import FeatureExtractor
from helpers import skelfile_cmp
from sklearn.metrics import confusion_matrix
from scipy import stats
from DST import DST
import matplotlib.pyplot as plt
plt.rcdefaults()
plt.ioff()

####################
## Initialization ##
####################
## Fingers
ENABLE_FINGERS = True
display = False
write_flag = False

## Skeleton
skel_folder_path = r'H:\AHRQ\Study_IV\NewData\L2'

## Variables
all_subject_ids = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
eliminate_subject_id = 'S6'
out_filename_suffix = '_data.pickle'

## CPM
pickle_base_path1 = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers'
pickle_file_suffix = '_fingers_from_hand_base_equate_dim_subsample.pkl'

pickle_path1 = os.path.join(pickle_base_path1,os.path.basename(skel_folder_path))
fingers_pkl_fname = os.path.basename(skel_folder_path) + pickle_file_suffix
#######################

## Find out pickle filename
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)
out_pkl_fname = os.path.join(dirname, fileprefix + out_filename_suffix)

## Process Skeleton Data - Generate I/O
annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
fe = FeatureExtractor(json_param_path = 'param.json')
print('Generating IO: ', end = '')
out = fe.generate_io(skel_folder_path, annot_folder_path)
print('DONE !!!')
body_data_input = deepcopy(out['data_input'])
hand_data_input = None
combined_data_input = None

## Extract some variables from fe object
num_points = fe.fixed_num_frames
num_fingers = fe.num_fingers
skel_file_order = deepcopy(fe.skel_file_order)
dominant_types_order = deepcopy(fe.dominant_type)
assert len(dominant_types_order) == len(skel_file_order), 'ERROR! MISMATCH'

if(ENABLE_FINGERS):
	# # ## Appending finger lengths with dominant_hand first
	print('Appending finger lengths: ', end = '')
	with open(os.path.join(pickle_path1, fingers_pkl_fname), 'rb') as fp:
		fingers_data = pickle.load(fp)
	data_merge=[]
	for idx,txt_file in enumerate(fe.skel_file_order):
		key = os.path.splitext(txt_file)[0].split('_')[:-1]
		s='_'
		key=s.join(key)
		dom_type=fe.dominant_type[idx]
		for idx1,line in enumerate(np.round(fingers_data.get(key),4)):
			if dom_type[idx1]==1:data_merge.append(line)
			else:
				gesture_shuffle=[]
				gesture=np.array(line).reshape(num_points,int(len(line)/num_points))
				for frame in gesture:
					gesture_shuffle.append(frame[num_fingers:].tolist()+frame[:num_fingers].tolist())
				data_merge.append(np.array(gesture_shuffle).flatten().tolist())
				
	hand_data_input = deepcopy(np.array(data_merge))
	full_data_input = np.concatenate([body_data_input, hand_data_input], axis = 1)
	print('DONE !!!')

## Plotting histogram - No. of instances per class
if(display):
	objects = tuple(fe.inst_per_class.keys())
	y_pos = np.arange(len(objects))
	performance = fe.inst_per_class.values()
	plt.figure()
	plt.bar(y_pos, performance, align='center', alpha=0.5)
	# plt.xticks(y_pos, objects)
	plt.xlabel('Class IDs')
	plt.ylabel('No. of instances')
	plt.title('No. of instances per class')
	plt.grid(True)
	plt.show()

## Leave One Subject Out - Create IDs
subject_name_order = np.array([fname.split('_')[2] for fname in skel_file_order])
partial_train_subject_flags = (subject_name_order != eliminate_subject_id)
all_train_flags = []
for idx, dom_types_list in enumerate(dominant_types_order):
	all_train_flags += [partial_train_subject_flags[idx]]*len(dom_types_list)
all_train_flags = np.array(all_train_flags)

## Body + Hands
print('\nBody + Hand ====> SVM')
data_input, data_output = deepcopy(full_data_input), deepcopy(out['data_output'])
train_data_input = data_input[all_train_flags, :]
train_data_output = data_output[all_train_flags, :]
test_data_input = data_input[np.logical_not(all_train_flags), :]
test_data_output = data_output[np.logical_not(all_train_flags), :]
fe.run_svm(train_data_input, train_data_output, test_data_input, test_data_output, train_per = 0.80, inst_var_name = 'svm_clf', display = display)
full_prob = fe.svm_clf.predict_proba(test_data_input)
full_pred_output = np.argmax(full_prob, axis = 1)
print('DONE !!! Storing variable in svm_clf')

## Only Body
print('\nBody ====> SVM')
data_input, data_output = deepcopy(body_data_input), deepcopy(out['data_output'])
train_data_input = data_input[all_train_flags, :]
train_data_output = data_output[all_train_flags, :]
test_data_input = data_input[np.logical_not(all_train_flags), :]
test_data_output = data_output[np.logical_not(all_train_flags), :]
fe.run_svm(train_data_input, train_data_output, test_data_input, test_data_output, train_per = 0.80, inst_var_name = 'svm_clf_body', display = display)
body_prob = fe.svm_clf_body.predict_proba(test_data_input)
body_pred_output = np.argmax(body_prob, axis = 1)
print('DONE !!! Storing variable in svm_clf_body')

## Only Hand
print('\nHand ====> SVM')
data_input, data_output = deepcopy(hand_data_input), deepcopy(out['data_output'])
train_data_input = data_input[all_train_flags, :]
train_data_output = data_output[all_train_flags, :]
test_data_input = data_input[np.logical_not(all_train_flags), :]
test_data_output = data_output[np.logical_not(all_train_flags), :]
fe.run_svm(train_data_input, train_data_output, test_data_input, test_data_output, train_per = 0.80, inst_var_name = 'svm_clf_hand', display = display)
hand_prob = fe.svm_clf_hand.predict_proba(test_data_input)
hand_pred_output = np.argmax(hand_prob, axis = 1)
print('DONE !!! Storing variable in svm_clf_hand')

print('\nJOINT Prediction ====> Predicted label is one ATLEAST one of the models')
joint_predictions = np.concatenate((body_pred_output.reshape(1,-1), full_pred_output.reshape(1,-1), hand_pred_output.reshape(1,-1)), axis = 0).T ##
temp = np.sum(joint_predictions == np.argmax(test_data_output, axis = 1).reshape(-1, 1), axis = 1) > 0
print('Top 1 - Combined Acc of three classifiers - %.04f'%np.mean(temp))
print('Note. True label is predicted correctly by one of the three classifiers. This is INCORRECT!!')

print('\nJOINT Prediction ====> ARG MODE is the final predicted label')
joint_predictions = np.concatenate((body_pred_output.reshape(1,-1), full_pred_output.reshape(1,-1), hand_pred_output.reshape(1,-1)), axis = 0).T ##
temp = (stats.mode(joint_predictions, axis = 1)[0].flatten() == np.argmax(test_data_output, axis = 1))
print('Top 1 - Combined Acc of three classifiers - %.04f'%np.mean(temp))
print('Note. Arg Mode is the final class lablel. This is CORRECT!!')

#### Using DST for predictions ####
print('\nDST =========> Prediction')
dst = DST(num_models = 3, num_classes = test_data_output.shape[1])
prob_mat = np.zeros((full_prob.shape[0], full_prob.shape[1], 3))
prob_mat[:,:,0] = full_prob
prob_mat[:,:,1] = body_prob
prob_mat[:,:,2] = hand_prob
pred_output = dst.batch_predict(prob_mat)
temp = (pred_output == np.argmax(test_data_output, axis = 1))
print('Top 1 - DST - Combined Acc of three classifiers - %.04f'%np.mean(temp))

if(write_flag):
	print('\nSaving in: ', out_pkl_fname)
	with open(out_pkl_fname, 'wb') as fp:
		pickle.dump({'fe': fe, 'out': out}, fp)