import numpy as np
import os, glob, pickle, re
from scipy.stats import linregress
import matplotlib.pyplot as plt

def compute_distance(arr):
	arr = np.array(arr)
	arr = np.diff(arr, 1, 0)
	left = arr[:,2:4] - arr[:,0:2]
	right = arr[:,4:6] - arr[:,0:2]
	traj_len = np.sum(np.sqrt(np.sum(left**2, 1)).flatten()) + np.sum(np.sqrt(np.sum(right**2, 1)).flatten())
	return (traj_len - 356) * 0.5 / 256

def compute_time(arr):
	return np.array(arr).shape[0] / 30.0

def compute_per_stat_time(arr, thresh):
	tim = compute_time(arr)
	arr = np.array(arr)
	arr = np.diff(arr, 1, 0)
	left = np.sqrt(np.sum((arr[:,2:4] - arr[:,0:2])**2, 1)).flatten()
	right = np.sqrt(np.sum((arr[:,4:6] - arr[:,0:2])**2, 1)).flatten()
	stat_time = 0.5 * (np.sum(left < thresh) + np.sum(right < thresh)) / np.size(left)
	return stat_time

base_ahrq_path = 'F:\Rahul\DropBox\Dropbox\AHRQ_Temp'
base_input_folder = 'F:\Rahul\DropBox\Dropbox\AHRQ_Temp\Results'

folders = os.listdir(base_input_folder)

final_data = [[] for folder in folders if os.path.isdir(os.path.join(base_input_folder, folder))]

for folder in folders:
	folder_path = os.path.join(base_input_folder, folder)
	if not os.path.isdir(folder_path): continue
	pkl_files = glob.glob(os.path.join(folder_path, '*.pkl'))
	coeff = []
	for pkl_file in pkl_files:
		with open(pkl_file, 'rb') as fid:
			arr = pickle.load(fid)
		coeff.append([compute_distance(arr), compute_time(arr), compute_per_stat_time(arr, 8)])
	final_data[int(folder.split('_')[0])-1] = coeff

final_data = np.array(final_data)

with open(os.path.join(base_input_folder, 'kin_prop_data.pkl'), 'wb') as fid:
	pickle.dump(final_data, fid)

with open(os.path.join(base_input_folder, 'kin_prop_data.pkl'), 'rb') as fid:
	kin_data = pickle.load(fid)

vac_info = np.load(os.path.join(base_ahrq_path, 'scores.npz'))
vac_scores = vac_info['scores']

props = ['length', 'time', 'stat_percent']
vacs = ['Iconicity', 'Complexity', 'Efficiency', 'Compactness', 'Salience', 'Amount_of_movement']

stats = []

for kin_idx in range(3):
	for vac_idx in range(6):
		kin_mat = kin_data[:, :, kin_idx].flatten()
		vac_mat = vac_scores[:, :, vac_idx].flatten()
		slope, intercept, r_value, p_value, std_err = linregress(kin_mat, vac_mat)
		print r_value, p_value
		stats.append([kin_idx, vac_idx, r_value**2, p_value])

cmd_idx = 0

for idx in range(len(stats)):
	if abs(stats[idx][2]) > 0.3 and stats[idx][3] < 0.05:
		print props[stats[idx][0]], vacs[stats[idx][1]], stats[idx][2], stats[idx][3]
		kin_mat = kin_data[cmd_idx, :, stats[idx][0]].flatten()
		vac_mat = vac_scores[cmd_idx, :, stats[idx][1]].flatten()
		plt.scatter(kin_mat, vac_mat)
		plt.xlabel(props[stats[idx][0]])
		plt.ylabel(vacs[stats[idx][1]])
		plt.show()

# stats = []
# for vac_idx1 in range(6):
# 	for vac_idx2 in range(vac_idx1+1, 6):
# 		vac_mat1 = vac_scores[:, :, vac_idx1].flatten()
# 		vac_mat2 = vac_scores[:, :, vac_idx2].flatten()
# 		slope, intercept, r_value, p_value, std_err = linregress(vac_mat1, vac_mat2)
# 		print slope, intercept, r_value, p_value, std_err
# 		stats.append([vac_idx1, vac_idx2, r_value, p_value])

# for idx in range(len(stats)):
# 	if abs(stats[idx][2]) > 0.3 and stats[idx][3] < 0.05:
# 		print vacs[stats[idx][0]], vacs[stats[idx][1]], stats[idx][2], stats[idx][3]
# 		vac_mat1 = vac_scores[:, :, stats[idx][0]].flatten()
# 		vac_mat2 = vac_scores[:, :, stats[idx][1]].flatten()
# 		plt.scatter(vac_mat1, vac_mat2)
# 		plt.xlabel(vacs[stats[idx][0]])
# 		plt.ylabel(vacs[stats[idx][1]])
# 		plt.show()