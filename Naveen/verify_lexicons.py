import cv2
import numpy as np
from glob import glob
from os.path import join
import json
import sys
from helpers import *
from copy import deepcopy

###
# Use 'n' for next video
# Use 'p' for previous video
# Use 'q' or 'escape' for exit
###

## Global Variables
lex_folder = '..\\Data\\L3' # Where to write the files
fps = 30

## Initialization
cmd_dict = json_to_dict('commands.json')
all_cmds = sorted(cmd_dict.keys(), cmp=class_str_cmp)
cmds = deepcopy(all_cmds)
class_dict = {}
bframe = []

for cmd in all_cmds:
	vids = glob(join(lex_folder, cmd+'*_rgb.avi'))
	if(len(vids)==0) : cmds.remove(cmd); continue
	class_dict[cmd] = len(vids)

expect_num_inst = max(class_dict.values())
print 'Max no. of instances : ' + str(expect_num_inst)
print 'Min no. of instances : ' + str(min(class_dict.values()))

if(expect_num_inst <= 6): M = 2
else: M = 3

if(expect_num_inst%2 == 1):	N = 1 + expect_num_inst/M
else: N = expect_num_inst/M

for _ in range(M):
	temp = []
	for _ in range(N):
		temp.append(np.zeros((1080/(M+1), 1920/(N+1), 3)))
	bframe.append(temp)

# for key, value in class_dict.items():
# 	if(value != expect_num_inst):
# 		print 'Error! '+key+' : '+str(value)

close_flag = False
cmd_idx = 0
while(True):
	cmd = cmds[cmd_idx]
	if(close_flag): break

	vids = glob(join(lex_folder, cmd+'*_rgb.avi'))
	vcaps = [cv2.VideoCapture(vid) for vid in vids]
	while(True and (not close_flag)):
		for idx, vcap in enumerate(vcaps):
			j = idx/M
			i = idx - M * j
			ret, frame = vcap.read()
			if ret: frame = cv2.resize(frame, None, fx = 1.0/(N+1), fy = 1.0/(M+1))
			else: frame = np.zeros((1080/(M+1), 1920/(N+1), 3))
			bframe[i][j] = np.uint8(frame)
		cframe = []
		for sublist in bframe: cframe.append(np.concatenate(sublist, axis = 1))
		cframe = np.concatenate(cframe, axis = 0)
		cv2.putText(cframe,cmd_dict[cmd], (1920/(N+2), 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (120,50,220),3,cv2.LINE_AA)
		cv2.imshow('Full Frame', np.uint8(cframe))

		key = cv2.waitKey(1000/fps)
		if(key in [ord('q'), 27]): close_flag = True
		if(key in [ord('n'), ord('N')]): cmd_idx += 1; break
		if(key in [ord('p'), ord('P')]): cmd_idx -= 1; break
	if(cmd_idx<0): cmd_idx = 0
	if(cmd_idx>=len(cmds)): cmd_idx = len(cmds) - 1

	for vcap in vcaps: vcap.release()



