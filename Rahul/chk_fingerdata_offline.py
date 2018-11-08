# import numpy as np
# import sys,os, time
# import cv2
# from copy import copy, deepcopy
# from utils import *
# from glob import glob
# from cpm_frame_extraction import get_lhand_bbox, get_rhand_bbox, readlines_txt

# left_hand_id = 7
# left_wrist_id = 6
# right_hand_id = 11
# right_wrist_id = 10
# blur_nondom_hand=False

# skip_existing_folder = True # True if don't want to override existing folders


# read_base_path = r"G:\AHRQ\S2_L7\L7"
# write_base_path = r"G:\AHRQ\S2_L7\Frames"

# def extract_frames_cpm(video_file,rgb_skel_file,write_folder,frame_gap=None):

#     # print(s_to_r)
#     # sys.exit(0)
#     skel_coo=readlines_txt(rgb_skel_file)
#     cap = cv2.VideoCapture(video_file)
#     success, frame = cap.read()
#     counter=0
#     while success:
#         r_hand_coord,[lx,ly,lw,lh]=get_lhand_bbox([np.float(coord) for coord in skel_coo[counter].split(' ')],\
#             max_wh=(frame.shape[1],frame.shape[0]))
#         l_hand_coord,[rx,ry,rw,rh]=get_rhand_bbox([np.float(coord) for coord in skel_coo[counter].split(' ')],\
#             max_wh=(frame.shape[1],frame.shape[0]))
#         # cv2.rectangle(frame,(lx,ly),(lx+lw,ly+lh),(255,0,0),2)      
#         # cv2.rectangle(frame,(rx,ry),(rx+rw,ry+rh),(0,0,255),2)
#         # frame_l=frame
#         # frame_r=frame
#         lbbox=frame[ly:ly+lh,lx:lx+lw]
#         rbbox=frame[ry:ry+rh,rx:rx+rw]
#         cv2.imwrite(os.path.join(write_folder,'{0:06}'.format(counter)+'_l.jpg'), lbbox)
#         cv2.imwrite(os.path.join(write_folder,'{0:06}'.format(counter)+'_r.jpg'), rbbox)
#         # cv2.imwrite(os.path.join(r'./cpm_check/extract_imgs',str(counter)+'_l.jpg'),lbbox)
#         # cv2.imwrite(os.path.join(r'./cpm_check/extract_imgs',str(counter)+'_r.jpg'),rbbox)
#         success, frame = cap.read()
#         counter+=1
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# rgb_skel_file = glob(os.path.join(read_base_path,'*_color*'))
# gesture_video = glob(os.path.join(read_base_path,'*_rgb.avi'))

# extract_frames_cpm(video_file=gesture_video[0],rgb_skel_file=rgb_skel_file[0], write_folder=write_base_path)


# code for extracting finger lengths provided bounding boxes have been extracted from the frames