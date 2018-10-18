import numpy as np,sys,os
from helpers import skel_col_reduce
import matplotlib.pyplot as plt
import json
from glob import glob

def pose_calib_data(skelpath):
	def filtered_max(skelpath, plot = False):
		ignore_from = int(0.25*len(lines))
		arm_list = [] 

		for line in lines[ignore_from:]:
			right, left = skel_col_reduce(line, num_joints = 2)
			right, left = np.array(right), np.array(left)
			r_hand, r_elbow = right[:3], right[3:]
			l_hand, l_elbow = left[:3], left[3:]

			r_hand = r_hand - r_elbow 
			l_hand = l_hand - l_elbow 
			arm_list.append(np.linalg.norm(l_elbow) + np.linalg.norm(l_hand))
			arm_list.append(np.linalg.norm(r_elbow) + np.linalg.norm(r_hand))

		if(plot):
			plt.plot(arm_list)
			plt.show()

		# return min(np.max(arm_list), np.median(arm_list) + 3 * np.std(arm_list))
		return np.median(arm_list)
	with open(skelpath, 'r') as fp:
		lines = fp.readlines()
		lines = [map(float, line.strip().split(' ')) for line in lines]

	max_r = np.round(filtered_max(lines),4)

	lines = np.abs(np.diff(np.array(lines), axis = 0)).tolist()
	max_dr = np.round(filtered_max(lines),4)
	return max_r,max_dr

if __name__ == '__main__':
	basepath = r'H:\AHRQ\Study_IV\Flipped_Data\L6'
	subject_ids = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
	skelfiles = glob(os.path.join(basepath, '*skel.txt'))

	arm_length_dict = {subject_id: [] for subject_id in subject_ids}
	final_lengths = {subject_id: [] for subject_id in subject_ids}

	for subject_id in subject_ids:
		print subject_id, 
		for skelfile in skelfiles:
			if subject_id in skelfile:
				max_r, _ = pose_calib_data(skelfile)
				arm_length_dict[subject_id].append(max_r)
		final_lengths[subject_id] = np.max(arm_length_dict[subject_id])
		print final_lengths[subject_id]

	print final_lengths


