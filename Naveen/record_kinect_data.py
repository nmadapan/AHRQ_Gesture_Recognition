from __future__ import print_function
import numpy as np
from helpers import *
import cv2
import os, sys, time, copy
from os.path import basename, dirname, splitext, isfile, join, isdir
from KinectReader import kinect_reader
from XefParser import Parser
from glob import glob
import argparse

######################################
########## INITIALIZATION ############
######################################
lexicon_id = 'L6'
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
lexicon_id = args['lexicon_id']
subject_id = args['subject_id']
task_id = args['task_id']

## Path to the lexicon
lexicon_path = join(base_write_folder, lexicon_id)

## Check if the files already exist
existing_files_path = glob(join(lexicon_path, \
	'_'.join([subject_id, lexicon_id, task_id]) + '*'))
if(len(existing_files_path) != 0):
	val = raw_input('_'.join([subject_id, lexicon_id, task_id]) \
		+ ' exists !! \n' + 'Do you want to continue incrementing subject id ?')
	if(val in ['q','Q','n','N']):
		sys.exit('Exiting!!')

if(not isdir(base_write_folder)): os.makedirs(base_write_folder)
if(not isdir(lexicon_path)):
	if subject_id is None: subject_id = 'S1'
else:
	files_path = glob(join(lexicon_path, \
	'_'.join(['S*', lexicon_id, task_id]) + '*'))
	existing_subject_ids = list(set([int(float(basename(file_path).split('_')[0][1:])) \
		for file_path in files_path]))
	print(existing_subject_ids)
	if(len(existing_subject_ids) != 0):
		if(int(float(subject_id[1:])) in existing_subject_ids):
			subject_id = 'S' + str(max(existing_subject_ids)+1)
	elif subject_id is None: subject_id = 'S1'

xef_file_name = 'A_A_' + str(subject_id) + '_' + lexicon_id + '_A_A'
after_file_name = '_'.join([subject_id, lexicon_id, task_id])

print('Subject ID: ', subject_id)
print('Lexicon ID: ', lexicon_id)
print('Task ID: ', task_id)

parser = Parser(xef_file_name + '.xef', base_write_folder, in_format_flag = True, display = True)
parser.parse()

## Renaming the files properly
all_files_paths = glob(join(lexicon_path, xef_file_name+'*.*'))

for fpath in all_files_paths:
	nfpath = deepcopy(fpath)
	nfpath = nfpath.replace(xef_file_name, after_file_name)
	# print fpath, nfpath
	if(isfile(nfpath)):
		nfpath = nfpath.replace(subject_id, 'S'+str(int(float(subject_id[1:]))+1))
	try:
		os.rename(fpath, nfpath)
	except Exception as exp:
		print('Rename ', basename(fpath), ' manually')