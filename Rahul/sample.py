import numpy as np
import pickle,os,sys,json
# from scipy.interpolate import interp1d
# from utils import *

# base_path = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\Frames\L8'

# lex_gest_dict = {'L2':'2_1',
#  'L3':'4_0',
#  'L6':'6_3',
#  'L8':'6_4'
# }


# gest_id = lex_gest_dict[os.path.basename(base_path)]
# gest_folders=glob.glob(os.path.join(base_path,gest_id+'*'))

# for fold in gest_folders:
# 	print(os.path.basename(fold).split("_")[2])

pickle_base_path = r'H:\\AHRQ\\Study_IV\\Data\\Data_cpm_new\\fingers'
pickle_file_suffix = '_fingers_from_hand_base_equate_dim_subsample.pkl'
skel_folder_path = r'G:\\AHRQ\\Study_IV\\NewData2\\L8'
pickle_path = os.path.join(pickle_base_path, os.path.basename(skel_folder_path))
fingers_pkl_fname = os.path.basename(skel_folder_path) + pickle_file_suffix

print('loading pickle file')
with open(os.path.join(pickle_path, fingers_pkl_fname), 'rb') as fp:
	fingers_data = pickle.load(fp)
print('pickle file loaded')

# print(fingers_data.keys())

for key in fingers_data.keys():
	# print(np.array(fingers_data.get(key)).shape)
	for idx1,line in enumerate(np.round(fingers_data.get(key),4)):
	# for idx,line in (fingers_data.get(key)):
		print(idx1)
		print(line)
		sys.exit(0)