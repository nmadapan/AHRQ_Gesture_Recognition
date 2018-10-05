import numpy as np
from KinectReader import kinect_reader
from helpers import *
import cv2
from copy import deepcopy
from CustomSocketClient import CustomSocket
import sys, os

####################
### Socket Setup  ##
####################
TCP_IP = 'localhost'
TCP_PORT = 3000
sock = CustomSocket(TCP_IP, TCP_PORT)
sock.init_socket()

####################
### Kinect Setup  ##
####################
kr = kinect_reader()
wait_for_kinect(kr)

#####################
### Miscellaneous  ##
#####################
base_write_dir = 'Backup'
# TODO: skeleton and rgb are out of sync. Not sure if we can use the current pair. 

####################
### Kinect Joints ##
####################
## Right hand
WristRight = 10
HandRight = 11
HandTipRight = 23
ThumbRight = 24
## Left hand
WristLeft = 6
HandLeft = 7
HandTipLeft = 21
ThumbLeft = 22

def get_lhand_info(color_skel_pts, des_size = 300):
	hand = np.array(color_skel_pts[2*HandLeft:2*HandLeft+2])
	return [np.int32(hand[0]) - des_size/2, np.int32(hand[1]) - des_size/2, des_size, des_size]

def get_rhand_info(color_skel_pts, des_size = 300):
	hand = np.array(color_skel_pts[2*HandRight:2*HandRight+2])
	# wrist = np.array(color_skel_pts[2*WristRight:2*WristRight+2])
	# tip = np.array(color_skel_pts[2*HandTipRight:2*HandTipRight+2])
	# thumb = np.array(color_skel_pts[2*ThumbRight:2*ThumbRight+2])

	# height = np.int32(3.5 * (wrist - tip)[1])
	# width = height 

	# corner = np.int32(wrist - np.array([width/2, height/2]))

	# if(height >= 0):
	# 	bbox = [corner[0], corner[1], np.abs(width), np.abs(height)]
	# else:
	# 	bbox = [corner[0] - width, corner[1] - height, np.abs(width), np.abs(height)]

	# # print bbox

	return [np.int32(hand[0]) - des_size/2, np.int32(hand[1]) - des_size/2, des_size, des_size]

color_img = None
skel_pts = None
color_skel_pts = None

counter = 0

while(True):
	# Refreshing Frames
	rgb_flag = kr.update_rgb()
	body_flag = kr.update_body()

	if(rgb_flag):
		color_img = kr.color_image
		clone_color_img = deepcopy(color_img)

	if(body_flag):
		counter += 1
		skel_pts = kr.skel_pts.tolist() # list of 75 floats
		color_skel_pts = kr.color_skel_pts.tolist()

		rbbox = get_rhand_info(color_skel_pts)
		rx, ry, rw, rh = tuple(rbbox)
		lbbox = get_lhand_info(color_skel_pts)
		lx, ly, lw, lh = tuple(lbbox)

		if color_img is None: continue
		
		rcropped_image = clone_color_img[ry:ry+rh, rx:rx+rw]
		lcropped_image = clone_color_img[ly:ly+lh, lx:lx+lw]
		
		cv2.rectangle(color_img, (rx,ry),(rx+rw,ry+rh), (0,255,0), 3)
		cv2.rectangle(color_img, (lx,ly),(lx+lw,ly+lh), (0,255,0), 3)

		cv2.imwrite(os.path.join(base_write_dir, str(counter)+'_r.jpg'), rcropped_image)
		cv2.imwrite(os.path.join(base_write_dir, str(counter)+'_l.jpg'), lcropped_image)

		cv2.imshow('new_img', cv2.resize(color_img, None, fx = 0.5, fy = 0.5))
		if cv2.waitKey(10) == ord('q'):
			cv2.destroyAllWindows()
			break

kr.close()
