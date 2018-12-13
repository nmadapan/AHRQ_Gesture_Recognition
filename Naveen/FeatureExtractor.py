from __future__ import print_function

import numpy as np
import os, sys
from glob import glob
import pickle
from copy import deepcopy
from random import shuffle
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import itertools

from helpers import *

'''
BASE class for creating features from (SKELETON files and respective annotation files)

How to use it:
	from FeatureExtractor import FeatureExtractor
	fe = FeatureExtractor(json_param_path = 'param.json')
		* param.json contains following variables:
		* all_feature_types: If True, all features types are considered.
		* feature_types: List of feature types to consider. It is necessary iff all_feature_types is false
		* num_joints: 1 --> only hand, 2 --> both hand and the elbow
		* randomize: If true, the data is randomized
		* equate_dim: If true, no. of frames in each gesture is equated via interpolation. No. of frames is
			equated to fixed_num_frames variable in param.json
		* dim_per_joint = 3; Since we have x, y, z
		* dominant_first: If true, dominant hand goes first followed by other hand. Else, right follows left

	fe.extract_raw_features(skel_filepath, annot_filepath) # See the comments inside function
	fe.generate_features(skel_filepath, annot_filepath) # See the comments inside function
	fe.batch_generate_features(skel_folder_path, annot_folder_path, ignore_missing_files = False)
	fe.generate_io(skel_folder_path, annot_folder_path)
'''

class FeatureExtractor():
	def __init__(self, json_param_path = 'param.json'):
		## Private variables
		self.available_types = ['right', 'd_right', 'theta_right', 'd_theta_right',\
							 	'left', 'd_left', 'theta_left', 'd_theta_left']
		self.num_available_types = len(self.available_types)
		self.id_to_available_type = {idx: feat_type for idx, feat_type in zip(range(self.num_available_types), self.available_types)}
		# right type ids: [0, 1, 2, 3], left type ids: [4, 5, 6, 7]

		## Initialize variables from json param path
		param_dict = json_to_dict(json_param_path)
		for key, value in param_dict.items(): setattr(self, key, value)

		## Initialize variables from subject specific parameters
		# The variable subject_param_path is present in param.json
		subject_param_dict = json_to_dict(self.subject_param_path)
		for key, value in subject_param_dict.items(): setattr(self, key, value)

		## Initialize Kinect joint names
		kinect_joint_names_dict = json_to_dict(self.kinect_joint_names_path)
		## Left hand
		self.left_hand_id = kinect_joint_names_dict['JointType_HandLeft'] # 7
		self.left_elbow_id = kinect_joint_names_dict['JointType_ElbowLeft'] # 5
		self.left_shoulder_id = kinect_joint_names_dict['JointType_ShoulderLeft'] # 4
		## Right hand
		self.right_hand_id = kinect_joint_names_dict['JointType_HandRight'] # 11
		self.right_elbow_id = kinect_joint_names_dict['JointType_ElbowRight'] # 9
		self.right_shoulder_id = kinect_joint_names_dict['JointType_ShoulderRight'] # 8

		## Initialize the label to class name
		# The variable commands_filepath is present in param.json
		self.label_to_name = json_to_dict(self.commands_filepath)

		self.type_flags = {feat_type: False for feat_type in self.available_types} # What feature types to consider
		self.num_feature_types = None

		self.skel_file_order = None # What is the order in which skeleton files are read.
		self.dominant_type = None # What is the dominant type of each instance in the skeleton files (in the same order).
		self.svm_clf = None
		self.classifiers = {}

		# num_joints can either be 1 or 2
		if(not (self.num_joints == 1 or self.num_joints == 2)):
			raise ValueError('Error: Number of joints should be either 1 or 2\n')
		# dim_per_joint can either be 2 or 3
		if(not (self.dim_per_joint == 2 or self.dim_per_joint == 3)):
			raise ValueError('Error: Dimension per joint should be either 2 or 3\n')
		# If self.feature_types exists, the feature types should exist in the availabe types
		if((not self.all_feature_types) and (not set(self.feature_types).issubset(set(self.available_types)))):
			miss = list(set(self.feature_types).difference(set(self.feature_types).intersection(set(self.available_types))))
			raise ValueError('Error: Some feature types: \'' + ', '.join(miss) + '\' do not exist\n')

		# Updating the feature type flags: True -> consider, False -> ignore
		if(not self.all_feature_types):
			self.num_feature_types = len(self.feature_types)
			for feat_type in self.feature_types:
				if feat_type in self.available_types:
					self.type_flags[feat_type] = True
		else:
			self.feature_types = deepcopy(self.available_types)
			self.num_feature_types = len(self.feature_types)
			self.type_flags = {feat_type: True for feat_type in self.available_types}

		## Other variables - updated by generate_io()
		self.num_classes = None
		self.class_labels = None
		self.id_to_labels = None
		self.label_to_ids = None
		self.inst_per_class = None
		self.num_instances = None # total no. of instances

		## Other variables - updated batch_generate_features()
		self.skel_file_order = None # order in which files are being read
		self.dominant_type = None # list of list. one sublist per skeleton file.
			# Size of sublist is no. of gesture instances in that skeleton file.
			# Each sublist = [1 0 0 1 0], 1-> right is dominant, left otherwise.

	###### OFFLINE Function ########
	def init_calib_params(self, json_param_path):
		########################
		# Description:
		#		Given the json params file, initialize all of the
		#		class variables with those values
		#		i.e. trajectories of hand, elbow, shoulder of both hands.
		# Input arguments:
		########################

		# Initialize variables from json param path
		param_dict = json_to_dict(json_param_path)
		for key, value in param_dict.items(): setattr(self, key, value)

	###### OFFLINE Function ########
	def extract_raw_features(self, skel_filepath, annot_filepath):
		########################
		# Description:
		#	Given the skeleton file and its annotation file, it extracts raw features,
		#		i.e. trajectories of hand, elbow, shoulder of both hands.
		# Input arguments:
		#	1. skel_filepath: full path of skeleton file.
		#		It contains M rows, and each row has 75 values (3 for each of 25 kinect joints)
		#	2. annot_filepath: full path of annotation file
		#		It contains start and end gesture ids. It will have 2 x K rows, and each row has one integer.
		#		K - No of gesture instances.
		# Return:
		#	xf - dictionary of raw trajectories
		#	xf['left'] and xf['right'] are lists of 1D numpy arrays
		#	If there are 20 frames, 2 joints - then, each element in xf['left'] is a flattened numpy array of size is (3*(2+1)*20) -->
		#		[x_hand .., y_hand .., z_hand, x_elbow .., y_elbow .., z_elbow .., x_shoulder .., y_shoulder .., z_shoulder ..]
		#	Similary xf['right']
		########################

		# Read annotations
		with open(annot_filepath, 'r') as fp:
			annots = np.array([int(word.strip('\n')) for word in fp.readlines()])
			annots = annots.reshape(annots.shape[0]/2, -1)

		# Read skeleton file
		with open(skel_filepath, 'r') as fp:
			lines = [map(float, line.split(' ')) for line in fp.readlines()]

		xf = {'left': [], 'right': []}

		# Column reduction . .
		dim = self.dim_per_joint
		if(self.num_joints == 2):
			left = [[ \
					line[dim*self.left_hand_id:dim*self.left_hand_id+dim], \
					line[dim*self.left_elbow_id:dim*self.left_elbow_id+dim], \
				 	line[dim*self.left_shoulder_id:dim*self.left_shoulder_id+dim]\
				 	] for line in lines]
			right = [[\
					 line[dim*self.right_hand_id:dim*self.right_hand_id+dim], \
					 line[dim*self.right_elbow_id:dim*self.right_elbow_id+dim], \
					 line[dim*self.right_shoulder_id:dim*self.right_shoulder_id+dim]\
					 ] for line in lines]
		else:
			left = [[\
					line[dim*self.left_hand_id:dim*self.left_hand_id+dim], \
					line[dim*self.left_shoulder_id:dim*self.left_shoulder_id+dim]\
					] for line in lines]
			right = [[\
					 line[dim*self.right_hand_id:dim*self.right_hand_id+dim], \
					 line[dim*self.right_shoulder_id:dim*self.right_shoulder_id+dim]\
					 ] for line in lines]
		left = np.array([np.array(line).flatten().tolist() for line in left]) # Shape - (num_total_frames x 9) if num_joints = 2
		right = np.array([np.array(line).flatten().tolist() for line in right])

		# Split the skeleton file based on annotations. start to end of the gesture instacne.
		# Row wise splitting
		for annot in annots:
			xf['left'].append(left[annot[0]:annot[1]+1, :].transpose().flatten())
			xf['right'].append(right[annot[0]:annot[1]+1, :].transpose().flatten())

		return xf

	###### OFFLINE Function ########
	def generate_features(self, skel_filepath, annot_filepath):
		########################
		# Input arguments:
		#	1. skel_filepath: full path of skeleton file
		#		It contains M rows, and each row has 75 values (3 for each of 25 kinect joints)
		#	2. annot_filepath: full path of annotation file
		#		It contains start and end gesture ids. It will have 2 x K rows, and each row has one integer.
		#		K - No of gesture instances.
		# Return:
		#	'result' - list of elements. Number of elements = no. of gesture instances in the skeleton file.
		#	Each element is a dictionary where keys are of three kinds:
		#		1. feature types (refer to available_types), 2. class label ('label') and 3. order of feature type ids ('types_order')
		#		For feature types, value is the following:
		#			* None if the flag of that feature type (self.type_flags) is False
		#			* If there are 20 frames, 2 joints - then, flattened numpy array of size is (3*2*20) -->
		#			* [x_hand .., y_hand .., z_hand, x_elbow .., y_elbow .., z_elbow ..]
		#		For class label, value is groupID_commandID. For instance, 3_0.
		#		'types_order', it is a list of ids: dominant ids followed by non dominant feature ids.
		########################

		result = []

		## Obtain raw features
		xf = self.extract_raw_features(skel_filepath, annot_filepath)

		## Expected format 1_0_S*_L*_Scroll_X.txt
		skel_fname = os.path.basename(skel_filepath)
		subject_id = skel_fname.split('_')[2] # S*
		lexicon_id = skel_fname.split('_')[3] # L*

		for inst_id in range(len(xf['right'])):
			## Initialize the feature instance. Also, put a label
			features = {feat_type: None for feat_type in self.available_types}
			features['label'] = '_'.join(os.path.basename(skel_filepath).split('_')[:2])

			## Preprocess:
			right = xf['right'][inst_id] # get right arm raw feature
			left = xf['left'][inst_id] # get left arm feature
			right = right.reshape(self.dim_per_joint*(self.num_joints+1), -1).transpose()
			left = left.reshape(self.dim_per_joint*(self.num_joints+1), -1).transpose()

			d_reps = np.ones(right.shape[0]-2).tolist(); d_reps.append(2) # diff() reduced length by one. Using this we can fix it.

			## Right arm
			# Change reference frame to shoulder
			# Precompute position, velocity and angles
			dim = self.dim_per_joint
			right = right[:,0:self.dim_per_joint*self.num_joints] - np.tile(right[:,self.dim_per_joint*self.num_joints:], (1, self.num_joints))
			d_right = np.repeat(np.diff(right, axis = 0), d_reps, axis = 0)
			theta_right = np.zeros(right.shape)
			for jnt_idx in range(self.num_joints):
				# '''
				# Convert each difference into a unit vector
				# For instance: [dx, dy, dz] ==> [dx/L, dy/L, dz/L] where L = \sqrt{dx^2 + dy^2, dz^2}
				# '''
				# t_d_right = d_right[:, dim*jnt_idx:dim*(jnt_idx+1)] ## Get the first three (dim) columns
				# d_right_norm = np.linalg.norm(t_d_right, axis = 1) ## Compute the norm of rows
				# d_right_norm[d_right_norm < 1e-6] = 1e6 ## Suppress the elements that are less than 1e-6
				# t_d_right = t_d_right.T / d_right_norm # Divide each column by its norm
				# d_right[:, dim*jnt_idx:dim*(jnt_idx+1)] = t_d_right.T # Save it back in d_right

				temp = d_right[:, dim*jnt_idx:dim*(jnt_idx+1)]
				theta_right[:, dim*jnt_idx:dim*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)

			## Position
			if(self.type_flags['right']):
				features['right'] = right.transpose().flatten() / self.subject_params[lexicon_id][subject_id]['arm_length']
			## Velocity
			if(self.type_flags['d_right']):
				features['d_right'] = d_right.transpose().flatten() / self.max_dr
			## Angle
			if(self.type_flags['theta_right']):
				features['theta_right'] = theta_right.transpose().flatten() / self.max_th
			## Angular velocity
			if(self.type_flags['d_theta_right']):
				d_theta_right = np.diff(theta_right, axis = 0);
				d_theta_right = np.repeat(d_theta_right, d_reps, axis = 0)
				features['d_theta_right'] = d_theta_right.transpose().flatten() / self.max_dth

			## Left arm
			# Change reference frame to shoulder
			# Precompute position, velocity and angles
			left = left[:,0:self.dim_per_joint*self.num_joints] - np.tile(left[:,self.dim_per_joint*self.num_joints:], (1, self.num_joints))
			d_left = np.repeat(np.diff(left, axis = 0), d_reps, axis = 0)
			theta_left = np.zeros(left.shape)
			for jnt_idx in range(self.num_joints):
				# '''
				# Convert each difference into a unit vector
				# For instance: [dx, dy, dz] ==> [dx/L, dy/L, dz/L] where L = \sqrt{dx^2 + dy^2, dz^2}
				# '''
				# t_d_left = d_left[:, dim*jnt_idx:dim*(jnt_idx+1)] ## Get the first three (dim) columns
				# d_left_norm = np.linalg.norm(t_d_left, axis = 1) ## Compute the norm of rows
				# d_left_norm[d_left_norm < 1e-6] = 1e6 ## Suppress the elements that are less than 1e-6
				# t_d_left = t_d_left.T / d_left_norm # Divide each column by its norm
				# d_left[:, dim*jnt_idx:dim*(jnt_idx+1)] = t_d_left.T # Save it back in d_left

				temp = d_left[:, dim*jnt_idx:dim*(jnt_idx+1)]
				theta_left[:, dim*jnt_idx:dim*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)
			## Position
			if(self.type_flags['left']):
				features['left'] = left.transpose().flatten() / self.subject_params[lexicon_id][subject_id]['arm_length']
			## Velocity
			if(self.type_flags['d_left']):
				features['d_left'] = d_left.transpose().flatten() / self.max_dr
			## Angle
			if(self.type_flags['theta_left']):
				features['theta_left'] = theta_left.transpose().flatten() / self.max_th
			## Angular velocity
			if(self.type_flags['d_theta_left']):
				d_theta_left = np.diff(theta_left, axis = 0);
				d_theta_left = np.repeat(d_theta_left, d_reps, axis = 0)
				features['d_theta_left'] = d_theta_left.transpose().flatten() / self.max_dth

			if(self.dominant_first):
				features['types_order'] = self.find_type_order(left, right)
			else:
				features['types_order'] = list(range(self.num_available_types))

			result.append(features)

		return result

	###### OFFLINE Function ########
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
		#	Each element is a dictionary where keys are of three kinds:
		#		1. feature types (refer to available_types), 2. class label ('label') and 3. order of feature type ids ('types_order')
		#		For feature types, value is the following:
		#			* None if the flag of that feature type (self.type_flags) is False
		#			* If there are 20 frames, 2 joints - then, flattened numpy array of size is (3*2*20) -->
		#			* [x_hand .., y_hand .., z_hand, x_elbow .., y_elbow .., z_elbow ..]
		#		For class label, value is groupID_commandID. For instance, 3_0.
		#		'types_order', it is a list of ids: dominant ids followed by non dominant feature ids.
		########################

		# Error checks
		if(not os.path.isdir(skel_folder_path)):
			raise IOError('Error: '+ skel_folder_path + ' does not exists\n')
		if(not os.path.isdir(annot_folder_path)):
			raise IOError('Error: '+ annot_folder_path + ' does not exists\n')

		skel_filepaths = glob(os.path.join(skel_folder_path, '*_skel.txt'))
		if(len(skel_filepaths) == 0):
			raise IOError('No skeleton files in ' + skel_folder_path + '\n')
		skel_filepaths = sorted(skel_filepaths, cmp=skelfile_cmp)

		self.skel_file_order = map(os.path.basename, skel_filepaths)
		# skel_fileorder_path = os.path.join(os.path.dirname(skel_folder_path), os.path.basename(skel_folder_path)+'_skel_order.txt')
		# with open(skel_fileorder_path, 'w') as fp:
		# 	for fpath in skel_filepaths: fp.write(os.path.basename(fpath)+ '\n')

		combos = []
		for skel_filepath in skel_filepaths:
			annot_filepath = os.path.join(annot_folder_path, os.path.basename(skel_filepath)[:-8]+'annot2.txt')
			flag = os.path.isfile(annot_filepath)
			if flag:
				combos.append((skel_filepath, annot_filepath))
			else:
				message = 'Annotation file of {} --> {}: does not exist'.format(skel_filepath, annot_filepath)
				if(not ignore_missing_files): raise IOError(message)
				else: print(message)

		features = []
		self.dominant_type = [] # 1 for right hand, 0 otherwise

		for skel_filepath, annot_filepath in combos:
			temp_features = self.generate_features(skel_filepath, annot_filepath)
			temp_dom_type = []
			for feat in temp_features:
				features.append(feat)
				temp_dom_type.append(int(feat['types_order'][0]==0))
			self.dominant_type.append(temp_dom_type)
		return features

	###### OFFLINE Function ########
	def generate_io(self, skel_folder_path, annot_folder_path):
		########################
		# Input arguments:
		#	1. skel_folder_path: full path to folder containing skeleton files
		#	2. annot_folder_path: full path to folder containing annotation files
		#
		# Update:
		#	This function updates the following variables:
		# 		self.num_classes, self.class_labels, self.id_to_labels, self.label_to_ids, self.inst_per_class, self.num_instances
		#
		# Return:
		#	out - A dictionary containing the following keys:
		#		1. data_input - List of flattened numpy arrays. Each numpy array is the final feature vector
		#			All feature vectors will be of same length if 'self.equate_dim' is True
		#			Each feature vector is a result of concatenation of flattened numpy arrays corresponding to each feature type.
		#			If 'self.equate_dim' is True, this is a numpy array of shape (num_instances x fixed_num_of_features)
		#		2. data_output - One hot representation of corresponding class the feature vector
		########################

		## Obtain all features
		features = self.batch_generate_features(skel_folder_path, annot_folder_path)

		## Initialize the return variable
		out = {'data_input': [], 'data_output': []}

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

		self.num_classes = len(class_labels)
		self.class_labels = class_labels
		self.id_to_labels = id_to_labels
		self.label_to_ids = label_to_ids
		self.inst_per_class = inst_per_class
		self.num_instances = len(features)

		I = np.eye(self.num_classes)

		for feature in features:
			inst = []
			# for feat_id, feat_type in self.id_to_available_type.items():
			for feat_id in feature['types_order']:
				feat_type = self.id_to_available_type[feat_id]
				if(feature[feat_type] is not None):
					if(self.equate_dim):
						# Interpolate or Extrapolate to fixed dimension
						mod_feat = feature[feat_type].reshape(self.dim_per_joint*self.num_joints, -1).transpose()
						mod_feat = interpn(mod_feat, self.fixed_num_frames)
						mod_feat = mod_feat.transpose().flatten()
					else:
						mod_feat = feature[feat_type]
					inst = inst + mod_feat.tolist()
			out['data_input'].append(np.array(inst))
			out['data_output'].append(I[label_to_ids[feature['label']], :])
		if(self.randomize):
			# self.randomize data input and output
			temp = zip(out['data_input'], out['data_output'])
			shuffle(temp)
			out['data_input'], out['data_output'] = zip(*temp)
			out['data_input'], out['data_output'] = list(out['data_input']), list(out['data_output'])
		if(self.equate_dim):
			out['data_input'] = np.array(out['data_input'])
			out['data_output'] = np.array(out['data_output'])
		return out

	###### ONLINE Function ########
	def update_rt_params(self, subject_id = None, lexicon_id = None):
		if subject_id is None or lexicon_id is None:
			return ValueError('subject_id and lexicon_id CAN NOT BE None')
		self.rt_subject_id = subject_id
		self.rt_lexicon_id = lexicon_id

	###### ONLINE Function ########
	def process_data_realtime(self, colproc_skel_data):
		########################
		# Input arguments:
		#	colproc_skel_data: a list of tuples [(a, b), (c, d)] --> a and c belong to right hand and b and d for left hand.
		#	'a' is a list of right hand followed right elbow coordinates [x_hand, y_hand, z_hand, x_elbow, y_elbow, z_elbow]
		#		These coordinates are relative to the right shoulder. similarly for the left hand.
		#
		# Return:
		#	features: dictionary.
		#	key: feature types --> value: flattened numpy array or None
		#	key: types_order --> value: dominant feature type ids followed by the nondominant ones.
		########################

		features = {feat_type: None for feat_type in self.available_types}

		right, left = zip(*colproc_skel_data)  #### IMPORTANT --> Order is opposite. right comes first. Refer to skel_col_reduce() in helpers.py
		right, left = np.array(list(right)), np.array(list(left)) # left and right are (_ x 3/6) ndarrays

		d_reps = np.ones(right.shape[0]-2).tolist(); d_reps.append(2) # diff() reduced length by one. Using this we can fix it.

		## Right hand
		# Precompute position, velocity and angles
		d_right = np.repeat(np.diff(right, axis = 0), d_reps, axis = 0)
		theta_right = np.zeros(right.shape)
		for jnt_idx in range(self.num_joints):
			## TODO: Normalize d_right so that norm of each row of a joint is one.
			temp = d_right[:, 3*jnt_idx:3*(jnt_idx+1)]
			theta_right[:, 3*jnt_idx:3*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)

		## Position
		if(self.type_flags['right']):
			features['right'] = right.transpose().flatten() / self.subject_params[self.rt_lexicon_id][self.rt_subject_id]['arm_length']
		## Velocity
		if(self.type_flags['d_right']):
			features['d_right'] = d_right.transpose().flatten() / self.max_dr
		## Angle
		if(self.type_flags['theta_right']):
			features['theta_right'] = theta_right.transpose().flatten() / self.max_th
		## Angular velocity
		if(self.type_flags['d_theta_right']):
			d_theta_right = np.diff(theta_right, axis = 0);
			d_theta_right = np.repeat(d_theta_right, d_reps, axis = 0)
			features['d_theta_right'] = d_theta_right.transpose().flatten() / self.max_dth

		## Left arm
		# Precompute position, velocity and angles
		d_left = np.repeat(np.diff(left, axis = 0), d_reps, axis = 0)
		theta_left = np.zeros(left.shape)
		for jnt_idx in range(self.num_joints):
			temp = d_left[:, 3*jnt_idx:3*(jnt_idx+1)]
			theta_left[:, 3*jnt_idx:3*(jnt_idx+1)] = np.arctan2(np.roll(temp, 1, axis = 1), temp)
		## Position
		if(self.type_flags['left']):
			features['left'] = left.transpose().flatten() / self.subject_params[self.rt_lexicon_id][self.rt_subject_id]['arm_length']
		## Velocity
		if(self.type_flags['d_left']):
			features['d_left'] = d_left.transpose().flatten() / self.max_dr
		## Angle
		if(self.type_flags['theta_left']):
			features['theta_left'] = theta_left.transpose().flatten() / self.max_th
		## Angular velocity
		if(self.type_flags['d_theta_left']):
			d_theta_left = np.diff(theta_left, axis = 0);
			d_theta_left = np.repeat(d_theta_left, d_reps, axis = 0)
			features['d_theta_left'] = d_theta_left.transpose().flatten() / self.max_dth

		if(self.dominant_first):
			features['types_order'] = self.find_type_order(left, right)
		else:
			features['types_order'] = list(range(self.num_available_types))

		return features

	###### ONLINE Function ########
	def generate_features_realtime(self, colproc_skel_data):
		########################
		# Input arguments:
		#	colproc_skel_data: a list of tuples [(a, b), (c, d)] --> a and c belong to right hand and b and d for left hand.
		#	'a' is a list of right hand followed right elbow coordinates [x_hand, y_hand, z_hand, x_elbow, y_elbow, z_elbow]
		#		These coordinates are relative to the right shoulder. similarly for the left hand.
		#
		# Return:
		#	feature instance: numpy.ndarray (1 x feature_size)
		########################

		feature = self.process_data_realtime(colproc_skel_data)
		inst = []
		for feat_id in feature['types_order']:
			feat_type = self.id_to_available_type[feat_id]
			if(feature[feat_type] is not None):
				if(self.equate_dim):
					# Interpolate or Extrapolate to fixed dimension
					# print(feature[feat_type].shape)
					mod_feat = feature[feat_type].reshape(self.dim_per_joint*self.num_joints, -1).transpose()
					mod_feat = interpn(mod_feat, self.fixed_num_frames)
					mod_feat = mod_feat.transpose().flatten()
				else:
					mod_feat = feature[feat_type]

				inst = inst + mod_feat.tolist()
		dom_rhand = feature['types_order'][0] == 0 # True if right hand is dominant. False otherwise.
		return dom_rhand, np.array([inst])

	###### ONLINE Function ########
	def decision_fusion(self, prediction_list):
		## DST Code should go here.
		return prediction_list[0]


	###### ONLINE Function ########
	def pred_output_realtime(self, feature_instance, K = 3):
		########################
		# Input arguments:
		#	'feature_instance': numpy.ndarray (1 x feature_size)
		#
		# Return:
		#	class label <string>. for instance, '3_0'
		#	class name <string>. for instance, Rotate_X
		########################

		## Predict
		prediction_list = []
		# for _, clf in self.classifiers.items():
		clf = self.classifiers['svm_clf']
		pred_output = clf.predict(feature_instance)[0]
		class_probabilities = clf.predict_proba(feature_instance)[0]
		top_three_class_ids = np.argsort(class_probabilities)[::-1][:K]
		top_three_class_labels = [self.id_to_labels[self.new_to_old[pred_id]] for pred_id in top_three_class_ids]
		top_three_class_labels_str = ','.join(top_three_class_labels)

		label = self.id_to_labels[self.new_to_old[pred_output]]
		cname = self.label_to_name[label]
		prediction_list.append((pred_output, label, cname))

		final_pred_output, final_label, final_cname = self.decision_fusion(prediction_list)

		# pred_test_output = self.svm_clf.predict(feature_instance)[0]
		# label = self.id_to_labels[pred_test_output]
		# cname = self.label_to_name[label]
		# # print(cname)

		return final_label, final_cname, top_three_class_labels_str

	###### Miscellaneous Function ########
	def find_type_order(self, left, right):
		#####
		# Description:
		#	Determines what hand is dominant. It returns dominant feature type IDs followed by nondominant ones.
		#	If none of them are dominant, it returns RIGHT feature type IDs followed by LEFT ones
		#	Threshold to determine dominancy is ('dominant_first_thresh' = 0.08m). It is found by observation.
		# Input arguments:
		#	'left': numpy.ndarray (_ x 3/6)
		#	'right': numpy.ndarray (_ x 3/6)
		# Return:
		#	list of all ids. Dominant ids followed by nondominant ids.
		#####
		left_std = np.max(np.std(left, axis = 0))
		right_std = np.max(np.std(right, axis = 0))
		assert self.num_available_types % 2 == 0, 'Error! Total no. of types should be even.'
		sz = int(self.num_available_types / 2) # Assumes that actual types ordered as right followed by left
		right_order = range(0, sz)
		left_order = range(sz, 2*sz)
		# print('Right STD: ', right_std)
		# print('Left STD: ', left_std)
		if((right_std - left_std) >= self.dominant_first_thresh): return right_order+left_order
		elif((left_std - right_std) >= self.dominant_first_thresh): return left_order+right_order
		else: return right_order+left_order

	###### Miscellaneous Function ########
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
		plt.xticks(tick_marks, classes, rotation=90)
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

	###### OFFLINE Function ########
	def run_svm(self, data_input, data_output, test_input = None, test_output = None, train_per = 0.8, kernel = 'linear', inst_var_name = 'clf', display = False):
		result = {}

		num_inst = data_input.shape[0]
		feat_dim = data_input.shape[1]
		num_classes = data_output.shape[1]

		## self.randomize
		perm = list(range(data_input.shape[0]))
		shuffle(perm)
		K = int(train_per*num_inst)
		train_input = data_input[perm[:K], :]
		train_output = data_output[perm[:K], :]
		valid_input = data_input[perm[K:], :]
		valid_output = data_output[perm[K:], :]

		# Train
		clf = svm.SVC(decision_function_shape='ova', kernel = kernel, probability = True)
		clf.fit(train_input, np.argmax(train_output, axis =1 ))

		# Train Predict
		pred_train_output = clf.predict(train_input)
		train_acc = float(np.sum(pred_train_output == np.argmax(train_output, axis = 1))) / pred_train_output.size
		result['train_acc'] = train_acc
		print('Train Acc: %.04f'%train_acc)

		# Validation Predict
		pred_valid_output = clf.predict(valid_input)
		valid_acc = float(np.sum(pred_valid_output == np.argmax(valid_output, axis = 1))) / pred_valid_output.size
		result['valid_acc'] = valid_acc
		print('Valid Acc: %.04f'%valid_acc)
		if(display):
			conf_mat = confusion_matrix(np.argmax(valid_output, axis = 1), pred_valid_output)
			cname_list = []
			for idx in range(num_classes):
				cname_list.append(self.label_to_name[self.id_to_labels[self.new_to_old[idx]]])
			self.plot_confusion_matrix(conf_mat, cname_list, normalize = True, title = 'Validation Confusion Matrix')

		## Test Predict
		if(test_input is not None):
			pred_test_output = clf.predict(test_input)

			## Compute top - 3/5 accuracy
			pred_test_prob = clf.predict_proba(test_input)
			temp = np.sum(np.argsort(pred_test_prob, axis = 1)[:,-5:] == np.argmax(test_output, axis = 1).reshape(-1, 1), axis = 1) > 0
			result['test_acc_top5'] = np.mean(temp)
			print('LOSO - Top-5 Acc - ', np.mean(temp))
			temp = np.sum(np.argsort(pred_test_prob, axis = 1)[:,-3:] == np.argmax(test_output, axis = 1).reshape(-1, 1), axis = 1) > 0
			result['test_acc_top3'] = np.mean(temp)
			print('LOSO - Top-3 Acc - ', np.mean(temp))

			test_acc = float(np.sum(pred_test_output == np.argmax(test_output, axis = 1))) / pred_test_output.size
			result['test_acc_top1'] = test_acc
			print('LOSO - Top-1 Acc - %.04f'%test_acc)
			if(display):
				conf_mat = confusion_matrix(np.argmax(test_output, axis = 1), pred_test_output)
				cname_list = []
				for idx in range(test_output.shape[1]):
					cname_list.append(self.label_to_name[self.id_to_labels[self.new_to_old[idx]]])
				self.plot_confusion_matrix(conf_mat, cname_list, normalize = True, title = 'LOSO Confusion Matrix')

		setattr(self, inst_var_name, deepcopy(clf))
		self.classifiers[inst_var_name] = deepcopy(clf)
		result['clf'] = deepcopy(clf)

		return result
