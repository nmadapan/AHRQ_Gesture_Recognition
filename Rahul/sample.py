from utils import *
import json

json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)

variables=json_to_dict(json_file_path)
num_points = variables['fixed_num_frames']
equate_dim = variables['equate_dim']
cpm_downsample_rate = variables['cpm_downsample_rate']

print num_points