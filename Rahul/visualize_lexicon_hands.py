#NOTE: This file uses Convolutional Pose Machines(CPM), hence runs with Python3
"""
This file takes the path to lexicon containing folders with hand bounding boxes. Then for each command it shows the sequence of frames and finger joints(extracted from CPM
) for all subjects.
"""

import numpy as np
import os, time, glob, sys, json
import cv2
from copy import deepcopy

# if this file is in some other location than "convolutional-pose-machines-tensorflow-master", then 
# uncomment the following line and use the path to the CPM folder
# sys.path.insert(0, r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master')
# from CpmClass_offline import CpmClass

# utils_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Rahul'
# sys.path.insert(0,utils_file_path)
# from utils import *

#NOTE: importing utils is not working coherently with cpm so functions can not be imported

lex_path = r"H:\AHRQ\Study_IV\Data\Data_cpm_new\frames_with_joints\L6"

commands_file_path = r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\commands.json'

real_time  = False # if True, it will run the cpm and show the live results else the code will show the results from the saved images

default_width, default_height = 1920, 1080

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

def sort_filenames(annot_rgb_files):
##################################################
### sorts annotation files
### works differently for python 2 and python 3
##################################################
    if sys.version_info.major==3:
        basenames=[os.path.basename(file) for file in annot_rgb_files]
        base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
        zipped= zip(base_ids,basenames)
        sorted_gestures = sorted(zipped)
        sorted_gestures_final = [gest_name[1] for gest_name in sorted_gestures]    
    else:
        basenames=[os.path.basename(file) for file in annot_rgb_files]
        base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
        zipped= zip(base_ids,basenames)
        zipped.sort(key = lambda t: t[0])
        sorted_gestures_final = list(zip(*zipped)[1])
    return sorted_gestures_final

def equate_list_length(list1):
	"""
	Since lengths of recorded videos are different for different subjects, this function appends empty string after 
	video ends so that length of frames if same for all the subjects 
	"""
	max_len=max([len(l) for l in list1])
	for j in list1:
		len_j = len(j)
		if len_j != max_len:
			j+=['']*(max_len-len_j)
	return max_len,np.array(list1)


cmd_dict = json_to_dict(commands_file_path)
all_cmds = sort_filenames(cmd_dict)
cmds = deepcopy(all_cmds)
class_dict = {}
bframe = []

for cmd in all_cmds:
	folders = glob.glob(os.path.join(lex_path,cmd+'*'))
	if(len(folders)==0) : cmds.remove(cmd); continue
	class_dict[cmd] = len(folders)

expect_num_inst = max(class_dict.values())

M=expect_num_inst #number of rows to display 
N=2 #number of columns to display

des_w, des_h  = 200,150
for _ in range(M):
	temp = []
	for _ in range(N):
		temp.append(255 * np.ones((des_h, des_w, 3)))
	bframe.append(temp)

if real_time:
	from CpmClass_offline import CpmClass
	inst = CpmClass(display_flag = False, visualize_lexicon = True)

close_flag = False
cmd_idx = 0
while(True and (not close_flag)):
	cmd = cmds[cmd_idx]
	## Resetting the bframe
	for idx1 in range(len(bframe)):
		for idx2 in range(len(bframe[0])):
			bframe[idx1][idx2][:] = 255 * np.ones((des_h, des_w, 3))

	left_images_list=[]
	right_images_list=[]
	folders = glob.glob(os.path.join(lex_path,cmd+'*'))

	for folder in folders:
		left_images = glob.glob(os.path.join(folder, '*_l.jpg'))
		right_images = glob.glob(os.path.join(folder, '*_r.jpg'))
		left_images_list.append(left_images)
		right_images_list.append(right_images)

	max_len,left_images_arr=equate_list_length(left_images_list)
	_,right_images_arr=equate_list_length(right_images_list)

	for idx in range(max_len):
		left_arr,right_arr = left_images_arr[:,idx],right_images_arr[:,idx]
		img_arr = []
		img_list_l = []
		img_list_r = []
		for i,j in zip(left_arr,right_arr):
			# if string is empty, append the empty frame else append the frame extrected from CPM
			if not i:
				frame_l = 255 * np.ones((des_h, des_w, 3))
			else:
				if real_time:frame_l = inst.get_hand_skel(i)
				else: frame_l = cv2.imread(i)
			if not j:
				frame_r = 255 * np.ones((des_h, des_w, 3))
			else:
				if real_time: frame_r = inst.get_hand_skel(j)
				else: frame_r = cv2.imread(j)
			img_list_l.append(cv2.resize(frame_l,(des_w,des_h)))
			img_list_r.append(cv2.resize(frame_r,(des_w,des_h)))
		img_arr_l = np.vstack((np.array(img_list_l))) # vertically stack all the left frames
		img_arr_r = np.vstack((np.array(img_list_r))) # vertically stack all the right frames
		img_arr = np.concatenate((img_arr_l,img_arr_r),axis=1)
		cv2.putText(img_arr,cmd_dict[cmd], (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120,50,220),2,cv2.LINE_AA)
		cv2.imshow('CPM hands',np.uint8(img_arr))
		key = cv2.waitKey(int(1000/30))
		if(key in [ord('q'), 27]): 
			close_flag = True
			cv2.destroyAllWindows()
			break
		if(key in [ord('n'), ord('N')]): cmd_idx += 1; break
		if(key in [ord('p'), ord('P')]): cmd_idx -= 1; break
	if(cmd_idx<0): cmd_idx = 0
	if(cmd_idx>=len(cmds)): cmd_idx = len(cmds) - 1