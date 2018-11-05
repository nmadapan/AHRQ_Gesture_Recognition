###############################################################################
#This code extracts finger lengths from hands using Cobvolutional Pose Machines(CPM)
# this code is in Python 3(most of the python files in this repository are in python2)
# as CPM require tensorflow which runs only in python 3 

    #################################
# This file contains additional functionality for sending hands to CPM
#if wrist is below the threshold it doesn't send the frames to CPM but returns zeros
    #################################
###############################################################################
#ToCheck: framesnums sent to the cpm are matches geture annotations


import numpy as np
import os, time, glob, pickle, re, copy, sys, json
from scipy.interpolate import interp1d
import cv2

# if this file is in some other location than "convolutional-pose-machines-tensorflow-master", then 
# uncomment the following line and use the path to the CPM folder
# sys.path.insert(0, r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master')
from CpmClass_offline import CpmClass

data_basepath=r'H:\AHRQ\Study_IV\NewData' #path to data parsed from xef files
read_base_path = r"H:\AHRQ\Study_IV\Data\Data_cpm_new" # path to directory where fames extracted from the xef files are 

frames_folder = "Frames"
fingers_folder='fingers'
frames_dir=os.path.join(read_base_path,frames_folder)
fingers_dir=os.path.join(read_base_path,fingers_folder)
lexicons = glob.glob(os.path.join(data_basepath,"*"))
lexicons_names=[os.path.basename(x) for x in glob.glob(os.path.join(data_basepath,"*"))]       #[L2,L3,...]

dominant_hand = True
hand_all_coords = True # if all hand skeleton coordinates are required
num_hand_all_coords = 21 #number of hand skeleton keypoints
num_fingers_coords=10 #number of keypoints only for fingers
# hands_key_points=[3,5,6,9,10,13,14,17,18,21]  # first point starts from 1 
hands_key_points=[2,4,5,8,9,12,13,16,17,20] #referencing elements of joint coord set
skip_exisiting_fold = True
num_fingers = 5 #number of fingers per hand
frame_gap = 3
thresh_level=0.2
torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11

base_id=torso_id
inst= CpmClass(display_flag = False) #instantiating CpmClass

def fingers_length(key_points):
###############################################################################
## Returns finger lengths given the coordinates(x,y) of hand keypoints/joints
##############################################################################
    fingers_len=[]
    for i in range(0,len(key_points),4):
        finger_len=np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)
        fingers_len.append(finger_len)
    return np.round(fingers_len,4)

def create_writefolder_dir(create_dir):
#################################################
### creates the folders/directories
#################################################
    try:
        os.mkdir(create_dir)
    except WindowsError:
        create_writefolder_dir()


def sort_filenames(annot_rgb_files):
##################################################
### sorts annotation files
### works differently for python 2 and python 3
##################################################
    if sys.version_info.major==3:
        basenames=[os.path.basename(file) for file in annot_rgb_files]
        base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
        zipped= zip(base_ids,basenames)
        sorted_gestures = sorted(zipped)
        sorted_gestures_final = [gest_name[1] for gest_name in sorted_gestures]    
    else:
        basenames=[os.path.basename(file) for file in annot_rgb_files]
        base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
        zipped= zip(base_ids,basenames)
        zipped.sort(key = lambda t: t[0])
        sorted_gestures_final = list(zip(*zipped)[1])
    return sorted_gestures_final

def get_annot_files(lexicon):
    '''
        Description:
            Given the lexicon name this function returns the sorted rgb and skeleton annotation files 
        Input : 
            Lexicon ID (L2,L3...)
        Returns: 
            annot_rgb_files -  list of sorted rgb gesture annottaion files for the entire lexicon    
            annot_skel_files - list of sorted skelton annotation files for the entire lexicon             
    '''
    annot_fold_path=os.path.join(data_basepath,lexicon)
    annot_folder=os.path.join(annot_fold_path,"Annotations")
    annot_rgb_files = sort_filenames(glob.glob(os.path.join(annot_folder,"*_rgbannot2.txt")))
    annot_skel_files = sort_filenames(glob.glob(os.path.join(annot_folder,"*_annot2.txt")))
    annot_rgb_files=[os.path.join(annot_folder,file) for file in annot_rgb_files]
    annot_skel_files=[os.path.join(annot_folder,file) for file in annot_skel_files]
    return annot_rgb_files,annot_skel_files

def readlines_txt(f_name,str_to_num):
    '''
        Description: 
            for a text file returns the content of the file in list form
        Input Arguments:
            f_name - path to the file
            str_to_num - int or float
        Returns:
            f_lines - list of the contents of the file  
    '''
    with open(f_name) as f:
        f_lines=f.readlines()
        f_lines=[str_to_num(x.strip()) for x in f_lines]
    return f_lines

def match_ts(rgb_ts,skel_ts):
    '''
        Description: 
            This function maps skeleton time stamps to rgb time stamps and vice versa
        Input Arguments:
            rgb_ts - path to the file with rgb time stamps
            skel_ts - path to the file with skeleton time stamps
        Returns:
            s_to_r - mapping from skeleton time stamps to rgb time stamps 
            r_to_s - mapping from rgb time stamps to skeleton time stamps
    '''
    rgb_ts=np.array(rgb_ts)
    skel_ts=np.array(skel_ts)
    s_to_r=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=1)
    r_to_s=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=0)
    return s_to_r,r_to_s

def get_gesture_names(skel_files):
    '''
        Description: 
            This function returns gesture names from the skeleton file paths
        Input Arguments:
            skel_files: path to skeleton files e.g. 1_1_S1_L2_Scroll_Up_annot2
        Returns:
            gesture_names - gesture names associated with those files
    '''
    gesture_names=[]
    for file in skel_files:
        strings_=os.path.basename(file).split('_')
        gesture_names.append('_'.join(strings_[:-1]))
    return gesture_names


def cpm_fingers(frame):     #must return a list
    '''
        Description: 
            This function returns finger lengths using Convolutional Pose Machines(CPM)
        Input Arguments:
            frame: rgb image from which to extract finger lengths
        Returns:
            finger_lengths - finger lengths extracted from frame using CPM
    '''
    joint_coord_set = inst.get_hand_skel(frame) #(x,y) coordinates of all the 21 joints of the hand
    finger_lengths = inst.get_finger_lengths(joint_coord_set) #finger lengths from the all the hand joints
    return  finger_lengths.tolist()

def cpm_fingers_coords(frame):     #must return a list
    '''
        Description: 
            This function either returns fingers coordinates or joint coordinates of  whole hand using Convolutional Pose Machines(CPM)
        Input Arguments:
            frame: rgb image from which to extract finger lengths
            fingers: True if fingers extreme joint coordinates are required
        Returns:
            finger_coords - finger coordinates extracted from frame using CPM
                                         or
            joint_coord_set -hand joint coordinates extracted from frame using CPM
    '''
    joint_coord_set = inst.get_hand_skel(frame)
    finger_coords = inst.get_hand_keypoints(joint_coord_set)
    if not hand_all_coords:
        return  np.array(finger_coords).flatten().tolist() #list
    else:
        return  np.array(joint_coord_set).flatten().tolist()

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
num_points = variables['fixed_num_frames']


def interpn(yp, num_points=num_points, kind = 'linear'):
    # yp is a gesture instance
    # yp is 2D numpy array of size num_frames x 3 if num_joints = 1
    # No. of frames will be increased/reduced to num_points
    xp = np.linspace(0, 1, num = yp.shape[0])
    x = np.linspace(0, 1, num = num_points)
    y = np.zeros((x.size, yp.shape[1]))
    for dim in range(yp.shape[1]):
        f = interp1d(xp, yp[:, dim], kind = kind)
        y[:, dim] = f(x)
    return y


def create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,rgb_skel_file,frames_folder,\
                        num_fingers = num_fingers, dominant_hand = dominant_hand):

    '''
        Description: 
            This function uses rgb annotation file and skel annotation files to get the gesture start and end.
            Since there could be offset between rgb and skeleton gesture annotations,both have to be mapped 
            to each other.
            Then it grabs the frames,corresponding to the gesture annotations, and send them to CPM to extract the
            fingers'/whole hand joint coordinates. 
            Since CPM works with only one hand, we are segmenting bounding boxes around both the hands and sending 
            that to CPM sequentially.
            Since SVM only works for constant length features, all the gestures are interpolated/extrapolated to 
            have the same length(same number of features).
            For each gesture one column vector is outputted.   
            List of all the gestures(approixmately 20), is returned 
                        
        Input Arguments:
            annot_rgb_file: path to rgb annotation file corresponding to the gesture 
            annot_skel_file: path to skeleton annotation file corresponding to the gesture
            rgb_ts_file: path to rgb frames' time stamps file corresponding to the gesture
            skel_ts_file: path to skel frames' time stamps file corresponding to the gesture
            frames_folder: path to folder containing frames of corresponding gesture
            num_fingers: number of finger lengths(starting from thumb)
            dominant_hand: Features of dominant hand are being appended first. takes value 'left' or "right"

        Returns:
            full_gesture_data: List of lists for gestures' features.
                               Each inner list has features complete of the gestures, interpolated to the
                               fixed number of frames imported from the "params.json" file.

                
    '''


    rgb_frame_nums=readlines_txt(annot_rgb_file,int)
    skel_frame_nums=readlines_txt(annot_skel_file,int)
    rgb_ts=readlines_txt(rgb_ts_file,float)
    skel_ts=readlines_txt(skel_ts_file,float)
    #left and right are interchanged to accomodate kinect's inversion
    left_files=glob.glob(os.path.join(frames_folder,'*_r*'))
    right_files=glob.glob(os.path.join(frames_folder,'*_l*'))
    num_gestures=len(rgb_frame_nums)/2
    full_gesture_data=[]
    with open(rgb_skel_file, 'r') as fp:
        lines = fp.readlines()
        lines = [map(float, line.split(' ')) for line in lines]

    if hand_all_coords:
        num_zeros_coords=num_hand_all_coords*2
    else:
        num_zeros_coords=num_fingers_coords*2

    for i in range(0,int(len(rgb_frame_nums)),2): #loop over num_gestures times
        rgb_gest_start=rgb_frame_nums[i]
        rgb_gest_end=rgb_frame_nums[i+1]
        skel_gest_start=skel_frame_nums[i]
        skel_gest_end=skel_frame_nums[i+1]
        gest_rgb_ts = rgb_ts[rgb_gest_start:rgb_gest_end+1]
        gest_skel_ts = skel_ts[skel_gest_start:skel_gest_end+1]

        s_to_r,r_to_s = match_ts(rgb_ts[rgb_gest_start:rgb_gest_end],skel_ts[skel_gest_start:skel_gest_end])    
        gesture_left_frames=left_files[rgb_gest_start:rgb_gest_end+1]    
        gesture_right_frames=right_files[rgb_gest_start:rgb_gest_end+1]

        skel_frames_to_rgb=skel_gest_start + s_to_r #skeleton frames corresponding to rgb. Must be equal to the #rgb_frames

        # gesture_left_frames=[left_files[i] for i in np.array(r_to_s)+rgb_gest_start] #or rgb_gest_start
        # gesture_right_frames=[right_files[i] for i in np.array(r_to_s)+rgb_gest_start] #or skel_gest_start #TO VERIFY 
        # print(gesture_left_frames[0],gesture_left_frames[-1])
        gesture_left_frames=left_files[rgb_gest_start:rgb_gest_end+1]    
        gesture_right_frames=right_files[rgb_gest_start:rgb_gest_end+1]

        print('rgb gesture start:',rgb_gest_start,'rgb gesture end:',rgb_gest_end)
        print('skel gesture start:',skel_gest_start,'skel gesture end:',skel_gest_end)
        print(len(skel_frames_to_rgb)==len(gesture_left_frames))
        print(len(skel_frames_to_rgb),len(gesture_left_frames))
        print(skel_frames_to_rgb[0],skel_frames_to_rgb[-1])


        gesture_data=[]       
        num_gest_frames = len(gesture_left_frames)

    #start_y_coo is found using the first frame of the gesture        
        start_y_coo = thresh_level * (lines[skel_frames_to_rgb[0]][2*neck_id+1] - lines[skel_frames_to_rgb[0]][2*base_id+1]) 

        for j in range(0,num_gest_frames):   
        # dominant hand is assumed to be left. if not the replace dominat_hand with not dominant_hand 
            frame_l=cv2.imread(gesture_left_frames[j])
            frame_r=cv2.imread(gesture_right_frames[j])

            left_y = skel_frames_to_rgb[j][2*left_hand_id+1] - skel_frames_to_rgb[j][2*base_id+1]
            right_y = skel_frames_to_rgb[j][2*right_hand_id+1] - skel_frames_to_rgb[j][2*base_id+1]
            if left_y <= start_y_coo:
                left_fingers = np.zeros(num_zeros_coords).tolist() 
            else:    
                if frame_l is None:
                    print('this',gesture_left_frames[j],'is not processed due to 0 size')
                    left_fingers = np.zeros(num_zeros_coords).tolist()
                else:
                    left_fingers = cpm_fingers_coords(gesture_left_frames[j])

            if right_y <= start_y_coo:
                right_fingers = np.zeros(num_zeros_coords).tolist() 
            else:    
                if frame_r is None:
                    print('this',gesture_right_frames[j],'is not processed due to 0 size')
                    right_fingers = np.zeros(num_zeros_coords).tolist()
                else:
                    right_fingers = cpm_fingers_coords(gesture_right_frames[j])

            if not  dominant_hand:
                gesture_data.append(left_fingers+right_fingers)
            else:
                gesture_data.append(right_fingers+left_fingers)
                    
        gesture_data_updated=[]
        for k in range(len(r_to_s)):
        ###############################################################################################################    
        # final number of frames should be equal to the number of skeleton frames as we are meging with them
        # However it shouldn't matter much as we are interpolating the gestures to fixed number of frames
        ###############################################################################################################
            gesture_data_updated.append(gesture_data[r_to_s[k]])
        
        # if due to some error there is only one frame in a gesture, it can't be interpolated to num_frames.
        # that is being handled with try and catch
        try:
            frames_data=interpn(np.array(gesture_data_updated))
            full_gesture_data.append(np.array(frames_data).flatten().tolist())
        except:
            gest_len=rgb_gest_end-rgb_gest_start
            print('Can-not append gesture {0} with lengths {1}'.format(os.path.basename(annot_rgb_file),str(gest_len)))
    return full_gesture_data


#verify a particular gesture
# annot_rgb_file=r'H:\AHRQ\Study_IV\Flipped_Data\L2\Annotations\1_1_S6_L2_Scroll_Up_rgbannot2.txt'
# annot_skel_file=r'H:\AHRQ\Study_IV\Flipped_Data\L2\Annotations\1_1_S6_L2_Scroll_Up_annot2.txt'
# rgb_ts_file = r'H:\AHRQ\Study_IV\Flipped_Data\L2\1_1_S6_L2_Scroll_Up_rgbts.txt'
# skel_ts_file = r'H:\AHRQ\Study_IV\Flipped_Data\L2\1_1_S6_L2_Scroll_Up_skelts.txt'
# rgb_skel_file = r'H:\AHRQ\Study_IV\Flipped_Data\L2\1_1_S6_L2_Scroll_Up_color.txt'
# frames_folder=r'H:\AHRQ\Study_IV\Data\Data_cpm\Frames\L2\1_1_S6_L2_Scroll_Up'
# print('extracting fingerlengths from gesture', frames_folder)
# data=create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,skel_file,
#                     frames_folder=frames_folder)
# print(data)
# sys.exit(0)


##########################################################
# code for accessing files and folders and 
# send it to create_fingers_data
##########################################################


for lexicon in lexicons[2:4]:
    lexicon_name=os.path.basename(lexicon)
    print(lexicon_name)
    frames_lexicon_folder=os.path.join(frames_dir,lexicon_name)
    write_base_folder=os.path.join(fingers_dir,lexicon_name)
    if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)
    frames_folders=glob.glob(os.path.join(frames_lexicon_folder,"*"))
    annot_rgb_files,annot_skel_files=get_annot_files(lexicon_name) 
    rgb_ts_files = glob.glob(os.path.join(lexicon,"*_rgbts.txt"))
    skel_ts_files =glob.glob(os.path.join(lexicon,"*_skelts.txt"))
    rgb_skel_files =glob.glob(os.path.join(lexicon,"*_color.txt"))
    gestures=get_gesture_names(annot_rgb_files) 
    gest_dict = {}
    for gesture in gestures:
        print('extracting fingerlengths from gesture', gesture)
        annot_rgb_file = [file for file in annot_rgb_files if gesture in file][0]
        annot_skel_file = [file for file in annot_skel_files if gesture in file][0]
        rgb_ts_file = [file for file in rgb_ts_files if gesture in file][0]
        skel_ts_file = [file for file in skel_ts_files if gesture in file][0]
        rgb_skel_file = [file for file in rgb_skel_files if gesture in file][0]
        frames_folder = [folder for folder in frames_folders if gesture in folder][0]
        start=time.time()
        data_to_write = create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,rgb_skel_file,\
                frames_folder=frames_folder)
        print('Time taken',time.time()-start)
        data_to_write_list=[]
        for line in data_to_write:
            data_to_write_list.append(line)
        gest_dict[gesture] = data_to_write_list
    with open(os.path.join(write_base_folder,lexicon_name+'_fingers_coords.pkl'),'wb') as pkl_file:
        pickle.dump(gest_dict,pkl_file,protocol=2)
