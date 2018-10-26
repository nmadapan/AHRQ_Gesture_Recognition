import numpy as np
import pickle,os,sys

num_fingers=3
pickle_path1 = r'H:\AHRQ\Study_IV\Data\Data_cpm\fingers\L3'
lexicon=os.path.basename(pickle_path1)


with open(os.path.join(pickle_path1, 'L3_fingers_300_normalized.pkl'), 'rb') as fp:
	fingers_data = pickle.load(fp)

new_dict={}
for key in fingers_data:
	gest_list = []
	for line in fingers_data[key]:
		gest_frames=[]
		gest=np.array(line).reshape(40,10)
		for frame in gest:
			frame_f=frame[:5]
			frame_l=frame[5:]
			gest_frames.append(frame_f[:num_fingers].tolist()+frame_l[:num_fingers].tolist())

		gest_list.append(np.array(gest_frames).flatten().tolist()) 

	new_dict[key]=gest_list

with open(os.path.join(pickle_path1,lexicon+'_fingers_norm_3003'+str(num_fingers)+'.pkl'),'wb') as pkl_file:
	pickle.dump(new_dict,pkl_file)