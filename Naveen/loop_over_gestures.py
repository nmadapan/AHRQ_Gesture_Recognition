import cv2
import numpy as np
from glob import glob
from os.path import join, isfile, dirname, basename
from helpers import *
from copy import deepcopy
import argparse

##########################
#####   PARSING       ####
##########################
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lexicon_id",
					default='L2',
					help=("Lexicon ID. For example: L2"))
parser.add_argument("-s", "--subject_id",
					default='S3',
					help=("Subject ID. For example: S2"))
parser.add_argument("-p", "--data_path",
					default=r'G:\AHRQ\Study_IV\NewData',
					help=("Data path to the folders containing L2/6/8..."))

### Arguments
fps = 20
args = vars(parser.parse_args())
lexicon_id = args['lexicon_id']
data_path = args['data_path']
subject_id = args['subject_id']

## Initialization
cmd_dict = json_to_dict('commands.json')
all_cmds = sorted(cmd_dict.keys(), cmp=class_str_cmp)
cmds = deepcopy(all_cmds)

lexicon_path = join(data_path, lexicon_id)

for cmd in all_cmds:
	vids = glob(join(lexicon_path, cmd+'*_rgb.avi'))
	if(len(vids)==0): cmds.remove(cmd); continue

cv2.namedWindow(lexicon_id)

close_flag = False
cmd_idx = 0

while not close_flag:
	cmd = cmds[cmd_idx]
	vid = glob(join(lexicon_path, cmd+'*'+subject_id+'*_rgb.avi'))[0]
	vcap = cv2.VideoCapture(vid)
	counter = 0
	while not close_flag:
		ret, frame = vcap.read()
		if(ret):
			counter += 1
			frame = cv2.putText(frame, cmd_dict[cmd], (frame.shape[1]/4,frame.shape[0]/8), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,50,0), 4,cv2.LINE_AA)
			frame = cv2.resize(frame, None, fx = 0.5, fy = 0.5)
			cv2.imshow(lexicon_id, frame)
		else:
			vcap.release()
			vcap = cv2.VideoCapture(vid)

		key = cv2.waitKey(1000/fps)

		if(key in [ord('q'), 27]): close_flag = True
		if(key in [ord('n'), ord('N')]): counter = 0; cmd_idx += 1; break
		if(key in [ord('p'), ord('P')]): counter = 0; cmd_idx -= 1; break

	if(cmd_idx < 0): cmd_idx = 0
	if(cmd_idx >= len(cmds)): cmd_idx = len(cmds) - 1
	vcap.release()
