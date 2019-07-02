import cv2
import numpy as np
from glob import glob
from os.path import join, isfile, dirname, basename, splitext
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
					default='S7',
					help=("Subject ID. For example: S2"))
parser.add_argument("-p", "--data_path",
					default=r'H:\AHRQ\Study_IV\NewData2',
					help=("Data path to the folders containing L2/6/8..."))
parser.add_argument("-wp", "--write_path",
					default=r'H:\AHRQ\Study_IV\SurgeonData',
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
print('No. of commands: ', len(cmd_names))

if __name__ == '__main__':
	cmd_idx = 0
	reject_counter = 0

	while True:
		if(cmd_idx >= len(cmd_names)): break
		cmd = cmd_names[cmd_idx]
		value = raw_input('Do you want to continue? (Y/N): ')
		if(value in ['y', 'Y']):
			print 'Recording: ', cmd_dict[cmd]
			name = cmd_dict[cmd]
			if(len(name.split(' ')) == 2):
				name = '_'.join(name.split(' '))
			elif(len(name.split(' ')) == 1):
				name = name + '_X'
			xef_file_name = '_'.join([cmd, subject_id, lexicon_id, name + '.xef'])
			print xef_file_name
			parser = Parser(xef_file_name, write_path, in_format_flag = True, display = True)
			parser.parse()
		
			inp = raw_input('Accept(y)/Reject(n): ')
			if(inp in ['y', 'Y']):
				reject_counter = 0
				cmd_idx += 1
			else:
				reject_counter += 1
				## Rename the files
				curr_files = glob(join(join(write_path, lexicon_id), splitext(xef_file_name)[0] + '*'))
				curr_files = [cfile for cfile in curr_files if 'reject' not in cfile] 
				for curr_file in curr_files:
					old_path = curr_file
					fname, ext = splitext(basename(curr_file))[0], splitext(basename(curr_file))[1]
					new_path = join(join(write_path, lexicon_id), fname + '_reject' + str(reject_counter)+ ext)
					os.rename(old_path, new_path)
		else:
			break