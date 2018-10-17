import numpy as np
import pickle
import sys, os
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
skel_folder_path = r'H:\AHRQ\Study_IV\Flipped_Data\L6'
# skel_folder_path = r'H:\AHRQ\Study_IV\Data\Data\L6'
## Fingers
num_fingers = 0
ENABLE_FINGERS = False
pickle_path1 = r'H:\AHRQ\Study_IV\Data\Data_cpm\fingers\L3'
fingers_pkl_fname = 'L3_fingers_norm_30033.pkl'
#######################

annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)

out_pkl_fname = os.path.join(dirname, fileprefix+'_'+str(num_fingers)+'_data.pickle')

fe = FeatureExtractor(json_param_path = 'param.json')
out = fe.generate_io(skel_folder_path, annot_folder_path)

print fe.skel_file_order
sys.exit()

if(ENABLE_FINGERS):
	# # ## Appending finger lengths
	with open(os.path.join(pickle_path1, fingers_pkl_fname), 'rb') as fp:
		fingers_data = pickle.load(fp)
	data_merge=[]
	for txt_file in fe.skel_file_order:
		key = os.path.splitext(txt_file)[0].split('_')[:-1]
		s='_'
		key=s.join(key)
		for line in np.round(fingers_data.get(key),4):
			data_merge.append(line)
	out['data_input'] = np.concatenate([out['data_input'][:np.array(data_merge).shape[0]], np.array(data_merge)], axis = 1)

# Randomize data input and output
temp = zip(out['data_input'], out['data_output'])
shuffle(temp)
out['data_input'], out['data_output'] = zip(*temp)
out['data_input'], out['data_output'] = list(out['data_input']), list(out['data_output'])
if(fe.equate_dim):
	out['data_input'] = np.array(out['data_input'])
	out['data_output'] = np.array(out['data_output'])

# print fe.id_to_labels
# print fe.label_to_name

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

clf, _, _ = fe.run_svm(out['data_input'], out['data_output'], train_per = 0.60)
with open(out_pkl_fname, 'wb') as fp:
	pickle.dump({'fe': fe, 'out': out}, fp)