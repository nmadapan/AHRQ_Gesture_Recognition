import numpy as np
import pickle
import sys
from FeatureExtractor import FeatureExtractor
import matplotlib.pyplot as plt
plt.rcdefaults()

skel_folder_path = '..\\Data\\L3'
annot_folder_path = '..\\Data\\L3\\Annotations'

fe = FeatureExtractor(all_flag = False, feature_types = ['left', 'right'], num_joints = 1) #

# features = fe.generate_features(skel_filepath, annot_filepath)

# all_features = fe.batch_generate_features(skel_folder_path, annot_folder_path)

out = fe.generate_io(skel_folder_path, annot_folder_path, equate_dim = True, num_points = 40)

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

fe.run_svm(out['data_input'], out['data_output'], train_per = 0.60)

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
