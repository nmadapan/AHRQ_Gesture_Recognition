import os,sys,glob,re,cv2,json,time
import numpy as np
from utils import *
openpose_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
sys.path.insert(0,openpose_path)
os.chdir(openpose_path)
from run_openpose import run_OpenPose

img_dir  = 'R:\openpose\images'
base_path="R:\openpose"
#creates the directory for xml_files outputted by OpenPose
num_images=len(os.listdir(img_dir))
print 'number of images are',num_images
start_time=time.time()

xml_dir=os.path.join(base_path,'xml_fold')
if not os.path.isdir(xml_dir):
	create_writefolder_dir(xml_dir)
#remove files(if any) present in the xml_dir
exist_files=glob.glob(os.path.join(xml_dir,"*"))

for file in exist_files:
	os.unlink(file)

print 'writing xml_files in',xml_dir
system_str = exe_addr + ' --image_dir '+ img_dir + ' --write_keypoint_format ' + 'xml ' + \
					 ' --write_keypoint ' + xml_dir +' --hand ' + '--keypoint_scale '+'4 '+'--no_display'
run_OpenPose(system_str)
print 'time taken by openpose',time.time()-start_time
print 'Average time per image',(time.time()-start_time)/num_images
# import time
# start_time=time.time()
# print 'starting time',start_time
# img_path  = 'R:\openpose\images'
# print extract_fingers_realtime(img_path,1)
# print 'Time taken by openpose',time.time()-start_time