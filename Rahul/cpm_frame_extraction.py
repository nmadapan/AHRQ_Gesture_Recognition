#extract left and right bounding box for each frame from the video
import numpy as np
import sys,os, time
import cv2
from copy import copy, deepcopy
from utils import *
import glob

LEXICON_ID = 'L11'

left_hand_id = 7
left_wrist_id = 6
right_hand_id = 11
right_wrist_id = 10
blur_nondom_hand=False

skip_existing_folder = True # set it to True if don't want to override existing folders

read_base_path = r"G:\AHRQ\Study_IV\NewData2"
write_base_path = r"G:\AHRQ\Study_IV\Data\Data_cpm_new"
frames_folder="Frames"

frames_dir=os.path.join(write_base_path,frames_folder)
if not os.path.isdir(frames_dir): create_writefolder_dir(frames_dir)
lexicons = [os.path.join(read_base_path, LEXICON_ID)]
# lexicons = glob.glob(os.path.join(read_base_path,"*"))

def get_lhand_bbox(color_skel_pts, max_wh , \
                   des_size = 300):
    '''
    Input arguments:
        * color_skel_pts: A list of 50 elements. Pixel coordinates of 25 Kinect joints. Format: [x1, y1, x2, y2, ...]
        * des_size: Size of the square bounding box
    Return:
        * bbox: list of four values. [x, y, w, h].
            (x, y): pixel coordinates of top LEFT corner of the bbox
            (w, h): width and height of the bounding box.
    '''
    ##
    half_sz = np.int32(des_size/2)
    max_x, max_y = max_wh

    ## Return left hand bounding box
    hand = np.array(color_skel_pts[2*left_hand_id:2*left_hand_id+2])
    x = np.int32(hand[0]) - half_sz
    y = np.int32(hand[1]) - half_sz

    ## Handle the boundary conditions
    if(x < 0): x = 0
    if(y < 0): y = 0
    if(x+des_size >= max_x): x = max_x - des_size - 1
    if(y+des_size >= max_y): y = max_y - des_size - 1

    return hand.tolist(),[x, y, des_size, des_size]

def get_rhand_bbox(color_skel_pts, max_wh, des_size = 300):
    '''
    Input arguments:
        * color_skel_pts: A list of 50 elements. Pixel coordinates of 25 Kinect joints. Format: [x1, y1, x2, y2, ...]
        * des_size: Size of the square bounding box
    Return:
        * bbox: list of four values. [x, y, w, h].
            (x, y): pixel coordinates of top RIGHT corner of the bbox
            (w, h): width and height of the bounding box.
    '''
    ##
    half_sz = np.int32(des_size/2)
    max_x, max_y = max_wh

    ## Return right hand bounding box
    hand = np.array(color_skel_pts[2*right_hand_id:2*right_hand_id+2])
    x = np.int32(hand[0]) - half_sz
    y = np.int32(hand[1]) - half_sz

    ## Handle the boundary conditions
    if(x < 0): x = 0
    if(y < 0): y = 0
    if(x+des_size > max_x): x = max_x - des_size - 1
    if(y+des_size > max_y): y = max_y - des_size - 1

    return hand.tolist(),[x, y, des_size, des_size]

def readlines_txt(f_name,str_to_num=False):
    with open(f_name) as f:
        f_lines=f.readlines()
        f_lines=[x.strip() for x in f_lines]
    return f_lines

def blur_hand(frame,hand_coord):
    x=int(hand_coord[0])
    y=int(hand_coord[1])
    return cv2.rectangle(frame,(x-25,y-25),(x+10,y+10),(122,230,100),75)    

def euclidean_dist(r_hand_coord,l_hand_coord):
    rhand_x,rhand_y=r_hand_coord
    lhand_x,lhand_y=l_hand_coord
    return np.sqrt(np.square(rhand_y-lhand_y)+np.square(rhand_x-lhand_x))

def extract_frames_cpm(video_file,rgb_ts_file,skle_ts_file,rgb_skel_file,write_folder,frame_gap=None):

    rgb_ts = readlines_txt(rgb_ts_file)
    skel_ts = readlines_txt(skle_ts_file)
    rgb_ts_num = [np.float32(ts) for ts in rgb_ts]
    skel_ts_num = [np.float32(ts) for ts in skel_ts]
    s_to_r,_ = match_ts(rgb_ts_num,skel_ts_num)
    # print(s_to_r)
    # sys.exit(0)
    skel_coo=readlines_txt(rgb_skel_file)

    cap = cv2.VideoCapture(video_file)
    success, frame = cap.read()
    counter=0
    while success:
        r_hand_coord,[lx,ly,lw,lh]=get_lhand_bbox([np.float(coord) for coord in skel_coo[s_to_r[counter]].split(' ')],\
            max_wh=(frame.shape[1],frame.shape[0]))
        l_hand_coord,[rx,ry,rw,rh]=get_rhand_bbox([np.float(coord) for coord in skel_coo[s_to_r[counter]].split(' ')],\
            max_wh=(frame.shape[1],frame.shape[0]))
        # cv2.rectangle(frame,(lx,ly),(lx+lw,ly+lh),(255,0,0),2)      
        # cv2.rectangle(frame,(rx,ry),(rx+rw,ry+rh),(0,0,255),2)
        if blur_nondom_hand:
            hand_dist=euclidean_dist(r_hand_coord,l_hand_coord)
            if hand_dist<150:
                lframe=deepcopy(frame)
                rframe=deepcopy(frame)
                frame_l=blur_hand(lframe,l_hand_coord)
                frame_r=blur_hand(rframe,r_hand_coord)

        else:
            frame_l=frame
            frame_r=frame

        lbbox=frame_l[ly:ly+lh,lx:lx+lw]
        rbbox=frame_r[ry:ry+rh,rx:rx+rw]
        cv2.imwrite(os.path.join(write_folder,'{0:06}'.format(counter)+'_l.jpg'), lbbox)
        cv2.imwrite(os.path.join(write_folder,'{0:06}'.format(counter)+'_r.jpg'), rbbox)
        # cv2.imwrite(os.path.join(r'./cpm_check/extract_imgs',str(counter)+'_l.jpg'),lbbox)
        # cv2.imwrite(os.path.join(r'./cpm_check/extract_imgs',str(counter)+'_r.jpg'),rbbox)
        success, frame = cap.read()
        counter+=1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



def sort_filenames(files):
    dir_name=[os.path.dirname(os.path.splitext(file)[0])for file in files]
    extension=os.path.splitext(files[0])[1]
    basenames=[os.path.basename(os.path.splitext(file)[0])for file in files]
    base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
    zipped= zip(base_ids,basenames)
    zipped.sort(key = lambda t: t[0])
    sorted_gestures = list(zip(*zipped)[1])
    sorted_file_paths=[]
    for gesture in sorted_gestures:
        sorted_file_paths.append(os.path.join(dir_name[0],gesture+extension))
    return sorted_file_paths

def get_gesture_names(skel_files):
    gesture_names=[]
    for file in skel_files:
        strings_=os.path.basename(file).split('_')
        gesture_names.append('_'.join(strings_[:-1]))
    return gesture_names

def generate_data():
    for lexicon in lexicons:
        lexicon_name=os.path.basename(lexicon)
        write_base_folder=os.path.join(frames_dir,lexicon_name)

        if not os.path.isdir(write_base_folder): create_writefolder_dir(write_base_folder)  
        rgb_skel_files=glob.glob(os.path.join(lexicon,"*color.txt"))
        rgb_skel_files=sort_filenames(rgb_skel_files)
        rgb_ts_files=glob.glob(os.path.join(lexicon,"*rgbts.txt"))
        skel_ts_files=glob.glob(os.path.join(lexicon,"*skelts.txt"))
        gestures=get_gesture_names(rgb_skel_files)
        rgb_videos=glob.glob(os.path.join(lexicon,"*rgb.avi"))

        for gesture in gestures:
            # if gesture in missing_gestures:
            gesture_folder=os.path.join(write_base_folder,gesture)
            if skip_existing_folder and os.path.isdir(gesture_folder): continue
            else:
                create_writefolder_dir(gesture_folder)
            # if not os.path.isdir(gesture_folder): create_writefolder_dir(gesture_folder)
            # else:continue
                print 'extracting frames from the gesture', gesture
                gesture_video=[video for video in rgb_videos if gesture in video][0]
                rgb_skel_file=[file for file in rgb_skel_files if gesture in file][0]
                rgb_ts_file=[file for file in rgb_ts_files if gesture in file][0]
                skel_ts_file=[file for file in skel_ts_files if gesture in file][0]
                print 'writing in folder:',gesture_folder
                extract_frames_cpm(video_file=gesture_video,rgb_skel_file=rgb_skel_file,rgb_ts_file=rgb_ts_file,skle_ts_file=skel_ts_file,\
                    write_folder=gesture_folder)
            # print os.path.basename(rgb_skel_file),os.path.basename(rgb_ts_file),os.path.basename(skel_ts_file),os.path.basename(gesture_video)


generate_data()