"""
This file contains the basic essential functions for extracting fingers data from openpose.
This file has following functions:
	1.  create_writefolder_dir: creating directory for writing data
	2. 	conv_xml: extracting finger coordinates from xml_files generated by Open Pose
	3.  fingers_length: converting raw finger coordinates(from conv_xml) to finger lengths
    4. json_to_dict: for converting param.json to a dictionary
"""

import os,sys,glob,re,cv2,json
import numpy as np
import xml.etree.ElementTree as ET
from scipy.interpolate import interp1d 
import math


#open pose path
# exe_addr = '.\\bin\\OpenPoseDemo.exe'

json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'
sys.path.insert(0,json_file_path)

hands_key_points=[2,4,5,8,9,12,13,16,17,20]
hand_base_key_points= [0,4,8,12,16,20]
# fingers_norm_constant=300
num_fingers=5

def create_writefolder_dir(create_dir):
#################################################
### creates the folders/directories
#################################################
    try:
        os.mkdir(create_dir)
    except WindowsError:
        create_writefolder_dir()

def fingers_length(key_points):
    fingers_len=[]
    for i in range(0,len(key_points),4):
        finger_len=np.sqrt((key_points[i+2]-key_points[i])**2+(key_points[i+3]-key_points[i+1])**2)
        fingers_len.append(finger_len)
    return np.round(fingers_len,4)

def conv_xml(file_path):
    tree = ET.parse(file_path)
    root=tree.getroot()
    vals=root[0][2].text  # this refers to the data we need
    vals = vals.strip().replace('\n','') # Removing the ending white spaces and new lines
    vals = re.sub(' +', ' ', vals).split(' ') # Removing the intermediate excess white spaces
    vals = map(float, vals) # Convert strings to floats
    x = vals[0::3]
    y = vals[1::3]

    xy=[]

    for i in hands_key_points:
        xy.append(np.round(x[i],4))
        xy.append(np.round(y[i],4))
       
    return fingers_length(xy)

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

def interpn(yp, num_points=40, kind = 'linear'):
    # yp is a gesture instance
    # yp is 2D numpy array of size num_frames x 3 if num_joints = 1
    # No. of frames will be increased/reduced to num_points
    xp = np.linspace(0, 1, num = yp.shape[0])
    x = np.linspace(0, 1, num = num_points)
    y = np.zeros((x.size, yp.shape[1]))
    for dim in range(yp.shape[1]):
        f = interp1d(xp, yp[:, dim], kind = kind)
        y[:, dim] = f(x)
    return y

def fingers_length_from_base(key_points,norm_constant=300):
    fingers_len=[]
    fingers_tips=[]
    for x in hand_base_key_points[1:]:
        finger_len=(np.sqrt((key_points[2*x]-key_points[0])**2+(key_points[2*x+1]-key_points[1])**2))
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)

def fingers_length_from_base_with_direction(key_points,norm_constant=300,norm='L2'):
    fingers_len=[]
    fingers_tips=[]
    for x in hand_base_key_points[1:]:
        if norm=='L1':
            finger_len=np.sign(key_points[2*x+1]-key_points[1])*(np.abs(key_points[2*x]-key_points[0])+np.abs(key_points[2*x+1]-key_points[1]))
        else:
            finger_len=np.sign(key_points[2*x+1]-key_points[1])*(np.sqrt((key_points[2*x]-key_points[0])**2+(key_points[2*x+1]-key_points[1])**2))
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)

def fingers_length_with_direction(key_points,norm_constant=300):
    fingers_len=[]  
    key_points_base=fingers_key_points[0::2]
    key_points_tip=fingers_key_points[1::2]
    # if key_points_base != key_points_tip: #add assertion here to verify that key_points_base=key_points_tip
    #   assert 
    for i,j in zip(key_points_base,key_points_tip):
        finger_len=np.sign(key_points[2*j+1]-key_points[2*i+1])*(np.abs(key_points[2*j]-key_points[2*i])+np.abs(key_points[2*j+1]-key_points[2*i+1]))
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)

def fingers_length(key_points,norm_constant=300):
    '''
    Description:
        Given all the hand keypoints(of a frame) extracted from CPM, returns finger lengths
    Input Arguments:
        key_points - 1D array of hand coordiantes(21(jointss)*2(x,y)) extarcted from CPM
    Return:
        1D array of length of fingers 
    '''
    fingers_len=[]  
    key_points_base=fingers_key_points[0::2]
    key_points_tip=fingers_key_points[1::2]
    # if key_points_base != key_points_tip: #add assertion here to verify that key_points_base=key_points_tip
    #   assert 
    for i,j in zip(key_points_base,key_points_tip):
        finger_len=(np.sqrt((key_points[2*j]-key_points[2*i])**2+(key_points[2*j+1]-key_points[2*i+1])**2)) #unsigned Euclidean
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)


def hand_direction(key_points):
    '''
    mean of the angles of fingers tips 
    '''
    angle=[]
    for x in hand_base_key_points[1:]:
        angle.append(math.atan2(key_points[2*x+1],key_points[2*x]))
    return np.round(np.mean(angle)/math.pi,4)

def thumb_pinky_dist(key_points,norm_constant=300):
    fingers_key_points= [4,20]
    i,j = fingers_key_points
    finger_dist=np.sqrt((key_points[2*j]-key_points[2*i])**2+(key_points[2*j+1]-key_points[2*i+1])**2)
    return np.round((finger_dist/norm_constant),4)

def match_ts(rgb_ts,skel_ts):
    '''
        Description: 
            This function maps skeleton time stamps to rgb time stamps and vice versa
        Input Arguments:
            rgb_ts - path to the file with rgb time stamps
            skel_ts - path to the file with skeleton time stamps
        Returns:
            s_to_r - mapping from skeleton time stamps to rgb time stamps 
            r_to_s - mapping from rgb time stamps to skeleton time stamps
    '''
    rgb_ts=np.array(rgb_ts)
    skel_ts=np.array(skel_ts)
    s_to_r=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=1)
    r_to_s=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=0)
    return s_to_r,r_to_s


