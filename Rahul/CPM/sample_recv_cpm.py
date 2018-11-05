# import tensorflow as tf
# from CpmClass import CpmClass
import socket
import sys
sys.path.insert(0, r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen')
from CustomSocket import Server
from CpmClass import CpmClass
import numpy as np

# set this flag if we normalized finger lengths are required.
# by default normalization constant is set to 300
normalize_finger_flag = True
normalization_constant = 300

def nparray_to_str(arr, dlim = '_'):
	return dlim.join(map(str, np.array(arr).flatten().tolist()))

base_images_dir = r'C:\Users\Rahul\convolutional-pose-machines-tensorflow-master\test_imgs'

####################
### Socket Setup  ##
####################
TCP_IP = 'localhost'
TCP_PORT = 3000
server = Server(TCP_IP, TCP_PORT, buffer_size = 1000000)

####################
### CPM Setup     ##
####################
inst = CpmClass(base_images_dir, display_flag = True)

# It waits here for hand shake
if(not server.connect_status): server.wait_for_connection()

socket.setdefaulttimeout(2.0)

while True:
	try:
		img_name = server.recv_data()
	except Exception as exp:
		print(exp)

	if(len(img_name) == 0): continue
	print('Received: ', img_name)
	joint_coord_set = inst.get_hand_skel(img_name)
	finger_lengths = inst.get_fing_lengths(joint_coord_set,normalize = normalize_finger_flag, normalization_const = normalization_constant)
	str_finger_lengths = nparray_to_str(finger_lengths)
	print(len(joint_coord_set))

	try:
		server.send_data(str_finger_lengths.encode('utf-8')) ## MAYBE we need to send a bytes array
	except Exception as exp:
		print(exp)
