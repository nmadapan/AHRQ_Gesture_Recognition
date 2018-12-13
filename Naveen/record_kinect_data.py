import numpy as np
from helpers import *
import cv2
import os, sys, time, copy
from os.path import basename, dirname, splitext, isfile
from KinectReader import kinect_reader
from XefParser import Parser

xef_file_name = '9_9_S21_L21_X_X.xef'
base_write_folder = r'H:\AHRQ\Study_IV\RealData'
in_format_flag = True

parser = Parser(xef_file_name, base_write_folder, in_format_flag = in_format_flag, display = True)
parser.parse()
