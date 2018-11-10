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
import matplotlib.pyplot as plt
plt.rcdefaults()

####################
## Initialization ##
####################
## Skeleton
skel_folder_path = r'H:\AHRQ\Study_IV\NewData\L6'
eliminate_subject_id = 'S3'

## Fingers
ENABLE_FINGERS = False
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

skel_file_order = deepcopy(fe.skel_file_order)
dominant_types_order = deepcopy(fe.dominant_type)

assert len(dominant_types_order) == len(skel_file_order), 'ERROR! MISMATCH'

subject_name_order = np.array([fname.split('_')[2] for fname in skel_file_order])

partial_train_subject_flags = (subject_name_order != eliminate_subject_id)

# print(zip(skel_file_order, partial_train_subject_flags))

all_train_flags = []

for idx, dom_types_list in enumerate(dominant_types_order):
	all_train_flags += [partial_train_subject_flags[idx]]*len(dom_types_list)

all_train_flags = np.array(all_train_flags)

# full_list = []
# for sublist in fe.dominant_type:
# 	full_list += sublist

# print(np.mean(np.array(full_list) == 0))

# print(out['data_output'])

# sys.exit()

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
					gesture_shuffle.append(frame[5:].tolist()+frame[:5].tolist())
				data_merge.append(np.array(gesture_shuffle).flatten().tolist())
				
	out['data_input'] = np.concatenate([out['data_input'], np.array(data_merge)], axis = 1)
	print('DONE !!!')

# Randomize data input and output
data_input, data_output = deepcopy(out['data_input']), deepcopy(out['data_output'])

## TODO: It is assumed that out['data_input'] and out['data_output'] are numpy arrays. It is not the case when equate_dim is False
train_data_input = data_input[all_train_flags, :]
train_data_output = data_output[all_train_flags, :]

test_data_input = data_input[np.logical_not(all_train_flags), :]
test_data_output = data_output[np.logical_not(all_train_flags), :]

temp = zip(train_data_input, train_data_output)
shuffle(temp)
train_data_input, train_data_output = zip(*temp)
train_data_input, train_data_output = list(train_data_input), list(train_data_output)
if(fe.equate_dim):
	train_data_input, train_data_output = np.array(train_data_input), np.array(train_data_output)

# print(fe.label_to_ids)
# print(fe.label_to_name)

## Plotting histogram - No. of instances per class
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

print('Train SVM: ', end = '')
clf, _, _ = fe.run_svm(train_data_input, train_data_output, train_per = 0.60, inst_var_name = 'svm_clf')
print('DONE !!! Storing variable in svm_clf')

# Test Predict
pred_test_output = clf.predict(test_data_input)
test_acc = float(np.sum(pred_test_output == np.argmax(test_data_output, axis = 1))) / pred_test_output.size
print('New Subject Test Acc: ', test_acc)

conf_mat = confusion_matrix(np.argmax(test_data_output, axis = 1), pred_test_output)
cname_list = []
for idx in range(test_data_output.shape[1]):
	cname_list.append(fe.label_to_name[fe.id_to_labels[idx]])

fe.plot_confusion_matrix(conf_mat, cname_list, normalize = True)

print('Saving in: ', out_pkl_fname)
with open(out_pkl_fname, 'wb') as fp:
	pickle.dump({'fe': fe, 'out': out}, fp)