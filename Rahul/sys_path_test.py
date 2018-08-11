import sys,os
import time
# print sys.path[0]
# open_pose_basepath='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\bin'
# sys.path.insert(0,open_pose_basepath)
# open_pose_basepath='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\src'
# sys.path.insert(0,open_pose_basepath)
# # print sys.path[0]

# while(True):
# 	# os.chdir(open_pose_basepath)
# 	os.system('python ' +'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\' + 'syspath_openpose.py')
# 	# os.chdir(cwd)
# 	time.sleep(2)
# 	sys.exit(0)

open_pose_basepath='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\bin'
sys.path.insert(0,open_pose_basepath)
python_file_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
sys.path.insert(0,python_file_path)

img_dir='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\examples\\calibrate_img\\img_dir'
xml_dir='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\examples\\calibrate_img\\xml_dir'

from calibrate_fingers import *

f_lengths = extract_fingers_from_video(vid_path,img_dir,xml_dir)
