"""
Notes rgb video from kinect inverts person's hands.
Hands are inverted in this code to match kinect's nomenclature

fingers-Sequence = [Thumb, Index Finger, Middle Finger, Ring Finger, Baby Finger]

#dominant_type is extracted from the pickle files saved by run_svm, make sure pickle files exist before
running this code
"""
import xml.etree.ElementTree as ET
import numpy as np
import os, time, glob, pickle, re, copy, sys, json
from scipy.interpolate import interp1d
#copy or interpolate missing frames#
hands_key_points=[2,4,5,8,9,12,13,16,17,20]
skip_exisiting_fold = True
method='copy'
num_fingers = 5 #number of fingers per hand

if num_fingers > 5 or num_fingers <0:
    raise ValueError('num_fingers can not be greater than 5')

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

json_file_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
frame_gap = variables['openpose_downsample_rate']
num_points = variables['fixed_num_frames']
dominant_hand = variables['dominant_first']

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

def sort_filenames(annot_rgb_files):
    basenames=annot_rgb_files
    base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
    zipped= zip(base_ids,basenames)
    zipped.sort(key = lambda t: t[0])
    sorted_gestures = list(zip(*zipped)[1])

    return sorted_gestures

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

json_file_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
frame_gap = variables['openpose_downsample_rate']
num_points = variables['fixed_num_frames']
dominant_hand = variables['dominant_first']

read_base_path = "H:\\AHRQ\\Study_IV\\Data\\Data"
write_base_path = "H:\\AHRQ\\Study_IV\\Data\\Data_OpenPose"
xml_folder = "xml_files"
fingers_folder='fingers_data'
fingers_dir=os.path.join(write_base_path,fingers_folder)
xml_path = os.path.join(write_base_path,xml_folder)
lexicons=glob.glob(os.path.join(read_base_path,"*"))

def create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,gest_xml_folder,method='copy',\
                        num_fingers = num_fingers, dominant_hand = dominant_hand):
    with open(annot_rgb_file, 'r') as f:
        frame_nums=f.readlines()
        frame_nums=[int(x.strip()) for x in frame_nums] 
    #left and right are interchanged to accomodate kinect's inversion    
    left_files=glob.glob(os.path.join(gest_xml_folder,'*right*'))
    right_files=glob.glob(os.path.join(gest_xml_folder,'*left*'))

    count=0
    file_counter=0
    gesture_full_fingers = []

    file_last_frame=int(os.path.basename(left_files[len(left_files)-1]).split('_')[1])

    frame_counter = 1

    for left_file,right_file in zip(left_files,right_files):
        # current_frame_number=int(os.path.splitext(left_file)[0][-20:-11])
        current_frame_number=int(os.path.basename(left_file).split('_')[1])
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
        ####equate_dim code goes here####
        # print np.array(frames_data).shape
        frames_data=interpn(np.array(frames_data))
        # print np.array(frames_data).shape
        # sys.exit(0)

        fingers_final_data.append(np.array(frames_data).flatten())
    return fingers_final_data  

for lexicon in lexicons[-1:]:
    lexicon_name=os.path.basename(lexicon)
    xml_lexicon_folder=os.path.join(xml_path,lexicon_name)
    # print xml_lexicon_folder,len(os.listdir(xml_lexicon_folder))
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
    gestures=sort_filenames(gestures)
    print gestures
    sys.exit(0)
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
                gest_xml_folder=xml_folder,method=method)

            data_to_write_list=[]
            for line in data_to_write:
                data_to_write_list.append(line.tolist())
            gest_dict[gesture] = data_to_write_list
        pickle.dump(gest_dict,pkl_file)
        break
