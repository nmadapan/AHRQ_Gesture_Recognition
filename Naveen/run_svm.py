import numpy as np
import pickle
import sys, os
from glob import glob
from random import shuffle
from FeatureExtractor import FeatureExtractor
from helpers import skelfile_cmp
import matplotlib.pyplot as plt
plt.rcdefaults()

skel_folder_path = '..\\Data\\L3'
annot_folder_path = os.path.join(skel_folder_path, 'Annotations')

fe = FeatureExtractor(all_flag = False, feature_types = ['left', 'right'], num_joints = 1, dominant_first = True) #

equate_dim = True
num_points = 40

out = fe.generate_io(skel_folder_path, annot_folder_path, randomize = False, equate_dim = equate_dim, num_points = num_points)

# Randomize data input and output
temp = zip(out['data_input'], out['data_output'])
shuffle(temp)
out['data_input'], out['data_output'] = zip(*temp)
out['data_input'], out['data_output'] = list(out['data_input']), list(out['data_output'])
if(equate_dim):
	out['data_input'] = np.array(out['data_input'])
	out['data_output'] = np.array(out['data_output'])

## Plotting histogram - No. of instances per class
objects = tuple(out['inst_per_class'].keys())
y_pos = np.arange(len(objects))
performance = out['inst_per_class'].values()
plt.figure()
plt.bar(y_pos, performance, align='center', alpha=0.5)
# plt.xticks(y_pos, objects)
plt.xlabel('Class IDs')
plt.ylabel('No. of instances')
plt.title('No. of instances per class')
plt.grid(True)
#plt.show()

clf, _, _ = fe.run_svm(out['data_input'], out['data_output'], train_per = 0.60)

# pickle_fname = os.path.join('..', 'Test', os.path.basename(skel_folder_path)+'_svm_weights.pickle')
# pickle.dump({'clf': clf, 'fe': fe}, open(pickle_fname, 'wb'))

# for feat in out['data_input']:
# 	print feat.shape

# with open('raw_features.pickle', 'wb') as fp:
# 	pickle.dump(features, fp)

# with open('raw_features.pickle', 'rb') as fp:
# 	dic = pickle.load(fp)

# x = np.array(range(num_points))
# x_new = np.linspace(0, num_points - 1)

# for keys, values in features.items():
# 	data = features[keys]
# 	x = np.array(range())
