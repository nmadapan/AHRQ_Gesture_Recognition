import numpy as np
import pickle,os,sys

num_fingers=5
norm_constant=300
pickle_path1 = r'H:\AHRQ\Study_IV\Data\Data_cpm\fingers\L2'
lexicon=os.path.basename(pickle_path1)

hands_key_points=[2,4,5,8,9,12,13,16,17,20]

def fingers_length(key_points):
    #keypoints as a list of x,y coordinates of relevant fingers' joints
    #lengths of thumb(2,4) and first 2 fingers(5,8,9,12) plus distance from tip of thumb to base of pinky(4,17)
    fingers_len=[]
    for i in range(0,num_fingers*4,4):
        # finger_len=np.sign(key_points[i+3]-key_points[i+1])*(np.abs(key_points[i+2]-key_points[i])+np.abs(key_points[i+3]-key_points[i+1]))
        # finger_len=np.sign(key_points[i+3]-key_points[i+1])*(np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)) #signed euclidean
        finger_len=(np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)) #unsigned Euclidean
        fingers_len.append(finger_len)
    # horizon_dist=np.abs(key_points[2]-key_points[16])+np.abs(key_points[3]-key_points[17])
    horizon_dist=np.sqrt((key_points[2]-key_points[16])**2+(key_points[3]-key_points[17])**2)
    fingers_len.append(horizon_dist)
    return np.round((np.array(fingers_len)/norm_constant),4)


with open(os.path.join(pickle_path1, 'L2_fingers_coords.pkl'), 'rb') as fp:
	fingers_data = pickle.load(fp)

new_dict={}
for key in fingers_data:
	gest_list=[]
	for line in fingers_data[key]:
		gest_frames=[]
		gest=np.array(line).reshape(40,40)
		for frame in gest:
			frame_f=frame[:20]
			frame_l=frame[20:]
			gest_frames.append(fingers_length(frame_f).tolist()+fingers_length(frame_l).tolist())
		gest_list.append(np.array(gest_frames).flatten().tolist()) 


	new_dict[key]=gest_list

with open(os.path.join(pickle_path1,lexicon+'_'+str(num_fingers)+'fingers_from_coord_euclid_norm_'+str(norm_constant)+'.pkl'),'wb') as pkl_file:
	pickle.dump(new_dict,pkl_file)