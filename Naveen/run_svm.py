import numpy as np
import pickle
import sys, os
from glob import glob
from FeatureExtractor import FeatureExtractor
from helpers import skelfile_cmp
import matplotlib.pyplot as plt
plt.rcdefaults()

skel_folder_path = '..\\Data\\L6'
annot_folder_path = os.path.join(skel_folder_path, 'Annotations')
skel_fileorder_path = os.path.join(os.path.dirname(skel_folder_path), os.path.basename(skel_folder_path)+'_skel_order.txt')

fe = FeatureExtractor(all_flag = False, feature_types = ['left', 'right'], num_joints = 1, dominant_first = True) #

# features = fe.generate_features(skel_filepath, annot_filepath)

# all_features = fe.batch_generate_features(skel_folder_path, annot_folder_path)

out = fe.generate_io(skel_folder_path, annot_folder_path, randomize = False, equate_dim = True, num_points = 40)
print np.argmax(out['data_output'], axis = 1)[:80]
print out['id_to_labels']

skel_filepaths = glob(os.path.join(skel_folder_path, '*_skel.txt'))
skel_filepaths = sorted(skel_filepaths, cmp=skelfile_cmp)
with open(skel_fileorder_path, 'w') as fp:
	for fpath in skel_filepaths:
		cmd_str =  '_'.join(os.path.basename(fpath).split('_')[:2])
		fp.write(os.path.basename(fpath)+' '+str(out['label_to_ids'][cmd_str]) + '\n')

sys.exit(0)
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

pickle_fname = os.path.join('..', 'Test', os.path.basename(skel_folder_path)+'_svm_weights.pickle')
pickle.dump({'clf': clf, 'fe': fe}, open(pickle_fname, 'wb'))

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
