import numpy as np
import cv2, os, sys, time
from KinectReader import kinect_reader
from helpers import *
from threading import Thread
from copy import deepcopy
import pickle
from FeatureExtractor import FeatureExtractor

pickle_fname = os.path.join('..', 'Test', 'L6_svm_weights.pickle')
svm_clf = pickle.load(open(pickle_fname, 'rb'))

## Global parameters
torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2
base_id = torso_id

out = []
gest_acq_status = False

def get_gest(kr):
	global out, gest_acq_status
	gest_acq_status = True
	result = []
	start_flag = False

	while(gest_acq_status):
		# try:
		body_flag = kr.update_body()
		if(body_flag):
			skel_pts = kr.skel_pts.tolist()
			start_y_coo = thresh_level * (skel_pts[3*neck_id+1] - skel_pts[3*base_id+1])
			left_y = skel_pts[3*left_hand_id+1] - skel_pts[3*base_id+1]
			right_y = skel_pts[3*right_hand_id+1] - skel_pts[3*base_id+1]
			if (left_y >= start_y_coo or right_y >= start_y_coo) and (not start_flag): 
				start_flag = True
			if (left_y < start_y_coo and right_y < start_y_coo) and start_flag: 
				start_flag = False
			if(start_flag):
				result.append(skel_col_reduce(skel_pts))
		if(len(result)!=0 and (not start_flag) ):
			out.append(deepcopy(result))
			start_flag = False
			result = []

		time.sleep(0.1)
		# except Exception as exp:
		# 	print exp

display_flag = True

# Initialize Kinect
kr = kinect_reader()
wait_for_kinect(kr)

# Initialize feature extractor
svm_fpath = os.path.join('..', 'Test', 'L6_svm_weights.pickle')
dt = pickle.load(open(pickle_fname, 'rb'))
clf, fe = dt['clf'], dt['fe']

gest_acq_thread = Thread(name = 'gesture_spotter', target = get_gest, args = (kr, ))
gest_acq_thread.start()

spin = True
prev_out_len = len(out)

try:
	start_time = time.time()
	while spin:
		# Refreshing Frames
		rgb_flag = kr.update_rgb()
		depth_flag = kr.update_depth()
		# body_flag = kr.update_body()
		if rgb_flag and display_flag:
			cv2.imshow('RGB_Video', cv2.resize(kr.color_image, None, fx=0.4, fy=0.4))
			if cv2.waitKey(1) == ord('q') : 
				cv2.destroyAllWindows()
				spin = False
				gest_acq_status = False
		if(len(out) > prev_out_len):
			prev_out_len = len(out)
			# print len(out)
			fe.pred_output_realtime(out[-1], clf)
			### Now generate features and recognize the gesture. 
			### Code in the FeatureExtractor should be changed or new functions should be added to work in the realtime

		time.sleep(0.1)

except Exception as exp:
	print exp

## Closing Kinect, RGB, Depth, and annotation file streams
kr.sensor.close()
