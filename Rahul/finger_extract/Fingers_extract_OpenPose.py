import cv2
import numpy as np 
import os
import glob

base_path='F:\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Rahul\\finger_extract'

annot_files=glob.glob(os.path.join(base_path,'*.txt'))
video_files=glob.glob(os.path.join(base_path,'*.avi'))

# reading the frame numbers from .txt file
for i in range(len(annot_files)):
	with open(annot_files[i]) as f:
		frame_nums=f.readlines()
		frame_nums=[int(x.strip()) for x in frame_nums]

#extracting the frames in a gesture from the rgb video
#below snippet is for showing every 10th frame 
	# vidcap = cv2.VideoCapture(video_files[i])
	# success,image=vidcap.read()
	# count = 0
	# success = True
	# while success:
	#   # cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
	#   success,image = vidcap.read()
	#   if count%10 == 0:
	# 	 cv2.imshow('frame' ,image)
	# 	 print(count)
	# 	 if cv2.waitKey(1) & 0xFF == ord('q'):
	# 		break
	#   count += 1

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
	  	while count <= frame_nums[j+1]:
	  		success,image = vidcap.read()
			cv2.imshow('frame' ,image)
		 	count += 1
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		print 'later count is', count
	  		# count += 1


vidcap.release()
cv2.destroyAllWindows()
