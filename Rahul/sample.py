import numpy as np
import pickle

pkl_path = r'H:\AHRQ\Study_IV\Data\Data_cpm\fingers\L6\L6_fingers_pp.pkl'
write_pkl_path = r'H:\AHRQ\Study_IV\Data\Data_cpm\fingers\L6\L6_fingers_pp.pkl'

with open(pkl_path, 'rb') as fp:
    fingers_data = pickle.load(fp)

# for key in fingers_data.keys()[:130]:		
print np.array(fingers_data['11_2_S6_L2_ContrastPresets_X']).shape

# print type(fingers_data)
# print np.array(fingers_data['6_1_S1_L6_Pan_Left']).shape