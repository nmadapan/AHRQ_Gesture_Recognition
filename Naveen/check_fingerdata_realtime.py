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

## TCP/IP of CPM Computer
IP_CPM = 'localhost'
PORT_CPM = 3000

## 
base_write_dir = r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master\test_imgs'
base_path = r'G:\AHRQ\S2_L7\L7'
fileprefix = '1_1_S2_L7_Random_thing'
param_path = 'param.json'

param_dict = json_to_dict(param_path)

neck_id = 2
base_id = 0
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2

## CPM Should be running in the background
client_cpm = Client(IP_CPM, PORT_CPM)

## Call CPM init socket
client_cpm.init_socket()

kr = kinect_reader()

def save_hand_bbox(img, hand_pixel_coo, out_fname):
	'''
	Description:
		Writes the hand bbox to base_write_dir
	Input arguments:
		'img': An RGB image. np.ndarray of shape (H x W x 3).
		'bbox': list of four values. [x, y, w, h].
			(x, y): pixel coordinates of top left corner of the bbox
			(w, h): width and height of the boox.
	'''
	if(img is None): return
	bbox = get_hand_bbox(hand_pixel_coo, max_wh = (img.shape[1], img.shape[0]))
	rx, ry, rw, rh = tuple(bbox)
	cropped_img = img[ry:ry+rh, rx:rx+rw]
	cv2.imwrite(os.path.join(base_write_dir, out_fname), cropped_img)

avi_path = os.path.join(base_path, fileprefix + '_rgb.avi')
color_path = os.path.join(base_path, fileprefix + '_color.txt')
skel_path = os.path.join(base_path, fileprefix + '_skel.txt')
out_file_path = os.path.join(base_path, fileprefix + '_out.txt')

cap = cv2.VideoCapture(avi_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fp_colortxt = open(color_path, 'r')
fp_skeltxt = open(skel_path, 'r')
fp_outtxt = open(out_file_path, 'w')

frame_count = 0

while(cap.isOpened()):
	ret, frame = cap.read()
	color_line = fp_colortxt.readline()
	skel_line = fp_skeltxt.readline()
	
	if(len(skel_line) == 0 or len(color_line) == 0 or (not ret)):
		cv2.destroyAllWindows()
		break
	
	color_skel_pts = np.array(map(float, color_line.split(' '))).astype(int)
	skel_pts = np.array(map(float, skel_line.split(' ')))
	# print(skel_pts)

	start_y_coo = thresh_level * (skel_pts[3*neck_id+1] - skel_pts[3*base_id+1]) ## Threshold level
	left_y = skel_pts[3*left_hand_id+1] - skel_pts[3*base_id+1] # left hand
	right_y = skel_pts[3*right_hand_id+1] - skel_pts[3*base_id+1] # right hand

	left_status = left_y >= start_y_coo
	right_status = right_y >= start_y_coo

	rgb_hand_coo = skel_col_reduce(color_skel_pts, dim=2, wrt_shoulder = False)

	if(right_status):
		r_fname = str(frame_count) + '_r.jpg'
		save_hand_bbox(frame, rgb_hand_coo[0], r_fname)
	# Left hand
	if(left_status):
		l_fname = str(frame_count) + '_l.jpg'
		save_hand_bbox(frame, rgb_hand_coo[1], l_fname)

	## Step 3: Socket send image names for both images. This will return finger lengths.
	# Right hand
	if(right_status):
		client_cpm.sock.send(r_fname)
		r_fing_data = client_cpm.sock_recv(display = False)
		r_finger_lengths = str_to_nparray(r_fing_data, dlim = '_').tolist()
	else:
		r_finger_lengths = np.zeros(param_dict['num_fingers']).tolist()
	# Left hand
	if(left_status):
		client_cpm.sock.send(l_fname)
		l_fing_data = client_cpm.sock_recv(display = False)
		l_finger_lengths = str_to_nparray(l_fing_data, dlim = '_').tolist()
	else:
		l_finger_lengths = np.zeros(param_dict['num_fingers']).tolist()

	print(l_finger_lengths, r_finger_lengths)

	
	lstr = 'Left: ' + ' '.join(map(str, l_finger_lengths)) + '     '
	rstr = 'Right: ' + ' '.join(map(str, r_finger_lengths)) + '\n'
	fp_outtxt.write(lstr + rstr)

	image_with_skel = kr.draw_body(deepcopy(frame), color_skel_pts)
	cv2.imshow('Hello World', cv2.resize(image_with_skel, None, fx = 0.5, fy = 0.5))

	frame_count += 1

	if cv2.waitKey(3) == ord('q'):
		cv2.destroyAllWindows()

print('No. of frames: ', frame_count)

fp_outtxt.flush()
fp_outtxt.close()

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
