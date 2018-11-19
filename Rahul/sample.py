from utils import *
import json
import numpy as np
import math

# json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
# sys.path.insert(0,json_file_path)

# variables=json_to_dict(json_file_path)
# num_points = variables['fixed_num_frames']
# equate_dim = variables['equate_dim']
# cpm_downsample_rate = variables['cpm_downsample_rate']
# a=np.random.randint(1,100,42)
# def hand_direction(a):
#     angle=[]
#     for i in range(0,len(a[2:]),2):
#         angle.append(math.atan2(a[i+1],a[i]))
#     return np.round(np.mean(angle)/math.pi,4)


a=np.random.randint(1,50,42)
print a
print thumb_pinky_dist(a)

26 10,18 37