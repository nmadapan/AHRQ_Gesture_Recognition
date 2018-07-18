import cv2
import numpy as np 
import os, sys
import glob

#enter the frame gap after first frame you want to save
frame_gap=7

read_base_path = "F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data"
write_base_path = "F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data_OpenPose"
frames_folder="Frames"
xml_folder = "xml_files"
frames_dir=os.path.join(write_base_path,frames_folder)

lexicons=glob.glob(os.path.join(read_base_path,"*"))

def create_writefolder_dir(create_dir):
	try:
		os.mkdir(create_dir)
	except WindowsError:
	    create_writefolder_dir()

def extract_frames(video_file,annot_file,write_folder,frame_gap):
	with open(annot_file) as f:
		frame_nums=f.readlines()
		frame_nums=[int(x.strip()) for x in frame_nums]


#following snippet shows the frames of a gesture as read from the annot file
	vidcap = cv2.VideoCapture(video_file)
	success,image=vidcap.read()
	
		# print frame_nums[j],frame_nums[j+1]
	count = 0
	success = True
	# while success:
	for j in range(0,len(frame_nums),2):
	  	while count<frame_nums[j]:
	  		success,image = vidcap.read()
	  		count+=1
	  	# print 'frame number at gesture start', count
	  	f_num=count
	  	while count <= frame_nums[j+1]:
	  		success,image = vidcap.read()
	  		# save first frame of the gesture
	  		if count == frame_nums[j]:
	  			cv2.imwrite(os.path.join(write_folder,'frame_'+'{0:08}'.format(count)+'.jpg'), image)
	  		count+=1

	  	#every frame_gap'th frame will be extracted from the gesture	
	  		if count == f_num+frame_gap:
	  			cv2.imwrite(os.path.join(write_folder,'frame_'+'{0:08}'.format(count)+'.jpg'), image)
	  			f_num+=frame_gap
	  	# print 'frame number at gesture end', count		

	vidcap.release()
	cv2.destroyAllWindows()



#frames extraction
for lexicon in lexicons:
	lexicon_name=os.path.basename(lexicon)
	write_base_folder=os.path.join(frames_dir,lexicon_name)
	if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)

	#locate "Annotations" folder
	annot_folder=glob.glob(os.path.join(lexicon,"Annotations"))
	annot_rgb_files=glob.glob(os.path.join(annot_folder[0],"*rgbannot2.txt"))
	gestures=[os.path.basename(file)[:-14] for file in annot_rgb_files]

	rgb_videos=glob.glob(os.path.join(lexicon,"*rgb.avi"))
	#create folders with gesture names
	# match video with the annotation folder
	for gesture in gestures:
		gesture_folder=os.path.join(write_base_folder,gesture)
		if not os.path.isdir(gesture_folder): create_writefolder_dir(gesture_folder)
		gesture_video=[video for video in rgb_videos if gesture in video][0]
		gesture_annot_file=[file for file in annot_rgb_files if gesture in file][0]
		print 'writing in folder:',gesture_folder
		extract_frames(gesture_video,gesture_annot_file,gesture_folder,frame_gap)
	
