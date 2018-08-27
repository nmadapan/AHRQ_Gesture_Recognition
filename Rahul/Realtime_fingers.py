"""
for real time gesture recognition this file outputs finger lengths for an image(frame)
if directory has more than one image: value error will be raised
arguments:
	img_dir:path to the directory of the image
	dom_hand:most active hand first(by default right hand comes first)
	num_fingers:number of fingers per hand(starting from thumb).
Note: num_fingers can be changed in param.json file

output:
	a list [dominant_hand_fingers,non_dominant_hand_fingers] 
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



img_path  = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo\examples\\realtime_fingers\img_fold'
print(extract_fingers_realtime(img_path,1))
