import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d
from utils import *


pickle_path1= r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L8'
pkl_suffix=r'_fingers_coords_no_intrpn.pkl'

#FEATURES FOR HANDS
subject_wise_normalization=False
direction=False #set this flag if finger lengths from the base with direction are required
num_hand_all_coords = 21
normalization_constant=300
subsample = True
lexicon = os.path.basename(pickle_path1)

params_json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(params_json_file_path)
num_points = variables['fixed_num_frames']
equate_dim = variables['equate_dim']
cpm_downsample_rate = variables['cpm_downsample_rate']

json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\subject_params_custom.json'
subject_param_dict=json_to_dict(json_file_path)
subject_parameters=subject_param_dict['subject_params']

with open(os.path.join(pickle_path1,os.path.basename(pickle_path1)+ pkl_suffix), 'rb') as fp:
    fingers_data = pickle.load(fp)

new_dict={}
for key in fingers_data:
    subject_id = key.split('_')[2]
    lexicon_id = key.split('_')[3]
    gest_list=[]
    if subject_wise_normalization: norm_const = subject_parameters[lexicon_id][subject_id]['finger_length']
    else: norm_const = normalization_constant
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
            if direction:
                gest_frames.append(fingers_length_from_base_with_direction(frame_f,norm_const,norm='L2').tolist()+\
                    fingers_length_from_base_with_direction(frame_l,norm_const,norm='L2').tolist() + hand_direction(frame_f)+hand_direction(frame_l)+\
                    [thumb_pinky_dist(frame_f,norm_const)]+[thumb_pinky_dist(frame_l,norm_const)])
            else:
                gest_frames.append(fingers_length_from_base(frame_f,norm_const).tolist()+\
                    fingers_length_from_base(frame_l,norm_const).tolist()+[hand_direction(frame_f)]+[hand_direction(frame_l)]+\
                    [thumb_pinky_dist(frame_f,norm_const)]+[thumb_pinky_dist(frame_l,norm_const)])   
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

