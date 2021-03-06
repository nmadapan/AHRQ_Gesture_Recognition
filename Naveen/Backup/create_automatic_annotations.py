import cv2, numpy as np, os, sys
import glob

#####################
#
# Description:
# 	This script creates annotations (start and end of each gesture) automatically for the given text file.
#	The text file should end with '_skel.txt' --> File format
#	The output annotation file will be written as '_annot2.txt'
# 	If this format is not followed, initialize in_format_flag to False. 
#
# How to use:
#	skel_file_path: Absolute path to the skeleton data file (txt file)
#	base_write_folder: The annotations will be written to this file.
#	in_format_flag: Whether or not the file naming format is followed. 
#	Thats it. Run this file. 
#
#####################

## Initialization
skel_file_path = '..\\Data\\S2_L6\\10_1_S2_L6_X_OnePanel_skel.txt'
base_write_folder = 'F:\\AHRQ\Study_IV\\AHRQ_Gesture_Recognition\Data\\S2_L6\\Annotations'
in_format_flag = True

## Code
skel_file_paths = [skel_file_path]

## Global parameters
torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2

for skel_path in skel_file_paths:
	# print '. ', 
	count_gestures = 0
	with open(skel_path, 'r') as fp:
		lines = fp.readlines()
		lines = [map(float, line.split(' ')) for line in lines]
	if len(lines) == 0: 
		print skel_path, ' has 0 lines'
		continue
	start_y_coo = thresh_level * (lines[0][3*neck_id+1] - lines[0][3*torso_id+1])
	start_flag = False
	if(in_format_flag):
		write_filename = os.path.basename(skel_path)[:-8] + 'annot2.txt'
	else:
		write_filename = os.path.basename(skel_path)[:-4] + 'annot2.txt'
	write_file_id = open(os.path.join(base_write_folder, write_filename), 'w')
	for idx, line in enumerate(lines):
		left_y = line[3*left_hand_id+1] - line[3*torso_id+1]
		right_y = line[3*right_hand_id+1] - line[3*torso_id+1]
		if (left_y >= start_y_coo or right_y >= start_y_coo) and (not start_flag): 
			count_gestures += 1
			start_flag = True
			write_file_id.write(str(idx))
			write_file_id.write('\n')
		if (left_y < start_y_coo and right_y < start_y_coo) and start_flag: 
			count_gestures += 1
			start_flag = False
			write_file_id.write(str(idx))
			write_file_id.write('\n')
	if(count_gestures%2 != 0):
		print '\nManual verification needed for: ', 
		print write_filename + ' ',
		print 'Odd no. of entries'
	if(count_gestures < 40):
		print '\nManual verification needed for: ', 
		print write_filename + ' ',
		print 'no. of entries less than 20'

