from glob import glob
import os, sys, time
import numpy as np
import json
from scipy.interpolate import interp1d
import cv2

#######################
### Kinect Joint IDs ##
#######################
## Left hand
left_hand_id = 7
left_elbow_id = 5
left_shoulder_id = 4
left_wrist_id = 6
left_handtip_id = 21
left_thumb_id = 22

## Right hand
right_hand_id = 11
right_elbow_id = 9
right_shoulder_id = 8
right_wrist_id = 10
right_handtip_id = 23
right_thumb_id = 24

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

def get_lhand_bbox(color_skel_pts, des_size = 300):
	############
	# Input arguments:
	#	'color_skel_pts': A list of 50 elements. Pixel coordinates of 25 Kinect joints. 
	#		Format: [x1, y1, x2, y2, ...]
	#	'des_size': Size of the bounding box
	#
	# Return:
	#	'bbox': list of four values. [x, y, w, h]. 
	#		(x, y): pixel coordinates of top left corner of the bbox
	#		(w, h): width and height of the boox. 
	############
	## Return left hand bounding box
	hand = np.array(color_skel_pts[2*left_hand_id:2*left_hand_id+2])
	return [np.int32(hand[0]) - des_size/2, np.int32(hand[1]) - des_size/2, des_size, des_size]

def get_rhand_bbox(color_skel_pts, des_size = 300):
	############
	# Input arguments:
	#	'color_skel_pts': A list of 50 elements. Pixel coordinates of 25 Kinect joints. 
	#		Format: [x1, y1, x2, y2, ...]
	#	'des_size': Size of the bounding box
	#
	# Return:
	#	'bbox': list of four values. [x, y, w, h]. 
	#		(x, y): pixel coordinates of top left corner of the bbox
	#		(w, h): width and height of the boox. 
	############	
	## Return right hand bounding box
	hand = np.array(color_skel_pts[2*right_hand_id:2*right_hand_id+2])
	return [np.int32(hand[0]) - des_size/2, np.int32(hand[1]) - des_size/2, des_size, des_size]

def get_hand_bbox(hand_pixel_coo, des_size = 300):
	############
	# Input arguments:
	#	'hand_pixel_coo': A list of two elements. Pixel coordinates of hand.
	#		Format: [x1, y1]
	#	'des_size': Size of the bounding box
	#
	# Return:
	#	'bbox': list of four values. [x, y, w, h]. 
	#		(x, y): pixel coordinates of top left corner of the bbox
	#		(w, h): width and height of the boox. 
	############	
	hand = hand_pixel_coo
	return [np.int32(hand[0]) - des_size/2, np.int32(hand[1]) - des_size/2, des_size, des_size]

def nparray_to_str(arr, dlim = '_'):
	return dlim.join(map(str, np.array(arr).flatten().tolist()))

def str_to_nparray(arr_str, dlim = '_'):
	return np.array(map(float, arr_str.split(dlim)))

def sync_ts(skel_ts, rgb_ts):
	# skel_ts: List of skeleton time stamps. [t1, t2, ...]
	# rgb_ts: list of rgb timestams. [t1, t2, t3, ...]
	skel_ts = np.reshape(skel_ts, (-1, 1))
	rgb_ts = np.reshape(rgb_ts, (1, -1))
	M = np.abs(skel_ts - rgb_ts)
	apply_on_skel = np.argmin(M, axis = 0)
	apply_on_rgb = np.argmin(M, axis = 1)
	return apply_on_skel.tolist(), apply_on_rgb.tolist()

def get_body_length(line):
	# line is a list of 75 elements. [x, y, z, so on for all of the kinect joints]

	torso_id = 0
	neck_id = 2

	torso = np.array(line[3*torso_id:3*torso_id+3])
	neck = np.array(line[3*neck_id:3*neck_id+3])

	return np.linalg.norm(neck-torso)

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

def skel_col_reduce(line, dim = 3, num_joints = 1, wrt_shoulder = True):
	# Input arguments:
	#	'line' is a list of 75/50 elements (25 Kinect joints x 3 XYZ)
	#	'num_joints': 1 - only hand, 2 - both hands and the elbow
	#	'dim': 3 if 'line' consists of 3D x,y,z. 2 if 'line' consists of pixel coordinates. 
	#	'wrt_shoulder': If True, return hand/elbow coordinates w.r.t shoulder. 
	#		If False, return actual corrdinates of hand/elbow.
	#
	# Return arguments:
	#	A tuple (r1, l1)
	#	r1 - list of right hand and elbow xyz in the same order
	#	l1 - list of left hand ane elbow xyz in the same order
	#	NOTE: hand and elbow xyz are wrt shoulder if 'wrt_shoulder' is True.
	#
	# Initialize joint IDs
	left_hand_id = 7
	left_elbow_id = 5
	left_shoulder_id = 4
	right_hand_id = 11
	right_elbow_id = 9
	right_shoulder_id = 8

	left_shoulder =  np.array(line[dim*left_shoulder_id:dim*left_shoulder_id+dim])
	left_hand = np.array(line[dim*left_hand_id:dim*left_hand_id+dim])
	left_elbow = np.array(line[dim*left_elbow_id:dim*left_elbow_id+dim])

	right_shoulder =  np.array(line[dim*right_shoulder_id:dim*right_shoulder_id+dim])
	right_hand = np.array(line[dim*right_hand_id:dim*right_hand_id+dim])
	right_elbow = np.array(line[dim*right_elbow_id:dim*right_elbow_id+dim])

	if(wrt_shoulder): 
		left_hand -= left_shoulder
		left_elbow -= left_shoulder	
		right_hand -= right_shoulder
		right_elbow -= right_shoulder	

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
		raise IOError('There are NO folders in this path')
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
		raise IOError('file: '+filepath+' does NOT exist')
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
		raise IOError('Error! Json file: '+json_filepath+' does NOT exists!')
	with open(json_filepath, 'r') as fp:
		var = json.load(fp)
	return var


def flip_skeleton(skel_path, out_path, dim_per_joint=3):
	############
	# Flips the body skeleton along the persons vertical axis.
	# Input argument:
	#	* skel_path: path to skeleton file. Each line in the file has dim_per_joint*25 elements. [x1, y1, z1 ...]
	#	* outPath: path to place the output file.
	#   * dim_per_joint: the number of joints to be flipped
	#
	# Assumptions:
	#	* There is only roll angle about person's veritcal axis
	#	* Kinect is not tilted.
	###########
	
	with open(skel_path, 'r') as fp:
		lines = fp.readlines()
		lines = [map(float, line.strip().split(' ')) for line in lines]

	fp = open(out_path, 'w') 

	left_sh_idx = 4
	right_sh_idx = 8
	spine_idx = 0

	for line in lines:
		torso = np.array(line[dim_per_joint*spine_idx:dim_per_joint*spine_idx+dim_per_joint] )
		left_sh = np.array(line[dim_per_joint*left_sh_idx:dim_per_joint*left_sh_idx+dim_per_joint])
		right_sh = np.array(line[dim_per_joint*right_sh_idx:dim_per_joint*right_sh_idx+dim_per_joint])
		
		mat = np.reshape(line, (25, dim_per_joint))

		# Normalize w.r.t torso
		mat = mat - torso

		if dim_per_joint > 2:
			# Find the theta
			zr = right_sh[-1]
			zl = left_sh[-1]
			shoulder_length = np.linalg.norm(left_sh-right_sh)
			theta = np.arcsin((zr-zl)/shoulder_length)

			R = np.eye(dim_per_joint)
			R[0, 0] = np.cos(theta)
			R[0, 2] = np.sin(theta)
			R[2, 0] = -np.sin(theta)
			R[2, 2] = np.cos(theta)

			# Transform the matrix
			mat = np.dot(R, mat.transpose())
			mat[0, :] = -mat[0, :]
			mat = mat.transpose() + torso
		else:
			mat[0, :] = -mat[0, :]
			mat = mat + torso

		line = mat.flatten()
		fp.write(' '.join(map(str, line)) + '\n')

	fp.flush()
	fp.close()

def smart_interpn(yp, reps, kind = 'copy'):
	# yp:
	#	2D numpy array of size num_frames x 3 if num_joints = 1
	#
	# reps:
	#	1D numpy array whose elements range from [0, num_frames-1]. Note that the size of reps is usually larger than num_frames
	#
	# kind: 
	#	'linear'	- linear interpolation
	#	'copy'		- do the copy

	assert isinstance(yp, np.ndarray), 'yp is NOT a numpy array'
	assert yp.ndim == 2, 'yp should be a 2D numpy array'

	out = np.float32(yp[reps, :])

	if(kind == 'copy'): return out

	rep_ids = range(0, 1 + np.max(reps))
	for idx, rep_id in enumerate(rep_ids):
		# We will not interpolate the last index
		if idx == len(rep_ids)-1 : break
		elem_ids = np.argwhere(reps == rep_id).flatten()
		req_ids = [elem_ids[0], elem_ids[-1]+1]
		out[elem_ids, :] =  interpn(out[req_ids, :], elem_ids.size+1)[:-1, :]
	return out

def interpn(yp, num_points, kind = 'linear'):
	# yp is a gesture instance
	# yp is 2D numpy array of size num_frames x 3 if num_joints = 1
	# No. of frames will be increased/reduced to num_points
	xp = np.linspace(0, 1, num = yp.shape[0])
	x = np.linspace(0, 1, num = num_points)
	y = np.zeros((x.size, yp.shape[1]))
	yp = np.float16(yp)
	for dim in range(yp.shape[1]):
		f = interp1d(xp, yp[:, dim], kind = kind)
		y[:, dim] = f(x)
	return y

def flip_video(input_video_path, out_video_path):
	cap = cv2.VideoCapture(input_video_path)
	fps = cap.get(cv2.CAP_PROP_FPS)
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

	# Define the codec and create VideoWriter object
	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	out = cv2.VideoWriter(out_video_path,fourcc, fps, (width,height))

	while(cap.isOpened()):
	    ret, frame = cap.read()
	    if ret==True:
	        frame = cv2.flip(frame,1)
	        out.write(frame)
	    else:
	        break
	# Release everything if job is finished
	cap.release()
	out.release()
	cv2.destroyAllWindows()
