"""
This code extracts frames from gesture videos for offline training.
Inputs:
	1. read_base_path: path to directory where data extracted from xef files is located
	2. write_base_path: path to directory where frames extracted are to be kept
Outputs:
	1. for each gesture id a folder is created with same name and corresponding frames are saved in that folder 
Note: 1. The code assumes the data extracted from the xef files is stored in following order:
		read_base_path\Lexicon_name\gesture\extracted data 
	  2. each lexicon folder should contain an 'Annotation' folder which has rgb and depth gesture
	  	 annotations for each gesture 	
"""
import cv2
import numpy as np 
import os, sys, json
import glob
from utils import *

read_base_path = "H:\AHRQ\Study_IV\Data\Data"
write_base_path = "H:\AHRQ\Study_IV\Data\Data_OpnePose1"
frames_folder="Frames"
frames_dir=os.path.join(write_base_path,frames_folder)
if not os.path.isdir(frames_dir): create_writefolder_dir(frames_dir)
lexicons=glob.glob(os.path.join(read_base_path,"*"))

json_file_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
frame_gap = variables['openpose_downsample_rate']

def extract_frames(video_file,annot_file,write_folder,frame_gap):
	with open(annot_file) as f:
		frame_nums=f.readlines()
		frame_nums=[int(x.strip()) for x in frame_nums]
#following snippet shows the frames of a gesture as read from the annot file
	vidcap = cv2.VideoCapture(video_file)
	success,image=vidcap.read()

	count = 0
	success = True
	# while success:
	for j in range(0,len(frame_nums),2):
	  	while count<frame_nums[j]:
	  		success,image = vidcap.read()
	  		count+=1
	  	f_num=count
	  	while count <= frame_nums[j+1]:
	  		success,image = vidcap.read()
	  		# save first frame of the gesture
	  		if count == frame_nums[j]:
	  			cv2.imwrite(os.path.join(write_folder,'frame_'+'{0:09}'.format(count)+'.jpg'), image)

	  	#every frame_gap'th frame will be extracted from the gesture	
	  		if count == f_num+frame_gap:
	  			cv2.imwrite(os.path.join(write_folder,'frame_'+'{0:09}'.format(count)+'.jpg'), image)
	  			f_num+=frame_gap
	  		count+=1
	vidcap.release()
	cv2.destroyAllWindows()

def sort_filenames(annot_rgb_files):
	dir_name=[os.path.dirname(os.path.splitext(file)[0])for file in annot_rgb_files]
	extension=os.path.splitext(annot_rgb_files[0])[1]
	basenames=[os.path.basename(os.path.splitext(file)[0])for file in annot_rgb_files]
	base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
	zipped= zip(base_ids,basenames)
	zipped.sort(key = lambda t: t[0])
	sorted_gestures = list(zip(*zipped)[1])
	sorted_annot_file_paths=[]
	for gesture in sorted_gestures:
		sorted_annot_file_paths.append(os.path.join(dir_name[0],gesture+extension))
	return sorted_annot_file_paths

def generate_data():
	for lexicon in lexicons:
		lexicon_name=os.path.basename(lexicon)
		write_base_folder=os.path.join(frames_dir,lexicon_name)
		if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)

		#locate "Annotations" folder
		annot_folder=glob.glob(os.path.join(lexicon,"Annotations"))
		annot_rgb_files=glob.glob(os.path.join(annot_folder[0],"*rgbannot2.txt"))
		annot_rgb_files=sort_filenames(annot_rgb_files)
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
	
generate_data()