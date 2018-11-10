import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d
from utils import *


pickle_path1= r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L2'
pkl_suffix=r'_fingers_coords_no_intrpn.pkl'

#FEATURES FOR HANDS
num_hand_all_coords = 21
# fingerlens_from_base = True
# sort_lengths=False
subsample = True
lexicon=os.path.basename(pickle_path1)
# fingers_key_points=[2,4,5,8,9,12,13,16,17,20]
# hand_base_key_points= [0,4,8,12,16,20]
params_json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(params_json_file_path)
num_points = variables['fixed_num_frames']
equate_dim = variables['equate_dim']
cpm_downsample_rate = variables['cpm_downsample_rate']

with open(os.path.join(pickle_path1,os.path.basename(pickle_path1)+ pkl_suffix), 'rb') as fp:
    fingers_data = pickle.load(fp)


new_dict={}
for key in fingers_data:
    gest_list=[]
    for line in fingers_data[key]:
        gest_frames=[]
        #Since each gesture is 1D array ,interpolated to 40 frames, 
        #reshaping it back to an array of size: num_frames*frame_features
        gest=np.array(line).reshape(int(len(line)/((num_hand_all_coords*2)*2)),((num_hand_all_coords*2)*2))
        # gest_interpolated=interpn(gest)
        if subsample:
            gest = gest[0::cpm_downsample_rate]

        if equate_dim:
            gest = interpn(gest,num_points=num_points, kind = 'nearest') #kind - nearest(for copying)

        for frame in gest:
            frame_f=frame[:len(frame)/2] #features of dominat hand
            frame_l=frame[len(frame)/2:] #features of non dominat hand

            gest_frames.append(fingers_length_from_base(frame_f).tolist()+\
                fingers_length_from_base(frame_l).tolist())
        gest_list.append(np.array(gest_frames).flatten().tolist()) 
    new_dict[key]=gest_list

if equate_dim and subsample:
    with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_from_hand_base'+'_equate_dim'+'_subsample.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)
if equate_dim and not subsample:
    with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_from_hand_base'+'_equate_dim.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)
if not equate_dim and subsample:
    with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_from_hand_base'+'_subsample.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)    
if not equate_dim and not subsample:
    with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_from_hand_base.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)

