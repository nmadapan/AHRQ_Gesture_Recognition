"""
This file intends to find the subject wise normalization constant for fingers. Since this file access CPM, it must be run in python 3 with tensorflow GPU installation.

inputs_required:
            -base_path - path to the lexicon directory containing extracted frames from videos.
            - seq_start - starting number of the frames (by default 200) 
            - seq_end - starting number of the frames (by default 500)
            for each subject 300 frames are being used for calculating the fingers' lengths

output: dictionary with subject id as key and middle finger length as value
e.g.
{
    'S1':169,
    'S2':132,
    ...
}
"""             

import numpy as np
import os,sys,glob
from CpmClass_offline import CpmClass

base_path = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\Frames\L2'

seq_start = 200
seq_end = 500


# for each lexicon, gesture id is selected with max visibility of hand
lex_gest_dict = {'L2':'2_1',
 'L3':'4_0',
 'L6':'6_3',
 'L8':'6_4'
}
hand_base_key_points= [0,4,8,12,16,20]

def fingers_length_from_base(key_points):
    '''
    Description:
        Given all the hand keypoints(of a frame) extracted from CPM, returns finger lengths. Lengths are calculated from the hand of the base
    Input Arguments:
        key_points - 1D array of hand coordiantes(21(jointss)*2(x,y)) extarcted from CPM
        norm -  L1 or L2 distance
    Return:
        1D array of signed length of fingers
    '''
    fingers_len=[]
    for x in hand_base_key_points[1:]:
        finger_len=(np.sqrt((key_points[2*x]-key_points[0])**2+(key_points[2*x+1]-key_points[1])**2))
        fingers_len.append(finger_len)
 
    return np.round(np.array(fingers_len),4)


inst = CpmClass() #instantiation of CPM class

gest_id = lex_gest_dict[os.path.basename(base_path)]
gest_folders=glob.glob(os.path.join(base_path,gest_id+'*'))


finger_lengths = {}

for fold in gest_folders:
    all_images = glob.glob(os.path.join(fold,'*_r*'))
    use_images = all_images[seq_start:seq_end]
    finger_lengths_list=[]
    for image in use_images:
        joint_coord_set = inst.get_hand_skel(image)
        key_points = np.array(joint_coord_set).flatten().tolist()
        finger_lengths_list.append(fingers_length_from_base(key_points))
    mean_lengths = np.mean(finger_lengths_list,axis = 0)
    finger_lengths[os.path.basename(fold).split("_")[2]] = int(mean_lengths[2]) # length of the middle finger

print(finger_lengths)