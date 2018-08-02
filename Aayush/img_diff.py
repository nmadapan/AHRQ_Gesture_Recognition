import numpy as np
import cv2
import os

def get_bbox(before, after, thresholds = None, draw = False):
	########
	# Input Arguments:
	# 	before, after: path to the image before right click, and after right click OR
	# 	before, after: numpy image before right click, and after right click
	# 	thresholds: tuple (x_thresh, y_thresh). thresholds in both x and y directions
	# 	draw: True, display the bounding box. False, do not display
	#
	# Output Arguments:
	# (x1, y1, x2, y2): where x1, y1 are top left corner and x2, y2 are bottom right corner
	########

	# Type of before and after should be same
	if(type(before) != type(after)):
		return ValueError('before and after should have same type')

	# If both are strings
	if(isinstance(before, str)):
		if(not os.path.isfile(before)):
			sys.exit(before + ' does NOT exist')
		if(not os.path.isfile(after)):
			sys.exit(after + ' does NOT exist')
		before = cv2.imread(before)
		after = cv2.imread(after)
	elif(isinstance(before, np.ndarray)):
		assert before.ndim == 3 and after.ndim == 3, 'before and after needs to be rgb arrays'
		assert (before.shape[0] == after.shape[0]) and (before.shape[1] == after.shape[1]),\
			 'before and after arrays should be of same dimension'

	dif = cv2.cvtColor(np.uint8(np.abs(after - before)), cv2.COLOR_BGR2GRAY)
	_, dif = cv2.threshold(dif,127,255,0)

	x_sum = np.mean(dif, axis = 0)
	y_sum = np.mean(dif, axis = 1)

	if(thresholds == None):
		x_thresh = np.mean(x_sum)
		y_thresh = x_thresh
	else:
		x_thresh = thresholds[0]
		y_thresh = thresholds[1]

	x_sum, y_sum = x_sum > x_thresh, y_sum > y_thresh

	x1, x2 = np.argmax(x_sum), x_sum.size - np.argmax(np.flip(x_sum, 0)) - 1
	y1, y2 = np.argmax(y_sum), y_sum.size - np.argmax(np.flip(y_sum, 0)) - 1

	if(draw):
		after = cv2.rectangle(after,(x1,y1),(x2,y2),(0,255,0),4)
		cv2.imshow('Frame', cv2.resize(after, None, fx=0.5, fy=0.5))
		cv2.waitKey(0)

	return (x1, y1, x2, y2)

before, after = os.path.join('.', 'Images', 'beforeRight.png'), os.path.join('.', 'Images', 'afterRight.png')
x1, y1, x2, y2 = get_bbox(before, after, thresholds = (100, 30), draw = False)
# print get_bbox(before, after)

# before = cv2.imread(before)
# after = cv2.imread(after)
# print get_bbox(before, after, draw = True)

