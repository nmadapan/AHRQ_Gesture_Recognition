'''
Verify if the lexicons and the associated files are correctly named.
'''

from os.path import join, basename, dirname, isfile, isdir, splitext
import sys
from glob import glob
import numpy as np
from copy import deepcopy 

xef_names = ['1_1_S3_L8_Scroll_Up', '10_4_S3_L6_X_FourPanels', '3_0_S3_L3_Rotate_X',\
			'2_1_S3_L3_X_Horizontal', '2_0_S3_L3_Flip_X', '1_0_S3_L3_Scroll_X', \
			'5_1_S6_L6_SwitchPanel_Left', '1_1_S1_L8_Scroll_Up','8_2_S4_L8_PIW_Close','8_1_S4_L8_PIW_Open','1_1_S4_L8_Scroll_Up']

data_path = r'H:\AHRQ\Study_IV\NewData'

for xef_name in xef_names:
	print xef_name, 
	fpath = join(data_path, '*\\'+xef_name+'*')
	print '===========>', len(glob(fpath))

sys.exit()

## Global variables
lexicon_id = 'L8'
naveen_path = '.'
data_path = r'H:\AHRQ\Study_IV\Flipped_Data'
subject_ids = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
file_exts = ['_rgb.avi', '_depth.avi', '_rgbts.txt', '_skelts.txt', '_color.txt', '_depth.txt', '_skel.txt']

command_list_file = join(naveen_path, lexicon_id+'_commands_list.txt')
if(not isfile(command_list_file)): 
	sys.exit(command_list_file + ' does not exists')

with open(command_list_file, 'r') as fp:
	command_names = [line.strip() for line in fp.readlines()]

lexicon_path = join(data_path, lexicon_id)
if(not isdir(lexicon_path)): 
	sys.exit(lexicon_path + ' does not exists!')

####################################################
### Check the existency of file exts in data_path ##
####################################################

for command_name in command_names:
	for subject_id in subject_ids:
		new_command_name = command_name.replace('*', subject_id[1:])
		all_cmd_files = [join(data_path, join(lexicon_id, new_command_name + file_ext)) for file_ext in file_exts]
		missing_files = [each_file for each_file in all_cmd_files if(not isfile(each_file))]
		if(len(missing_files) != 0):
			print new_command_name
			print '\t', missing_files

#############################################
### Check the existence of the xef files ####
#############################################

# xef_paths = [r'H:\AHRQ\Study_IV\XEF_Files', r'G:\AHRQ\XEF_Files', r'E:\AHRQ\Study_IV\XEF_Files']

# all_folders = []
# for xef_path in xef_paths: all_folders += glob(join(xef_path, '*'))	
# all_folders = [folder for folder in all_folders if(folder.endswith('_' + lexicon_id))]
# print 'No. of folders: ', len(all_folders), '\n\t', all_folders, '\n'

# for i_idx in range(len(all_folders)):
# 	i_sub_id = basename(all_folders[i_idx]).split('_')[0]
# 	i_files = glob(join(all_folders[i_idx], '*.xef'))
# 	old_i_files = np.array(deepcopy(i_files))
# 	i_files = [basename(i_file) for i_file in i_files]
# 	i_files = np.array([i_file.replace(i_sub_id, 'S*') for i_file in i_files])
# 	for j_idx in range(i_idx+1, len(all_folders)):
# 		j_sub_id = basename(all_folders[j_idx]).split('_')[0]
# 		j_files = glob(join(all_folders[j_idx], '*.xef'))
# 		old_j_files = np.array(deepcopy(j_files))
# 		j_files = [basename(j_file) for j_file in j_files]
# 		j_files = np.array([j_file.replace(j_sub_id, 'S*') for j_file in j_files])

# 		if(len(i_files) != len(j_files)):
# 			print 'Length mismatch: '+ all_folders[i_idx] + ' and ' + all_folders[j_idx] + ' do not match' + '\n'
	
# 		mismatch_ids = np.nonzero(np.array(i_files) != np.array(j_files))[0]
# 		if(len(mismatch_ids) == 0): continue
# 		print 'Naming error: ' + all_folders[i_idx] + ' and ' + all_folders[j_idx]
# 		print zip(old_i_files[mismatch_ids], old_j_files[mismatch_ids])
# 		print ''


####################
# def sort_filenames(annot_rgb_files):
#     basenames=[basename(file) for file in annot_rgb_files]
#     base_ids=[int(file.split('_')[0]+file.split('_')[1]) for file in basenames]
#     zipped= zip(base_ids,basenames)
#     zipped.sort(key = lambda t: t[0])
#     sorted_gestures = list(zip(*zipped)[1])
#     return sorted_gestures

# ## Print all xef filenames
# xef_path = r'H:\AHRQ\Study_IV\XEF_Files\S4_L8'
# fnames = sort_filenames(glob(join(xef_path, '*.xef')))
# for fname in fnames:
# 	print splitext(fname)[0]