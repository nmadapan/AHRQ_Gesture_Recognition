import numpy as np
import pickle
import sys
from FeatureExtractor import FeatureExtractor

skel_filepath = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\S2_L6\\3_1_S2_L6_Rotate_CW_skel.txt'
annot_filepath = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\S2_L6\\Annotations\\3_1_S2_L6_Rotate_CW_annot2.txt'
num_points = 60

feat_extractor = FeatureExtractor(num_points = num_points)
xf = feat_extractor.extract_raw_features(skel_filepath, annot_filepath)

features = feat_extractor.generate_all_features(skel_filepath, annot_filepath)

# with open('raw_features.pickle', 'wb') as fp:
# 	pickle.dump(features, fp)

# with open('raw_features.pickle', 'rb') as fp:
# 	dic = pickle.load(fp)

# x = np.array(range(num_points))
# x_new = np.linspace(0, num_points - 1)

# for keys, values in features.items():
# 	data = features[keys]
# 	x = np.array(range())