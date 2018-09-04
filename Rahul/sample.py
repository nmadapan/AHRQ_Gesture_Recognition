from opnepose_realtime_routines import extract_fingers_realtime
import os, time
print os.getcwd()

fing_rt = extract_fingers_realtime

img_dir = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\temp_dir'

st = time.time()
fing_rt(img_dir,dom_hand=1,num_fingers=10)
st2 = time.time()
print st2 - st