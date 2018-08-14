import numpy as np
from helpers import skel_col_reduce
import matplotlib.pyplot as plt
import json

# skelpath = 'E:\\AHRQ\\XEF_Files\\Calib\\Calib_Data\\S3_Pose1_skel.txt'

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

	return min(np.max(arm_list), np.mean(arm_list) + np.std(arm_list))

def pose_calib_data(skelpath):
	# def filtered_max(skelpath, plot = False):
	# 	ignore_from = int(0.25*len(lines))
	# 	arm_list = [] 

	# 	for line in lines[ignore_from:]:
	# 		right, left = skel_col_reduce(line, num_joints = 2)
	# 		right, left = np.array(right), np.array(left)
	# 		r_hand, r_elbow = right[:3], right[3:]
	# 		l_hand, l_elbow = left[:3], left[3:]

	# 		r_hand = r_hand - r_elbow 
	# 		l_hand = l_hand - l_elbow 
	# 		arm_list.append(np.linalg.norm(l_elbow) + np.linalg.norm(l_hand))
	# 		arm_list.append(np.linalg.norm(r_elbow) + np.linalg.norm(r_hand))

	# 	if(plot):
	# 		plt.plot(arm_list)
	# 		plt.show()

	# 	return min(np.max(arm_list), np.mean(arm_list) + np.std(arm_list))
	with open(skelpath, 'r') as fp:
		lines = fp.readlines()
		lines = [map(float, line.strip().split(' ')) for line in lines]

	max_r = np.round(filtered_max(lines),4)

	lines = np.abs(np.diff(np.array(lines), axis = 0)).tolist()
	max_dr = np.round(filtered_max(lines),4)
	return max_r,max_dr
# print max_r, max_dr