"""this code is for offline finger calibration. 
	function calib_fingers takes the path to the directory of calibration data(calibration videos).
	Firstly, it extracts frames from video and saves in img_dir. Then OpenPose is used to extract
	xml files(and save in xml_dir) from the frames in img_dir. Then all the xml files of 1 hand(left or right)
	are used to extract finger lengths for every frame. Mean of finger lengths is returned.
	Also this function uses the pose_calib_data function for calibrating pose data
	Arguments:
			Calib_data_path: path to directory where data for calibration is located
	Output:
			dictionary{subject_pose:Data for pose calibration;
						subject_fingers:Data for fingers calibration}

	Notes
	 1: For online training, where calibration data for only 1 user is required at a time, kindly use
		  the function 'calib_fingers' from opnepose_realtime_routines.py file located in the same directory.
		  Don't forget to read the notes at the beginning of the file openpose_realtime_routines.py	
	 2: Make sure calibration data is stored in following ways:
	 	  rgb_videos - "...Pose1_rgb.avi"
		  skel_files - "...Pose1_skel.txt"
"""

import os,sys,glob,re,cv2,json
import numpy as np
import xml.etree.ElementTree as ET 
calib_routine_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\\Naveen'
sys.path.insert(0,calib_routine_path)
from calib_routine import *
from utils import *
openpose_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
sys.path.insert(0,openpose_path)
os.chdir(openpose_path)
from run_openpose import run_OpenPose

#path to directory where calib_data is located
calib_data_path = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Data\Calib_Data'

def calib_fingers(calib_data_path):
	# calib_data_path = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Data\Calib_Data'
	videos_path=glob.glob(os.path.join(calib_data_path,"*Pose1_rgb.avi"))
	skel_paths=glob.glob(os.path.join(calib_data_path,"*Pose1_skel.txt"))

	#base_path to save images and xml directories
	base_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\examples\\calibrate_fingers'

	img_dir=os.path.join(base_path,'img_dir')
	if not os.path.isdir(img_dir):
		create_writefolder_dir(img_dir)
	xml_dir=os.path.join(base_path,'xml_dir')
	if not os.path.isdir(xml_dir):
		create_writefolder_dir(xml_dir)

	def extract_fingers(img_dir):
		exist_files=glob.glob(os.path.join(xml_dir,"*"))
		for file in exist_files:
			os.unlink(file)

		print 'writing xml_files in',xml_dir
		system_str = exe_addr + ' --image_dir '+ img_dir + ' --write_keypoint_format ' + 'xml ' + \
							 ' --write_keypoint ' + xml_dir + ' --hand ' + '--keypoint_scale '+'4 '+'--no_display'
		run_OpenPose(system_str)
		left_files=glob.glob(os.path.join(xml_dir,'*_left*'))
		if len(left_files)==1:
			fingers_length=conv_xml(left_files[0])
		else:
			fingers=[]
			for file in left_files:
				fingers.append(conv_xml(file).tolist())
		fingers_length=np.mean(fingers, axis=0)
		return np.round(fingers_length,4).tolist()


	def extract_fingers_from_video(vid_path,img_dir,xml_dir):
		exist_files=glob.glob(os.path.join(img_dir,"*"))
		for file in exist_files:
			os.unlink(file)
		vidcap = cv2.VideoCapture(vid_path)
		success,image = vidcap.read()
		count = 0
		print 'writing images in',img_dir
		while success:   
		  cv2.imwrite(os.path.join(img_dir,'frame_'+'{0:09}'.format(count)+'.jpg'), image)
		  success,image = vidcap.read()
		  count += 1 
		return extract_fingers(img_dir)

	calib_dict={}
	for skel_path,vid_path in zip(skel_paths,videos_path):
		pose_data=pose_calib_data(skel_path)
		f_length=extract_fingers_from_video(vid_path,img_dir,xml_dir) 
		subject_id=os.path.basename(os.path.splitext(vid_path)[0]).split('_')[0]
		calib_dict[subject_id+'_pose'] = pose_data
		calib_dict[subject_id+'_fingers'] = f_length

	return calib_dict

# write_json_file='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Naveen\\calib_data.json'
#calib_dict=calib_fingers(calib_data_path)
# with open(write_json_file,'w') as fp:
# 	json.dump(calib_dict,fp,indent=2)
print(calib_fingers(calib_data_path))
