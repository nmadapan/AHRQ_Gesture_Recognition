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

## TCP/IP of Synapse Computer
IP_SYNAPSE = '10.186.47.6' # IP of computer that is running Synapse
PORT_SYNAPSE = 10000  # Both server and client should have a common IP and Port

## TCP/IP of CPM Computer
IP_CPM = 'localhost'
PORT_CPM = 3000

## Flags
ENABLE_SYNAPSE_SOCKET = False
ENABLE_CPM_SOCKET = False
ONLY_SKELETON = True

## IMPORTANT
LEXICON_ID = 'L6'
SUBJECT_ID = 'S7'

'''
10/31
	* All threads exit when main exits 
	* Got a good idea about thread Conditions. 
		* Changes have been made to access_kinect thread and gen_skel thread.
11/01
	* How does calibration works for finger lengths. 
		* What functions to call. How to update the calibration file. 
		* Ask Rahul. Also, incorporate in both offline and online codes.
		* Finishing the calibration
	*  Need to fix other threads w.r.t Condition variables. 
	* Communication between the threads. Using the flags properly. 
	* Make modification to the skel_instance data structure, so it contains information 
		* about if the hands are below or above the threshold. 
	* Do not send frames to CPM if hands are below the threshold. Modify code in the CPM.
	* When we fill the buffers (buf_body_skel and buf_rgb_skel), we assume that body_skel and rgb_skel are in sync
		* When we access the buffers (buf_rgb_skel and buf_rgb), we assume that both of them are in sync which maynot be the case
		* FIX this
	* If the no. of frames in skeleton are less than a threshold, ignore. Make changes to run()
'''


class Realtime:
	def __init__(self):
		###################
		### DATA PATHS ####
		###################
		# Path where _reps.txt file is present.
		self.data_path = r'H:\AHRQ\Study_IV\Data\Data'
		# path to trained .pickle file.
		self.trained_pkl_fpath = 'H:\\AHRQ\\Study_IV\\Flipped_Data\\' + LEXICON_ID + '_0_data.pickle'
		self.cmd_dict = json_to_dict('commands.json')
		self.base_write_dir = r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master\test_imgs'

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
		 # timestamp, frame_list
		self.buf_finglen = [(None, None) for _ in range(self.buf_size)]

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

		########################
		### INTIALIZE KINECT ###
		########################
		self.kr = kinect_reader()
		self.base_id = 0
		self.neck_id = 2
		self.left_hand_id = 7
		self.right_hand_id = 11
		self.thresh_level = 0.3 #TODO: It seems to be working.

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
		self.op_instance = None # Updated in self.th_gen_cpm(). It is a tuple (timestamp, feature_vector of finger lengths - ndarray(num_frames, 10)).
		self.cmd_reps = {} # Updated by self.update_cmd_reps()
		self.prev_executed_cmds = [] # Updated by self.update_cmd_reps()
		self.update_cmd_reps()

		######################################
		### LOAD TARINED FEATURE EXTRACTOR ###
		######################################
		## Use previously trained Feature extractor
		with open(self.trained_pkl_fpath, 'rb') as fp:
			res = pickle.load(fp)
			self.feat_ext = res['fe'] # res['out'] exists but we dont need training data.
		self.feat_ext.update_rt_params(subject_id = SUBJECT_ID, lexicon_id = LEXICON_ID) ## This will let us know which normalization parameters are used.

	def update_cmd_reps(self):
		rep_path = os.path.join(self.data_path, LEXICON_ID + '_reps.txt')
		if(not os.path.isfile(rep_path)): raise IOError('reps.txt file does NOT exist')
		with open(rep_path, 'r') as fp:
			lines = fp.readlines()
			if(len(lines) == 0): raise ValueError('reps file is empty')
		lines = [line.strip().split(' ') for line in lines]
		for line in lines:
			self.cmd_reps[line[0]] = line[1:]

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

		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, stop producing the rgb/skeleton data
			# elif(self.fl_skel_ready and self.fl_cpm_ready): continue # If previous skeleton features and op features are not used, stop producing.

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

				## Make sure that hands are below the threshold in the beginning
				if(not first_time):
					fl_hands_position = (left_y < start_y_coo) and (right_y < start_y_coo)
					if(fl_hands_position): first_time = True

				## Identify if the gesture started
				if (left_y >= start_y_coo or right_y >= start_y_coo) and (not self.fl_gest_started) and first_time:
					self.fl_gest_started = True
					print 'Gesture started :)'
				if (left_y < start_y_coo and right_y < start_y_coo) and self.fl_gest_started:
					self.fl_gest_started = False
					print 'Gesture ended :('

				## When you want to wait() based on a shared variables, make sure to include them in the thread.Condition.
				with self.cond_body_skel: # Producer. Consumers will wait for the notify call #
					# Update the skel buffer after gesture is started
					if(self.fl_gest_started):
						ts = int(time.time()*100)
						# Update body skel buffers
						self.buf_body_skel.append((ts, skel_col_reduce(skel_pts)))
						self.buf_body_skel.pop(0) # Buffer is of fixed length. Append an element at the end and pop the first element.
						# Update rgb skel buffers
						self.buf_rgb_skel.append((ts, skel_col_reduce(color_skel_pts, dim=2, wrt_shoulder = False)))
						self.buf_rgb_skel.pop(0) # Buffer is of fixed length. Append an element at the end and pop the first element.
					# The notify_all call should be outside (if condition) and inside (with condition) because if not, the cosumer
					# can wait for this call just after the flags that allow it to enter the "consuming condition" have changed
					self.cond_body_skel.notify_all()

			if(rgb_flag):
				## Update RGB image buffer after gesture is started
				if self.fl_gest_started:
					with self.cond_rgb: # Producer. Consumers need to wait for producer's 'notify' call
						ts = int(time.time()*100)
						self.buf_rgb.append((ts, self.kr.color_image))
						self.buf_rgb.pop(0)
						self.cond_rgb.notify_all()
				## Visualization
				if((self.kr.color_image is not None) and (self.kr.color_skel_pts is not None)):
					image_with_skel = self.kr.draw_body(self.kr.color_image, self.kr.color_skel_pts)
					if(image_with_skel is not None):
						resz_img = cv2.resize(image_with_skel, None, fx = 0.5, fy = 0.5)
						cv2.imshow('Visualization', resz_img)

			if(cv2.waitKey(1) == ord('q')):
				cv2.destroyAllWindows()
				self.fl_alive = False

		print 'Exiting access kinect thread !!!'

	def th_gen_skel(self):
		##
		# Consume: skeleton data
		# Produce: skeleton features
		##

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
				frame_count = 0
				self.skel_instance = deepcopy(skel_frames) # [(ts1, ([left_x, y, z], [right_x, y, z])), ...]
				skel_frames = []
				self.fl_skel_ready = True

		print 'Exiting gen_skel !!!'

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
		##
		# Consume: RGB data, RGB Skeletons
		# Produce: finger lengths features
		##

		## Wait for kinect stream to be ready
		while(not self.fl_stream_ready): continue

		frame_count = 0 # this is zeroed internally
		op_instance = []
		first_time = False
		print_first_time = True

		rgb_frame = None
		rgb_hand_coo = None
		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, dont do anything
			if(self.fl_cpm_ready): continue # If previous cpm data is not used, dont do anything
			if self.fl_gest_started:
				if print_first_time:
					# print "IN RGB THREAD, GESTURE STARTED: "
					print_first_time = False
				first_time = True
				with self.cond_rgb:
					self.cond_rgb.wait()
					rgb_frame = deepcopy(self.buf_rgb[-1]) # (timestamp, ndarray)
					_, rgb_hand_coo = deepcopy(self.buf_rgb_skel[-1]) # (timestamp, ([rx1, ry1], [lx1, ly1]))
					frame_count += 1

				## Key assumptions: TODO:
				# When we fill the buffers (buf_body_skel and buf_rgb_skel), we assume that body_skel and rgb_skel are in sync
				# When we access the buffers (buf_rgb_skel and buf_rgb), we assume that both of them are in sync which maynot be the case
				# Be cautious

				## Step 1: Crop left and right hands
				## Step 2: Write both the images to the disk
				# Right hand
				r_fname = str(frame_count) + '_r.jpg'
				self.save_hand_bbox(rgb_frame[1], rgb_hand_coo[0], r_fname)
				# Left hand
				l_fname = str(frame_count) + '_l.jpg'
				self.save_hand_bbox(rgb_frame[1], rgb_hand_coo[1], l_fname)

				## Step 3: Socket send image names for both images. This will return finger lengths.
				# Right hand
				self.client_cpm.sock.send(r_fname)
				r_fing_data = self.client_cpm.sock_recv(display = False)
				r_finger_lengths = str_to_nparray(r_fing_data, dlim = '_').tolist()
				# Left hand
				self.client_cpm.sock.send(l_fname)
				l_fing_data = self.client_cpm.sock_recv(display = False)
				l_finger_lengths = str_to_nparray(l_fing_data, dlim = '_').tolist()
				## Step 4: Put the finger lengths of right and left hand together and append it to op_instance.
				op_instance.append((rgb_frame[0], (r_finger_lengths, l_finger_lengths)))
				# op_instance.append((rgb_frame[0], (r_finger_lengths, [])))
				print op_instance[-1]
			if not self.fl_gest_started and first_time:
				# print "IN RGB THREAD, GESTURE ENDED: "
				first_time = False
				print_first_time = True
				frame_count = 0

				## TODO: Condition it on cond_rgb, otherwise, we might run into race conditions
				self.op_instance = deepcopy(op_instance) # [(ts1, ([left_f1, f2, .., f5], [right_f1, f2, .., f5])), ...]

				# timestamps, raw_op_features = zip(*op_instance)
				# # pp(len(raw_op_features))

				# self.op_instance = (timestamps, np.array(raw_op_features))
				op_instance = []
				self.fl_cpm_ready = True #### Think about conditioning

		print 'Exiting CPM thread !!!'

	def th_synapse(self):
		#
		while(self.fl_alive):
			if(not self.fl_cmd_ready): continue
			self.fl_synapse_running = True

			# If command is ready: Do the following:
			# Wait for five seconds for the delivery message.
			command_executed = self.client_synapse.send_data(self.command_to_execute)
			# print self.client_synapse.sock.send(self.command_to_execute)
			# data = self.client_synapse.sock_recv(display = False)
			print 'Received: ', command_executed
			if(command_executed):
				self.fl_cmd_ready = False
				self.fl_synapse_running = False
			else:
				print 'Synapse execution failed !'
				## What to do now
				# sys.exit(0)

		print 'Exiting Synapse thread !!!'

	def get_next_cmd(self, pred_cmd):
		# pred_cmd : predicted command name

		# If there are no previous commands, return the same command
		if(len(self.prev_executed_cmds) == 0):
			self.prev_executed_cmds.append(pred_cmd)
			return pred_cmd

		## Temporarily
		return pred_cmd
		##
		# TODO: Code to smartly select the next command goes here.
		##

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
				# pp(self.skel_instance)
				# pp(self.op_instance)

				#####################
				### SKEL FEATURE ####
				#####################
				# Detuple skel_instance
				skel_ts, raw_skel_frames = zip(*self.skel_instance)
				## TODO: If length of skel_instance is less than a certain number, ignore that gesture.
				dom_rhand, final_skel_inst = self.feat_ext.generate_features_realtime(list(raw_skel_frames))
				#####################

				## Interpolate cpm instances
				if(not ONLY_SKELETON):
					###################
					### OP FEATURE ####
					###################
					# Detuple op_instance
					op_ts, raw_op_frames = zip(*self.op_instance)
					# Detuple op frames int right and left
					right_op, left_op = zip(*raw_op_frames)
					# Merge op features based on dom_rhand
					if(dom_rhand): op_inst = np.append(right_op, left_op, axis = 1)
					else: op_inst = np.append(left_op, right_op, axis = 1)
					# Synchronize rgb and skel time stamps
					_, sync_op_ts = sync_ts(skel_ts, op_ts)
					# Interpolate so that rgb and skel same no. of frames
					op_inst = smart_interpn(np.array(op_inst), sync_op_ts, kind = 'copy') # Change kind to 'linear' for linear interpolation
					# Interpolate op features to fixed_num_frames
					final_op_inst = interpn(op_inst, self.feat_ext.fixed_num_frames).reshape(1, -1)
					#####################

					# Append skel features followed by op features
					final_overall_inst = np.append(final_skel_inst, final_op_inst).reshape(1, -1)
				else: # Only skeleton
					final_overall_inst = final_skel_inst

				label, cname = self.feat_ext.pred_output_realtime(final_overall_inst)
				self.command_to_execute = find_key(self.cmd_dict, self.get_next_cmd(cname))

				print 'Predicted: ', label, cname

				#### Temporary ####
				time.sleep(0.5)
				#### Temporary ####

				self.fl_cmd_ready = True

				'''
					* Passing the feature to the actual svm:
						cname = self.feat_ext.pred_output_realtime(final_inst)
					* Logic that operates over the command names. This is lexicon specific. We have L*_repetition.txt file.
						self.command_to_execute = get_next_command(cname)
						set self.fl_cmd_ready to True
						set self.fl_synapse_running	to True
						Wait for data from the server. If True, set self.fl_synapse_running	to False
						When self.fl_synapse_running is True, stop everything else.
					* Let the synapse thread know that command is ready. It can execute it.
				'''

				self.fl_skel_ready = False
				if(ENABLE_CPM_SOCKET): self.fl_cpm_ready = False

		# If anything fails do the following
		self.kr.close()
		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse.close()
		if(ENABLE_CPM_SOCKET):
			self.client_cpm.close()

		print 'Exiting main thread !!!'


if(__name__ == '__main__'):
	rt = Realtime()
	rt.run()
