"""
Since, most of the gestures in L10 and L11 are coming from other lexicons(L2,L3,L6 & L8); this code copies missing gestures to parsed L10 and L11.


"""
import os, sys, json
import numpy as np 
import pandas as pd 
import glob
from shutil import copy



lexicon_ID = 'L11'
destination_base_path = r'H:\AHRQ\Study_IV\NewData'
destination_path = os.path.join(destination_base_path,lexicon_ID)

source_path = r'H:\AHRQ\Study_IV\NewData'

gest_lexicon_dict = {'L10':'Worst Lexicon','L11':'Best Lexicon'}
existing_gestures_paths = glob.glob(os.path.join(destination_path,'*_rgb.avi'))

csv_file_path = r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Rahul\best_worst_lexicons.csv'
data =  pd.read_csv(csv_file_path)
# existing_gestures_ids=[for gesture_path in existing_gestures_paths for os.path.basename()]
# print existing_gestures_paths
gesture_ids=[]
#gesture_ids like 1_1,1_2,1_3
for gesture_path in existing_gestures_paths:
	split_gest = os.path.basename(gesture_path).split('_')
	gesture_ids.append('_'.join(split_gest[:2]))
	# gesture_ids.append(split_gest[:3].join('_'))
unique_existing_gestures_ids = set(gesture_ids)

#ids of gestures not in the folder
missing_gesture_ids = [idx for idx in data['Code'] if idx not in unique_existing_gestures_ids]

lexicon_tag = gest_lexicon_dict[lexicon_ID] #worse/best lexicon

missing_ids_lexicon = data.loc[data['Code'].isin(missing_gesture_ids)][['Code',gest_lexicon_dict[lexicon_ID]]] #data frame of gesture_id and corresponding lexicon

#
for lexicon in set(missing_ids_lexicon[gest_lexicon_dict[lexicon_ID]]):
	# lexicon = 2,3...
	# lexicon and corresponding gesture ids
	missing_ids = missing_ids_lexicon.loc[missing_ids_lexicon[gest_lexicon_dict[lexicon_ID]] == lexicon]['Code'] 
	# find the unique starting gesture ids, like 7,8 and match 7_, 8_ etc
	num_gests = len(missing_ids)
	gest_start = set(([idx.split('_')[0] for idx in missing_ids]))
	# go to the lexicon folder
	lexicon_path = os.path.join(source_path,'L'+str(lexicon)) # path from where the get the data

	print 'copying files from', lexicon_path
	print 'IDs of gesture groups being copied', gest_start
	gest_files = [glob.glob(os.path.join(lexicon_path,str(x)+'_*')) for x in gest_start]	

# lexicon number has to be updated in the files to be copied. If it is changed before copying, 
# it will point to a path that doesn't exist. So firstly copy the files and then rename them.
	for file in gest_files:
		for f in file:
			copy(f,destination_path)


# rename files 
print 'Renaming Copied files'
files = glob.glob(os.path.join(destination_path,'*'))
rename_files = [file for file in files if lexicon_ID not in os.path.basename(file)]

for file in rename_files:
	file_base = os.path.basename(file).split('_')
	file_base[3] = lexicon_ID
	try:
		os.rename(file,os.path.join(destination_path,'_'.join(file_base))) 
	except:
		print 'file with this name already exists', os.path.basename(file)