from __future__ import print_function

import numpy as np
import pickle
import sys, os
from copy import deepcopy
from glob import glob
from random import shuffle
from FeatureExtractor import FeatureExtractor
from helpers import *
import matplotlib.pyplot as plt
import time
plt.rcdefaults()

####################
## Initialization ##
####################

## Global constants
ENABLE_FINGERS = True
MULTIPLIER = 1
TASK_ID = 1
LEXICON_ID = 'L6'
DISPLAY = False
WRITE_FLAG = True

## Paths and variables
skel_folder_path = r'G:\\AHRQ\\Study_IV\\NewData2\\' + LEXICON_ID
pickle_base_path = r'H:\\AHRQ\\Study_IV\\Data\\Data_cpm_new\\fingers'
pickle_file_suffix = '_fingers_from_hand_base_equate_dim_subsample.pkl'
out_filename_suffix = '_data.pickle'
task_command_path = r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\Commands\commands_t' + str(TASK_ID) + '.json'
full_command_path = r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\commands.json'
pickle_path = os.path.join(pickle_base_path, os.path.basename(skel_folder_path))
fingers_pkl_fname = os.path.basename(skel_folder_path) + pickle_file_suffix
#####################

############################
### Ignore some comamnds ###
############################
## The command ids to ignore
all_commands = json_to_dict(full_command_path).keys()
task_commands = json_to_dict(task_command_path).keys()
ignore_command_ids_list = list(set(all_commands).difference(set(task_commands)))

## Annotations for skeleton files
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)
## Save the trained classifier in this file
out_pkl_fname = os.path.join(dirname, fileprefix + out_filename_suffix)

## Instantiate FeatureExtractor
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

## Extract from out dictionary
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
		for idx1,line in enumerate(np.round(fingers_data.get(key),4)):
			if dom_type[idx1]==1: data_merge.append(line)
			else:
				gesture_shuffle=[]
				gesture=np.array(line).reshape(num_points,int(len(line)/num_points))
				for frame in gesture:
					gesture_shuffle.append(frame[num_fingers:].tolist()+frame[:num_fingers].tolist())
				data_merge.append(np.array(gesture_shuffle).flatten().tolist())

	# 		# data_merge.append(line)
	hand_data_input = deepcopy(np.array(data_merge))
	combined_data_input = np.concatenate([body_data_input, hand_data_input], axis = 1)
	print('DONE !!!')
else:
	combined_data_input = body_data_input

def train_test(data_in, data_out, inst_var_name, display = False):
	st = time.time()
	t_data_in, t_data_out = deepcopy(data_in), deepcopy(data_out)
	t_data_in = t_data_in[cmd_flags, :]
	t_data_out = modify_output_indices(t_data_out, old_to_new, cmd_flags)
	X, Y = augment_data(t_data_in, t_data_out, multiplier = MULTIPLIER)
	result = fe.run_svm(X, Y, train_per = 0.60, inst_var_name = inst_var_name, display = DISPLAY)
	print('Time taken: %.04f seconds'%(time.time()-st))
	return result

## Plotting histogram - No. of instances per class
if(DISPLAY): plot_class_hist(fe)

## Only Body
print('\nBody ====> SVM')
train_test(body_data_input, data_output, 'svm_clf', display = DISPLAY)
print('DONE !!! Storing variable in svm_clf')

if(ENABLE_FINGERS):
	## Only Hand
	print('\nHand ====> SVM')
	train_test(hand_data_input, data_output, 'svm_clf_hand', display = DISPLAY)
	print('DONE !!! Storing variable in svm_clf_hand')

	## combined Data
	print('\nBody + Hand ====> SVM')
	train_test(combined_data_input, data_output, 'svm_clf_both', display = DISPLAY)
	print('DONE !!! Storing variable in svm_clf_both')

if(WRITE_FLAG):
	print('\nSaving in: ', out_pkl_fname)
	with open(out_pkl_fname, 'wb') as fp:
		pickle.dump({'fe': fe, 'out': out}, fp)
