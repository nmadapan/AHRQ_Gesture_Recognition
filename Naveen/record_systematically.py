import cv2
import numpy as np
from glob import glob
from os.path import join, isfile, dirname, basename
from helpers import *
from KinectReader import kinect_reader
from copy import deepcopy
import argparse
from XefParser  import Parser
from threading import Thread

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
parser.add_argument("-wp", "--write_path",
					default=r'G:\AHRQ\Study_IV\SurgeonData',
					help=("Data path to the folders containing L2/6/8..."))

### Arguments
fps = 20
args = vars(parser.parse_args())
lexicon_id = args['lexicon_id']
subject_id = args['subject_id']
data_path = args['data_path']
write_path = args['write_path']

## Initialization
cmd_dict = json_to_dict('commands.json')
all_cmds = sorted(cmd_dict.keys(), cmp=class_str_cmp)
cmds = deepcopy(all_cmds)

lexicon_path = join(data_path, lexicon_id)

for cmd in all_cmds:
	vids = glob(join(lexicon_path, cmd+'*_rgb.avi'))
	if(len(vids)==0): cmds.remove(cmd); continue

cmd_names = cmds
window_key = None

def stream_rgb(kr):
	cv2.namedWindow('Recording Data')
	while True:
		rgb_flag = kr.update_rgb()
		if(rgb_flag):
			frame = deepcopy(kr.color_image)
			frame = cv2.resize(frame, None, fx = 0.5, fy = 0.5)
			cv2.imshow('Recording Data', frame)
		window_key = cv2.waitKey(1)
		if(window_key == ord('e')):
			cv2.destroyAllWindows()

if __name__ == '__main__':
	kr = kinect_reader()
	wait_for_kinect(kr)

	th_stream = Thread(name = 'stream_thread', target = stream_rgb, args = (kr, ))
	th_stream.start()

	cmd_idx = 0
	curr_status = False

	while True:
		cmd = cmd_names[cmd_idx]
		key = cv2.waitKey(1)
		if(key in [32, 10]): curr_status = True
		## If prev status is false and curr status is true
		if(curr_status):
			xef_file_name = '_'.join(cmd, subject_id, lexicon_id, cmd_dict[cmd]+.xef)
			parser = Parser(xef_file_name, write_path, in_format_flag = True, display = True)
			parser.parse()
		curr_status = False

		inp = raw_input('Accept(y)/Reject(n)')
		if(inp in ['y', 'Y', 10]):
			## Leave the files as they are
			cmd_idx += 1
			pass
		else:
			## Rename the files
			pass
