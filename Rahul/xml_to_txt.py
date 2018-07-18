import xml.etree.ElementTree as ET
import numpy as np
import os, time, glob, pickle, re

def conv_xml(file_path):
    tree = ET.parse(file_path)
    root=tree.getroot()
    vals=root[0][2].text  # this refers to the data we need
    vals = vals.strip().replace('\n','') # Removing the ending white spaces and new lines
    vals = re.sub(' +', ' ', vals).split(' ') # Removing the intermediate excess white spaces
    vals = map(float, vals) # Convert strings to floats
    x = vals[0::3]
    y = vals[1::3]
    prob = vals[2::3]
    return [x[1], y[1], x[4], y[4], x[7], y[7]]

base_ahrq_path = '..'
base_input_folder = os.path.join(base_ahrq_path, 'Results')

folders = os.listdir(base_input_folder)
folders = [folder for folder in folders if os.path.isdir(os.path.join(base_input_folder, folder))]

for folder in folders:
    folder_path = os.path.join(base_input_folder, folder)
    sub_folders = os.listdir(folder_path)
    sub_folders = [temp for temp in sub_folders if os.path.isdir(os.path.join(folder_path, temp))]
    for sub_folder in sub_folders:
        print '. ',
        left_files = glob.glob(os.path.join(folder_path, sub_folder, '*hand_left*'))
        right_files = glob.glob(os.path.join(folder_path, sub_folder, '*hand_right*'))
        pose_files = glob.glob(os.path.join(folder_path, sub_folder, '*pose*'))
        # left_data = [conv_xml(file) for file in left_files]
        # right_data = [conv_xml(file) for file in right_files]

        # start_time = time.time()
        pose_data = [conv_xml(file) for file in pose_files]
        # print 'Time taken per xml file: ', len(pose_files), ': ', (time.time()-start_time)
        with open(os.path.join(folder_path, sub_folder+'.pkl'), 'wb') as fid:
            pickle.dump(pose_data, fid)
