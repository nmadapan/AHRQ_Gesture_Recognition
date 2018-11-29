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

## Skeleton variables/paths
skel_folder_path = r'F:\AHRQ\Study_IV\NewData\L2'

## Fingers variables/paths
ENABLE_FINGERS = True
MULTIPLIER = 1
pickle_base_path = r'F:\AHRQ\Study_IV\Data\Data_cpm_new\fingers'
pickle_path = os.path.join(pickle_base_path, os.path.basename(skel_folder_path))
fingers_pkl_fname = os.path.basename(skel_folder_path)+'_fingers_from_hand_base_equate_dim_subsample.pkl'

#####################

## Annotations for skeleton files
annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)
## Save the trained classifier in this file
out_pkl_fname = os.path.join(dirname, fileprefix+'_data.pickle')

## Instantiate FeatureExtractor
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

############################
### Ignore some comamnds ###
############################
## The command ids to ignore
ignore_command_ids_list = ['5_3', '5_4', '7_0', '7_1', '7_2', '8_0', '8_1', '8_2'] ## For Task 2
# ignore_command_ids_list = ['5_3', '5_4', '7_0', '7_1', '7_2', '8_0', '8_1', '8_2'] ## For Task 3

if(ENABLE_FINGERS):
	# # ## Appending finger lengths with dominant_hand first
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
			if dom_type[idx1]==1:data_merge.append(line)
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

## Plot Histogram - No. of instances per class
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
#plt.show()

## Only Body
print('\nBody ====> SVM')
st = time.time()
t_data_in, t_data_out = deepcopy(body_data_input), deepcopy(data_output)
old_to_new, cmd_flags = remove_some_classes(t_data_out, id_to_labels, ignore_command_ids_list)
t_data_in = t_data_in[cmd_flags, :]
t_data_out = modify_output_indices(t_data_out, old_to_new, cmd_flags)
X, Y = augment_data(t_data_in, t_data_out, multiplier = MULTIPLIER)
result = fe.run_svm(X, Y, train_per = 0.60, inst_var_name = 'svm_clf_body')
print('Time taken: %.04f seconds'%(time.time()-st))
print('DONE !!! Storing variable in svm_clf_body')

if(ENABLE_FINGERS):
	## Only Hand
	print('\nHand ====> SVM')
	st = time.time()
	t_data_in, t_data_out = deepcopy(hand_data_input), deepcopy(data_output)
	old_to_new, cmd_flags = remove_some_classes(t_data_out, id_to_labels, ignore_command_ids_list)
	t_data_in = t_data_in[cmd_flags, :]
	t_data_out = modify_output_indices(t_data_out, old_to_new, cmd_flags)
	X, Y = augment_data(t_data_in, t_data_out, multiplier = MULTIPLIER)
	result = fe.run_svm(X, Y, train_per = 0.60, inst_var_name = 'svm_clf_hand')
	print('Time taken: %.04f seconds'%(time.time()-st))
	print('DONE !!! Storing variable in svm_clf_hand')

	## combined Data
	print('\nBody + Hand ====> SVM')
	st = time.time()
	t_data_in, t_data_out = deepcopy(combined_data_input), deepcopy(data_output)
	old_to_new, cmd_flags = remove_some_classes(t_data_out, id_to_labels, ignore_command_ids_list)
	t_data_in = t_data_in[cmd_flags, :]
	t_data_out = modify_output_indices(t_data_out, old_to_new, cmd_flags)
	X, Y = augment_data(combined_data_input, data_output, multiplier = MULTIPLIER)
	result = fe.run_svm(X, Y, train_per = 0.60, inst_var_name = 'svm_clf')
	print('Time taken: %.04f seconds'%(time.time()-st))
	print('DONE !!! Storing variable in svm_clf')

print('\nSaving in: ', out_pkl_fname)
with open(out_pkl_fname, 'wb') as fp:
	pickle.dump({'fe': fe, 'out': out}, fp)
