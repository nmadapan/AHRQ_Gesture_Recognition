from glob import glob
import os, sys, time
import numpy as np

def wait_for_kinect(kr):
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

def skel_col_reduce(line, num_joints = 1):
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

def file_filter(xef_files_paths, base_write_folder, xef_rgb_factor):
	final_file_paths = []
	# Include only xef files that were not completely read before
	for xef_file_path in xef_files_paths:
		xef_filename = os.path.basename(xef_file_path)[:-4]
		rgb_path = os.path.join(base_write_folder, xef_filename.split('_')[3], xef_filename+'_rgb.avi')
		pred_rgb_size = 1000.0 * xef_rgb_factor * get_file_size(xef_file_path)/1024.0/1024.0
		# 5.0 * xef_filesize_in_gb --> this gives no. of seconds in the rgb video. Each sec is an MB approx. 
		# Multiply with 1000 to convert into KB. # The value 3.8 is empirically found. 
		if(os.path.isfile(rgb_path)):
			if(get_file_size(rgb_path) < float(pred_rgb_size)): # File size in KB
				final_file_paths.append(xef_file_path)
		else:
			final_file_paths.append(xef_file_path)
	return final_file_paths
