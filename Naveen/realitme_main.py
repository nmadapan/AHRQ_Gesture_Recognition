import cv2
import numpy as np
import os, sys, time
from threading import Thread, Condition
from copy import copy, deepcopy
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
		self.buf_rgb = [(None, None) for _ in range(self.buf_rgb_size)] # timestamp, frame_nparray
		self.buf_finglen = [(None, None) for _ in range(self.buf_rgb_size)] # timestamp, frame_list

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

		## thread conditions
		self.cond_skel = Condition()
		self.cond_rgb = Condition()

		## Initialize Feature extractor
		self.feat_ext = FeatureExtractor()

		## Other variables
		self.skel_instance = None # Updated in self.th_gen_skel(). It is a tuple (timestamp, feature_vector of skeleton).

		## Skeleton constants
		self.base_id = 0
		self.neck_id = 2
		self.left_hand_id = 7
		self.right_hand_id = 11
		self.thresh_level = 0.2 #TODO: It seems to be working. 

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
				if (left_y >= start_y_coo or right_y >= start_y_coo) and (not self.fl_gest_started):
					self.fl_gest_started = True
				if (left_y < start_y_coo and right_y < start_y_coo) and self.fl_gest_started:
					self.fl_gest_started = False

				# if(self.fl_gest_started): print 'Gesture started!'
								
				# Update the skel buffer
				if(self.fl_gest_started):
					with self.cond_skel: # Producer. Consumers will wait for the notify call
						ts = int(time.time()*100)
						self.buf_skel.append((ts, skel_col_reduce(skel_pts)))
						self.buf_skel.pop(0)
						self.cond_skel.notify_all()
						tslist, _ = zip(*self.buf_skel)
						# print 'skel: ', tslist

			if(rgb_flag and self.fl_gest_started):
				with self.cond_rgb: # Producer. Consumers need to wait for producer's 'notify' call
					ts = int(time.time()*100)
					self.buf_rgb.append((ts, self.kr.color_image))
					self.buf_rgb.pop(0)
					self.cond_rgb.notify_all()
					tslist, _ = zip(*self.buf_rgb)
					# print 'rgb: ', tslist
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

		frame_count = 0 # this needs to be zeroed internally too
		skel_frames = []
		while(self.fl_alive):
			# print self.fl_gest_started
			if self.fl_gest_started: 
				with self.cond_skel:
					# Waiting for the producer (th_access_kinect) to add frames
					self.cond_skel.wait()
					# reduce -> append
					skel_frames.append(deepcopy(self.buf_skel[-1])) 
					frame_count += 1
					# print frame_count
			elif (not self.fl_gest_started) and (frame_count > 0):
				frame_count = 0
				timestamps, raw_frames = zip(*skel_frames)
				# This returns 2D numpy array (1 x num_features)
				instance_feed = [skel_col_reduce(raw_frame) for raw_frame in raw_frames]
				self.skel_instance = (timestamps[-1], self.feat_ext.generate_features_realtime(instance_feed))
				print self.skel_instance[0], self.skel_instance[0].shape
				print "ARE WE EVEN GETTING HERE???"
				skel_frames = []
			print "but are we here.... and WTF is the problem"

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
		acces_kinect_thread = Thread(name = 'access_kinect', target = self.th_access_kinect) # P: RGB, skel
		gen_skel_thread = Thread(name = 'gen_skel', target = self.th_gen_skel) # C: skel ; P: skel_features
		# acces_openpose_thread = Thread(name = 'access_openpose', target = self.th_access_openpose) # C: RGB ; P: finger_lengths
		# synapse_thread = Thread(name = 'autoclick_synapse', target = self.th_synapse) #

		acces_kinect_thread.start()
		gen_skel_thread.start()


if(__name__ == '__main__'):
	rt = Realtime()
	rt.run()