import numpy as np
import os, time, glob, pickle, re, copy, sys, json


annot_files_basepath=r'H:\AHRQ\Study_IV\Flipped_Data'
read_base_path = r"H:\AHRQ\Study_IV\Data\Data_cpm"
# write_base_path = "H:\\AHRQ\\Study_IV\\Data\\Data_OpenPose"
frames_folder = "Frames"
fingers_folder='fingers'
frames_dir=os.path.join(read_base_path,frames_folder)
fingers_dir=os.path.join(read_base_path,fingers_folder)
lexicons=[os.path.basename(x) for x in glob.glob(os.path.join(frames_dir,"*"))]		#[L2,L3,...]


hands_key_points=[3,5,6,9,10,13,14,17,18,21]  # first point starts from 1 
skip_exisiting_fold = True
# method='copy'
num_fingers = 5 #number of fingers per hand

def fingers_length(key_points):
    fingers_len=[]
    for i in range(0,len(key_points),4):
        finger_len=np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)
        fingers_len.append(finger_len)
    return np.round(fingers_len,4)

def create_writefolder_dir(create_dir):
    try:
        os.mkdir(create_dir)
    except WindowsError:
        create_writefolder_dir()

def sort_filenames(annot_rgb_files):
    basenames=[os.path.basename(file) for file in annot_rgb_files]
    base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
    zipped= zip(base_ids,basenames)
    zipped.sort(key = lambda t: t[0])
    sorted_gestures = list(zip(*zipped)[1])
    return sorted_gestures

def get_annot_rgb(lexicon):
	#return sorted filenames with extension(not the complete path)
	annot_fold_path=os.path.join(annot_files_basepath,lexicon)
	annot_folder=os.path.join(annot_fold_path,"Annotations")
	annot_rgb_files = sorted(glob.glob(os.path.join(annot_folder,"*_rgbannot2.txt")))
	annot_skel_files = sorted(glob.glob(os.path.join(annot_folder,"*_annot2.txt")))
	annot_rgb_files=[os.path.join(annot_folder,file) for file in annot_rgb_files]
	annot_skel_files=[os.path.join(annot_folder,file) for file in annot_skel_files]
	return sort_filenames(annot_rgb_files),sort_filenames(annot_skel_files)

print(get_annot_rgb('L2'))