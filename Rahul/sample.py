import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d
from utils import *


pickle_path1= r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L2'
pkl_suffix=r'_fingers_from_hand_base_equate_dim_subsample.pkl'

file_path = 'G:\\AHRQ\\Study_IV\\Data\\Data_cpm_new\\fingers\\L2_fingers_coords_no_intrpn.pkl'

with open(file_path, 'rb') as fp:
    fingers_data = pickle.load(fp)

for key in fingers_data.keys():
	print(key,fingers_data[key])
	sys.exit(0)