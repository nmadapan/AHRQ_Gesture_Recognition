import cv2, numpy as np, os, sys

skel_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\S2_L6\\5_4_S2_L6_SwitchPanel_Down_skel.txt'

with open(skel_path, 'r') as fp:
	lines = fp.readlines()
	lines = [map(float, line.split(' ')) for line in lines]

print 'Total No. of frames: ', len(lines)

torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2
start_y_coo = thresh_level * (lines[0][3*neck_id+1] - lines[0][3*torso_id+1])

start_flag = False

for idx, line in enumerate(lines):
	left_y = line[3*left_hand_id+1] - line[3*torso_id+1]
	right_y = line[3*right_hand_id+1] - line[3*torso_id+1]
	# if start_flag: print left_y, right_y, start_y_coo
	if (left_y >= start_y_coo or right_y >= start_y_coo) and (not start_flag):
		# print 'Starting --- ', left_y, right_y, start_y_coo
		start_flag = True
		print idx
	if (left_y < start_y_coo and right_y < start_y_coo) and start_flag:
		# print 'Ending --- ', left_y, right_y, start_y_coo
		start_flag = False
		print idx
		# sys.exit(0)
