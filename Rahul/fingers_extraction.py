import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d
from utils import *

LEXICON_ID = 'L11'

base_path = r'G:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\\' + LEXICON_ID
base_write_path = r'G:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\\' + LEXICON_ID
pkl_suffix =r'_fingers_coords_no_intrpn.pkl'  #suffix of the pickle file from which data needs to be extracted

#FEATURES FOR HANDS
combine_pkls = False # if new and old raw fatures need to be combined before fingerleangths extraction
subject_wise_normalization=False
direction=False #set this flag if finger lengths from the base with direction are required
num_hand_all_coords = 21
normalization_constant = 300
subsample = True
lexicon = os.path.basename(base_path)

if combine_pkls:
    print('Combining pickle files')
    pkl_old = os.path.basename(base_path)+r'_fingers_coords_no_intrpn.pkl'
    pkl_new = os.path.basename(base_path)+r'_fingers_coords_no_intrpn_new.pkl' 

    pkl_paths = [os.path.join(base_path,pkl_old),os.path.join(base_path,pkl_new)]

    dicts=[]

    for ind,pkl_path in enumerate(pkl_paths,1):
        fp = open(pkl_path,'rb') 
        dicts.append(pickle.load(fp))

    for key in dicts[1].keys():
        dicts[0][key]=dicts[1][key]

    with open(os.path.join(base_path,os.path.basename(base_path)+pkl_suffix),'wb') as pkl_file:
        pickle.dump(dicts[0],pkl_file)
    print('pickle files combined and saved')

params_json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)
variables=json_to_dict(params_json_file_path)
num_points = variables['fixed_num_frames']
equate_dim = variables['equate_dim']
cpm_downsample_rate = variables['cpm_downsample_rate']

json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\subject_params_custom.json'
subject_param_dict=json_to_dict(json_file_path)
subject_parameters=subject_param_dict['subject_params']

if not combine_pkls:
    with open(os.path.join(base_path,os.path.basename(base_path)+ pkl_suffix), 'rb') as fp:
        fingers_data = pickle.load(fp)
else:
    fingers_data = dicts[0]

new_dict={}
print('Extracting finger features')
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

print('writing fingers features')
if equate_dim and subsample:
    with open(os.path.join(base_write_path,lexicon+'_'+'fingers_from_hand_base'+'_equate_dim'+'_subsample.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)
    with open(os.path.join(base_path,lexicon+'_'+'fingers_from_hand_base'+'_equate_dim'+'_subsample.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)        
if equate_dim and not subsample:
    with open(os.path.join(base_write_path,lexicon+'_'+'fingers_from_hand_base'+'_equate_dim.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)
    with open(os.path.join(base_path,lexicon+'_'+'fingers_from_hand_base'+'_equate_dim.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)        
if not equate_dim and subsample:
    with open(os.path.join(base_write_path,lexicon+'_'+'fingers_from_hand_base'+'_subsample.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)    
    with open(os.path.join(base_path,lexicon+'_'+'fingers_from_hand_base'+'_subsample.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)            
if not equate_dim and not subsample:
    with open(os.path.join(base_write_path,lexicon+'_'+'fingers_from_hand_base.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)
    with open(os.path.join(base_path,lexicon+'_'+'fingers_from_hand_base.pkl'),'wb') as pkl_file:
        pickle.dump(new_dict,pkl_file)
