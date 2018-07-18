import cv2
import numpy as np 
import os, sys
import glob

base_path = 'F:\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Rahul\\finger_extract'
open_pose_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\openpose\\Open_Pose_Demo\\bin\\OpenPoseDemo.exe'
frame_foder = 'frames'
fingers_folder='fingers'
write_frames_path=os.path.join(base_path,frames)
write_finger_path=os.path.join(base_path,write_folder)

annot_files=glob.glob(os.path.join(base_path,'*.txt'))
video_files=glob.glob(os.path.join(base_path,'*.avi'))

# reading the frame numbers from .txt file
for i in range(len(annot_files)):
	with open(annot_files[i]) as f:
		frame_nums=f.readlines()
		frame_nums=[int(x.strip()) for x in frame_nums]

#following snippet shows the frames of a gesture as read from the annot file
	vidcap = cv2.VideoCapture(video_files[i])
	success,image=vidcap.read()
	
		# print frame_nums[j],frame_nums[j+1]
	count = 0
	success = True
	# while success:
	for j in range(0,len(frame_nums),2):
	  	while count<frame_nums[j]:
	  		success,image = vidcap.read()
	  		count+=1
	  	print 'frame number at gesture start', count
	  	while count <= frame_nums[j+1]:
	  		success,image = vidcap.read()
	  		count+=1
	  	#extracts every 5th frame. Take input 'a' from user, so that 
	  	#every 'a'th frame will be extracted from the gesture	
	  		if count%5 == 0:
	  			cv2.imwrite(os.path.join(write_finger_path,str(count)+'.jpg'), image)
	  			if cv2.waitKey(1) & 0xFF == ord('q'):
					break
	  	print 'frame number at gesture end', count		

vidcap.release()
cv2.destroyAllWindows()
