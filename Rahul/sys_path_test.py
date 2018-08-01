import sys,os
import time
# print sys.path[0]
open_pose_basepath='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\bin'
sys.path.insert(0,open_pose_basepath)
open_pose_basepath='F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\src'
sys.path.insert(0,open_pose_basepath)
# print sys.path[0]

while(True):
	# os.chdir(open_pose_basepath)
	os.system('python ' +'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\' + 'syspath_openpose.py')
	# os.chdir(cwd)
	time.sleep(2)
	sys.exit(0)

