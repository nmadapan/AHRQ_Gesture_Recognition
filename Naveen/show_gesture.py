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
parser.add_argument("-c", "--command_id",
					default='1_1',
					help=("Command ID. For example: 4_1"))
parser.add_argument("-p", "--data_path",
					default=r'G:\AHRQ\Study_IV\NewData',
					help=("Data path to the folders containing L2/6/8..."))

### Arguments
args = vars(parser.parse_args())
lexicon_id = args['lexicon_id']
command_id = args['command_id']
data_path = args['data_path']

commands_json_path = 'commands.json'
commands_dict = json_to_dict(commands_json_path)
command_name = commands_dict[command_id]

lexicon_path = join(data_path, lexicon_id)

fname_pref = '_'.join([command_id, 'S2', lexicon_id])
video_path = glob(join(lexicon_path, fname_pref+'*_rgb.avi'))[0]

if(not isfile(video_path)):
	sys.exit(video_path + ' does NOT exist!')

cv2.namedWindow(command_name)
vcap = cv2.VideoCapture(video_path)

while True:
	ret, frame = vcap.read()
	if(not ret):
		vcap.release()
		vcap = cv2.VideoCapture(video_path)
		continue
	frame = cv2.putText(frame, command_name, (frame.shape[1]/3,frame.shape[0]/8), cv2.FONT_HERSHEY_SIMPLEX, 4, (120,50,120), 4, cv2.LINE_AA)
	frame = cv2.resize(frame, None, fx = 0.5, fy = 0.5)
	cv2.imshow(command_name, frame)
	if cv2.waitKey(1000/30) == ord('q'):
		cv2.destroyAllWindows()
		break
