import cv2
import numpy as np
import os, sys, time
from threading import Thread
from copy import deepcopy
import pickle

from FeatureExtractor import FeatureExtractor
from KinectReader import kinect_reader
from helpers import *

class Realtime:
	def __init__(self):
	## Global Constants
	self.buf_skel_size = 10
	self.buf_rgb_size = 10

	## Buffers
	self.buf_skel = [(None, None) for _ in range(self.buf_skel_size)] # timestamp, frame_list # [..., t-3, t-2, t-1, t]
	self.fl_skel_ready = True
	self.buf_rgb = [(None, None) for _ in range(self.buf_rgb_size)] # timestamp, frame_nparray
	self.fl_rgb_ready = True
	self.buf_finglen = [(None, None) for _ in range(self.buf_rgb_size)] # timestamp, frame_list
	self.fl_finglen_ready = True

	# self.que_skel_io = [] # list of sub lists. sub list is ['R', None] or ['W', data]
	# self.que_rgb_io = [] # list of sub lists. sub list is ['R', None] or ['W', data]
	# self.cur_skel_inst = None
	# self.cur_rgb_inst = None

	## Flags
	self.fl_alive = True
	self.fl_stream_ready = False # th_access_kinect
	self.fl_gen_skel = False # th_gen_skel
	self.fl_openpose_ready = False # th_access_openpose
	self.fl_synapse_ready = False # th_synapse

	self.fl_gest_started = False
	self.fl_cmd_running = False # Synapse running

	# Initialize the Kinect
	self.kr = kinect_reader()

	# def th_rw_skel(self): ## IT WILL NOT WORK
	# 	while(True):
	# 		for _str, data in self.que_skel_io:
	# 			if(_str.lower() == 'w'):
	# 				self.buf_skel.pop(0)
	# 				self.buf_skel.append(data)
	# 				# After writing delete ### IMPORTANT
	# 				## THIS IS NOT A GOOD IDEA. IT STILL HAS THE SAME PROBLEM.					
	# 			elif(_str.lower() == 'r'):
	# 				self.cur_skel_inst = self.buf_skel[-1]
	# 				# Instead of doing -1 use a pointer, and keep updating after both read and write. 
	# 				# Careful about the boundary conditions

	# def th_rw_rgb(self): ##### IT WILL NOT WORK
	# 	while(True):
	# 		for _str, data in self.que_rgb_io:
	# 			if(_str.lower() == 'w'):
	# 				self.buf_rgb.pop(0)
	# 				self.buf_rgb.append(data)
	# 				# After writing delete ### IMPORTANT
	# 				## THIS IS NOT A GOOD IDEA. IT STILL HAS THE SAME PROBLEM.
	# 			elif(_str.lower() == 'r'):
	# 				self.cur_rgb_inst = self.buf_rgb[-1]
	# 				# Instead of doing -1 use a pointer, and keep updating after both read and write. 
	# 				# Careful about the boundary conditions

	def th_access_kinect(self):
		# Initialize Kinect
		wait_for_kinect(self.kr)

		# Now this thread is ready
		self.fl_stream_ready = True

		While(self.fl_alive):
			# Refreshing Frames
			rgb_flag = kr.update_rgb()
			body_flag = kr.update_body()

			while(rgb_flag):
				# THIS HAS THE RACING CONDITION PROBLEMS
				# if(self.fl_rgb_ready):
				# 	self.fl_rgb_ready = False
				# 	self.buf_rgb.pop(0)
				# 	self.buf_rgb.append(kr.color_image)
				# 	break
				pass


			if(body_flag):
				# THIS HAS THE RACING CONDITION PROBLEMS
				# skel_pts = kr.skel_pts.tolist()

				## GESTURE SPOTTING NEEDS TO HAPPEN HERE
				# Check if gesture started
				# start_y_coo = thresh_level * (skel_pts[3*neck_id+1] - skel_pts[3*base_id+1])
				# left_y = skel_pts[3*left_hand_id+1] - skel_pts[3*base_id+1]
				# right_y = skel_pts[3*right_hand_id+1] - skel_pts[3*base_id+1]
				# if (left_y >= start_y_coo or right_y >= start_y_coo) and (not start_flag):
				# 	start_flag = True
				# if (left_y < start_y_coo and right_y < start_y_coo) and start_flag:
				# 	start_flag = False
				# if(start_flag):
				# 	result.append(skel_col_reduce(skel_pts))
				
				# # Update the skel buffer
				# self.buf_skel.pop(0)
				# self.buf_skel.append(skel_col_reduce(skel_pts))
			pass

	def th_gen_skel(self):
		while(self.fl_alive):
			if self.fl_gest_started:
				pass
			else:
				continue

	def th_access_openpose(self):
		while(self.fl_alive):
			if self.fl_gest_started:
				pass
			else:
				continue

	def th_synapse(self):
		pass

	def run(self):
		# Main thread
		# rw_skel_thread = Thread(name = 'read_write_skel_thread', target = self.th_read_write)
		# rw_rgb_thread = Thread(name = 'read_write_skel_thread', target = self.th_read_write)
		acces_kinect_thread = Thread(name = 'access_kinect', target = self.th_access_kinect)
		gen_skel_thread = Thread(name = 'gen_skel', target = self.th_gen_skel)
		acces_openpose_thread = Thread(name = 'access_openpose', target = self.th_access_openpose)
		synapse_thread = Thread(name = 'autoclick_synapse', target = self.th_synapse)

if(__name__ == '__main__'):
	rt = Realtime()
	rt.run()