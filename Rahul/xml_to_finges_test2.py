#for each gesture- read start and end from annot file - 
#use the keypoints of same frame till the availability of next frame
#convert the raw coordinates to the finger lengths
#use keypoints of the closest person
#left - right first
# 1 text file with same name as folder
# 0s when frame is not in gesture
# frames till the last frame in rgbannot2 file

import xml.etree.ElementTree as ET

import numpy as np
import os, time, glob, pickle, re, copy, sys
from OpenPose_Data_generate import frame_gap

# # pose_key_points=[0,1,2,3,4,5,6,7,8,11]
hands_key_points=[2,4,5,8,9,12,13,16,17,20]

def fingers_length(key_points):
    fingers_len=[]
    for i in range(0,len(key_points),4):
        finger_len=np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)
        fingers_len.append(finger_len)
    return np.round(fingers_len,4)

def conv_xml(file_path):
    tree = ET.parse(file_path)
    root=tree.getroot()
    vals=root[0][2].text  # this refers to the data we need
    vals = vals.strip().replace('\n','') # Removing the ending white spaces and new lines
    vals = re.sub(' +', ' ', vals).split(' ') # Removing the intermediate excess white spaces
    vals = map(float, vals) # Convert strings to floats
    x = vals[0::3]
    y = vals[1::3]

    xy=[]

    for i in hands_key_points:
        xy.append(np.round(x[i],4))
        xy.append(np.round(y[i],4))
       
    return fingers_length(xy)

def create_writefolder_dir(create_dir):
    try:
        os.mkdir(create_dir)
    except WindowsError:
        create_writefolder_dir()

read_base_path = "F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data"
write_base_path = "F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data_OpenPose"
xml_folder = "xml_files"
fingers_folder='fingers_data'

fingers_dir=os.path.join(write_base_path,fingers_folder)

lexicons=glob.glob(os.path.join(read_base_path,"*"))
xml_path = os.path.join(write_base_path,xml_folder)

# base_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Rahul\\finger_extract\\fingers_xml'
# xml_fold='10_0_S1_L2_Layout_X'

# xml_path = os.path.join(base_path,xml_folder)

# annot_rgb_file = glob.glob(os.path.join(base_path,'*rgbannot2*'))[0]

def create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,gest_xml_folder,method='copy'):
    with open(annot_rgb_file, 'r') as f:
        frame_nums=f.readlines()
        frame_nums=[int(x.strip()) for x in frame_nums] 

    left_files=glob.glob(os.path.join(gest_xml_folder,'*left*'))
    right_files=glob.glob(os.path.join(gest_xml_folder,'*right*'))

    count=0
    file_counter=0
    gesture_full_fingers = []

    #try string.split for extracting numbers
    file_last_frame=int(os.path.splitext(left_files[len(left_files)-1])[0][-18:-10])

    frame_counter = 1
    # def first_interpolate():
    for left_file,right_file in zip(left_files,right_files):

        current_frame_number=int(os.path.splitext(left_file)[0][-18:-10])
        if current_frame_number==frame_nums[frame_counter-2]:
            gesture_full_fingers.append(conv_xml(left_file).tolist() +
                conv_xml(right_file).tolist())
            continue

        # print frame_nums[frame_counter],current_frame_number 
        if frame_nums[frame_counter]-current_frame_number > frame_gap:
            for i in range(frame_gap):
                gesture_full_fingers.append(conv_xml(left_file).tolist() +
                        conv_xml(right_file).tolist())

        elif frame_nums[frame_counter]-current_frame_number > 0 and frame_nums[frame_counter]-current_frame_number<frame_gap:
            for i in range((frame_nums[frame_counter]-current_frame_number)+1):
                gesture_full_fingers.append(conv_xml(left_file).tolist() +
                        conv_xml(right_file).tolist())
            frame_counter+=2

        else:
            for i in range((frame_nums[frame_counter]-current_frame_number)):
                gesture_full_fingers.append(conv_xml(left_file).tolist() +
                        conv_xml(right_file).tolist())
            frame_counter+=2

        # return gesture_full_fingers
        

    # gesture_full_fingers=first_interpolate()
    # print len(gesture_full_fingers)

    #rgb to skel mapping must be done on gesture basis
    #rgb -> gest_start and end and correpsonding time stamps
    #skel -> gest_start and end and correpsonding time stamps
    # prduce mapping
    # from gest_full_fingers extract frames equal to gest length
    # update the gesture based on mapping

    fingers_frames=copy.copy(gesture_full_fingers)
    fingers_final_data=[]
    with open(annot_rgb_file, 'r') as f:
        skel_frame_nums=f.readlines()
        skel_frame_nums=[int(x.strip()) for x in skel_frame_nums]


    with open(rgb_ts_file, 'r') as f:
        rgb_ts=f.readlines()
        rgb_ts=[float(x.strip()) for x in rgb_ts]

    with open(skel_ts_file, 'r') as f:
        skel_ts=f.readlines()
        skel_ts=[float(x.strip()) for x in skel_ts]

    last_skel_frame=0
    frames_data=[]

    for i in range(0,len(frame_nums),2):
        rgb_gest_start=frame_nums[i]
        rgb_gest_end=frame_nums[i+1]
        skel_gest_start=skel_frame_nums[i]
        skel_gest_end=skel_frame_nums[i+1]
        gest_rgb_ts = rgb_ts[rgb_gest_start:rgb_gest_end+1]
         # +1 for including the last frame
         #  gesture from 12-14; 14 won't be include if we don't add 1 at the end 
        gest_skel_ts = skel_ts[skel_gest_start:skel_gest_end+1]

        r_ts=np.array(gest_rgb_ts)
        s_ts=np.array(gest_skel_ts)

        mat = np.abs(r_ts.reshape(-1,1)-s_ts)
        r_to_s = np.argmin(mat, axis=1)
        s_to_r = np.argmin(mat, axis=0)

        # print s_to_r
    # #  iterate over previous fingers_data
    # # create a new object and and add the length of tha
    # #  add last_skel_frame to r_to_s and iterate

        frames_data=[]
        for i in range(len(s_to_r)):
            frames_data.append(fingers_frames[s_to_r[i]])
         
        del(fingers_frames[0:len(r_to_s)])    
        fingers_final_data.append(np.array(frames_data).flatten())
    return  fingers_final_data  

for lexicon in lexicons:
    method='copy'
    lexicon_name=os.path.basename(lexicon)
    xml_lexicon_folder=os.path.join(xml_path,lexicon_name)
    write_base_folder=os.path.join(fingers_dir,lexicon_name)
    if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)

    xml_folders=glob.glob(os.path.join(xml_lexicon_folder,"*"))
    annot_folder = glob.glob(os.path.join(lexicon,"Annotations"))
    annot_rgb_files = glob.glob(os.path.join(annot_folder[0],"*_rgbannot2.txt"))
    annot_skel_files = glob.glob(os.path.join(annot_folder[0],"*_annot2.txt"))
    rgb_ts_files = glob.glob(os.path.join(lexicon,"*_rgbts.txt"))
    skel_ts_files = glob.glob(os.path.join(lexicon,"*_skelts.txt"))


    # gestures = [os.path.basename(file)[:-14] for file in annot_rgb_files]
    if len(annot_rgb_files)!=len(annot_skel_files):
        sys.exit('#annot_rgb_files not equal to #annot_skel_files') 
    
    annot_rgb_seq = [os.path.basename(os.path.splitext(gest_name)[0]).split('_') for gest_name in annot_rgb_files]
    annot_skel_seq = [os.path.basename(os.path.splitext(gest_name)[0]).split('_') for gest_name in annot_skel_files]
    s='_'
    annot_rgb_seqq=[s.join(seq[:-1]) for seq in annot_rgb_seq]
    annot_skel_seqq = [s.join(seq[:-1]) for seq in annot_skel_seq]
    gestures=annot_rgb_seqq
    #check on the sequence of the rgb and skel sequence
    if annot_rgb_seqq != annot_skel_seqq: sys.exit('sequence of rgb and skeleton files do not match in'+lexicon)
    # if we can make full check early on we can avodi the comaparison
    with open(os.path.join(write_base_folder,lexicon_name+"_"+method+'.pkl'),'wb') as pkl_file:
        gest_dict = {}

        for gesture in gestures:
            annot_rgb_file = [file for file in annot_rgb_files if gesture in file][0]
            annot_skel_file = [file for file in annot_skel_files if gesture in file][0]
            rgb_ts_file = [file for file in rgb_ts_files if gesture in file][0]
            skel_ts_file = [file for file in skel_ts_files if gesture in file][0]
            xml_folder = [folder for folder in xml_folders if gesture in folder][0]


            data_to_write = create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,
                gest_xml_folder=xml_folder,method='copy')
            # print data_to_write.shape
            data_to_write_list=[]
            for line in data_to_write:
                data_to_write_list.append(line.tolist())
            gest_dict[gesture] = data_to_write_list
        pickle.dump(gest_dict,pkl_file)
