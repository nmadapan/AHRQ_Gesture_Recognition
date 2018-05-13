import numpy as np
import os, sys
from glob import glob
import pickle

class FeatureExtractor():
	def __init__(self, num_points = 60):
		self.num_points = num_points
		pass

	def extract_raw_features(self, skel_filepath, annot_filepath):
		with open(annot_filepath, 'r') as fp:
			annots = np.array([int(word.strip('\n')) for word in fp.readlines()])
			annots = annots.reshape(annots.shape[0]/2, -1)

		left_hand_id = 7
		left_elbow_id = 5
		left_shoulder_id = 4

		right_hand_id = 11
		right_elbow_id = 9
		right_shoulder_id = 8

		with open(skel_filepath, 'r') as fp:
			lines = [map(float, line.split(' ')) for line in fp.readlines()]

		left = [[line[3*left_hand_id:3*left_hand_id+3], line[3*left_elbow_id:3*left_elbow_id+3], \
				 line[3*left_shoulder_id:3*left_shoulder_id+3]] for line in lines]
		right = [[line[3*right_hand_id:3*right_hand_id+3], line[3*right_elbow_id:3*right_elbow_id+3], \
				 line[3*right_shoulder_id:3*right_shoulder_id+3]] for line in lines]

		left = np.array([np.array(line).flatten().tolist() for line in left])
		right = np.array([np.array(line).flatten().tolist() for line in right])

		xf = {'left': [], 'right': []}

		for annot in annots:
			xf['left'].append(left[annot[0]:annot[1]+1, :].transpose().flatten())
			xf['right'].append(right[annot[0]:annot[1]+1, :].transpose().flatten())
		
		return xf

	def generate_all_features(self, skel_filepath, annot_filepath):
		result = []

		xf = self.extract_raw_features(skel_filepath, annot_filepath)
		left, right = xf['left'], xf['right']

		for inst_id in range(len(xf['left'])):
			features = {}

			left = xf['left'][inst_id]
			right = xf['right'][inst_id]
			left = left.reshape(9, -1).transpose()
			right = right.reshape(9, -1).transpose()

			## Position
			left = left[:,0:6] - np.tile(left[:,6:], (1, 2))
			right = right[:,0:6] - np.tile(right[:,6:], (1, 2))
			features['left'] = left.transpose().flatten()
			features['right'] = right.transpose().flatten()

			## Velocity
			d_reps = np.ones(left.shape[0]-2).tolist(); d_reps.append(2)
			d_left = np.diff(left, axis = 0);
			d_left = np.repeat(d_left, d_reps, axis = 0)
			d_right = np.diff(right, axis = 0);
			d_right = np.repeat(d_right, d_reps, axis = 0)
			features['d_left'] = d_left.transpose().flatten()
			features['d_right'] = d_right.transpose().flatten()

			## Acceleration
			dd_reps = np.ones(left.shape[0]-3).tolist(); dd_reps.append(3)
			dd_left = np.diff(np.diff(left, axis = 0), axis = 0);
			dd_left = np.repeat(dd_left, dd_reps, axis = 0)
			dd_right = np.diff(np.diff(right, axis = 0), axis = 0);
			dd_right = np.repeat(dd_right, dd_reps, axis = 0)
			features['dd_left'] = dd_left.transpose().flatten()
			features['dd_right'] = dd_right.transpose().flatten()

			## Angle
			theta_left = np.arctan2(d_left, np.roll(d_left, 1, axis = 1))
			theta_right = np.arctan2(d_right, np.roll(d_right, 1, axis = 1))
			features['theta_left'] = theta_left.transpose().flatten()
			features['theta_right'] = theta_right.transpose().flatten()

			## Angular velocity
			d_theta_left = np.diff(theta_left, axis = 0);
			d_theta_left = np.repeat(d_theta_left, d_reps, axis = 0)
			d_theta_right = np.diff(theta_right, axis = 0);
			d_theta_right = np.repeat(d_theta_right, d_reps, axis = 0)
			features['d_theta_left'] = d_theta_left.transpose().flatten()
			features['d_theta_right'] = d_theta_right.transpose().flatten()

			## Angular acceleration
			dd_theta_left = np.diff(np.diff(theta_left, axis = 0), axis = 0);
			dd_theta_left = np.repeat(dd_theta_left, dd_reps, axis = 0)
			dd_theta_right = np.diff(np.diff(theta_right, axis = 0), axis = 0);
			dd_theta_right = np.repeat(dd_theta_right, dd_reps, axis = 0)
			features['dd_theta_left'] = dd_theta_left.transpose().flatten()
			features['dd_theta_right'] = dd_theta_right.transpose().flatten()

			result.append(features)

		return result

