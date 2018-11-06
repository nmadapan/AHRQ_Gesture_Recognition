from __future__ import print_function

from glob import glob
import os, sys, time
import numpy as np
import json
from scipy.interpolate import interp1d
import cv2
import re

###########
## PATHS ##
###########
kinect_joint_names_path = 'kinect_joint_names.json'

def json_to_dict(json_filepath):
	if(not os.path.isfile(json_filepath)):
		raise IOError('Error! Json file: '+json_filepath+' does NOT exists!')
	with open(json_filepath, 'r') as fp:
		var = json.load(fp)
	return var

########################
### Kinect Joint IDs ###
########################
## Refer to kinect_joint_names.json for all joint IDs

kinect_joint_names_dict = json_to_dict(kinect_joint_names_path)

## Left hand
left_hand_id = kinect_joint_names_dict['JointType_HandLeft'] # 7
left_elbow_id = kinect_joint_names_dict['JointType_ElbowLeft'] # 5
left_shoulder_id = kinect_joint_names_dict['JointType_ShoulderLeft'] # 4

## Right hand
right_hand_id = kinect_joint_names_dict['JointType_HandRight'] # 11
right_elbow_id = kinect_joint_names_dict['JointType_ElbowRight'] # 9
right_shoulder_id = kinect_joint_names_dict['JointType_ShoulderRight'] # 8

## Torso
torso_id = kinect_joint_names_dict['JointType_SpineBase'] # 0
neck_id = kinect_joint_names_dict['JointType_Neck'] # 2

def wait_for_kinect(kr, timeout = 30):
	'''
	Description:
		* This function waits for the all modalities (RGB, Depth, Body) of the Kinect to connect. It is a blocking function.
	Input arguments:
		* kr is an object of kinect_reader class present in KinectReader module
		* timeout is time in seconds. How long to wait for connection.
	How to call:
		from KinectReader import kinect_reader
		kr = kinect_reader()
		wait_for_kinect(kr)
	'''

	## Initialization
	first_rgb, first_depth, first_body = False, False, False
	init_start_time = time.time()
	print('Connecting to Kinect . ', end = '')

	## Wait for all modules (rgb, depth, skeleton) to connect for timeout secs.
	while True:
		try:
			# Refreshing RGB Frames
			if first_rgb: kr.update_rgb()
			else: first_rgb = kr.update_rgb()
			# Refreshing Depth Frames
			if first_depth: kr.update_depth()
			else: first_depth = kr.update_depth()
			# Refreshing Body Frames
			if first_body: kr.update_body()
			else: first_body = kr.update_body()
			if (first_rgb and first_depth and first_body): break
			time.sleep(0.5)
			print('. ', end = '')
		except Exception as exp:
			print(exp)
			time.sleep(0.5)
			print('. ', end = '')
		if(time.time()-init_start_time > timeout):
			sys.exit('Waited for more than ' + str(timeout) + ' seconds. Exiting')
	print('\nAll Kinect modules connected !!')

def get_lhand_bbox(color_skel_pts, max_wh = (1920, 1080), \
                   des_size = 300):
	'''
	Input arguments:
		* color_skel_pts: A list of 50 elements. Pixel coordinates of 25 Kinect joints. Format: [x1, y1, x2, y2, ...]
		* des_size: Size of the square bounding box
	Return:
		* bbox: list of four values. [x, y, w, h].
			(x, y): pixel coordinates of top LEFT corner of the bbox
			(w, h): width and height of the bounding box.
	'''
	##
	half_sz = np.int32(des_size/2)
	max_x, max_y = max_wh

	## Return left hand bounding box
	hand = np.array(color_skel_pts[2*left_hand_id:2*left_hand_id+2])
	x = np.int32(hand[0]) - half_sz
	y = np.int32(hand[1]) - half_sz

	## Handle the boundary conditions
	if(x < 0): x = 0
	if(y < 0): y = 0
	if(x+des_size >= max_x): x = max_x - des_size - 1
	if(y+des_size >= max_y): y = max_y - des_size - 1

	return [x, y, des_size, des_size]

def get_rhand_bbox(color_skel_pts, max_wh = (1920, 1080), des_size = 300):
	'''
	Input arguments:
		* color_skel_pts: A list of 50 elements. Pixel coordinates of 25 Kinect joints. Format: [x1, y1, x2, y2, ...]
		* des_size: Size of the square bounding box
	Return:
		* bbox: list of four values. [x, y, w, h].
			(x, y): pixel coordinates of top RIGHT corner of the bbox
			(w, h): width and height of the bounding box.
	'''
	##
	half_sz = np.int32(des_size/2)
	max_x, max_y = max_wh

	## Return right hand bounding box
	hand = np.array(color_skel_pts[2*right_hand_id:2*right_hand_id+2])
	x = np.int32(hand[0]) - half_sz
	y = np.int32(hand[1]) - half_sz

	## Handle the boundary conditions
	if(x < 0): x = 0
	if(y < 0): y = 0
	if(x+des_size > max_x): x = max_x - des_size - 1
	if(y+des_size > max_y): y = max_y - des_size - 1

	return [x, y, des_size, des_size]

def get_hand_bbox(hand_pixel_coo, max_wh = (1920, 1080), des_size = 300):
	'''
	Input arguments:
		* hand_pixel_coo: A list/tuple of two elements. Pixel coordinates of hand. Format: [x1, y1] or (x1, y1)
		* des_size: Size of the bounding box
	Return:
		* bbox: list of four values. [x, y, w, h].
			(x, y): pixel coordinates of top left corner of the bbox
			(w, h): width and height of the boox.
	'''
	##
	half_sz = np.int32(des_size/2)
	max_x, max_y = max_wh

	## Return hand bounding box
	hand = hand_pixel_coo
	x = np.int32(hand[0]) - half_sz
	y = np.int32(hand[1]) - half_sz

	## Handle the boundary conditions
	if(x < 0): x = 0
	if(y < 0): y = 0
	if(x+des_size > max_x): x = max_x - des_size - 1
	if(y+des_size > max_y): y = max_y - des_size - 1

	return [x, y, des_size, des_size]

def nparray_to_str(arr, dlim = '_'):
	'''
	Description:
		Convert a np.ndarray of ints/floats to string with a given delimiter.
	Input arguments:
		* arr: np.ndarray of any dimension
		* dlim: delimiter. It is a string.
	Return:
		* String of elements in the np.ndarray joined using the given delimiter.
	'''
	return dlim.join(map(str, np.array(arr).flatten().tolist()))

def str_to_nparray(arr_str, dlim = '_'):
	'''
	Description:
		Convert a string consisting of ints/floats concatenated using the given delimiter into a flattened np.ndarray.
	Input arguments:
		* arr_str: string
		* dlim: delimiter. It is a string.
	Return:
		* np.ndarray of ints/floats.
	'''
	return np.array(map(float, arr_str.split(dlim)))

def sync_ts(skel_ts, rgb_ts):
	'''
	Description:
		Synchronize two lists of time stamps.
	Input arguments:
		* skel_ts: list of skeleton time stamps. [t1, t2, ..., ta]
		* rgb_ts: list of rgb times tamps. [t1, t2, t3, ..., tb]
	Return:
		* A tuple (apply_on_skel, apply_on_rgb)
			apply_on_skel: What is the corresponding rgb time stamp for every skeleton time stamp.
			apply_on_rgb: What is the corresponding skeleton time stamp for every rgb time stamp.
	'''
	skel_ts = np.reshape(skel_ts, (-1, 1))
	rgb_ts = np.reshape(rgb_ts, (1, -1))
	M = np.abs(skel_ts - rgb_ts)
	apply_on_skel = np.argmin(M, axis = 0)
	apply_on_rgb = np.argmin(M, axis = 1)
	return apply_on_skel.tolist(), apply_on_rgb.tolist()

def get_body_length(line):
	'''
	Description:
		Given the body skeleton, compute the distance between torso and neck.
	Input arguments:
		* line: a list of 75 elements. [x, y, z, so on for all of the 25 kinect joints]. Refer to kinect_joint_names.json for full list of joint ids.
	Return:
		* The distance between neck and the torso in meters.
	'''
	torso = np.array(line[3*torso_id:3*torso_id+3])
	neck = np.array(line[3*neck_id:3*neck_id+3])
	return np.linalg.norm(neck-torso)

def skelfile_cmp(path1, path2):
	'''
	Description:
		Compare two skeleton file paths. Format of the path is the following ('a/b/4_1_S*_L*_Context_Modifier_skel.txt)
	Input arguments:
		* path1: string. Path to a skeleton file.
		* path2: string. Path to a skeleton file.
	Return:
		* Negative number if path2 is smaller than path1, positive number otherwise.
	Example usage:
		# skelfile_cmp('4_1_S2_L2_Zoom_In_skel.txt', '3_0_S2_L2_Rotate_X_skel.txt')
		# 4_1 is supposed to come after 3_0. So it returns a negative number
	'''
	c1, m1 = tuple(map(int, os.path.basename(path1).split('_')[:2]))
	c2, m2 = tuple(map(int, os.path.basename(path2).split('_')[:2]))
	if(c1==c2): return m1 - m2
	else: return c1 - c2

def class_str_cmp(str1, str2):
	'''
	Description:
		Compare two class_strings. Format of the class_string is the following: ('4_1'). Refer to commands.json for all available class_strings.
	Input arguments:
		* str1: a class string.
		* str2: a class string.
	Return:
		* Negative number if str2 is smaller than str1, positive number otherwise.
	Example usage:
		# class_str_cmp('4_1', '3_0')
		# 4_1 is supposed to come after 3_0. So it returns a negative number
	'''
	# str1 - 3_2, str_2 - 7_1
	# So 3_2 < 7_1
	c1, m1 = tuple(map(int, str1.split('_')))
	c2, m2 = tuple(map(int, str2.split('_')))
	if(c1==c2): return m1 - m2
	else: return c1 - c2

def skel_col_reduce(line, dim = 3, num_joints = 1, wrt_shoulder = True):
	'''
	Description:
		Given the skeleton frame of body or rgb from kinect (list of 75/50 elements), return hand and elbow coordinates of both the hands w.r.t the shoulder.
	Input arguments:
		* line is a list of 75/50 elements (25 Kinect joints x 3 XYZ)
		* num_joints: 1 - only hand, 2 - both hands and the elbow
		* dim: 3 if 'line' consists of 3D x,y,z. 2 if 'line' consists of pixel coordinates.
		* wrt_shoulder: If True, return hand/elbow coordinates w.r.t shoulder.
			If False, return actual corrdinates of hand/elbow.
	Return:
		A tuple (r1, l1)
		r1 - list of right hand and elbow xyz in the same order. [x, y, z]
		l1 - list of left hand ane elbow xyz in the same order. [x, y, z]
		NOTE: hand and elbow xyz are wrt shoulder if 'wrt_shoulder' is True.
	'''

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
	'''
	Description:
		Check if the files present in the folders of 'xef_folder_path' are consistent.
		Say 'xef_folder_path' consists of following folders with the names 'S1_L2' and 'S1_L6'. Now 'S1_L2' folder is expected to contain files in the following format: '*_*_S1_L2_*_*.xef'. Similarly, 'S1_L2' folder is expected to contain files in the following format: '*_*_S1_L6_*_*.xef'. This functions if the filenames are consistent w.r.t the folder names.
	Input arguments:
		* xef_folder_path: path to the directory consisting of folders which contain xef files.
	Return:
		A tuple (flag, error_strs)
			* if flag is True, all folders are consistent. If False, look at error_strs to find inconsistent XEF filenames.
			* error_strs is a list of inconsitent XEF filenames.
	Example:
		xef_folder_path = '.\\ABC', where folder ABC contains S1_L3, S2_L3, S3_L3, etc., while each of these folders contain the xef files in a specific format.
	'''
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
	'''
	Description:
		Return the estimated the size of the .xef file in KB
	Input arugments:
		* filepath: absolute path to the .xef file.
	Return:
		* Return the estimated the size of the .xef file in KB
	'''
	if(not os.path.isfile(filepath)):
		raise IOError('file: '+filepath+' does NOT exist')
	return float('%.1f'%(os.stat(filepath).st_size/1024.0))

def file_filter(xef_files_paths, base_write_folder, in_format_flag, xef_rgb_factor):
	'''
	Description:
		Filter the list of .xef file paths. Only retail those xef file paths whose corresponding rgb video size is less than a particular threshold. This threshold depends on the size of the xef file.
	Input arguments:
		* xef_file_paths: a list of xef file paths. Each file path points to a .xef file. Format of the file path: 'a/b/*_*_*_*_*_*.xef'
		* base_write_folder: path consisting of folders containing data (rgb video file, depth video file, skeleton timestamps, etc.) obtained from the .xef files.
		* in_format_flag: If True, file paths must be in the predetermined format. If False, file paths need not be in a specific format.
		* xef_rgb_factor: An factor that approximately maps the size of .xef file to the size of the rgb video.
	Return:
		A list of xef files paths whose size of rgb files is less than the predicted size.
	'''
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

def flip_skeleton(skel_path, out_path, dim_per_joint=3):
	'''
	Description:
		Flips the body skeleton along the persons vertical axis.
	Input arguments:
		* skel_path: path to skeleton file. Each line in the file has dim_per_joint*25 elements. [x1, y1, z1 ...]
		* outPath: path to place the output file.
		* dim_per_joint: the number of joints to be flipped
	Assumptions:
		* There is only roll angle about person's veritcal axis
		* Kinect is not tilted.
	'''

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
	'''
	Description:
		Smart inpterpolation of the given 2D np.ndarray along the rows.
	Input arguments:
		* yp: np.ndarray of shape nr x nc. For instance, it is a 2D numpy array of size num_frames x 3 if num_joints = 1
		* reps: 1D numpy array whose elements range from [0, num_frames-1]. Note that the size of reps is usually larger than num_frames
		* kind: type of interpolation. 'linear' (linear interpolation) or 'copy' (copy whenever replications happen).
	Return:
		np.ndarray with no. of rows equal to the size of 'reps' and no. of columns same as 'yp'.
	How to use:
		* 'yp': np.ndarray of size 7 x 3
		* If 'reps' looks like [0 0 1 1 2 2 3 4 5 5 6]. 'reps' has 11 elements.
			- It basically means 0th row is repeated twice, 1st row is repeated twice and so on.
		* Now the idea is to interpolate w.r.t the given 'reps'
		* It outputs the an np.ndarray of size 11 x 3. Type of interpolation is determined by the argument 'kind'
	'''
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
	'''
	Description:
		Inpterpolation the given 2D np.ndarray along the rows.
	Input arguments:
		* yp: np.ndarray of shape nr x nc
		* num_points: desired no. of rows
		* kind: type of interpolation. linear or poly. Refer to interp1d of scipy.interpolate for more types of interpolation.
	Return:
		np.ndarray with no. of rows equal to num_points and no. of columns same as 'yp'.
	'''
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

def save_list(list_of_values, out_file_path):
	# list_of_values: list of sublists where each sublist can be a list of values (integers, floats or strings)
	#	It can be a list of values too.
	if(not isinstance(list_of_values[0], list)):
		with open(out_file_path, 'w') as fp:
			for value in list_of_values:
				fp.write(str(value) + '\n')
	else:
		with open(out_file_path, 'w') as fp:
			for sublist in list_of_values:
				for value in sublist:
					fp.write(str(value) + ' ')
				fp.write('\n')

def save_video(list_of_frames, out_video_path, display = False):
	# list_of_frames: list of RGB or Grayscale frames

	assert len(list_of_frames) > 0, 'Error! list_of_frames is empty'

	# Define the codec and create VideoWriter object
	fourcc = cv2.VideoWriter_fourcc(*'XVID')

	if(list_of_frames[0].ndim == 2):
		height, width = list_of_frames[0].shape
	else:
		height, width, _ = list_of_frames[0].shape

	out = cv2.VideoWriter(out_video_path, fourcc, 30, (width,height))

	for frame in list_of_frames:
		out.write(frame)
		if(display):
			cv2.imshow('Frame', cv2.resize(frame, None, fx = 0.5, fy = 0.5))
			if cv2.waitKey(3) == ord('q'):
				cv2.destroyAllWindows()
				break
	out.release()

def flip_video(input_video_path, out_video_path):
	'''
	Description:
		Flip the video present in input_video_path.
	Input arguments:
		* input_video_path: absolute path to video that you want to flip
		* out_video_path: absolute path to video where you want to write to.
	Return:
		None
	'''
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

def find_key(d, value):
	for key, val in d.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
	    if val == value:
	        return key
	return None

def file_to_list(file_path):
	file = open(filepath, 'r')
	l_list = [re.sub("[^\w]", " ",  line).split() for line in file.read().splitlines() ]
	file.close()
	return l_list

