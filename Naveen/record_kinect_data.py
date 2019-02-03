from __future__ import print_function
import numpy as np
from helpers import *
import cv2
import os, sys, time, copy
from os.path import basename, dirname, splitext, isfile, join, isdir
from KinectReader import kinect_reader
from XefParser import Parser
from glob import glob

######################################
########## INITIALIZATION ############
######################################
lexicon_id = 'L21'
base_write_folder = r'D:\AHRQ\Study_IV\RealData'
subject_id = None

val = raw_input('Are you sure it is '+lexicon_id+' ?')
if(val in ['q','Q','n','N']):
	sys.exit('Exiting!!')

lexicon_path = join(base_write_folder, lexicon_id)

if(not isdir(base_write_folder)): os.makedirs(base_write_folder)

if(subject_id is None):
	if(not isdir(lexicon_path)):
		subject_id = 1
	else:
		files_path = glob(join(lexicon_path, '*'))
		existing_subject_ids = list(set([int(float(basename(file_path).split('_')[2][1:])) for file_path in files_path]))
		sorted(existing_subject_ids)
		if(len(existing_subject_ids) != 0):
			subject_id = existing_subject_ids[-1]+1
		else:
			subject_id = 1

xef_file_name = 'A_A_S' + str(subject_id) + '_' + lexicon_id + '_A_A.xef'

print('Subject ID: ', 'S'+str(subject_id))
print('Lexicon ID: ', lexicon_id)

parser = Parser(xef_file_name, base_write_folder, in_format_flag = True, display = True)
parser.parse()
