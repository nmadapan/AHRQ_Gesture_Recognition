import cv2
import numpy as np
import os, sys, time
from threading import Thread, Condition
from copy import copy, deepcopy
import pickle
import socket

from FeatureExtractor import FeatureExtractor
from KinectReader import kinect_reader
from helpers import *
from pprint import pprint as pp

# Fake openpose
from fake_openpose import extract_fingers_realtime
from helpers import sync_ts

TCP_IP = '10.186.130.167' # The static IP of Ubuntu computer
TCP_PORT = 5000 # Both server and client should have a common IP and Port
BUFFER_SIZE = 1024 # in bytes. 1 charecter is one byte.
INITIAL_MESSAGE = 'Handshake'

ENABLE_SOCKET = False

class Realtime:
	def __init__(self):
		## Global Constants
		self.lexicon_name = 'L6'
		self.data_path = r'H:\AHRQ\Study_IV\Data\Data'
		self.trained_pkl_fpath = r'H:\AHRQ\Study_IV\Data\Data\L6_data.pickle'

		self.buf_skel_size = 10
		self.buf_rgb_size = 10

		## Buffers
		self.buf_skel = [(None, None) for _ in range(self.buf_skel_size)] # timestamp, frame_list # [..., t-3, t-2, t-1, t]
		self.buf_rgb = [(None, None) for _ in range(self.buf_rgb_size)] # timestamp, frame_nparray
		self.buf_finglen = [(None, None) for _ in range(self.buf_rgb_size)] # timestamp, frame_list

		## Flags
		self.fl_alive = True
		self.fl_stream_ready = False # th_access_kinect
		self.fl_skel_ready = False # th_gen_skel
		self.fl_openpose_ready = False # th_gen_openpose

		##
		# TODO: If synapse breaks down, we should restart. So we need to save the current state info. 
		##

		# If true, we have command to execute ==> now call synapse, else command is not ready yet. 
		self.fl_cmd_ready = False

		self.fl_gest_started = False
		self.fl_synapse_running = False # Synapse running, # th_synapse. If False, meaning synapse is executing a command. So stop everything else. 

		# Initialize the Kinect
		self.kr = kinect_reader()

		## thread conditions
		self.cond_skel = Condition()
		self.cond_rgb = Condition()

		## Socket initialization
		# variable inits
		# wait_for_connection for the first time. 
		# Set the sself.fl_sock_com = True
		##
		## Socket communication
		if(ENABLE_SOCKET):
			self.fl_sock_com = False # If the socket com b/w server and client is established. 
			self.sock = None # updated in call to init_socket()
			self.connect_status = False # updated in call to init_socket()
			socket.setdefaulttimeout(2.0)
			self.init_socket()

		self.command_to_execute = None

		## Use trained Feature extractor
		with open(self.trained_pkl_fpath, 'rb') as fp:
			res = pickle.load(fp)
			self.feat_ext = res['fe'] # res['out'] exists but we dont need training data.

		## Other variables
		self.skel_instance = None # Updated in self.th_gen_skel(). 
		# It is a tuple (timestamp, feature_vector of skeleton - ndarray(1 x _)). It is a flattened array.

		self.op_instance = None # Updated in self.th_gen_openpose(). 
		# It is a tuple (timestamp, feature_vector of finger lengths - ndarray(num_frames, 10)).

		# Previously executed command
		self.cmd_reps = {} # Updated by a function call to update_cmd_reps
		self.prev_executed_cmds = []
		self.update_cmd_reps()

		## Skeleton constants
		self.base_id = 0
		self.neck_id = 2
		self.left_hand_id = 7
		self.right_hand_id = 11
		self.thresh_level = 0.2 #TODO: It seems to be working. 

	def sock_connect(self, timeout = 30):
		# Description:
		#	If connected, return as is
		#	Else, keep trying to connect forever. 
		print 'Connecting to server .', 
		if(self.connect_status): 
			print 'Connected!'
			return

		start = time.time()
		while(not self.connect_status):
			try:
				self.sock = socket.socket()
				self.sock.connect((TCP_IP, TCP_PORT)) ## Blocking call. Gives time out exception on time out.
				self.connect_status = True
				self.sock.send(INITIAL_MESSAGE)
				print '. ',
				time.sleep(0.5)					
			except Exception as exp:
				print '. ',
				time.sleep(0.5)
			if(time.time()-start > timeout):
				print 'Connection Failed! Waited for more than ' + str(timeout) + ' seconds.'
				sys.exit(0)

	def sock_recv(self, timeout = 30):
		print '\nWaiting for delivery message: .', 
		data_received = False
		data = None
		start = time.time()
		while(not data_received):
			try:
				data = self.sock.recv(32) # Blocking call # Gives time out exception
				if data:
					print('Success!')
					data_received = True
					break
				print '. ',
			except Exception as exp:
				print '. ',
				time.sleep(0.5)

			if(time.time()-start > timeout):
				print 'No delivery message! Waited for more than ' + str(timeout) + ' seconds.'
				sys.exit(0)		

		return data

	def init_socket(self, timeout = 10):
		self.sock_connect(timeout = timeout)
		self.sock_recv(timeout = timeout)

	def update_cmd_reps(self):
		rep_path = os.path.join(self.data_path, self.lexicon_name+'_reps.txt')
		if(not os.path.isfile(rep_path)): raise IOError('reps file does NOT exist')
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

		## opencv part
		cv2.namedWindow('RGB')

		# Now this thread is ready
		self.fl_stream_ready = True

		prev_left_y = None
		prev_right_y = None
		first_time = True

		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, stop producing the rgb/skeleton data
			# elif(self.fl_skel_ready and self.fl_openpose_ready): continue # If previous skeleton features and op features are not used, stop producing. 
			
			# Refreshing Frames
			rgb_flag = self.kr.update_rgb()
			body_flag = self.kr.update_body()

			if(body_flag):
				### TODO:
				## We need to take into account the direction of movement of hand. 
				## gestures starts when previous skeleton is below the threshold and current skeleton is above the threshold. 
				###

				skel_pts = self.kr.skel_pts.tolist() # list of 75 floats.

				# GESTURE SPOTTING NEEDS TO HAPPEN HERE
				# Check if gesture started
				# When start_flag=true the gesture started
				# When start_flag=false the hands are down and the
				# frames don't need to be collected
				start_y_coo = self.thresh_level * (skel_pts[3*self.neck_id+1] - skel_pts[3*self.base_id+1])
				left_y = skel_pts[3*self.left_hand_id+1] - skel_pts[3*self.base_id+1]
				right_y = skel_pts[3*self.right_hand_id+1] - skel_pts[3*self.base_id+1]

				## To incorporate the direction of hand motion to identify start/end of gesture
				if(first_time):
					prev_left_y = left_y
					prev_right_y = right_y
					first_time = False
					continue

				left_motion_direc = left_y - prev_left_y
				right_motion_direc = right_y - prev_right_y
				thresh_movement = 0.01
				overall_motion_direc = (left_motion_direc > thresh_movement) or (right_motion_direc > thresh_movement)

				## When you want to wait() based on a shared variables, make sure to include them in the thread.Condition. 
				with self.cond_skel: # Producer. Consumers will wait for the notify call #######
					if (left_y >= start_y_coo or right_y >= start_y_coo) and (not self.fl_gest_started) and overall_motion_direc:
						self.fl_gest_started = True
						print 'Gesture started :)'
					if (left_y < start_y_coo and right_y < start_y_coo) and self.fl_gest_started and (not overall_motion_direc):
						self.fl_gest_started = False
						print 'Gesture ended :('
									
					# Update the skel buffer
					if(self.fl_gest_started):
						ts = int(time.time()*100)
						self.buf_skel.append((ts, skel_col_reduce(skel_pts)))
						self.buf_skel.pop(0) # Buffer is of fixed length. Append an element at the end and pop the first element. 
						tslist, _ = zip(*self.buf_skel)

					# The Notify all should be outside because if not, the cosumer
					# can wait for this call just after the flags that allow
					# it to enter the "consuming condition" have changed
					self.cond_skel.notify_all()

				## resetting
				prev_left_y = left_y
				prev_right_y = right_y

			if(rgb_flag): # and self.fl_gest_started. Later dont even fill the buffers when others are running. q
				with self.cond_rgb: # Producer. Consumers need to wait for producer's 'notify' call
					ts = int(time.time()*100)
					self.buf_rgb.append((ts, self.kr.color_image))
					self.buf_rgb.pop(0)
					self.cond_rgb.notify_all()
					tslist, _ = zip(*self.buf_rgb)
					cv2.imshow('RGB', cv2.resize(self.kr.color_image, None, fx=0.5, fy=0.5))

			if(cv2.waitKey(1) == ord('q')):
				self.fl_alive = False

	def th_gen_skel(self):		
		##
		# Consume: skeleton data
		# Produce: skeleton features
		##

		## Wait for kinect stream to be ready
		while(not self.fl_stream_ready): continue

		frame_count = 0 # this is zeroed internally
		skel_frames = []
		first_time = False
		print_first_time = True
		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, dont do anything
			if(self.fl_skel_ready): continue # If previous skeleton features are not used, dont do anything.
			if self.fl_gest_started:
				if print_first_time:
					# print "IN SKEL THREAD, GESTURE STARTED: "
					print_first_time = False
				first_time = True 
				with self.cond_skel:
					self.cond_skel.wait()
					# reduce -> append
					skel_frames.append(deepcopy(self.buf_skel[-1])) 
					frame_count += 1
			if not self.fl_gest_started and first_time:
				# print "IN SKEL THREAD, GESTURE ENDED: "
				first_time = False
				print_first_time = True
				frame_count = 0

				self.skel_instance = deepcopy(skel_frames) # [(ts1, ([left_x, y, z], [right_x, y, z])), ...]
				skel_frames = []

				self.fl_skel_ready = True ##### Think about conditioning

	def th_gen_openpose(self):
		##
		# Consume: RGB data
		# Produce: finger lengths features
		##

		## Wait for kinect stream to be ready
		while(not self.fl_stream_ready): continue	

		frame_count = 0 # this is zeroed internally
		op_instance = []
		first_time = False
		print_first_time = True
		rgb_frame = None
		while(self.fl_alive):
			# if(self.fl_synapse_running): continue # If synapse is running, dont do anything
			if(self.fl_openpose_ready): continue # If previous openpose data is not used, dont do anything
			if self.fl_gest_started:
				if print_first_time:
					# print "IN RGB THREAD, GESTURE STARTED: "
					print_first_time = False
				first_time = True 
				with self.cond_rgb:
					self.cond_rgb.wait()
					rgb_frame = deepcopy(self.buf_rgb[-1]) # (timestamp, ndarray)
					frame_count += 1
				op_instance.append((rgb_frame[0], extract_fingers_realtime(rgb_frame[-1])))
			if not self.fl_gest_started and first_time:
				# print "IN RGB THREAD, GESTURE ENDED: "
				first_time = False
				print_first_time = True
				frame_count = 0

				self.op_instance = deepcopy(op_instance) # [(ts1, ([left_f1, f2, .., f5], [right_f1, f2, .., f5])), ...]

				# timestamps, raw_op_features = zip(*op_instance)
				# # pp(len(raw_op_features))

				# self.op_instance = (timestamps, np.array(raw_op_features))
				op_instance = []
				self.fl_openpose_ready = True #### Think about conditioning

	def th_synapse(self):
		#
		while(self.fl_alive):
			if(not self.fl_cmd_ready): continue
			self.fl_synapse_running = True

			# If command is ready: Do the following:
			self.sock.send(self.command_to_execute)
			data = self.sock_recv(timeout = 5)
			if(data): 
				self.fl_cmd_ready = False
				self.fl_synapse_running = False
			else:
				print 'Synapse execution failed !'
				## What to do now
				sys.exit(0)

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
		acces_openpose_thread = Thread(name = 'access_openpose', target = self.th_gen_openpose) # C: RGB ; P: finger_lengths
		synapse_thread = Thread(name = 'autoclick_synapse', target = self.th_synapse) #

		##########
		# TODO: Incorporate the calibration information in the realtime code
		#
		##########

		acces_kinect_thread.start()
		gen_skel_thread.start()
		acces_openpose_thread.start()
		if(ENABLE_SOCKET): synapse_thread.start()

		only_skeleton = True

		## Merger part of the code
		while(self.fl_alive):
			if(self.fl_synapse_running): continue
			if(self.fl_skel_ready and self.fl_openpose_ready):
				# pp(self.skel_instance)
				# pp(self.op_instance)
				
				#####################
				### SKEL FEATURE ####
				#####################
				# Detuple skel_instance
				skel_ts, raw_skel_frames = zip(*self.skel_instance)
				dom_rhand, final_skel_inst = self.feat_ext.generate_features_realtime(list(raw_skel_frames))
				#####################

				## Interpolate openpose instances
				if(not only_skeleton):
					###################
					### OP FEATURE ####
					###################
					# Detuple op_instance
					op_ts, raw_op_frames = zip(*op_instance)
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
				self.command_to_execute = self.get_next_cmd(cname)

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
				self.fl_openpose_ready = False

		# If anything fails do the following
		self.kr.close()
		if(ENABLE_SOCKET): self.sock.close()


if(__name__ == '__main__'):
	rt = Realtime()
	rt.run()