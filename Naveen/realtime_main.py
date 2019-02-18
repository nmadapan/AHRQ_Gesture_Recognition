from __future__ import print_function

## Existing libraries
import cv2
import numpy as np
import os, sys, time
from threading import Thread, Condition
from copy import copy, deepcopy
import pickle
from pprint import pprint as pp
import socket

## Custom
from FeatureExtractor import FeatureExtractor
from KinectReader import kinect_reader
from helpers import *
from CustomSocket import Client

###############################
### CHANGE THESE PARAMETERS ###
###############################

## TCP/IP of Synapse Computer
IP_SYNAPSE = '192.168.1.100' # IP of computer that is running Synapse
PORT_SYNAPSE = 9000  # Both server and client should have a common IP and Port

## TCP/IP of CPM Computer
IP_CPM = 'localhost'
PORT_CPM = 3000

## Flags
ENABLE_SYNAPSE_SOCKET = False
ENABLE_CPM_SOCKET = False
# If True, write data to disk
DATA_WRITE_FLAG = False
DEBUG = False

## IMPORTANT
LEXICON_ID = 'L6'
SUBJECT_ID = 'S1'

## If a gesture has less than 20 frames ignore.
MIN_FRAMES_IN_GESTURE = 20

## DATA PATHS
# path to trained *_data.pickle file.
TRAINED_PKL_PATH = 'G:\\AHRQ\\Study_IV\\NewData2\\' + LEXICON_ID + '_data.pickle'
# Path to json file consiting of list of command ids and command names
CMD_JSON_PATH  = 'commands.json'
# Path where to write images so that CPM can read from this path.
BASE_WRITE_DIR = r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master\test_imgs'

###############################

def print_global_constants():
	print('Synapse: ', end = '')
	if(ENABLE_SYNAPSE_SOCKET):
		print('ENABLED')
		print('IP: {0}, PORT: {1}'.format(IP_SYNAPSE, PORT_SYNAPSE))
	else: print('DISABLED')

	print('\nCPM: ', end = '')
	if(ENABLE_CPM_SOCKET):
		print('ENABLED')
		print('IP: {0}, PORT: {1}'.format(IP_CPM, PORT_CPM))
	else: print('DISABLED')

	print('\nWriting realtime data to {0}: --> {1}'.format(BASE_WRITE_DIR, DATA_WRITE_FLAG))

	print('\nLEXICON ID: ', LEXICON_ID)
	print('SUBJECT ID: ', SUBJECT_ID)

	print('\nMinimum size of gesture: ', MIN_FRAMES_IN_GESTURE)

	print('\nPath to trained pickle: ', TRAINED_PKL_PATH, end = ' --> ')
	pkl_flag = os.path.isfile(TRAINED_PKL_PATH)
	print(pkl_flag)

	print('\nPath to commands json file: ', CMD_JSON_PATH, end = ' --> ')
	cmd_flag = os.path.isfile(CMD_JSON_PATH)
	print(cmd_flag)

	print('\nPath to directory to write images: ', BASE_WRITE_DIR, end = ' --> ')
	write_dir_flag = os.path.isdir(BASE_WRITE_DIR)
	if(not write_dir_flag): os.mkdir(BASE_WRITE_DIR)
	print(True)

	return (pkl_flag and cmd_flag and write_dir_flag)

if not print_global_constants():
	print('ERROR! One or more files DOES NOT exist !!!')
	sys.exit()

'''
Key Assumptions:
	1. In realtime: body skeleton, RGB skeleton and RGB images are synchronized in time.
		When we fill the buffers (body skeleton and RGB skeleton) are in sync.
		* When we access the buffers, we assume that RGB skeleton and RGB images are in sync.

Tricks/Hacks:
	1. When using thread conditions, producer (who notifies consumers) should notify consumers without basing on any flags.

11/01
	* How does calibration works for finger lengths.
		* What functions to call. How to update the calibration file.
		* Ask Rahul. Also, incorporate in both offline and online codes.
		* Finishing the calibration
'''

class Realtime:
	def __init__(self):
		###################
		### DATA PATHS ####
		###################
		self.trained_pkl_fpath = TRAINED_PKL_PATH
		self.cmd_dict = json_to_dict(CMD_JSON_PATH)
		self.base_write_dir = BASE_WRITE_DIR

		#############
		## BUFFERS ##
		#############
		# Size of the buffer
		self.buf_size = 10
		# timestamp, frame_list (75 elements) # [..., t-3, t-2, t-1, t]
		self.buf_body_skel = [(None, None) for _ in range(self.buf_size)]
		# timestamp, frame_nparray
		self.buf_rgb = [(None, None) for _ in range(self.buf_size)]
		# timestamp, frame_list (50 elements) # [..., t-3, t-2, t-1, t]
		self.buf_rgb_skel = [(None, None) for _ in range(self.buf_size)]

		##################
		## THREAD FLAGS ##
		##################
		self.fl_alive = True # If False, kill all threads
		self.fl_stream_ready = False # th_access_kinect
		self.fl_skel_ready = False # th_gen_skel
		self.fl_cpm_ready = False # th_gen_cpm
		# If true, we have command to execute ==> now call synapse, else command is not ready yet.
		self.fl_cmd_ready = False
		self.fl_gest_started = False
		# Synapse running, # th_synapse. If False, meaning synapse is executing a command. So stop everything else.
		self.fl_synapse_running = False
		##
		# TODO: If synapse breaks down, we should restart. So we need to save the current state info.
		##

		######################################
		### LOAD TARINED FEATURE EXTRACTOR ###
		######################################
		## Use previously trained Feature extractor
		self.feat_ext = None ## Updated in load_feature_extractor()
		self.load_feature_extractor()

		########################
		### INTIALIZE KINECT ###
		########################
		self.kr = kinect_reader()
		self.base_id = 0
		self.neck_id = 2
		self.left_hand_id = 7
		self.right_hand_id = 11
		self.thresh_level = self.feat_ext.gesture_thresh_level

		#########################
		### THREAD CONDITIONS ###
		#########################
		self.cond_body_skel = Condition()
		self.cond_rgb = Condition()

		#############################
		### SOCKET INITIALIZATION ###
		#############################
		## Synapse Socket initialization
		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse = Client(IP_SYNAPSE, PORT_SYNAPSE, buffer_size = 1000000)
		## CPM Socket initialization
		# CPM Initialization takes up to one minute. Dont initialize any socket
		#	(by calling init_socket) before creating object of CPM Client.
		if(ENABLE_CPM_SOCKET):
			self.client_cpm = Client(IP_CPM, PORT_CPM)
		## Call Synapse init socket
		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse.init_socket()
		## Call CPM init socket
		if(ENABLE_CPM_SOCKET):
			self.client_cpm.init_socket()
		#socket.setdefaulttimeout(2.0) ######### TODO: Need to be tuned depending on the delays.

		##################################
		### INITIALIZE OTHER VARIABLES ###
		##################################
		self.command_to_execute = None # Updated in run()
		self.skel_instance = None # Updated in self.th_gen_skel(). It is a tuple (timestamp, feature_vector of skeleton - ndarray(1 x _)). It is a flattened array.
		self.cpm_instance = None # Updated in self.th_gen_cpm(). It is a tuple (timestamp, feature_vector of finger lengths - ndarray(num_frames, 10)).
		self.gesture_count = 0

	def load_feature_extractor(self):
		######################################
		### LOAD TARINED FEATURE EXTRACTOR ###
		######################################
		## Use previously trained Feature extractor
		with open(self.trained_pkl_fpath, 'rb') as fp:
			res = pickle.load(fp)
			self.feat_ext = res['fe'] # res['out'] exists but we dont need training data.
		self.feat_ext.update_rt_params(subject_id = SUBJECT_ID, lexicon_id = LEXICON_ID) ## This will let us know which normalization parameters are used.

		## Check if the no. of features in trained classifer and no. of features in realtime are same.
		num_clf_features = self.feat_ext.svm_clf.support_vectors_.shape[1] ## No. of features in trained classifier
		# No. of body skeleton features (No of finger length featuers.)
		num_skel_features = len(self.feat_ext.feature_types) * self.feat_ext.num_joints * self.feat_ext.fixed_num_frames * self.feat_ext.dim_per_joint
		if(num_clf_features != num_skel_features):
			assert ENABLE_CPM_SOCKET, 'ERROR! Trained classifier requires both body skeleton and finger lengths. Set ENABLE_CPM_SOCKET to True.'
		else:
			assert (not ENABLE_CPM_SOCKET), 'ERROR! Trained classifier requires ONLY body skeleton. Set ENABLE_CPM_SOCKET to False.'

	def th_access_kinect(self):
		##
		# Producer: RGB, skeleton
		##
		# Initialize Kinect
		wait_for_kinect(self.kr)

		# Now this thread is ready
		self.fl_stream_ready = True

		first_time = False

		skel_pts = None
		color_skel_pts = None

		body_frame_count = 0
		rgb_frame_count = 0

		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, stop producing the rgb/skeleton data
			# elif(self.fl_skel_ready and self.fl_cpm_ready): continue # If previous skeleton features and cpm features are not used, stop producing.

			## Refresh kinect frames
			rgb_flag = self.kr.update_rgb()
			body_flag = self.kr.update_body()

			if(body_flag):
				skel_pts = self.kr.skel_pts.tolist() # list of 75 floats.
				color_skel_pts = self.kr.color_skel_pts.tolist() # list of 50 floats
				'''
				GESTURE SPOTTING HAPPENS HERE:
					* Check if gesture started.
					* If fl_gest_started = true, gesture has started.
					* If fl_gest_started = false, hands are below the threshold and gesture has ended.
				'''
				start_y_coo = self.thresh_level * (skel_pts[3*self.neck_id+1] - skel_pts[3*self.base_id+1]) ## Threshold level
				left_y = skel_pts[3*self.left_hand_id+1] - skel_pts[3*self.base_id+1] # left hand
				right_y = skel_pts[3*self.right_hand_id+1] - skel_pts[3*self.base_id+1] # right hand

				left_status = left_y >= start_y_coo
				right_status = right_y >= start_y_coo

				## Make sure that hands are below the threshold in the beginning
				if(not first_time):
					fl_hands_position = (left_y < start_y_coo) and (right_y < start_y_coo)
					if(fl_hands_position): first_time = True

				## Identify if the gesture started
				if (left_y >= start_y_coo or right_y >= start_y_coo) and (not self.fl_gest_started) and first_time:
					self.fl_gest_started = True
					print('Gesture started :)')
				if (left_y < start_y_coo and right_y < start_y_coo) and self.fl_gest_started:
					self.fl_gest_started = False
					if(DEBUG): print('True no. of frames: Body -', body_frame_count, ' RGB - ', rgb_frame_count)
					rgb_frame_count, body_frame_count = 0, 0
					print('Gesture ended :(')

				## When you want to wait() based on a shared variables, make sure to include them in the thread.Condition.
				with self.cond_body_skel: # Producer. Consumers will wait for the notify call #
					# Update the skel buffer after gesture is started
					if(self.fl_gest_started):
						body_frame_count += 1
						ts = int(time.time()*100)
						# Update body skel buffers
						self.buf_body_skel.append((ts, [right_status, left_status], skel_col_reduce(skel_pts)))
						self.buf_body_skel.pop(0) # Buffer is of fixed length. Append an element at the end and pop the first element.
						# Update rgb skel buffers
						self.buf_rgb_skel.append((ts, [right_status, left_status], skel_col_reduce(color_skel_pts, dim=2, wrt_shoulder = False)))
						self.buf_rgb_skel.pop(0) # Buffer is of fixed length. Append an element at the end and pop the first element.
					# The notify_all call should be outside (if condition) and inside (with condition) because if not, the cosumer
					# can wait for this call just after the flags that allow it to enter the "consuming condition" have changed
					self.cond_body_skel.notify_all()

			if(rgb_flag):
				## Update RGB image buffer after gesture is started
				with self.cond_rgb: # Producer. Consumers need to wait for producer's 'notify' call
					if self.fl_gest_started:
						rgb_frame_count += 1
						ts = int(time.time()*100)
						self.buf_rgb.append((ts, self.kr.color_image))
						self.buf_rgb.pop(0)
					self.cond_rgb.notify_all()
				## Visualization
				if((self.kr.color_image is not None) and (self.kr.color_skel_pts is not None)):
					image_with_skel = self.kr.draw_body(deepcopy(self.kr.color_image), self.kr.color_skel_pts)
					if(image_with_skel is not None):
						resz_img = cv2.resize(image_with_skel, None, fx = 0.5, fy = 0.5)
						cv2.imshow('Visualization', resz_img)

			if(cv2.waitKey(1) == ord('q')):
				cv2.destroyAllWindows()
				self.fl_alive = False

		print('Exiting access kinect thread !!!')

	def th_gen_skel(self):
		'''
		# Consume: skeleton data
		# Produce: skeleton features
		'''

		## Wait for kinect stream to be ready
		while(not self.fl_stream_ready): continue

		frame_count = 0 # this is being reset internally
		skel_frames = []
		first_time = False
		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, dont do anything
			if(self.fl_skel_ready): continue # If previous skeleton features are not used, dont do anything.

			if self.fl_gest_started:
				with self.cond_body_skel:
					self.cond_body_skel.wait()
					skel_frames.append(deepcopy(self.buf_body_skel[-1]))
				first_time = True
				frame_count += 1
			elif first_time:
				first_time = False
				if(DEBUG): print('Actual no. of frames: Body -', frame_count-1) ## TODO
				frame_count = 0
				self.skel_instance = deepcopy(skel_frames) # [(ts1, ([right_x, y, z], [left_x, y, z])), ...]
				skel_frames = []
				self.fl_skel_ready = True

		print('Exiting gen_skel !!!')

	def save_hand_bbox(self, img, hand_pixel_coo, out_fname):
		'''
		Description:
			Writes the hand bbox to self.base_write_dir
		Input arguments:
			'img': An RGB image. np.ndarray of shape (H x W x 3).
			'bbox': list of four values. [x, y, w, h].
				(x, y): pixel coordinates of top left corner of the bbox
				(w, h): width and height of the boox.
		'''
		if(img is None): return
		bbox = get_hand_bbox(hand_pixel_coo, \
		                     max_wh = (img.shape[1], img.shape[0]))
		rx, ry, rw, rh = tuple(bbox)
		cropped_img = img[ry:ry+rh, rx:rx+rw]
		cv2.imwrite(os.path.join(self.base_write_dir, out_fname), cropped_img)

	def th_gen_cpm(self):
		'''
		Consume: RGB data, RGB Skeletons
		Produce: finger lengths features
		'''

		## Wait for kinect stream to be ready
		while(not self.fl_stream_ready): continue

		frame_count = 0 # this is zeroed internally
		cpm_instance = []
		first_time = False

		rgb_frame = None
		rgb_hand_coo = None

		list_of_rgb_frames = []

		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, dont do anything
			if(self.fl_cpm_ready): continue # If previous cpm data is not used, dont do anything
			if self.fl_gest_started:
				first_time = True
				with self.cond_rgb:
					self.cond_rgb.wait()
					rgb_frame = deepcopy(self.buf_rgb[-1]) # (timestamp, ndarray)
				_, hands_status, rgb_hand_coo = deepcopy(self.buf_rgb_skel[-1]) # (timestamp, [right_hand_status, left_hand_status] ([rx1, ry1], [lx1, ly1]))
				frame_count += 1
				right_status, left_status = tuple(hands_status)

				## Key assumptions: TODO:
				# When we fill the buffers (buf_body_skel and buf_rgb_skel), we assume that body_skel and rgb_skel are in sync. When we access the buffers (buf_rgb_skel and buf_rgb), we assume that both of them are in sync which maynot be the case

				## Step 1: Crop left and right hands
				## Step 2: Write both the images to the disk
				# Right hand
				if(right_status):
					r_fname = str(frame_count) + '_r.jpg'
					self.save_hand_bbox(rgb_frame[1], rgb_hand_coo[0], r_fname)
				# Left hand
				if(left_status):
					l_fname = str(frame_count) + '_l.jpg'
					self.save_hand_bbox(rgb_frame[1], rgb_hand_coo[1], l_fname)

				## Step 3: Socket send image names for both images. This will return finger lengths.
				# Right hand
				if(right_status):
					self.client_cpm.sock.send(r_fname)
					r_fing_data = self.client_cpm.sock_recv(display = False)
					r_finger_lengths = str_to_nparray(r_fing_data, dlim = '_').tolist()
				else:
					r_finger_lengths = np.zeros(self.feat_ext.num_fingers).tolist()
				# Left hand
				if(left_status):
					self.client_cpm.sock.send(l_fname)
					l_fing_data = self.client_cpm.sock_recv(display = False)
					l_finger_lengths = str_to_nparray(l_fing_data, dlim = '_').tolist()
				else:
					l_finger_lengths = np.zeros(self.feat_ext.num_fingers).tolist()

				## Step 4: Put the finger lengths of right and left hand together and append it to cpm_instance.
				cpm_instance.append((rgb_frame[0], (r_finger_lengths, l_finger_lengths)))

				# print(cpm_instance[-1])

			if not self.fl_gest_started and first_time:
				first_time = False
				if(DEBUG): print('Actual no. of frames: RGB -', frame_count)
				frame_count = 0
				self.cpm_instance = deepcopy(cpm_instance) # [(ts1, ([left_f1, f2, .., f5], [right_f1, f2, .., f5])), ...]
				cpm_instance = []
				self.fl_cpm_ready = True

		print('Exiting CPM thread !!!')

	def th_synapse(self):
		#
		while(self.fl_alive):
			if(not self.fl_cmd_ready): continue
			self.fl_synapse_running = True


			# If command is ready: Do the following:
			# Wait for five seconds for the delivery message.
			command_executed = self.client_synapse.send_data(self.command_to_execute)
			# print(self.client_synapse.sock.send(self.command_to_execute))
			# data = self.client_synapse.sock_recv(display = False)

			## Irrespective of whether synapse succeeded or failed, behave in the same way
			# switch the same flags.

			if(command_executed):
				print('SUCCESS: Comamnd executed: ', command_executed)
			else:
				print('Synapse execution failed !')

			self.fl_cmd_ready = False
			self.fl_synapse_running = False

		print('Exiting Synapse thread !!!')

	def run(self):
		# Main thread
		acces_kinect_thread = Thread(name = 'access_kinect', target = self.th_access_kinect) # P: RGB, skel
		gen_skel_thread = Thread(name = 'gen_skel', target = self.th_gen_skel) # C: skel ; P: skel_features
		acces_cpm_thread = Thread(name = 'access_cpm', target = self.th_gen_cpm) # C: RGB ; P: finger_lengths
		synapse_thread = Thread(name = 'autoclick_synapse', target = self.th_synapse) #

		## Kill all threads when main exits
		acces_kinect_thread.daemon = True
		gen_skel_thread.daemon = True
		acces_cpm_thread.daemon = True
		synapse_thread.daemon = True

		##########
		# TODO: Incorporate the calibration information in the realtime code
		#
		##########

		acces_kinect_thread.start()
		gen_skel_thread.start()
		if(ENABLE_CPM_SOCKET): acces_cpm_thread.start()
		if(ENABLE_SYNAPSE_SOCKET): synapse_thread.start()

		## Merger part of the code
		while(self.fl_alive):
			if(self.fl_synapse_running): continue

			if(ENABLE_CPM_SOCKET): flag = self.fl_skel_ready and self.fl_cpm_ready
			else: flag = self.fl_skel_ready

			if(flag):
				#####################
				### SKEL FEATURE ####
				#####################
				## Detuple skel_instance
				skel_ts, _, raw_skel_frames = zip(*self.skel_instance)
				## If no. of frames is too little, drop the gesture instance.
				if(len(raw_skel_frames) < MIN_FRAMES_IN_GESTURE):
					print('Less frames. Gesture Ignored. ')
					self.fl_cmd_ready = False
					self.fl_skel_ready = False
					if(ENABLE_CPM_SOCKET): self.fl_cpm_ready = False
					continue
				if(DEBUG): print('No. of frames in body skel feature: ', len(raw_skel_frames))
				dom_rhand, final_skel_inst = self.feat_ext.generate_features_realtime(list(raw_skel_frames))
				if(DEBUG): print('Size of body skel feature: ', final_skel_inst.shape)
				if(DEBUG): print('Dominant Right Hand', dom_rhand)
				self.gesture_count += 1
				#####################

				## If ENABLE_CPM_SOCKET is True, consider features from CPM
				if(ENABLE_CPM_SOCKET):
					####################
					### CPM FEATURE ####
					####################
					# Detuple cpm_instance
					cpm_ts, raw_cpm_frames = zip(*self.cpm_instance)
					if(DEBUG): print('No. of frames in CPM feature: ', len(raw_cpm_frames))
					if(len(raw_cpm_frames) < MIN_FRAMES_IN_GESTURE/3):
						print('Less frames. Gesture Ignored. ')
						self.fl_cmd_ready = False
						self.fl_skel_ready = False
						if(ENABLE_CPM_SOCKET): self.fl_cpm_ready = False
						continue
					# Detuple CPM frames int right and left
					right_cpm, left_cpm = zip(*raw_cpm_frames)
					if(DEBUG):
						print('Right CPM')
						pp(np.mean(right_cpm, axis = 0))
						print('Left CPM')
						pp(np.mean(left_cpm, axis = 0))
						print('Dominant Right Hand', dom_rhand)
					# Merge CPM features based on dom_rhand
					if(dom_rhand): cpm_inst = np.append(right_cpm, left_cpm, axis = 1)
					else: cpm_inst = np.append(left_cpm, right_cpm, axis = 1)
					##### %%%%%%%%%%%%%%%%%
					# # Synchronize rgb and skel time stamps
					# _, sync_cpm_ts = sync_ts(skel_ts, cpm_ts)
					# # Interpolate so that rgb and skel same no. of frames
					# # cpm_inst = smart_interpn(cpm_inst, sync_cpm_ts, kind = 'copy') # Change kind to 'linear' for linear interpolation
					# cpm_inst = cpm_inst[sync_cpm_ts, :]
					# # Interpolate CPM features to fixed_num_frames
					# final_cpm_inst = interpn(cpm_inst, self.feat_ext.fixed_num_frames).reshape(1, -1)
					##### %%%%%%%%%%%%%%%%%
					## Directly interpolate finger lengths independent of the skeleton frames.
					final_cpm_inst = interpn(cpm_inst, self.feat_ext.fixed_num_frames).reshape(1, -1)
					##### %%%%%%%%%%%%%%%%%
					if(DEBUG): print('Size of CPM feature: ', final_cpm_inst.shape)
					#####################

					## Append skel features followed by CPM features
					final_overall_inst = np.append(final_skel_inst, final_cpm_inst).reshape(1, -1)
				else: # Only skeleton
					final_overall_inst = final_skel_inst

				label, cname, top_three_labels_str = self.feat_ext.pred_output_realtime(final_overall_inst, K = 3, \
					clf_flag = ENABLE_CPM_SOCKET)
				# self.command_to_execute = label ## For only one label
				self.command_to_execute = top_three_labels_str ## For three labels
				print(self.command_to_execute)

				print('Predicted: ', label, cname, '\n\n')

				self.fl_cmd_ready = True

				self.fl_skel_ready = False
				if(ENABLE_CPM_SOCKET): self.fl_cpm_ready = False

		# If anything fails do the following
		self.kr.close()
		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse.close()
		if(ENABLE_CPM_SOCKET):
			self.client_cpm.close()

		print('Exiting main thread !!!')


if(__name__ == '__main__'):
	rt = Realtime()
	rt.run()
