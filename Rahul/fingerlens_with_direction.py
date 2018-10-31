import numpy as np
import pickle,os,sys

num_fingers=5
norm_constant=300
pickle_path1= r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L3'
lexicon=os.path.basename(pickle_path1)
fingers_key_points=[2,4,5,8,9,12,13,16,17,20]
hand_base_key_points= [0,4,8,12,16,20]

fingerlens_from_base = False

#FEATURES FOR HANDS

def fingers_length_from_base_with_direction(key_points):
    fingers_len=[]
    for x in hand_base_key_points[1:]:
        finger_len=np.sign(key_points[2*x+1]-key_points[1])*(np.abs(key_points[2*x]-key_points[0])+np.abs(key_points[2*x+1]-key_points[1]))
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)

with open(os.path.join(pickle_path1,os.path.basename(pickle_path1)+ '_fingers_coords.pkl'), 'rb') as fp:
	fingers_data = pickle.load(fp)

def fingers_length_with_direction(key_points):
    fingers_len=[]  
    key_points_base=fingers_key_points[0::2]
    key_points_tip=fingers_key_points[1::2]
    # if key_points_base != key_points_tip: #add assertion here to verify that key_points_base=key_points_tip
    #   assert 
    for i,j in zip(key_points_base,key_points_tip):
        finger_len=np.sign(key_points[2*j+1]-key_points[2*i+1])*(np.abs(key_points[2*j]-key_points[2*i])+np.abs(key_points[2*j+1]-key_points[2*i+1]))
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)


with open(os.path.join(pickle_path1,os.path.basename(pickle_path1)+ '_fingers_coords.pkl'), 'rb') as fp:
	fingers_data = pickle.load(fp)

new_dict={}
for key in fingers_data:
	gest_list=[]
	for line in fingers_data[key]:
		gest_frames=[]
		#Since each gesture is 1D array ,interpolated to 40 frames, 
		#reshaping it back to an array of size: num_frames*frame_features
		gest=np.array(line).reshape(40,int(len(line)/40))
		for frame in gest:
			frame_f=frame[:len(frame)/2] #features of dominat hand
			frame_l=frame[len(frame)/2:] #features of non dominat hand
			if fingerlens_from_base:
				gest_frames.append(fingers_length_from_base_with_direction(frame_f).tolist()+fingers_length_from_base_with_direction(frame_l).tolist())
			else:
				gest_frames.append(fingers_length_with_direction(frame_f).tolist()+fingers_length_with_direction(frame_l).tolist())
		gest_list.append(np.array(gest_frames).flatten().tolist()) 
	new_dict[key]=gest_list


if fingerlens_from_base:
	with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_from_base_with_direction.pkl'),'wb') as pkl_file:
		pickle.dump(new_dict,pkl_file)
else:
	with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_lengths_with_direction.pkl'),'wb') as pkl_file:
		pickle.dump(new_dict,pkl_file)