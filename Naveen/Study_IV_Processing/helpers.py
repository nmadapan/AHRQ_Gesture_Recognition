from __future__ import print_function

from glob import glob
import os, sys, time
from os.path import basename, dirname, join, isfile, isdir
import numpy as np
import json
from scipy.interpolate import interp1d
import cv2
import re
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from copy import deepcopy

def json_to_dict(json_filepath):
	if(not os.path.isfile(json_filepath)):
		raise IOError('Error! Json file: '+json_filepath+' does NOT exists!')
	with open(json_filepath, 'r') as fp:
		var = json.load(fp)
	return var

def class_str_cmp(str1, str2):
	'''
	Description:
		Compare two class_strings. Format of the class_string is the following: ('4_1'). Refer to commands.json for all available class_strings.
	Input arguments:
		* str1: a class string.
		* str2: a class string.
	Return:
		* Negative number if str2 is smaller than str1, positive number otherwise.
	Example usage:
		# class_str_cmp('4_1', '3_0')
		# 4_1 is supposed to come after 3_0. So it returns a negative number
	'''
	# str1 - 3_2, str_2 - 7_1
	# So 3_2 < 7_1
	c1, m1 = tuple(map(int, str1.split('_')))
	c2, m2 = tuple(map(int, str2.split('_')))
	if(c1==c2): return m1 - m2
	else: return c1 - c2

def lex_path_cmp(str1, str2):
	str1, str2 = basename(str1), basename(str2)
	return int(float(str1[1:])) - int(float(str2[1:]))

def lex_name_cmp(str1, str2):
	return int(float(str1[1:])) - int(float(str2[1:]))
