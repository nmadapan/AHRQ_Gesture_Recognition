import cv2
import numpy as np
import os, sys, time
from threading import Thread, Condition
from copy import copy, deepcopy
import pickle

from FeatureExtractor import FeatureExtractor
from KinectReader import kinect_reader
from helpers import *
from pprint import pprint as pp

# Fake openpose
from fake_openpose import extract_fingers_realtime
from helpers import sync_ts

class Realtime:
	def __init__(self):
		## Global Constants
		self.lexicon_name = 'L6'
		self.data_path = '..\\Data'

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
		self.fl_synapse_ready = False # th_synapse

		self.fl_gest_started = False
		self.fl_cmd_running = False # Synapse running
		self.dom_rhand = True # By default, right followed by left

		# Initialize the Kinect
		self.kr = kinect_reader()

		## thread conditions
		self.cond_skel = Condition()
		self.cond_rgb = Condition()

		## Initialize Feature extractor
		self.feat_ext = FeatureExtractor() ## LATER use a trained one. 

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

		while(self.fl_alive):
			# if(self.fl_skel_ready and self.fl_openpose_ready): continue ## UNCOMMET IT LATER ON
			# Refreshing Frames
			rgb_flag = self.kr.update_rgb()
			body_flag = self.kr.update_body()

			if(body_flag):
				skel_pts = self.kr.skel_pts.tolist()

				# GESTURE SPOTTING NEEDS TO HAPPEN HERE
				# Check if gesture started
				# When start_flag=true the gesture started
				# When start_flag=false the hands are down and the
				# frames don't need to be collected
				start_y_coo = self.thresh_level * (skel_pts[3*self.neck_id+1] - skel_pts[3*self.base_id+1])
				left_y = skel_pts[3*self.left_hand_id+1] - skel_pts[3*self.base_id+1]
				right_y = skel_pts[3*self.right_hand_id+1] - skel_pts[3*self.base_id+1]

				## When you want to wait() based on a shared variables, make sure to include them in the thread.Condition. 
				with self.cond_skel: # Producer. Consumers will wait for the notify call #######
					if (left_y >= start_y_coo or right_y >= start_y_coo) and (not self.fl_gest_started):
						self.fl_gest_started = True
					if (left_y < start_y_coo and right_y < start_y_coo) and self.fl_gest_started:
						self.fl_gest_started = False
									
					# Update the skel buffer
					if(self.fl_gest_started):
						ts = int(time.time()*100)
						self.buf_skel.append((ts, skel_col_reduce(skel_pts)))
						self.buf_skel.pop(0)
						tslist, _ = zip(*self.buf_skel)

					# The Notify all should be outside because if not, the cosumer
					# can wait for this call just after the flags that allow
					# it to enter the "consuming condition" have changed
					self.cond_skel.notify_all()

			if(rgb_flag and self.fl_gest_started):
				with self.cond_rgb: # Producer. Consumers need to wait for producer's 'notify' call
					ts = int(time.time()*100)
					self.buf_rgb.append((ts, self.kr.color_image))
					self.buf_rgb.pop(0)
					self.cond_rgb.notify_all()
					tslist, _ = zip(*self.buf_rgb)
					cv2.imshow('RGB', cv2.resize(self.kr.color_image, None, fx=0.5, fy=0.5))

			if(cv2.waitKey(1) == ord('q')):
				self.fl_alive = False
				self.kr.close()
				exit()

	def th_gen_skel(self):		
		##
		# Consume: skeleton data
		# Produce: skeleton features
		##

		frame_count = 0 # this is zeroed internally
		skel_frames = []
		first_time = False
		print_first_time = True
		while(self.fl_alive):
			if(self.fl_skel_ready): continue
			if self.fl_gest_started:
				if print_first_time:
					print "IN SKEL THREAD, GESTURE STARTED: "
					print_first_time = False
				first_time = True 
				with self.cond_skel:
					self.cond_skel.wait()
					# reduce -> append
					skel_frames.append(deepcopy(self.buf_skel[-1])) 
					frame_count += 1
			if not self.fl_gest_started and first_time:
				print "IN SKEL THREAD, GESTURE ENDED: "
				first_time = False
				print_first_time = True
				frame_count = 0
				timestamps, raw_frames = zip(*skel_frames)

				left, right = zip(*raw_frames)
				left, right = np.array(left), np.array(right)
				self.dom_rhand = self.feat_ext.find_type_order(left, right)[0] == 0

				self.skel_instance = (timestamps, self.feat_ext.generate_features_realtime(list(raw_frames)))
				# pp(len(skel_frames))

				skel_frames = []

				self.fl_skel_ready = True ##### Think about conditioning

	def th_gen_openpose(self):
		##
		# Consume: RGB data
		# Produce: finger lengths features
		##

		frame_count = 0 # this is zeroed internally
		op_instance = []
		first_time = False
		print_first_time = True
		rgb_frame = None
		while(self.fl_alive):
			if(self.fl_openpose_ready): continue
			if self.fl_gest_started:
				if print_first_time:
					print "IN RGB THREAD, GESTURE STARTED: "
					print_first_time = False
				first_time = True 
				with self.cond_rgb:
					self.cond_rgb.wait()
					rgb_frame = deepcopy(self.buf_rgb[-1]) # (timestamp, ndarray)
					frame_count += 1
				op_instance.append((rgb_frame[0], extract_fingers_realtime(rgb_frame[-1])))
			if not self.fl_gest_started and first_time:
				print "IN RGB THREAD, GESTURE ENDED: "
				first_time = False
				print_first_time = True
				frame_count = 0
				timestamps, raw_op_features = zip(*op_instance)
				# pp(len(raw_op_features))

				self.op_instance = (timestamps, np.array(raw_op_features))
				op_instance = []
				self.fl_openpose_ready = True #### Think about conditioning

	def th_synapse(self):
		## Socket communicaiton code goes here. 
		# Client

		# 
		pass

	def get_next_cmd(self, pred_cmd):
		# pred_cmd : predicted command name
		
		# If there are no previous commands, return the same command
		if(len(self.prev_executed_cmds) == 0):
			self.prev_executed_cmds.append(pred_cmd)
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

		acces_kinect_thread.start()
		gen_skel_thread.start()
		acces_openpose_thread.start()

		only_skeleton = True

		## Merger part of the code
		while(True):
			if(self.fl_skel_ready and self.fl_openpose_ready):
				# pp(self.skel_instance)
				# pp(self.op_instance)
				
				# Obtain timestamps
				skel_ts, skel_inst = self.skel_instance[0], self.skel_instance[1]
				op_ts, op_inst = self.op_instance[0], self.op_instance[1]
				_, sync_op_ts = sync_ts(skel_ts, op_ts)

				## Interpolate openpose instances
				op_inst = smart_interpn(op_inst, sync_op_ts, kind = 'copy') # Change kind to 'linear' for linear interpolation
				op_inst = interpn(op_inst, self.feat_ext.fixed_num_frames).reshape(1, -1)

				final_inst = np.append(skel_inst, op_inst).reshape(1, -1)

				print'skel_inst: ', skel_inst.shape
				print'op_inst: ', op_inst.shape
				print'final_inst: ', final_inst.shape

				if(only_skeleton): final_inst = skel_inst

				## Working until here. Debugged!!!!!!!!!!!

				'''
					* Passing the feature to the actual svm:
						cname = self.feat_ext.pred_output_realtime(final_inst)
					* Logic that operates over the command names. This is lexicon specific. We have L*_repetition.txt file. 
						command_to_execute = get_next_command(cname)
					* Let the synapse thread know that command is ready. It can execute it. 
				'''

				self.fl_skel_ready = False
				self.fl_openpose_ready = False


if(__name__ == '__main__'):
	rt = Realtime()
	rt.run()