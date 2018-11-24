from __future__ import print_function

import numpy as np
import pickle
import sys, os
from copy import deepcopy
from glob import glob
from random import shuffle
from FeatureExtractor import FeatureExtractor
from helpers import skelfile_cmp
import matplotlib.pyplot as plt
plt.rcdefaults()

####################
## Initialization ##
####################
## Skeleton
skel_folder_path = r'H:\AHRQ\Study_IV\NewData\L2'
# skel_folder_path = r'H:\AHRQ\Study_IV\Data\Data\L6'
## Fingers
ENABLE_FINGERS = True
pickle_base_path1 = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers'
pickle_path1=os.path.join(pickle_base_path1,os.path.basename(skel_folder_path))
fingers_pkl_fname = os.path.basename(skel_folder_path)+'_fingers_from_hand_base_equate_dim_subsample.pkl'
#######################

annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)

out_pkl_fname = os.path.join(dirname, fileprefix+'_data.pickle')

fe = FeatureExtractor(json_param_path = 'param.json')
print('Generating IO: ', end = '')
out = fe.generate_io(skel_folder_path, annot_folder_path)
print('DONE !!!')

body_data_input = deepcopy(out['data_input'])
hand_data_input = None
combined_data_input = None

num_points = fe.fixed_num_frames
num_fingers = fe.num_fingers

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

	# 		# data_merge.append(line)
	hand_data_input = deepcopy(np.array(data_merge))
	combined_data_input = np.concatenate([body_data_input, hand_data_input], axis = 1)
	print('DONE !!!')

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

## combined Data
print('\nBody + Hand ====> SVM')
result = fe.run_svm(combined_data_input, out['data_output'], train_per = 0.60, inst_var_name = 'svm_clf')
print('DONE !!! Storing variable in svm_clf')

## Only Body
print('\nBody ====> SVM')
result = fe.run_svm(body_data_input, out['data_output'], train_per = 0.60, inst_var_name = 'svm_clf_body')
print('DONE !!! Storing variable in svm_clf_body')

## Only Hand
print('\nHand ====> SVM')
result = fe.run_svm(hand_data_input, out['data_output'], train_per = 0.60, inst_var_name = 'svm_clf_hand')
print('DONE !!! Storing variable in svm_clf_hand')

print('\nSaving in: ', out_pkl_fname)
with open(out_pkl_fname, 'wb') as fp:
	pickle.dump({'fe': fe, 'out': out}, fp)