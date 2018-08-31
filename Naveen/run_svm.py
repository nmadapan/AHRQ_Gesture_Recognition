import numpy as np
import pickle
import sys, os
from glob import glob
from random import shuffle
from FeatureExtractor import FeatureExtractor
from helpers import skelfile_cmp
import matplotlib.pyplot as plt
plt.rcdefaults()

skel_folder_path = 'H:\\AHRQ\\Study_IV\\Data\\Data\\L8'
rerun = True
annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
dirname = os.path.dirname(skel_folder_path)
fileprefix = os.path.basename(skel_folder_path)

data_pickle = os.path.join(dirname, fileprefix+'_data.pickle')
if(rerun or (not os.path.isfile(data_pickle))):
	fe = FeatureExtractor(json_param_path = 'param.json')
	out = fe.generate_io(skel_folder_path, annot_folder_path)
	with open(data_pickle, 'wb') as fp:
		pickle.dump({'fe': fe, 'out': out}, fp)
else:
	with open(data_pickle, 'rb') as fp:
		res = pickle.load(fp)
		fe, out = res['fe'], res['out']

# # ## Appending finger lengths

# pickle_path1 = 'H:\\AHRQ\\Study_IV\\Data\\Data_OpenPose\\fingers_data'

# with open(os.path.join(pickle_path1, 'L3_copy.pkl'), 'rb') as fp:
# 	fingers_data = pickle.load(fp)

# data_merge=[]
# for txt_file in fe.skel_file_order:
# 	key = os.path.splitext(txt_file)[0].split('_')[:-1]
# 	s='_'
# 	key=s.join(key)
# 	for line in np.round(fingers_data.get(key),4):
# 		data_merge.append(line)
# out['data_input'] = np.concatenate([out['data_input'], np.array(data_merge)], axis = 1)

# Randomize data input and output
temp = zip(out['data_input'], out['data_output'])
shuffle(temp)
out['data_input'], out['data_output'] = zip(*temp)
out['data_input'], out['data_output'] = list(out['data_input']), list(out['data_output'])
if(fe.equate_dim):
	out['data_input'] = np.array(out['data_input'])
	out['data_output'] = np.array(out['data_output'])

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

pickle_name  = fileprefix + '_obj.pickle'

with open(os.path.join(dirname, pickle_name), 'wb') as fp:
	pickle.dump(fe, fp)