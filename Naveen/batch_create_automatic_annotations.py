import cv2, numpy as np, os, sys
import glob

#####################
#
# Description:
# 	This script BATCH processes multiple skeleton data text files. 
#	It creates annotations (start and end of each gesture) automatically for each text file.
#	The text files should end with '_skel.txt' --> File format
#	The output annotation file will be written as '_annot2.txt'
# 	If this format is not followed, initialize in_format_flag to False. 
#	if in_format_flag is False, it will read all .txt files in the folder
#
# How to use:
#	base_skel_folder: Absolute path to the folder containing skeleton data text files
#	base_write_folder: The annotations will be written to this file.
#	in_format_flag: Whether or not the file naming format is followed. 
#	Thats it. Run this file. 
#
#####################

## Initialization
base_skel_folder = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L8'
base_write_folder = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L8\\Annotations'
# base_skel_folder = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data'
# base_write_folder = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\Annotations'
in_format_flag = True

## Global parameters
torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2

base_id = torso_id

if(in_format_flag):
	skel_file_paths = glob.glob(os.path.join(base_skel_folder, '*_skel.txt'))
else:
	skel_file_paths = glob.glob(os.path.join(base_skel_folder, '*.txt'))

if(not os.path.isdir(base_write_folder)): os.makedirs(base_write_folder)

for skel_path in skel_file_paths:
	## Read timestamps
	# Read RGB timestamps
	tbase_path = '_'.join(skel_path.split('_')[:-1])
	if(not os.path.isfile(tbase_path+'_rgbts.txt')): 
		sys.exit(os.path.basename(tbase_path)+' - RGB timestamps file doesnt exist')
	if(not os.path.isfile(tbase_path+'_skelts.txt')): 
		sys.exit(os.path.basename(tbase_path)+' - Skel timestamps file doesnt exist')

	with open(tbase_path+'_rgbts.txt', 'r') as fp:
		rgb_ts = map(float, fp.readlines())
	if(len(rgb_ts) == 0): sys.exit(os.path.basename(tbase_path)+' - rgb timestamps file is empty')
	rgb_ts = np.array(rgb_ts)
	rgb_ts = rgb_ts - rgb_ts[0]
	# Read Skeleton timestamps
	with open(tbase_path+'_skelts.txt', 'r') as fp:
		skel_ts = map(float, fp.readlines())
	if(len(skel_ts) == 0): sys.exit(os.path.basename(tbase_path)+' - skeleton timestamps file is empty')	
	skel_ts = np.array(skel_ts)
	skel_ts = skel_ts - skel_ts[0]
	M = np.abs(skel_ts.reshape(-1, 1) - rgb_ts)
	skel_to_rgb = np.argmin(M, axis = 1)

	## Read skeleton file
	with open(skel_path, 'r') as fp:
		lines = fp.readlines()
		lines = [map(float, line.split(' ')) for line in lines]
	if len(lines) == 0: 
		print os.path.basename(skel_path), ' has 0 lines'
		continue
	start_y_coo = thresh_level * (lines[0][3*neck_id+1] - lines[0][3*base_id+1])
	start_flag = False
	if(in_format_flag):
		write_filename = os.path.basename(skel_path)[:-8] + 'annot2.txt'
		rgb_write_filename = os.path.basename(skel_path)[:-8] + 'rgbannot2.txt'
	else:
		write_filename = os.path.basename(skel_path)[:-4] + 'annot2.txt'
		rgb_write_filename = os.path.basename(skel_path)[:-4] + 'rgbannot2.txt'
	
	write_file_id = open(os.path.join(base_write_folder, write_filename), 'w')
	rgb_write_file_id = open(os.path.join(base_write_folder, rgb_write_filename), 'w')

	prev_idx = -1
	count_gestures = 0
	for idx, line in enumerate(lines):
		left_y = line[3*left_hand_id+1] - line[3*base_id+1]
		right_y = line[3*right_hand_id+1] - line[3*base_id+1]
		if (left_y >= start_y_coo or right_y >= start_y_coo) and (not start_flag): 
			start_flag = True
			prev_idx = idx
		if (left_y < start_y_coo and right_y < start_y_coo) and start_flag: 
			count_gestures += 2
			start_flag = False
			if(abs(prev_idx-idx) >= 20):
				write_file_id.write(str(prev_idx))
				write_file_id.write('\n')			
				write_file_id.write(str(idx))
				write_file_id.write('\n')

				rgb_write_file_id.write(str(skel_to_rgb[prev_idx]))
				rgb_write_file_id.write('\n')			
				rgb_write_file_id.write(str(skel_to_rgb[idx]))
				rgb_write_file_id.write('\n')		
	write_file_id.flush()		
	rgb_write_file_id.flush()		
	write_file_id.close()		
	rgb_write_file_id.close()		
	if(count_gestures%2 != 0):
		print 'Manual verification needed for: ', 
		print write_filename + ' ',
		print 'Odd no. of entries'
	if(count_gestures < 30):
		print 'Manual verification needed for: ', 
		print write_filename + ' ',
		print 'no. of gestures: ', count_gestures/2

