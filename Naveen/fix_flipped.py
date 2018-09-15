import cv2
import numpy as np
from glob import glob
from os.path import join
from helpers import *
from copy import deepcopy
import math

###
# Use 'n' for next video
# Use 'p' for previous video
# Use 'q' or 'escape' for exit
###

## Global Variables
# Directory for reading the data that might be possibly flipped
lex_folder = r'G:\AHRQ\Study_IV\Data\L2' 
target_folder = r''
fps = 120
default_width, default_height = 1920/2, 1080/2
# Initialize the dictionary where the video paths and location information
# will be stored
videos_per_cmd = {}
# The current command being evaluated
current_cmd = None 

## Functions

# Stores the clicks triggered by mouse events
# event: mouse event
# x: x coorninate of the click
# y: y coordinate if the click
def store_clicks(event, x, y, flags, param):
	# grab references to the global variables
	global videos_per_cmd
	global current_cmd
	frame_w, frame_h, max_win_size = param
	# if the left mouse button was clicked, toggle the video
	# selector to true 
	if event == cv2.EVENT_LBUTTONDOWN and \
		isinstance(vid_descriptor_list[0],(list,)):
		# Get video number
		col = x/frame_w
		row = y/frame_h
		index = row*max_win_size+col
		if index < len(videos_per_cmd[current_cmd]):
				videos_per_cmd[current_cmd][index][2] = not videos_per_cmd[current_cmd][index][2] 

## Initialization
cmd_dict = json_to_dict('commands.json')
all_cmds = sorted(cmd_dict.keys(), cmp=class_str_cmp)
cmds = deepcopy(all_cmds)
container_frame = []
cmd_key_list = []

for cmd in all_cmds:
	matching_videos = glob(join(lex_folder, cmd+'*_rgb.avi'))
	if matching_videos:
		videos_per_cmd[cmd] = matching_videos
		cmd_key_list.append(cmd)

max_num_inst = max(map(len,videos_per_cmd.values()))
# Fix the size of the window that will display the videos
max_win_size = int(math.ceil(math.sqrt(max_num_inst)))

# get the frame size for each video 
frame_w = default_width/(max_win_size) 
frame_h = default_height/(max_win_size)

# Initialize the window so we can attach the
# the mouse callback to it
window_name = "image"
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, store_clicks,[frame_w,frame_h, max_win_size])

# create the container frame that will hold all the videos
for _ in range(max_win_size):
	temp = [255 * np.ones((frame_h, frame_w, 3)) for _ in range(max_win_size)]
	container_frame.append(temp)

close_flag = False
cmd_idx = 0
while(True):
	if(close_flag): break
	current_cmd = cmd_key_list[cmd_idx]
	cmd_name = cmd_dict[current_cmd]
	vid_descriptor_list = videos_per_cmd[current_cmd] 
	# Add a variable for the position in the image and if the video 
	# was selected next to the video path
	if not isinstance(vid_descriptor_list[0],(list,)): 
		videos_per_cmd[current_cmd] = [[vid_path, None, False] \
		for vid_path in vid_descriptor_list]	
		vid_descriptor_list = videos_per_cmd[current_cmd]
	# get a video capture for each video in the list
	vid_list = [descriptor[0] for descriptor in vid_descriptor_list]
	vcaps = [(os.path.basename(vid).split('_')[2], cv2.VideoCapture(vid)) for vid in vid_list]
	print "vcaps: ", vcaps
	while(True and (not close_flag)):
		for idx, vcap_info in enumerate(vcaps):
			name, vcap = vcap_info
			# get row and column position of the element
			row = idx/max_win_size 
			col = idx%max_win_size 
			# record the position of the video in the frame descriptor
			videos_per_cmd[current_cmd][idx][1] = (row,col)
			ret, frame = vcap.read()
			if ret: 
				frame = cv2.resize(frame, dsize=(frame_w, frame_h))
				# if the video was selected
				if videos_per_cmd[current_cmd][idx][2]:
					gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
					frame = np.stack((gray_image,)*3, -1)
				cv2.putText(frame,name, (frame.shape[1]/8,frame.shape[0]/8), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,50,0),1,cv2.LINE_AA) 
			else: frame = 255*np.ones((frame_h, frame_w, 3))
			container_frame[row][col] = np.uint8(frame)
		cframe = []
		for sublist in container_frame: cframe.append(np.concatenate(sublist, axis = 1))
		cframe = np.concatenate(cframe, axis = 0)
		cv2.putText(cframe,cmd_name, (default_width/(max_win_size+1), 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (120,50,220),2,cv2.LINE_AA)
		cv2.imshow(window_name, np.uint8(cframe))

		key = cv2.waitKey(1000/fps)
		if(key in [ord('q'), 27]): close_flag = True
		if(key in [ord('n'), ord('N')]): cmd_idx += 1; break
		if(key in [ord('p'), ord('P')]): cmd_idx -= 1; break
	if(cmd_idx<0): cmd_idx = 0
	if(cmd_idx>=len(cmds)): cmd_idx = len(cmds) - 1

	for vcap in vcaps: vcap[1].release()

# Write the flipped version of the files in the target folder