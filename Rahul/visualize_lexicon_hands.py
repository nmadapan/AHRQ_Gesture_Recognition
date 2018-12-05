import numpy as np
import os, time, glob, pickle, re, copy, sys, json
from scipy.interpolate import interp1d
import cv2
from copy import deepcopy
import glob 

# if this file is in some other location than "convolutional-pose-machines-tensorflow-master", then 
# uncomment the following line and use the path to the CPM folder
# sys.path.insert(0, r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master')
# from CpmClass_offline import CpmClass

utils_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Rahul'
sys.path.insert(0,utils_file_path)
from utils import *

lex_path = r"H:\AHRQ\Study_IV\Data\Data_cpm_new\Frames\L2"

commands_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\commands.json'

default_width, default_height = 1920, 1080


# inst= CpmClass(display_flag = False,visualize_lexicon = True)
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
	max_len=max([len(l) for l in list1])
	for j in list1:
		len_j = len(j)
		if len_j != max_len:
			j+=['']*(max_len-len_j)
	return max_len,np.array(list1)

# 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen'
# sys.path.insert(0,commands_file_path)

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
print 'Max no. of instances : ' + str(expect_num_inst)
print 'Min no. of instances : ' + str(min(class_dict.values()))

# if(expect_num_inst <= 6): M = 2
# else: M = 3

# if(expect_num_inst%2 == 1):	N = 1 + expect_num_inst/M
# else: N = expect_num_inst/M
M=6
N=2

des_w, des_h = default_width/(N+2), default_height/(M/2)

# for _ in range(M):
# 	temp = []
# 	for _ in range(N):
# 		temp.append(255 * np.ones((des_h, des_w, 3)))
# 	bframe.append(temp)
for _ in range(M):
	temp = []
	for _ in range(N):
		temp.append(255 * np.ones((des_h, des_w, 3)))
	bframe.append(temp)

close_flag = False
cmd_idx = 0
# while(True):
cmd = cmds[cmd_idx]

## Resetting the bframe
for idx1 in range(len(bframe)):
	for idx2 in range(len(bframe[0])):
		bframe[idx1][idx2][:] = 255 * np.ones((des_h, des_w, 3))

# if(close_flag):
# 	break
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
	img_list_l = []
	img_list_r = []
	coord_l=[]
	coord_r=[]
	color_l = []
	color_r = []
	for i,j in zip(left_arr,right_arr):
		cpm_img_l,coord1_l,coord2_l,c_l = inst.get_image(i)
		cpm_img_r,coord1_r,coord2_r,c_r = inst.get_image(j)
		img_list_l.append(cpm_img_l)
		img_list_r.append(cpm_img_r)
		coord_l.append(cpm_img_l)
		coord_r.append(cpm_img_r)
		color_l.append(c_l)
		color_l.append(c_r)
	image1_l = cpm_img_l[0]
	image1_r = cpm_img_r[0]
	