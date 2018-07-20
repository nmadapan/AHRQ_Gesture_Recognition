import numpy as np
import os, sys
from glob import glob
import pickle
from scipy.interpolate import interp1d
from copy import deepcopy
from random import shuffle
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import itertools
from helpers import skel_col_reduce, class_str_cmp, skelfile_cmp

#####################
# BASE class for creating features from skeleton files and annotation files
#
# How to use it:
#
#	from FeatureExtractor import FeatureExtractor
#	fe = FeatureExtractor(all_flag = False, feature_types = ['left', 'right'], num_joints = 1)
#		* If all_flag = True, all features types are considered.
#			In this case, there is no need to have 'feature_types' argument. For instance
#			fe = FeatureExtractor(all_flag = True, num_joints = 1)
#		* num_joints = 1 --> only hand, num_joints = 2 --> both hand and the elbow
#
#	fe = FeatureExtractor(all_flag = True, num_joints = 1)
#	fe.extract_raw_features(skel_filepath, annot_filepath) # See the comments inside function
#	fe.generate_features(skel_filepath, annot_filepath) # See the comments inside function
#	fe.batch_generate_features(skel_folder_path, annot_folder_path, ignore_missing_files = False)
#	fe.generate_io(skel_folder_path, annot_folder_path, randomize = True, equate_dim = False)
#####################

class FeatureExtractor():
	def __init__(self, all_flag = False, num_joints = 1, dim_per_joint = 3, dominant_first = True, **kwargs):
		# kwargs['feature_types'] = ['left', 'right']
		## Private variables
		self.__available_types = ['right', 'd_right', 'dd_right', 'theta_right', 'd_theta_right', 'dd_theta_right',\
							 'left', 'd_left', 'dd_left', 'theta_left', 'd_theta_left', 'dd_theta_left']
		self.__num_available_types = len(self.__available_types)
		self.__id_to_available_type = {idx: feat_type for idx, feat_type in zip(range(self.__num_available_types), self.__available_types)}

		## Declaring instance variables
		self.num_joints = num_joints # 1 - only hand, 2 - both hand and the shoulder
		self.dim_per_joint = dim_per_joint
		self.dominant_first = dominant_first
		self.type_flags = {feat_type: False for feat_type in self.__available_types}
		self.num_feature_types = None
		self.feature_types = None

		## Check if input arguments take right values
		# If all_flag is False, then kwargs['feature_types'] should exist
		if((not all_flag) and ('feature_types' not in kwargs.keys())):
			sys.exit('Error! \'feature_types\' input argument is mandatory when \'all_flag\' is False \n')
		# num_joints can either be 1 or 2
		if(not (self.num_joints == 1 or self.num_joints == 2)):
			sys.exit('Error: Number of joints should be either 1 or 2\n')
		# dim_per_joint can either be 2 or 3
		if(not (self.dim_per_joint == 2 or self.dim_per_joint == 3)):
			sys.exit('Error: Dimension per joint should be either 2 or 3\n')
		# If kwargs['feature_types'] exists, the feature types should exist in the availabe types
		if((not all_flag) and (not set(kwargs['feature_types']).issubset(set(self.__available_types)))):
			miss = list(set(kwargs['feature_types']).difference(set(kwargs['feature_types']).intersection(set(self.__available_types))))
			sys.exit('Error: Some feature types: \'' + ', '.join(miss) + '\' do not exist\n')

		# Updating the feature type flags
		if(not all_flag):
			self.feature_types = kwargs['feature_types']
			self.num_feature_types = len(self.feature_types)
			for feat_type in self.feature_types:
				if feat_type in self.__available_types:
					self.type_flags[feat_type] = True
		else:
			self.feature_types = deepcopy(self.__available_types)
			self.num_feature_types = len(self.feature_types)
			self.type_flags = {feat_type: True for feat_type in self.__available_types}

	def find_type_order(self, left, right, thresh_std = 0.08):
		# thresh_std = 0.08 in meters. It is found by observation.
		left_std = np.max(np.std(left, axis = 0))
		right_std = np.max(np.std(right, axis = 0))
		assert self.__num_available_types % 2 == 0, 'Error! Total no. of types should be even.'
		sz = int(self.__num_available_types / 2) # Assumes that actual types ordered as right followed by left
		right_order = range(0, sz)
		left_order = range(sz, 2*sz)
		if((right_std - left_std) >= thresh_std): return right_order+left_order
		elif((left_std - right_std) >= thresh_std): return left_order+right_order
		else: return right_order+left_order

	def extract_raw_features(self, skel_filepath, annot_filepath):
		########################
		# Input arguments:
		#	1. skel_filepath: full path of skeleton file
		#	2. annot_filepath: full path of annotation file
		# Return:
		#	xf - dictionary of raw trajectories
		#	xf['left'] and xf['right'] are lists of 1D numpy arrays
		#	If there are 20 frames, 2 joints - then, flattened numpy array of size is (3*(2+1)*20) -->
		#	[x_hand .., y_hand .., z_hand, x_elbow .., y_elbow .., z_elbow .., x_shoulder .., y_shoulder .., z_shoulder ..]
		########################

		# Initialize joint IDs
		left_hand_id = 7
		left_elbow_id = 5
		left_shoulder_id = 4
		right_hand_id = 11
		right_elbow_id = 9
		right_shoulder_id = 8

		# Read annotations
		with open(annot_filepath, 'r') as fp:
			annots = np.array([int(word.strip('\n')) for word in fp.readlines()])
			annots = annots.reshape(annots.shape[0]/2, -1)

		# Read skeleton file
		with open(skel_filepath, 'r') as fp:
			lines = [map(float, line.split(' ')) for line in fp.readlines()]

		xf = {'left': [], 'right': []}

		# Extract the required joints: Only right hand if both_hands is False, both the hands otherwise.
		# Column reduction . .
		dim = self.dim_per_joint
		if(self.num_joints == 2):
			left = [[ \
					line[dim*left_hand_id:dim*left_hand_id+dim], \
					line[dim*left_elbow_id:dim*left_elbow_id+dim], \
				 	line[dim*left_shoulder_id:dim*left_shoulder_id+dim]\
				 	] for line in lines]
			right = [[\
					 line[dim*right_hand_id:dim*right_hand_id+dim], \
					 line[dim*right_elbow_id:dim*right_elbow_id+dim], \
					 line[dim*right_shoulder_id:dim*right_shoulder_id+dim]\
					 ] for line in lines]
		else:
			left = [[\
					line[dim*left_hand_id:dim*left_hand_id+dim], \
					line[dim*left_shoulder_id:dim*left_shoulder_id+dim]\
					] for line in lines]
			right = [[\
					 line[dim*right_hand_id:dim*right_hand_id+dim], \
					 line[dim*right_shoulder_id:dim*right_shoulder_id+dim]\
					 ] for line in lines]
		left = np.array([np.array(line).flatten().tolist() for line in left]) # Shape - (num_total_frames x 9) if num_joints = 2
		right = np.array([np.array(line).flatten().tolist() for line in right])

		# Split the skeleton file based on annotations. start to end of the gesture instacne.
		# Row wise splitting
		for annot in annots:
			xf['left'].append(left[annot[0]:annot[1]+1, :].transpose().flatten())
			xf['right'].append(right[annot[0]:annot[1]+1, :].transpose().flatten())

		return xf

	def process_data_realtime(self, colproc_skel_data):
		########################
		# colproc_skel_data is a list of tuples [(a, b), (c, d)] --> a and c belong to left hand and b and d for right hand.
		# Input arguments:
		#
		# Return:
		#
		########################

		features = {feat_type: None for feat_type in self.__available_types}

		left, right = zip(*colproc_skel_data)
		left = np.array(list(left))
		right = np.array(list(right))

		right = right.reshape(self.dim_per_joint*(self.num_joints), -1).transpose()
		left = left.reshape(self.dim_per_joint*(self.num_joints), -1).transpose()
		d_reps = np.ones(right.shape[0]-2).tolist(); d_reps.append(2) # diff() reduced length by one. Using this we can fix it.
		dd_reps = np.ones(right.shape[0]-3).tolist(); dd_reps.append(3) # This is similar to above but for double diff

		## Right hand
		# Precompute position, velocity and angles
		d_right = np.repeat(np.diff(right, axis = 0), d_reps, axis = 0)
		theta_right = np.zeros(right.shape)
		for jnt_idx in range(self.num_joints):
			temp = d_right[:, 3*jnt_idx:3*(jnt_idx+1)]
			theta_right[:, 3*jnt_idx:3*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)

		## Position
		if(self.type_flags['right']):
			features['right'] = right.transpose().flatten()
		## Velocity
		if(self.type_flags['d_right']):
			features['d_right'] = d_right.transpose().flatten()
		## Acceleration
		if(self.type_flags['dd_right']):
			dd_right = np.diff(np.diff(right, axis = 0), axis = 0);
			dd_right = np.repeat(dd_right, dd_reps, axis = 0)
			features['dd_right'] = dd_right.transpose().flatten()
		## Angle
		if(self.type_flags['theta_right']):
			features['theta_right'] = theta_right.transpose().flatten()
		## Angular velocity
		if(self.type_flags['d_theta_right']):
			d_theta_right = np.diff(theta_right, axis = 0);
			d_theta_right = np.repeat(d_theta_right, d_reps, axis = 0)
			features['d_theta_right'] = d_theta_right.transpose().flatten()
		## Angular acceleration
		if(self.type_flags['dd_theta_right']):
			dd_theta_right = np.diff(np.diff(theta_right, axis = 0), axis = 0);
			dd_theta_right = np.repeat(dd_theta_right, dd_reps, axis = 0)
			features['dd_theta_right'] = dd_theta_right.transpose().flatten()

		## Left arm
		# Precompute position, velocity and angles
		d_left = np.repeat(np.diff(left, axis = 0), d_reps, axis = 0)
		theta_left = np.zeros(left.shape)
		for jnt_idx in range(self.num_joints):
			temp = d_left[:, 3*jnt_idx:3*(jnt_idx+1)]
			theta_left[:, 3*jnt_idx:3*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)
		## Position
		if(self.type_flags['left']):
			features['left'] = left.transpose().flatten()
		## Velocity
		if(self.type_flags['d_left']):
			features['d_left'] = d_left.transpose().flatten()
		## Acceleration
		if(self.type_flags['dd_left']):
			dd_left = np.diff(np.diff(left, axis = 0), axis = 0);
			dd_left = np.repeat(dd_left, dd_reps, axis = 0)
			features['dd_left'] = dd_left.transpose().flatten()
		## Angle
		if(self.type_flags['theta_left']):
			features['theta_left'] = theta_left.transpose().flatten()
		## Angular velocity
		if(self.type_flags['d_theta_left']):
			d_theta_left = np.diff(theta_left, axis = 0);
			d_theta_left = np.repeat(d_theta_left, d_reps, axis = 0)
			features['d_theta_left'] = d_theta_left.transpose().flatten()
		## Angular acceleration
		if(self.type_flags['dd_theta_left']):
			dd_theta_left = np.diff(np.diff(theta_left, axis = 0), axis = 0);
			dd_theta_left = np.repeat(dd_theta_left, dd_reps, axis = 0)
			features['dd_theta_left'] = dd_theta_left.transpose().flatten()

		if(self.dominant_first):
			features['types_order'] = self.find_type_order(left, right)
		else:
			features['types_order'] = list(range(self.__num_available_types))

		return features


	def generate_features(self, skel_filepath, annot_filepath):
		########################
		# Input arguments:
		#	1. skel_filepath: full path of skeleton file
		#	2. annot_filepath: full path of annotation file
		# Return:
		#	result - list of elements. Number of elements = no. of gesture instances in the skeleton file.
		#	Each element is a dictionary where keys are of two kinds: 1. feature types (refer to available types) and 2. class label ('label')
		#		For feature types, value is the following:
		#			* None if the flag of that feature type (self.type_flags) is False
		#			* If there are 20 frames, 2 joints - then, flattened numpy array of size is (3*2*20) -->
		#			* [x_hand .., y_hand .., z_hand, x_elbow .., y_elbow .., z_elbow ..]
		#		For class label, value is groupID_commandID. For instance, 3_0.
		########################

		result = []

		## Obtain raw features
		xf = self.extract_raw_features(skel_filepath, annot_filepath)

		for inst_id in range(len(xf['right'])):
			## Initialize the feature instance. Also, put a label
			features = {feat_type: None for feat_type in self.__available_types}
			features['label'] = '_'.join(os.path.basename(skel_filepath).split('_')[:2])

			## Preprocess:
			right = xf['right'][inst_id] # get right arm raw feature
			left = xf['left'][inst_id] # get left arm feature
			right = right.reshape(self.dim_per_joint*(self.num_joints+1), -1).transpose()
			left = left.reshape(self.dim_per_joint*(self.num_joints+1), -1).transpose()
			d_reps = np.ones(right.shape[0]-2).tolist(); d_reps.append(2) # diff() reduced length by one. Using this we can fix it.
			dd_reps = np.ones(right.shape[0]-3).tolist(); dd_reps.append(3) # This is similar to above but for double diff

			## Right arm
			# Change reference frame to shoulder
			# Precompute position, velocity and angles
			right = right[:,0:self.dim_per_joint*self.num_joints] - np.tile(right[:,self.dim_per_joint*self.num_joints:], (1, self.num_joints))
			d_right = np.repeat(np.diff(right, axis = 0), d_reps, axis = 0)
			theta_right = np.zeros(right.shape)
			for jnt_idx in range(self.num_joints):
				temp = d_right[:, 3*jnt_idx:3*(jnt_idx+1)]
				theta_right[:, 3*jnt_idx:3*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)

			## Position
			if(self.type_flags['right']):
				features['right'] = right.transpose().flatten()
			## Velocity
			if(self.type_flags['d_right']):
				features['d_right'] = d_right.transpose().flatten()
			## Acceleration
			if(self.type_flags['dd_right']):
				dd_right = np.diff(np.diff(right, axis = 0), axis = 0);
				dd_right = np.repeat(dd_right, dd_reps, axis = 0)
				features['dd_right'] = dd_right.transpose().flatten()
			## Angle
			if(self.type_flags['theta_right']):
				features['theta_right'] = theta_right.transpose().flatten()
			## Angular velocity
			if(self.type_flags['d_theta_right']):
				d_theta_right = np.diff(theta_right, axis = 0);
				d_theta_right = np.repeat(d_theta_right, d_reps, axis = 0)
				features['d_theta_right'] = d_theta_right.transpose().flatten()
			## Angular acceleration
			if(self.type_flags['dd_theta_right']):
				dd_theta_right = np.diff(np.diff(theta_right, axis = 0), axis = 0);
				dd_theta_right = np.repeat(dd_theta_right, dd_reps, axis = 0)
				features['dd_theta_right'] = dd_theta_right.transpose().flatten()

			## Left arm
			# Change reference frame to shoulder
			# Precompute position, velocity and angles
			left = left[:,0:self.dim_per_joint*self.num_joints] - np.tile(left[:,self.dim_per_joint*self.num_joints:], (1, self.num_joints))
			d_left = np.repeat(np.diff(left, axis = 0), d_reps, axis = 0)
			theta_left = np.zeros(left.shape)
			for jnt_idx in range(self.num_joints):
				temp = d_left[:, 3*jnt_idx:3*(jnt_idx+1)]
				theta_left[:, 3*jnt_idx:3*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)
			## Position
			if(self.type_flags['left']):
				features['left'] = left.transpose().flatten()
			## Velocity
			if(self.type_flags['d_left']):
				features['d_left'] = d_left.transpose().flatten()
			## Acceleration
			if(self.type_flags['dd_left']):
				dd_left = np.diff(np.diff(left, axis = 0), axis = 0);
				dd_left = np.repeat(dd_left, dd_reps, axis = 0)
				features['dd_left'] = dd_left.transpose().flatten()
			## Angle
			if(self.type_flags['theta_left']):
				features['theta_left'] = theta_left.transpose().flatten()
			## Angular velocity
			if(self.type_flags['d_theta_left']):
				d_theta_left = np.diff(theta_left, axis = 0);
				d_theta_left = np.repeat(d_theta_left, d_reps, axis = 0)
				features['d_theta_left'] = d_theta_left.transpose().flatten()
			## Angular acceleration
			if(self.type_flags['dd_theta_left']):
				dd_theta_left = np.diff(np.diff(theta_left, axis = 0), axis = 0);
				dd_theta_left = np.repeat(dd_theta_left, dd_reps, axis = 0)
				features['dd_theta_left'] = dd_theta_left.transpose().flatten()

			if(self.dominant_first):
				features['types_order'] = self.find_type_order(left, right)
			else:
				features['types_order'] = list(range(self.__num_available_types))

			result.append(features)

		return result

	def batch_generate_features(self, skel_folder_path, annot_folder_path, ignore_missing_files = False):
		########################
		# Input arguments:
		#	1. skel_folder_path: full path to folder containing skeleton files
		#	2. annot_folder_path: full path to folder containing annotation files
		#	3. ignore_missing_files: if False, skip when annotation file for a skeleton file is missing, otherwise exit
		# 	There should be one to one association between files in skel_folder_path and annot_folder_path
		#		If skeleton file name is 1_1_S2_L6_Scroll_Up_skel.txt, then the name of annotation file is 1_1_S2_L6_Scroll_Up_annot2.txt
		# Return:
		#	result - list of elements. Number of elements = no. of gesture instances in all skeleton files.
		#	Each element is a dictionary where keys are of two kinds: 1. feature types (refer to available types) and 2. class label ('label')
		#		For feature types, value is the following:
		#			* None if the flag of that feature type (self.type_flags) is False
		#			* If there are 20 frames, 2 joints - then, flattened numpy array of size is (3*2*20) -->
		#			* [x_hand .., y_hand .., z_hand, x_elbow .., y_elbow .., z_elbow ..]
		#		For class label, value is groupID_commandID. For instance, 3_0.
		########################

		# Error checks
		if(not os.path.isdir(skel_folder_path)):
			sys.exit('Error: '+ skel_folder_path + ' does not exists\n')
		if(not os.path.isdir(annot_folder_path)):
			sys.exit('Error: '+ annot_folder_path + ' does not exists\n')

		skel_filepaths = glob(os.path.join(skel_folder_path, '*_skel.txt'))
		if(len(skel_filepaths) == 0):
			sys.exit('No skeleton files in ' + skel_folder_path + '\n')
		skel_filepaths = sorted(skel_filepaths, cmp=skelfile_cmp)

		skel_fileorder_path = os.path.join(os.path.dirname(skel_folder_path), os.path.basename(skel_folder_path)+'_skel_order.txt')
		with open(skel_fileorder_path, 'w') as fp:
			for fpath in skel_filepaths: fp.write(os.path.basename(fpath)+ '\n')

		combos = []
		for skel_filepath in skel_filepaths:
			annot_filepath = os.path.join(annot_folder_path, os.path.basename(skel_filepath)[:-8]+'annot2.txt')
			flag = os.path.isfile(annot_filepath)
			if flag:
				combos.append((skel_filepath, annot_filepath))
			else:
				message = 'Annotation file of {} --> {}: does not exist'.format(skel_filepath, annot_filepath)
				if(not ignore_missing_files): sys.exit(message)
				else: print message

		features = []
		for skel_filepath, annot_filepath in combos:
			temp_features = self.generate_features(skel_filepath, annot_filepath)
			for feat in temp_features: features.append(feat)
		return features

	def generate_features_realtime(self, colproc_skel_data):
		feature = self.process_data_realtime(colproc_skel_data)
		inst = []
		# for feat_id, feat_type in self.__id_to_available_type.items():
		for feat_id in feature['types_order']:
			feat_type = self.__id_to_available_type[feat_id]
			if(feature[feat_type] is not None):
				if(True): ####################
					# Interpolate or Extrapolate to fixed dimension
					print feature[feat_type].shape
					mod_feat = feature[feat_type].reshape(self.dim_per_joint*self.num_joints, -1).transpose()
					mod_feat = self.interpn(mod_feat, 40) ####################
					mod_feat = mod_feat.transpose().flatten()
				else:
					mod_feat = feature[feat_type]
				inst = inst + mod_feat.tolist()
		return np.array([inst])

	def pred_output_realtime(self, colproc_skel_data, clf):
		inst = self.generate_features_realtime(colproc_skel_data)
		# Test Predict
		pred_test_output = clf.predict(inst)
		print pred_test_output

	def generate_io(self, skel_folder_path, annot_folder_path, randomize = False, equate_dim = False, **kwargs):
		########################
		# Input arguments:
		#	1. skel_folder_path: full path to folder containing skeleton files
		#	2. annot_folder_path: full path to folder containing annotation files
		#	3. randomize: If True, features are randomized, otherwise, order is maintained
		#	4. equate_dim: If True, Each gesture instance is interpolated/extrapolated to
		#		a fixed number of frames given by the next argument
		#	5. num_points: How many frames each gesture instance should contain.
		#		If equate_dim is True, num_points variable is mandatory
		# Return:
		#	out - A dictionary containing the following keys:
		#		1. num_classes - No. of classes
		#		2. class_labels - Lis of labels of each class
		#		3. id_to_labels - dictionary where keys are class IDs and values are class labels
		#		4. label_to_ids	- dictionary where kyes are class labels and values are class IDs
		#		5. num_instances - Total number of instances
		#		6. data_input - List of flattened numpy arrays. Each numpy array is the final feature vector
		#			All feature vectors will be of same length if 'equate_dim' is True
		#			Each feature vector is a result of concatenation of flattened numpy arrays corresponding to each feature type.
		#			If 'equate_dim' is True, this is a numpy array of shape (num_instances x fixed_num_of_features)
		#		7. data_output - One hot representation of corresponding class the feature vector
		#		8. num_joints - Number of joints considered
		#		9. num_feature_types - Number of actual feature types considered.
		########################

		if(equate_dim and ('num_points' not in kwargs.keys())):
			sys.exit('Error! \'num_points\' input argument is mandatory when \'equate_dim\' is True \n')

		## Obtain all features
		features = self.batch_generate_features(skel_folder_path, annot_folder_path)

		## Initialize the return variable
		out = {'num_classes': -1, 'class_labels': None, 'id_to_labels':None, 'label_to_ids':None, \
				'num_instances': None, 'data_input': [], 'data_output': [], 'num_joints': -1, \
				'num_feature_types': -1, 'inst_per_class': {}}

		class_labels = []
		id_to_labels = {}
		label_to_ids = {}
		inst_per_class = {}

		## Obtain class labels
		for feature in features: class_labels.append(feature['label'])
		raw_class_labels = deepcopy(class_labels)
		class_labels = list(set(class_labels))
		class_labels = sorted(class_labels, cmp=class_str_cmp)

		## Generate class IDs
		for class_id, label in enumerate(class_labels):
			id_to_labels[class_id] = label
			label_to_ids[label] = class_id
			inst_per_class[label] = raw_class_labels.count(label)

		## Overwrite the keys in the return variable
		out['num_classes'] = len(class_labels)
		out['class_labels'] = class_labels
		out['id_to_labels'] = id_to_labels
		out['label_to_ids'] = label_to_ids
		out['num_instances'] = len(features)
		out['num_feature_types'] = self.num_feature_types
		out['num_joints'] = self.num_joints
		out['inst_per_class'] = inst_per_class

		I = np.eye(out['num_classes'])

		for feature in features:
			inst = []
			# for feat_id, feat_type in self.__id_to_available_type.items():
			for feat_id in feature['types_order']:
				feat_type = self.__id_to_available_type[feat_id]
				if(feature[feat_type] is not None):
					if(equate_dim):
						# Interpolate or Extrapolate to fixed dimension
						mod_feat = feature[feat_type].reshape(self.dim_per_joint*self.num_joints, -1).transpose()
						mod_feat = self.interpn(mod_feat, kwargs['num_points'])
						mod_feat = mod_feat.transpose().flatten()
					else:
						mod_feat = feature[feat_type]
					inst = inst + mod_feat.tolist()
			out['data_input'].append(np.array(inst))
			out['data_output'].append(I[label_to_ids[feature['label']], :])
		if(randomize):
			# Randomize data input and output
			temp = zip(out['data_input'], out['data_output'])
			shuffle(temp)
			out['data_input'], out['data_output'] = zip(*temp)
			out['data_input'], out['data_output'] = list(out['data_input']), list(out['data_output'])
		if(equate_dim):
			out['data_input'] = np.array(out['data_input'])
			out['data_output'] = np.array(out['data_output'])
		return out

	def interpn(self, yp, num_points, kind = 'linear'):
		# yp is a gesture instance
		# yp is 2D numpy array of size num_frames x 3 if num_joints = 1
		# No. of frames will be increased/reduced to num_points
		xp = np.linspace(0, 1, num = yp.shape[0])
		x = np.linspace(0, 1, num = num_points)
		y = np.zeros((x.size, yp.shape[1]))
		for dim in range(yp.shape[1]):
			f = interp1d(xp, yp[:, dim], kind = kind)
			y[:, dim] = f(x)
		return y

	def plot_confusion_matrix(self, cm, classes, normalize=False, title='Confusion matrix',cmap=plt.cm.Blues):
		"""
		This function prints and plots the confusion matrix.
		Normalization can be applied by setting `normalize=True`.
		"""
		if normalize:
			cm = 100 * (cm.astype('float') / cm.sum(axis=1)[:, np.newaxis])
			cm = cm.astype('int')
		else:
			print('Confusion matrix, without normalization')

		# print(cm)
		plt.figure()

		np.set_printoptions(precision=0)
		plt.imshow(cm, interpolation='nearest', cmap=cmap)
		plt.title(title)
		plt.colorbar()
		tick_marks = np.arange(len(classes))
		plt.xticks(tick_marks, classes, rotation=45)
		plt.yticks(tick_marks, classes)

		fmt = 'd' if normalize else 'd'
		thresh = cm.max() / 2.
		for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
			plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", \
				color="white" if cm[i, j] > thresh else "black")

		plt.tight_layout()
		plt.ylabel('True label')
		plt.xlabel('Predicted label')
		plt.show()

	def run_svm(self, data_input, data_output, train_per = 0.8, kernel = 'linear'):
		num_inst = data_input.shape[0]
		feat_dim = data_input.shape[1]
		num_classes = data_output.shape[1]

		## Randomize
		perm = list(range(data_input.shape[0]))
		shuffle(perm)
		train_input = data_input[0:int(train_per*num_inst), :]
		train_output = data_output[0:int(train_per*num_inst), :]
		test_input = data_input[int(train_per*num_inst):, :]
		test_output = data_output[int(train_per*num_inst):, :]

		# Train
		clf = svm.SVC(decision_function_shape='ova', kernel = kernel )
		clf.fit(train_input, np.argmax(train_output, axis =1 ))

		# Train Predict
		pred_train_output = clf.predict(train_input)
		train_acc = float(np.sum(pred_train_output == np.argmax(train_output, axis = 1))) / pred_train_output.size
		print 'Train Acc: ', train_acc

		# Test Predict
		pred_test_output = clf.predict(test_input)
		test_acc = float(np.sum(pred_test_output == np.argmax(test_output, axis = 1))) / pred_test_output.size
		print 'Test Acc: ', test_acc

		conf_mat = confusion_matrix(np.argmax(test_output, axis = 1), pred_test_output)
		self.plot_confusion_matrix(conf_mat, list(range(num_classes)), normalize = True)

		return clf, train_acc, test_acc
