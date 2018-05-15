import numpy as np
import pickle
import sys
from FeatureExtractor import FeatureExtractor

skel_filepath = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L6\\3_1_S2_L6_Rotate_CW_skel.txt'
annot_filepath = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L6\\Annotations\\3_1_S2_L6_Rotate_CW_annot2.txt'
skel_folder_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L6'
annot_folder_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L6\\Annotations'
num_points = 60

feat_extractor = FeatureExtractor(feature_types = ['left', 'right'], num_joints = 1)
# features = feat_extractor.generate_features(skel_filepath, annot_filepath)

# all_features = feat_extractor.batch_generate_features(skel_folder_path, annot_folder_path)

out = feat_extractor.generate_io(skel_folder_path, annot_folder_path, equate_dim = True, num_points = 40)

feat_extractor.check_svm(out['data_input'], out['data_output'], train_per = 0.60)

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