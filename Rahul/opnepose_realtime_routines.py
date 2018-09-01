"""
Since the functions in this file runs openpose, if these functions are required to be run from
a directory other than Open_Pose_Demo, kindly use following lines in the python files in other
directories

openpose_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
sys.path.insert(0,openpose_path)
os.chdir(openpose_path)

Following functions are implemented:
	1. extract_fingers_realtime(img_directory,dominant_hand,num_fingers)
		-extract fingers from a frame/image
	2. calib_fingers(video_path):
		- finger calibration from a video
"""
import os,sys,glob,re,cv2,json
import numpy as np
from utils import *

openpose_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
sys.path.insert(0,openpose_path)
os.chdir(openpose_path)
from run_openpose import run_OpenPose

json_file_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
num_fingers = variables['num_fingers']

def extract_fingers_realtime(img_dir,dom_hand=1,num_fingers=num_fingers):

	"""
	for real time gesture recognition this file outputs finger lengths for an image(frame)
	if directory has more than one image: value error will be raised
	arguments:
		img_dir:path to the directory of the image(direct path to image doesn't work)
		dom_hand:most active hand first(by default right hand comes first)
		num_fingers:number of fingers per hand(starting from thumb)
			extracted from param.json file
	output:
		a list [dominant_hand_fingers,non_dominant_hand_fingers] 
	"""
	base_path="F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\examples\\realtime_fingers"

#creates the directory for xml_files outputted by OpenPose
	xml_dir=os.path.join(base_path,'xml_fold')
	if not os.path.isdir(xml_dir):
		create_writefolder_dir(xml_dir)
#remove files(if any) present in the xml_dir
	exist_files=glob.glob(os.path.join(xml_dir,"*"))
	for file in exist_files:
		os.unlink(file)

	print 'writing xml_files in',xml_dir
	system_str = exe_addr + ' --image_dir '+ img_dir + ' --write_keypoint_format ' + 'xml ' + \
						 ' --write_keypoint ' + xml_dir + ' --hand ' + '--keypoint_scale '+'4 '+'--no_display'
	run_OpenPose(system_str)
	fingers=[]
	left_files=glob.glob(os.path.join(xml_dir,'*_right*'))
	right_files=glob.glob(os.path.join(xml_dir,'*_left*'))
	if len(left_files)==1:
		if dom_hand:
			fingers.append(conv_xml(right_files[0]).tolist()[:num_fingers])
			fingers.append(conv_xml(left_files[0]).tolist()[:num_fingers])
		else:
			fingers.append(conv_xml(left_files[0]).tolist()[:num_fingers])
			fingers.append(conv_xml(right_files[0]).tolist()[:num_fingers])
	else:
		raise ValueError('more than one image given')
	return np.array(fingers).flatten()


def calib_fingers(calib_data_path):
	"""
	This function returns the fingers' lengths for calibration.
	Firstly, it extracts frames from video and saves in img_dir. Then OpenPose is used to extraxct
	xml files(saved in xml_dir) from the frames in img_dir. Then all the frames of 1 hand(left or right)
	are used to extract finger lengths for every frame. Mean of finger lengths is returned.
	Arguments:
			Calib_data_path: video path for calibration(ending with filename.avi(or some other format)) 
	Output:
			list of five fingers lengths

	Note: for offline training, if calibration data for many users is to be extracted, kindly use
		  calibrate_fingers.py file located in the same directory				
	"""
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

	f_length=extract_fingers_from_video(calib_data_path,img_dir,xml_dir) 

	return f_length
#function check code
# calib_data_path = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Data\Calib_Data1\S1_Pose1_rgb.avi'
# print(calib_fingers(calib_data_path))
# img_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo\examples\\realtime_fingers\img_fold'
# print extract_fingers_realtime(img_path)