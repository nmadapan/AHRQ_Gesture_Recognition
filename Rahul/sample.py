import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d
from utils import *


pickle_path1= r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L2'
pkl_suffix=r'_fingers_from_hand_base_equate_dim_subsample.pkl'

with open(os.path.join(pickle_path1,os.path.basename(pickle_path1)+ pkl_suffix), 'rb') as fp:
    fingers_data = pickle.load(fp)

for key in fingers_data.keys():
	print(key,fingers_data[key])
	sys.exit(0)