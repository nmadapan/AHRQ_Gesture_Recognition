"""
This code extracts xml files from images(frames) extracted from gesture videos.It is assumed that frames
are already extracted from videos before running this code. 

inputs:
	base_path: base directory where data is located.
	frames_folder: folder name where frames(or different folders for different lexicons) are located
	xml_folder: folder name where extracted xml_files are to be stored

Note
	1.: xml files will be stored in same sequences of folders as frames folders 
	2.: frames are expected to be stored in the following format
			base_path/frames_folder/lexicon_name/gesture_id
		xml files will be stored in the following format
			base_path/xml_folder/lexicon_name/gesture_id
"""


import numpy as np 
import os, sys, shutil
import glob
from utils import *

openpose_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
sys.path.insert(0,openpose_path)
os.chdir(openpose_path)
from run_openpose import run_OpenPose

base_path = "F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo\examples"
frames_folder="frames_fold"
xml_folder='xml_files_1'
frames_path=os.path.join(base_path,frames_folder)
xml_fold_path=os.path.join(base_path,xml_folder)
if not os.path.isdir(xml_fold_path): create_writefolder_dir(xml_fold_path)
lexicons=glob.glob(os.path.join(frames_path,"*"))
for lexicon in lexicons:
	lexicon_name=os.path.basename(lexicon)
	write_base_folder=os.path.join(xml_fold_path,lexicon_name)
	if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)

	gestures = glob.glob(os.path.join(lexicon,"*"))

	for gesture in gestures:
		frame_folder = os.path.join(lexicon,os.path.basename(gesture))
		write_gesture_folder=os.path.join(write_base_folder,os.path.basename(gesture))
		if not os.path.isdir(write_gesture_folder): create_writefolder_dir(write_gesture_folder)
		print 'writing xml files in: ',write_gesture_folder

# openpose accepts the path to the directory of images not the path of every image  
# keypoint_scale = 3 output between [0,1]; (0,0) upper left corner and (1,1) bottom right corner
# keypoint_scale = 4 output between [-1,1]; (-1,-1) upper left corner and (1,1) bottom right corner

		system_str = exe_addr + ' --image_dir '+ frame_folder + ' --write_keypoint_format ' + 'xml ' + \
					 ' --write_keypoint ' + write_gesture_folder + ' --hand ' + '--keypoint_scale '+'4 '+'--no_display'

		run_OpenPose(system_str)
		