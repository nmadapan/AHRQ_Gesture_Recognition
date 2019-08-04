from PIL import ImageGrab
import numpy as np
import cv2
import os
from os.path import join, basename, dirname, isdir
import time
import argparse

######################################
########## INITIALIZATION ############
######################################
lexicon_id = 'L0'
subject_id = 'S22'
task_id = 'T1'
base_write_folder = r'D:\AHRQ\Study_V\Study_V_Data'

##########################
#####   PARSING       ####
##########################
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lexicon_id", default=lexicon_id,
					help=("Example: L1"))
parser.add_argument("-s", "--subject_id", default=subject_id,
					help=("Example: S1"))
parser.add_argument("-t", "--task_id", default=task_id,
					help=("Example: T1"))
args = vars(parser.parse_args())

subject_id = args['subject_id']
lexicon_id = args['lexicon_id']
task_id = args['task_id']

fname = '_'.join([subject_id, lexicon_id, task_id])
folder_path = join(base_write_folder, lexicon_id)

if(not isdir(folder_path)): os.mkdir(folder_path)

fps = 30.0
res = (1920, 1080)
display = False

cur_time = str(int(time.time()))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
vid_path = join(folder_path, fname + '_screen_' + cur_time + '.avi')
ts_path = join(folder_path, fname+'_screents_'+cur_time+'.txt')

out = cv2.VideoWriter(vid_path, fourcc, fps, res)
ts_file = open(ts_path, 'w')

while(True):
	try:
		img = ImageGrab.grab(bbox=(0,0,res[0],res[1])) # bbox specifies specific region (bbox= x,y,width,height)
		img_np = np.array(img)
		img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
		out.write(img_np)
		ts_file.write(str(time.time()) + '\n')
		if display:
			cv2.imshow('frame',cv2.resize(img_np, None, fx = 0.5, fy = 0.5))
			if cv2.waitKey(1) == ord('q'):
				break
	except KeyboardInterrupt:
		print('Ctrl+C encountered! Exiting!!')
		break

ts_file.flush()
ts_file.close()
out.release()
if display: cv2.destroyAllWindows()
print('Video written to:  ', vid_path)