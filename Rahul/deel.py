import os,sys

# openpose_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo'
# sys.path.insert(0,openpose_path)
# os.chdir(openpose_path)

#uncomment below three lines for extracting real time fingers' lengths from a frame/image
# from Realtime_fingers import extract_fingers_realtime
# img_path  = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo\examples\\realtime_fingers\img_fold'
# print(extract_fingers_realtime(img_path,0))

# from opnepose_realtime_routines import *
# video_path = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Data\Calib_Data\S1_Pose1_rgb.avi'
# fingers_len=calib_fingers(video_path)
# print fingers_len
from opnepose_realtime_routines import *
img_dir = 'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\openpose\Open_Pose_Demo\examples\\realtime_fingers\img_fold'
fingers_len=extract_fingers_realtime(img_dir)
print fingers_len