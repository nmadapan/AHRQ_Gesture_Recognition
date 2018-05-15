import numpy as np
import os, sys
from glob import glob
import pickle
from scipy.interpolate import interp1d
from copy import deepcopy
from random import shuffle 
from sklearn import svm

class FeatureExtractor():
	def __init__(self, feature_types = ['right'], all_flag = False, num_joints = 1):
		## Global variables
		self.__types = ['right', 'd_right', 'dd_right', 'theta_right', 'd_theta_right', 'dd_theta_right',\
							 'left', 'd_left', 'dd_left', 'theta_left', 'd_theta_left', 'dd_theta_left']
		self.__num_types = len(self.__types)
		self.__id_to_type = {idx: feat_type for idx, feat_type in zip(range(self.__num_types), self.__types)}

		## Initialization
		self.num_joints = num_joints
		self.type_flags = {feat_type: False for feat_type in self.__types}
		if(not all_flag):
			self.feature_types = feature_types
			self.num_feature_types = len(self.feature_types)
			for feat_type in self.feature_types: 
				if feat_type in self.__types: 
					self.type_flags[feat_type] = True
				else:
					print(feat_type, ' does not exist')
		else:
			self.feature_types = deepcopy(self.__types)
			self.num_feature_types = len(self.feature_types)
			self.type_flags = {feat_type: True for feat_type in self.__types}

	def extract_raw_features(self, skel_filepath, annot_filepath):
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
		if(self.num_joints == 2):
			left = [[line[3*left_hand_id:3*left_hand_id+3], line[3*left_elbow_id:3*left_elbow_id+3], \
				 line[3*left_shoulder_id:3*left_shoulder_id+3]] for line in lines]
			right = [[line[3*right_hand_id:3*right_hand_id+3], line[3*right_elbow_id:3*right_elbow_id+3], \
					 line[3*right_shoulder_id:3*right_shoulder_id+3]] for line in lines]
		else:
			left = [[line[3*left_hand_id:3*left_hand_id+3], line[3*left_shoulder_id:3*left_shoulder_id+3]] \
					for line in lines]
			right = [[line[3*right_hand_id:3*right_hand_id+3], line[3*right_shoulder_id:3*right_shoulder_id+3]] \
					for line in lines]

		left = np.array([np.array(line).flatten().tolist() for line in left])				 
		right = np.array([np.array(line).flatten().tolist() for line in right])

		# Split the skeleton file based on annotations. start to end of the gesture instacne. 
		# Row wise splitting
		for annot in annots:
			xf['left'].append(left[annot[0]:annot[1]+1, :].transpose().flatten())
			xf['right'].append(right[annot[0]:annot[1]+1, :].transpose().flatten())
		
		return xf

	def generate_features(self, skel_filepath, annot_filepath):
		result = []

		xf = self.extract_raw_features(skel_filepath, annot_filepath)

		for inst_id in range(len(xf['right'])):
			features = {feat_type: None for feat_type in self.__types}
						## Put a label
			features['label'] = '_'.join(os.path.basename(skel_filepath).split('_')[:2])

			## Preprocess
			right = xf['right'][inst_id]
			left = xf['left'][inst_id]
			right = right.reshape(3*(self.num_joints+1), -1).transpose()
			left = left.reshape(3*(self.num_joints+1), -1).transpose()			
			d_reps = np.ones(right.shape[0]-2).tolist(); d_reps.append(2)
			dd_reps = np.ones(right.shape[0]-3).tolist(); dd_reps.append(3)

			## Position
			if(self.type_flags['right']):
				right = right[:,0:3*self.num_joints] - np.tile(right[:,3*self.num_joints:], (1, self.num_joints))
				features['right'] = right.transpose().flatten()
			## Velocity
			if(self.type_flags['d_right']):
				d_right = np.diff(right, axis = 0);
				d_right = np.repeat(d_right, d_reps, axis = 0)
				features['d_right'] = d_right.transpose().flatten()
			## Acceleration
			if(self.type_flags['dd_right']):
				dd_right = np.diff(np.diff(right, axis = 0), axis = 0);
				dd_right = np.repeat(dd_right, dd_reps, axis = 0)
				features['dd_right'] = dd_right.transpose().flatten()
			## Angle
			if(self.type_flags['theta_right']):
				theta_right = np.arctan2(d_right, np.roll(d_right, 1, axis = 1))
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

			## Position
			if(self.type_flags['left']):
				left = left[:,0:3*self.num_joints] - np.tile(left[:,3*self.num_joints:], (1, self.num_joints))
				features['left'] = left.transpose().flatten()
			## Velocity
			if(self.type_flags['d_left']):			
				d_left = np.diff(left, axis = 0);
				d_left = np.repeat(d_left, d_reps, axis = 0)
				features['d_left'] = d_left.transpose().flatten()				
			## Acceleration
			if(self.type_flags['dd_left']):
				dd_left = np.diff(np.diff(left, axis = 0), axis = 0);
				dd_left = np.repeat(dd_left, dd_reps, axis = 0)
				features['dd_left'] = dd_left.transpose().flatten()				
			## Angle
			if(self.type_flags['theta_left']):
				theta_left = np.arctan2(d_left, np.roll(d_left, 1, axis = 1))
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

			result.append(features)

		return result

	def batch_generate_features(self, skel_folder_path, annot_folder_path):
		skel_filepaths = glob(os.path.join(skel_folder_path, '*_skel.txt'))
		combos = []
		for skel_filepath in skel_filepaths:
			annot_filepath = os.path.join(annot_folder_path, os.path.basename(skel_filepath)[:-8]+'annot2.txt')
			flag = os.path.isfile(annot_filepath)
			if flag: combos.append((skel_filepath, annot_filepath))

		features = []
		for skel_filepath, annot_filepath in combos:
			temp_features = self.generate_features(skel_filepath, annot_filepath)
			for feat in temp_features: features.append(feat)
		return features

	def generate_io(self, skel_folder_path, annot_folder_path, randomize = True, equate_dim = True, **kwargs):
		features = self.batch_generate_features(skel_folder_path, annot_folder_path)

		out = {'num_classes': -1, 'class_labels': None, 'id_to_labels':None, 'label_to_ids':None, \
				'num_instances': None, 'data_input': [], 'data_output': [], 'num_joints': -1, \
				'num_feature_types': -1}

		class_labels = []
		id_to_labels = {}
		label_to_ids = {}

		for feature in features: class_labels.append(feature['label'])
		class_labels = list(set(class_labels))
		for class_id, label in zip(range(len(class_labels)), class_labels): 
			id_to_labels[class_id] = label
			label_to_ids[label] = class_id
		out['num_classes'] = len(class_labels)
		out['class_labels'] = class_labels
		out['id_to_labels'] = id_to_labels
		out['label_to_ids'] = label_to_ids
		out['num_instances'] = len(features)
		out['num_feature_types'] = self.num_feature_types
		out['num_joints'] = self.num_joints

		I = np.eye(out['num_classes'])

		for feature in features:
			inst = []
			for feat_id, feat_type in self.__id_to_type.items():
				if(feature[feat_type] is not None):
					if(equate_dim):
						mod_feat = feature[feat_type].reshape(3*self.num_joints, -1).transpose()
						mod_feat = self.__interpn(mod_feat, kwargs['num_points'])
						mod_feat = mod_feat.transpose().flatten()
					else:
						mod_feat = feature[feat_type]
						pass
					inst = inst + mod_feat.tolist()
			out['data_input'].append(np.array(inst))
			out['data_output'].append(I[label_to_ids[feature['label']], :])
		if(randomize):
			temp = zip(out['data_input'], out['data_output'])
			shuffle(temp)
			out['data_input'], out['data_output'] = zip(*temp)
			out['data_input'], out['data_output'] = list(out['data_input']), list(out['data_output'])
		if(equate_dim):
			out['data_input'] = np.array(out['data_input'])
			out['data_output'] = np.array(out['data_output'])
		return out

	def __interpn(self, yp, num_points, kind='linear'):
		# yp is a gesture instance
		# yp is 2D numpy array of size num_frames x _
		# No. of frames will be increased/reduced to num_points
		xp = np.linspace(0, 1, num = yp.shape[0])
		x = np.linspace(0, 1, num = num_points)
		y = np.zeros((x.size, yp.shape[1]))
		for dim in range(yp.shape[1]):
			f = interp1d(xp, yp[:, dim], kind=kind)
			y[:, dim] = f(x)
		return y

	def check_svm(self, data_input, data_output, train_per = 0.8, kernel = 'linear'):
		num_inst = data_input.shape[0]
		feat_dim = data_input.shape[1]

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
		pred_output = clf.predict(test_input)
		test_acc = float(np.sum(pred_output == np.argmax(test_output, axis = 1))) / pred_output.size
		print 'Test Acc: ', test_acc