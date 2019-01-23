import cv2
import numpy as np
from glob import glob
from os.path import join, basename, dirname
from helpers import *
from copy import deepcopy
###
# Use 'n' for next video
# Use 'p' for previous video
# Use 'q' or 'escape' for exit
###

## Global Variables

lexicon_id = 'L11'
lex_folders = [r'G:\AHRQ\Study_IV\NewData2'] # Where to write the files
enable_skeleton = True
fps = 180
default_width, default_height = 1920, 1080

## Initialization
cmd_dict = json_to_dict('commands.json')
all_cmds = sorted(cmd_dict.keys(), cmp=class_str_cmp)
cmds = deepcopy(all_cmds)
class_dict = {}
bframe = []

lex_folders = [join(lex_folder, lexicon_id) for lex_folder in lex_folders]

def synchronize(color_skel_files_list):
	'''
	Description: synchronize the RGB timestamps with SKELETON timestamps.
	Input arguments:
		* color_skel_files: A list of absolute pats to the color skeleton files.
			An example file looks like 'a\\b\\1_0_S1_L2_x_x_color.txt'
	Return:
		* rgb_to_skel_list: Same sized list as color_skel_files_list.
			Each element is an numpy array containing synchronization information.
			Each value in the numpy array corresponds to the row id of color skeleton file \
			that corresponds to the current rgb image.
		* skel_data_list: Same sized list as color_skel_files_list.
			Each element is a 2D np.ndarray. Each row is 50 dim vector.
			25 joints and (x,y) for each joint.
			No. of rows is no. of frames.
	'''
	rgb_to_skel_list = []
	skel_data_list = []
	for idx, cskel_file in enumerate(color_skel_files_list):
		with open(cskel_file, 'r') as fp:
			skel_data = [map(float, line.split(' ')) for line in fp.readlines()]
		skel_data_list.append(np.array(skel_data))
		dir_path = dirname(cskel_file)
		fname = basename(cskel_file)
		rgb_fname = '_'.join(fname.split('_')[:-1]) + '_rgbts.txt'
		rgb_fpath = join(dir_path, rgb_fname)
		skel_fname = '_'.join(fname.split('_')[:-1]) + '_skelts.txt'
		skel_fpath = join(dir_path, skel_fname)

		with open(rgb_fpath, 'r') as fp:
			rgb_ts = np.array(fp.readlines()).astype(np.float32)

		with open(skel_fpath, 'r') as fp:
			skel_ts = np.array(fp.readlines()).astype(np.float32)

		on_skel, on_rgb = sync_ts(skel_ts, rgb_ts)
		rgb_to_skel_list.append(np.array(on_skel))
	return rgb_to_skel_list, skel_data_list

for cmd in all_cmds:
	vids = []
	for lex_folder in lex_folders: vids += glob(join(lex_folder, cmd+'*_rgb.avi'))
	if(len(vids)==0) : cmds.remove(cmd); continue
	class_dict[cmd] = len(list(set(vids)))

try:
	if(len(class_dict) == 0):
		raise Exception('No Videos Present !!')
except Exception as exp:
	print exp
	sys.exit()

expect_num_inst = max(class_dict.values())
M = int(np.ceil(np.sqrt(expect_num_inst)))
N = M
print M, ' X ', N, ' Window'

des_w, des_h = default_width/(N+2), default_height/(M+2)

for _ in range(M):
	temp = []
	for _ in range(N):
		temp.append(255 * np.ones((des_h, des_w, 3)))
	bframe.append(temp)

close_flag = False
cmd_idx = 0
while(True):
	cmd = cmds[cmd_idx]

	## Resetting the bframe
	for idx1 in range(len(bframe)):
		for idx2 in range(len(bframe[0])):
			bframe[idx1][idx2][:] = 255 * np.ones((des_h, des_w, 3))

	if(close_flag): break

	vids = []
	for lex_folder in lex_folders:
		vids += glob(join(lex_folder, cmd+'*_rgb.avi'))
	vids = list(set(vids)) ## Eliminate the duplicates
	vids = sorted(vids, cmp = subject_str_cmp)

	if(enable_skeleton):
		color_skel_files = []
		for lex_folder in lex_folders:
			color_skel_files += glob(join(lex_folder, cmd+'*_color.txt'))
		color_skel_files = list(set(color_skel_files)) ## Eliminate the duplicates
		color_skel_files = sorted(color_skel_files, cmp = subject_str_cmp)
		rgb_to_skel_list, skel_data_list = synchronize(color_skel_files)

	vcaps = [(os.path.basename(vid).split('_')[2], cv2.VideoCapture(vid)) for vid in vids]
	counter = [0]*len(vcaps)

	while(True and (not close_flag)):
		for idx, vcap_info in enumerate(vcaps):
			name, vcap = vcap_info
			j = idx/M
			i = idx - M * j
			ret, frame = vcap.read()

			if ret:
				if(enable_skeleton):
					skel_idx = rgb_to_skel_list[idx][counter[idx]]
					skel_pts = skel_data_list[idx][skel_idx, :]
					frame = draw_body(frame, skel_pts)
				frame = cv2.resize(frame, dsize=(des_w, des_h))
				cv2.putText(frame, name, (frame.shape[1]/8,frame.shape[0]/8), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,50,0),1,cv2.LINE_AA)
			else:
				frame = 255*np.ones((des_h, des_w, 3))
			bframe[i][j] = np.uint8(frame)
			counter[idx] += 1
		cframe = []
		for sublist in bframe: cframe.append(np.concatenate(sublist, axis = 1))
		cframe = np.concatenate(cframe, axis = 0)
		cv2.putText(cframe,cmd_dict[cmd], (cframe.shape[1]/3, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (120,50,220),2,cv2.LINE_AA)
		cv2.imshow('Full Frame', np.uint8(cframe))

		key = cv2.waitKey(1000/fps)

		if(key in [ord('q'), 27]): close_flag = True
		if(key in [ord('n'), ord('N')]): counter = [0]*len(vcaps); cmd_idx += 1; break
		if(key in [ord('p'), ord('P')]): counter = [0]*len(vcaps); cmd_idx -= 1; break

	if(cmd_idx<0): cmd_idx = 0
	if(cmd_idx>=len(cmds)): cmd_idx = len(cmds) - 1

	for vcap in vcaps: vcap[1].release()
