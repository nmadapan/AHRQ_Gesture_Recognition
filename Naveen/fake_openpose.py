"""
 Fake open pose
"""
import os,sys,glob,re,cv2,json
import numpy as np
# from utils import *
import time

def extract_fingers_realtime(image):
	# Takes image of form (num_rows, num_columns, num_channels) : ndarray
	time.sleep(3)
	return np.random.rand(10)