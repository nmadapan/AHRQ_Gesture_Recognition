import numpy as np
import os, time, glob, pickle, re, copy, sys, json
from scipy.interpolate import interp1d

data_basepath=r'H:\AHRQ\Study_IV\Flipped_Data'
read_base_path = r"H:\AHRQ\Study_IV\Data\Data_cpm"
# write_base_path = "H:\\AHRQ\\Study_IV\\Data\\Data_OpenPose"
frames_folder = "Frames"
fingers_folder='fingers'
frames_dir=os.path.join(read_base_path,frames_folder)
fingers_dir=os.path.join(read_base_path,fingers_folder)
lexicons = glob.glob(os.path.join(data_basepath,"*"))
lexicons_names=[os.path.basename(x) for x in glob.glob(os.path.join(data_basepath,"*"))]       #[L2,L3,...]


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

def cpm_fingers(frame):
    #must return a list
    return  np.random.randn(5).tolist()

def sort_frame_nums(frames):
    pass

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

json_file_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
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

    full_gesture_data=[]

    for i in range(0,num_gestures,1): #loop over num_gestures times
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
        for j in range(len(gesture_left_frames)):
        # dominant hand is assumed to be left. if not the replace dominat_hand with not dominant_hand 
            if dominant_hand:
                gesture_data.append(cpm_fingers(gesture_left_frames[j])+cpm_fingers(gesture_right_frames[j])) #should return lists so that they can be added
            else:
                gesture_data.append(cpm_fingers(gesture_right_frames[j])+cpm_fingers(gesture_left_frames[j]))

        gesture_data_updated=[]

        #taking into account variation in 
        for k in range(len(r_to_s)):
            gesture_data_updated.append(gesture_data[r_to_s[k]])
        # for ex one of the gesture in 5_3_S2_L2_X_Up has only 1 frame and interpolation doesn't work.
        #putting it into try catch
        try:
            frames_data=interpn(np.array(gesture_data_updated))
            full_gesture_data.append(np.array(frames_data).flatten().tolist())
        except:
            gest_len=rgb_gest_end-rgb_gest_start
            print 'Can-not append gesture {0} with lengths {1}'.format(os.path.basename(annot_rgb_file),str(gest_len))

    return full_gesture_data
# run cpm through whole of the gesture, save fingers and then match it with skel ts
# error causing gesture - 5_3_S2_L2_X_Up_rgbannot2.txt
# create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,
#                 frames_folder=frames_folder)

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
            annot_rgb_file = [file for file in annot_rgb_files if gesture in file][0]
            annot_skel_file = [file for file in annot_skel_files if gesture in file][0]
            rgb_ts_file = [file for file in rgb_ts_files if gesture in file][0]
            skel_ts_file = [file for file in skel_ts_files if gesture in file][0]
            frames_folder = [folder for folder in frames_folders if gesture in folder][0]

            data_to_write = create_fingers_data(annot_rgb_file, annot_skel_file,rgb_ts_file,skel_ts_file,
                    frames_folder=frames_folder)


        #     data_to_write_list=[]
        #     for line in data_to_write:
        #         data_to_write_list.append(line)
        #     gest_dict[gesture] = data_to_write_list
        # pickle.dump(gest_dict,pkl_file)
