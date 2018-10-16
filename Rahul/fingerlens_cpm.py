import numpy as np
import os, time, glob, pickle, re, copy, sys, json
from scipy.interpolate import interp1d
import cv2

sys.path.insert(0, r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master')
from CpmClass_offline import CpmClass

data_basepath=r'H:\AHRQ\Study_IV\Flipped_Data'
read_base_path = r"H:\AHRQ\Study_IV\Data\Data_cpm"
# write_base_path = "H:\\AHRQ\\Study_IV\\Data\\Data_OpenPose"
frames_folder = "Frames"
fingers_folder='fingers'
frames_dir=os.path.join(read_base_path,frames_folder)
fingers_dir=os.path.join(read_base_path,fingers_folder)
lexicons = glob.glob(os.path.join(data_basepath,"*"))
lexicons_names=[os.path.basename(x) for x in glob.glob(os.path.join(data_basepath,"*"))]       #[L2,L3,...]


# hands_key_points=[3,5,6,9,10,13,14,17,18,21]  # first point starts from 1 
hands_key_points=[2,4,5,8,9,12,13,16,17,20] #referencing elements of joint coord set
skip_exisiting_fold = True
# method='copy'
num_fingers = 5 #number of fingers per hand
frame_gap = 3

def fingers_length(key_points):
    #keypoints as a list of x,y coordinates of relevant fingers' joints
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

# def sort_filenames(annot_rgb_files):
#     basenames=[os.path.basename(file) for file in annot_rgb_files]
#     base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
#     zipped= zip(base_ids,basenames)
#     zipped.sort(key = lambda t: t[0])
#     sorted_gestures = list(zip(*zipped)[1])
#     return sorted_gestures

def sort_filenames(annot_rgb_files):
    basenames=[os.path.basename(file) for file in annot_rgb_files]
    base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
    zipped= zip(base_ids,basenames)
    sorted_gestures = sorted(zipped)
    sorted_gestures_final = [gest_name[1] for gest_name in sorted_gestures]
    return sorted_gestures_final

def get_annot_files(lexicon):
    #return sorted filenames with extension(not the complete path)
    annot_fold_path=os.path.join(data_basepath,lexicon)
    annot_folder=os.path.join(annot_fold_path,"Annotations")
    annot_rgb_files = sort_filenames(glob.glob(os.path.join(annot_folder,"*_rgbannot2.txt")))
    annot_skel_files = sort_filenames(glob.glob(os.path.join(annot_folder,"*_annot2.txt")))
    annot_rgb_files=[os.path.join(annot_folder,file) for file in annot_rgb_files]
    annot_skel_files=[os.path.join(annot_folder,file) for file in annot_skel_files]
    return annot_rgb_files,annot_skel_files

#take gesture start and end from the skel_file
#if number of gest_len_skel==gest_len_rgb do nothing 
# else match the timestamps from skel to rgb. Number of rgb frames should be equal to number of skel frames

# for interpolation, firstly extrac the data for all the frames in a gesture. I f interpolation is required subsample the data and
# do the interploation
 
 #TODO:Normalization


def readlines_txt(f_name,str_to_num):
    #str_to_num - int or float
    with open(f_name) as f:
        f_lines=f.readlines()
        f_lines=[str_to_num(x.strip()) for x in f_lines]
    return f_lines

def match_ts(rgb_ts,skel_ts):
    rgb_ts=np.array(rgb_ts)
    skel_ts=np.array(skel_ts)
    s_to_r=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=1)
    r_to_s=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=0)
    return s_to_r,r_to_s

def get_gesture_names(skel_files):
    gesture_names=[]
    for file in skel_files:
        strings_=os.path.basename(file).split('_')
        gesture_names.append('_'.join(strings_[:-1]))
    return gesture_names

inst= CpmClass(display_flag = False)

def cpm_fingers(frame):
    #must return a list
    joint_coord_set = inst.get_hand_skel(frame)
    # print(len(joint_coord_set))
    finger_lengths = inst.get_fing_lengths(joint_coord_set)
    return  finger_lengths.tolist()

def normalize_gesture():
    pass

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

dominant_hand = True

def create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,frames_folder,\
                        num_fingers = num_fingers, dominant_hand = dominant_hand):

    rgb_frame_nums=readlines_txt(annot_rgb_file,int)
    skel_frame_nums=readlines_txt(annot_skel_file,int)
    rgb_ts=readlines_txt(rgb_ts_file,float)
    skel_ts=readlines_txt(skel_ts_file,float)

    #left and right are interchanged to accomodate kinect's inversion
    #TODO: write a function to sort frame_nums    
    left_files=glob.glob(os.path.join(frames_folder,'*_r*'))
    right_files=glob.glob(os.path.join(frames_folder,'*_l*'))


    #match gesture wise
    # TODOextarct frames nums for gesture for both rgb and skel and use this function

    
    num_gestures=len(rgb_frame_nums)/2
    # print(num_gestures)

    full_gesture_data=[]

    for i in range(0,int(num_gestures),1): #loop over num_gestures times
        rgb_gest_start=rgb_frame_nums[i]
        rgb_gest_end=rgb_frame_nums[i+1]
        skel_gest_start=skel_frame_nums[i]
        skel_gest_end=skel_frame_nums[i+1]
        gest_rgb_ts = rgb_ts[rgb_gest_start:rgb_gest_end+1]
        gest_skel_ts = skel_ts[skel_gest_start:skel_gest_end+1]

        gesture_left_frames=left_files[rgb_gest_start:rgb_gest_end]    
        gesture_right_frames=right_files[rgb_gest_start:rgb_gest_end]
        #write a function to sort the frames
        
        s_to_r,r_to_s = match_ts(rgb_ts[rgb_gest_start:rgb_gest_end],skel_ts[skel_gest_start:skel_gest_end])
        
        gesture_data=[]

        for j in range(0,len(gesture_left_frames),frame_gap):
        # dominant hand is assumed to be left. if not the replace dominat_hand with not dominant_hand 
            frame_l=cv2.imread(gesture_left_frames[j])
            frame_r=cv2.imread(gesture_right_frames[j])

            if frame_l is None:
                print('this',gesture_left_frames[j],'is not processed due to 0 size')
                left_fingers = np.zeros(5).tolist()
            else:
                left_fingers = cpm_fingers(gesture_left_frames[j])

            if frame_r is None:
                print('this',gesture_right_frames[j],'is not processed due to 0 size')               
                right_fingers = np.zeros(5).tolist()
            else:
                right_fingers = cpm_fingers(gesture_right_frames[j])

            if len(gesture_left_frames)-j>frame_gap:
                if dominant_hand:
                    for p in range(frame_gap):
                        gesture_data.append(left_fingers+right_fingers)
                else:
                    for p in range(frame_gap):
                        gesture_data.append(right_fingers+left_fingers)                    

            else:
                if dominant_hand:
                    for p in range(len(gesture_left_frames)-j):
                        gesture_data.append(left_fingers+right_fingers)
                else:
                    for p in range(len(gesture_left_frames)-j):
                        gesture_data.append(right_fingers+left_fingers)


 #should return lists so that they can be added


        gesture_data_updated=[]

        #taking into account variation in 
        for k in range(len(r_to_s)):
            # print(gesture_data[r_to_s[k]])
            gesture_data_updated.append(gesture_data[r_to_s[k]])
        # for ex one of the gesture in 5_3_S2_L2_X_Up has only 1 frame and interpolation doesn't work.
        #putting it into try catch
        try:
            frames_data=interpn(np.array(gesture_data_updated))
            full_gesture_data.append(np.array(frames_data).flatten().tolist())
        except:
            gest_len=rgb_gest_end-rgb_gest_start
            print('Can-not append gesture {0} with lengths {1}'.format(os.path.basename(annot_rgb_file),str(gest_len)))

    return full_gesture_data
# run cpm through whole of the gesture, save fingers and then match it with skel ts
# error causing gesture - 5_3_S2_L2_X_Up_rgbannot2.txt
# create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,
#                 frames_folder=frames_folder)


#verify a particular gesture
# annot_rgb_file=r'H:\AHRQ\Study_IV\Flipped_Data\L2\Annotations\1_1_S6_L2_Scroll_Up_rgbannot2.txt'
# annot_skel_file=r'H:\AHRQ\Study_IV\Flipped_Data\L2\Annotations\1_1_S6_L2_Scroll_Up_annot2.txt'
# rgb_ts_file = r'H:\AHRQ\Study_IV\Flipped_Data\L2\1_1_S6_L2_Scroll_Up_rgbts.txt'
# skel_ts_file = r'H:\AHRQ\Study_IV\Flipped_Data\L2\1_1_S6_L2_Scroll_Up_skelts.txt'
# frames_folder=r'H:\AHRQ\Study_IV\Data\Data_cpm\Frames\L2\1_1_S6_L2_Scroll_Up'
# print('extracting fingerlengths from gesture', frames_folder)
# create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,
#                     frames_folder=frames_folder)
# sys.exit(0)


for lexicon in lexicons:
    lexicon_name=os.path.basename(lexicon)
    frames_lexicon_folder=os.path.join(frames_dir,lexicon_name)
    # print xml_lexicon_folder,len(os.listdir(xml_lexicon_folder))
    write_base_folder=os.path.join(fingers_dir,lexicon_name)
    if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)
    frames_folders=glob.glob(os.path.join(frames_lexicon_folder,"*"))
    annot_rgb_files,annot_skel_files=get_annot_files(lexicon_name) 
    rgb_ts_files = glob.glob(os.path.join(lexicon,"*_rgbts.txt"))
    skel_ts_files =glob.glob(os.path.join(lexicon,"*_skelts.txt"))

    gestures=get_gesture_names(annot_rgb_files)

    with open(os.path.join(write_base_folder,lexicon_name+'_fingers.pkl'),'wb') as pkl_file:
        gest_dict = {}

        for gesture in gestures:

            print('extracting fingerlengths from gesture', gesture)
            annot_rgb_file = [file for file in annot_rgb_files if gesture in file][0]
            annot_skel_file = [file for file in annot_skel_files if gesture in file][0]
            rgb_ts_file = [file for file in rgb_ts_files if gesture in file][0]
            skel_ts_file = [file for file in skel_ts_files if gesture in file][0]
            frames_folder = [folder for folder in frames_folders if gesture in folder][0]

            start=time.time()
            data_to_write = create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,
                    frames_folder=frames_folder)
            print('Time taken',time.time()-start)

            data_to_write_list=[]
            for line in data_to_write:
                data_to_write_list.append(line)
            gest_dict[gesture] = data_to_write_list
        pickle.dump(gest_dict,pkl_file,protocol=2)
