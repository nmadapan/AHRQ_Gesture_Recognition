"""
This files run OpenPoseDemo.exe; so this file should be kept at -
'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo\'
"""


import numpy as np 
import os, sys, shutil
import glob

base_path = "F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data_OpenPose"
frames_folder="Frames"
xml_folder='xml_files'

frames_path=os.path.join(base_path,frames_folder)
xml_fold_path=os.path.join(base_path,xml_folder)

exe_addr = '.\\bin\\OpenPoseDemo.exe'

def create_writefolder_dir(create_dir):
	try:
		os.mkdir(create_dir)
	except WindowsError:
	    create_writefolder_dir()

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

		os.system(system_str)
