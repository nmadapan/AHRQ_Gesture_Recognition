from glob import glob
import os, sys, time
import numpy as np
import json

def wait_for_kinect(kr):
	# Blocking function. It waits for the all modalities (RGB, Depth, Body) of the Kinect to connect.
	# kr is an object to the kinect_reader
	# from KinectReader import kinect_reader
	# kr = kinect_reader()
	spin = True
	first_rgb, first_depth, first_body = False, False, False
	init_start_time = time.time()
	print 'Connecting to Kinect . ',
	# Wait for all modules (rgb, depth, skeleton) to connect
	while True:
		try:
			# Refreshing Frames
			if first_rgb: kr.update_rgb()
			else: first_rgb = kr.update_rgb()
			if first_depth: kr.update_depth()
			else: first_depth = kr.update_depth()
			if first_body: kr.update_body()
			else: first_body = kr.update_body()
			if (first_rgb and first_depth and first_body): break
			time.sleep(0.5)
			print '. ',
		except Exception as exp:
			print exp
			time.sleep(0.5)
			print '. ',
		if(time.time()-init_start_time > 30):
			sys.exit('Waited for more than 30 seconds. Exiting')
	print '\nAll Kinect modules connected !!'

def skelfile_cmp(path1, path2):
	# Example usage:
		# skelfile_cmp('4_1_S2_L2_Zoom_In_skel.txt', '3_0_S2_L2_Rotate_X_skel.txt')
		# 4_1 is supposed to come after 3_0. So it returns a negative number
	c1, m1 = tuple(map(int, os.path.basename(path1).split('_')[:2]))
	c2, m2 = tuple(map(int, os.path.basename(path2).split('_')[:2]))
	if(c1==c2): return m1 - m2
	else: return c1 - c2

def class_str_cmp(str1, str2):
	# str1 - 3_2, str_2 - 7_1
	# So 3_2 < 7_1
	c1, m1 = tuple(map(int, str1.split('_')))
	c2, m2 = tuple(map(int, str2.split('_')))
	if(c1==c2): return m1 - m2
	else: return c1 - c2

def skel_col_reduce(line, num_joints = 1):
	# Input arguments:
	#	'line' is a list of 75 elements (25 Kinect joints x 3 XYZ)
	#	'num_joints': 1 - only hand, 2 - both hands and the elbow
	#
	# Return arguments:
	#	A tuple (r1, l1)
	#	r1 - list of right hand and elbow xyz in the same order
	#	l1 - list of left hand ane elbow xyz in the same order
	#	NOTE: hand and elbow xyz are wrt shoulder
	#
	# Initialize joint IDs
	left_hand_id = 7
	left_elbow_id = 5
	left_shoulder_id = 4
	right_hand_id = 11
	right_elbow_id = 9
	right_shoulder_id = 8

	dim = 3

	left_shoulder =  np.array(line[dim*left_shoulder_id:dim*left_shoulder_id+dim])
	left_hand = np.array(line[dim*left_hand_id:dim*left_hand_id+dim]) - left_shoulder
	left_elbow = np.array(line[dim*left_elbow_id:dim*left_elbow_id+dim]) - left_shoulder

	right_shoulder =  np.array(line[dim*right_shoulder_id:dim*right_shoulder_id+dim])
	right_hand = np.array(line[dim*right_hand_id:dim*right_hand_id+dim]) - right_shoulder
	right_elbow = np.array(line[dim*right_elbow_id:dim*right_elbow_id+dim]) - right_shoulder

	if(num_joints == 2):
		return np.append(right_hand, right_elbow).tolist(), np.append(left_hand, left_elbow).tolist()
	else:
		return right_hand.tolist(), left_hand.tolist()

def check_consis(xef_folder_path):
	# 'xef_folder_path' --> points to the folder containing folders of XEF files
	# Checks if the files in the subfolders are in correct format.
	# For instance: xef_folder_path = '.\\ABC', where folder ABC contains S1_L3, S2_L3, S3_L3, etc., while each of these folders contain the xef files in a specific format.
	folder_paths = glob(xef_folder_path+'\\') # Get only directories
	if(len(folder_paths) == 0):
		sys.exit('There are NO folders in this path')
	error_strs = []
	for folder_path in folder_paths:
		file_paths = glob(os.path.join(folder_path, '*.xef'))
		for file_path in file_paths:
			file_extract = '_'.join(os.path.basename(file_path).split('_')[2:4])
			fold_extract = os.path.basename(os.path.dirname(folder_path))
			if(file_extract != fold_extract):
				error_strs.append('Error! ' + file_path)
	return len(error_strs)==0, error_strs

def get_file_size(filepath):
	# return file size in KB
	if(not os.path.isfile(filepath)):
		sys.exit('file: '+filepath+' does NOT exist')
	return float('%.1f'%(os.stat(filepath).st_size/1024.0))

def file_filter(xef_files_paths, base_write_folder, in_format_flag, xef_rgb_factor):
	final_file_paths = []
	# Include only xef files that were not completely read before
	for xef_file_path in xef_files_paths:
		xef_filename = os.path.basename(xef_file_path)[:-4]
		if(in_format_flag):
			rgb_path = os.path.join(base_write_folder, xef_filename.split('_')[3], xef_filename+'_rgb.avi')
		else:
			rgb_path = os.path.join(base_write_folder, xef_filename+'_rgb.avi')
		pred_rgb_size = 1000.0 * xef_rgb_factor * get_file_size(xef_file_path)/1024.0/1024.0
		# 5.0 * xef_filesize_in_gb --> this gives no. of seconds in the rgb video. Each sec is an MB approx.
		# Multiply with 1000 to convert into KB. # The value 3.8 is empirically found.
		if(os.path.isfile(rgb_path)):
			if(get_file_size(rgb_path) < float(pred_rgb_size)): # File size in KB
				final_file_paths.append(xef_file_path)
		else:
			final_file_paths.append(xef_file_path)
	return final_file_paths

def json_to_dict(json_filepath):
	if(not os.path.isfile(json_filepath)):
		sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
	with open(json_filepath, 'r') as fp:
		var = json.load(fp)
	return var
