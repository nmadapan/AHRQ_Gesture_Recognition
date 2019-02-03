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

pkl_file = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L3\L3_fingers_coords_no_intrpn_new.pkl'
print('loading pickle file')
with open(pkl_file, 'rb') as fp:
	fingers_data = pickle.load(fp)
print('pickle file loaded')

pkl_file = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L3\L3_fingers_coords_no_intrpn_new.pkl_1'
print('loading pickle file')
with open(pkl_file, 'rb') as fp:
	fingers_data_1 = pickle.load(fp)

print('pickle file loaded')

key_ = r'3_0_S12_L3_Rotate_X'

fingers_data[key_]=fingers_data_1[key_]

print(fingers_data[key_])

with open(r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L3\L3_fingers_coords_no_intrpn_new_2.pkl','wb') as pkl_file:
    pickle.dump(fingers_data,pkl_file)