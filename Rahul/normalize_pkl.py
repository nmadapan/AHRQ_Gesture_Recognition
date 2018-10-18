import numpy as np
import pickle,os,sys

pickle_path1 = r'H:\AHRQ\Study_IV\Data\Data_cpm\fingers\L3'
lexicon=os.path.basename(pickle_path1)


with open(os.path.join(pickle_path1, 'L3_fingers_recent.pkl'), 'rb') as fp:
	fingers_data = pickle.load(fp)

new_dict={}
for key in fingers_data:
	gest_list = []
	print np.array(fingers_data[key]).shape
	for line in fingers_data[key]:
		# max_num = max(line)/2
		max_num=300
		norm_list = [np.round((x/max_num)-1,4) for x in line]
		gest_list.append(norm_list)

	new_dict[key]=gest_list

with open(os.path.join(pickle_path1,lexicon+'_fingers_300_normalized.pkl'),'wb') as pkl_file:
	pickle.dump(new_dict,pkl_file)


