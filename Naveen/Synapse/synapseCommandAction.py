import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import ImageGrab
from PIL import ImageChops
import signal
import sys
import math
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import json


auto.FAILSAFE = True
auto.PAUSE = 0.25

(width, height) = tuple(float(e) for e in auto.size())
(nativeW, nativeH) = tuple(float(e) for e in ImageGrab.grab().size)
scale = nativeW / width
print "WxH: %s" % ((width, height),)
print "nativeW, nativeH: %s" % ((nativeW, nativeH),)
print str(scale)

(macH, viewer, prompt) = ((0, "\\\\Remote", "Command Prompt") if platform.system() == "Windows"
	else (44.0 * nativeW / 2880.0, "Citrix Viewer", "Terminal"))

# Should have been the following:
# border = (19.0 * nativeW / 2880.0) + (2.0 * scale) + 1.0
# On AHRQ Mac, this would be 19 + (2*2) + 1 = 24
# On AHRQ Dell, this would be 12.6666667 + 2 + 1 = 15.6666667
# Sticking with calculation below to be on the safer side, going to figure out later what the actual numbers should be
border = (20.0 * nativeW / 2880.0) + (4.0 * scale)
boundBoxNoDash = (border, macH + border, nativeW - border, nativeH - border)

calibrationPath = "calibration" + "_".join(list(str(e) for e in [width, height, scale])).replace(".", "-") + ".txt"

# Close all other windows and open either command prompt or the Citrix Viewer
def openWindow(toOpen):
	# Look into "start" command for Windows
	if (platform.system() == "Windows"):
		window_names = auto.getWindows().keys()
		for window_name in window_names:
			auto.getWindow(window_name).minimize()
			if (toOpen in window_name):
				xef_window_name = window_name
		xef_window = auto.getWindow(xef_window_name)
		xef_window.maximize()
	else: os.system("open -a " + toOpen.replace(" ", "\\ "))

#Remove images already saved (avoids issues with git)
def removeImages():
	paths = [os.path.join("SCA_Images", "RightClick"), os.path.join("SCA_Images", "Window", "Closes"),
		os.path.join("SCA_Images", "Window"), os.path.join("SCA_Images", "Layout"), os.path.join("SCA_Images")]
	for path in paths:
		if (not os.path.exists(path)): continue
		for file in os.listdir(path):
			if file.endswith(".png"): os.remove(os.path.join(path, file))
	os.remove(calibrationPath)

# Prompt notification if choosing to remove the images
def removeImagesPrompt():
	openWindow(prompt)
	(status["hold_action"], status["defaultCommand"], status["group1_command"]) = (None, None, None)
	f = open(calibrationPath, "w")
	f.write(json.dumps(status, indent=4, separators=(',', ': ')))
	f.close()
	while True:
		ans = raw_input("Do you want to remove the images saved in the folder? (y/n)")
		if (len(ans) == 1 and (ans.lower() == "y" or ans.lower() == "n")):
			if ans.lower() == "y": removeImages()
			break
		else: print "Unrecognized request, please enter either 'y' or 'n'"
	print ""

# If exiting the synapse program, remove all images before closing synapse.
def signal_handler(sig, frame):
	removeImagesPrompt()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# def get_bbox(before, after, thresholds = None, draw = False, num_bins=20):
	# if (type(before) != type(after)):
	# 	return ValueError('before and after should have same type')
	# if (isinstance(before, str)):
	# 	if (not os.path.isfile(before)):
	# 		sys.exit(before + ' does NOT exist')
	# 	if (not os.path.isfile(after)):
	# 		sys.exit(after + ' does NOT exist')
	# 	before = cv2.imread(before)
	# 	after = cv2.imread(after)
	# elif (isinstance(before, np.ndarray)):
	# 	assert before.ndim == 3 and after.ndim == 3, 'before and after needs to be rgb arrays'
	# 	assert (before.shape[0] == after.shape[0]) and (before.shape[1] == after.shape[1]),\
	# 		 'before and after arrays should be of same dimension'
	# ###########################
	# #### Tuning Params ########
	# noise_percentage = 0.25
	# percentage_bins_for_mean = 0.5
	# ##########################

	# noise_index = int(num_bins*noise_percentage)
	# remaining_mean = int(math.ceil((num_bins - noise_index)*percentage_bins_for_mean))
	# dif = cv2.cvtColor(np.uint8(np.abs(after - before)), cv2.COLOR_BGR2GRAY)
	# # _, dif = cv2.threshold(dif,127,255,0)

	# x_sum = np.mean(dif, axis = 0)
	# y_sum = np.mean(dif, axis = 1)
 
	# x_sum = medfilt(x_sum, 211)
	# y_sum = medfilt(y_sum, 211)

	# if (thresholds == None):
	# 	frequencies, avg_hist_values = np.histogram(x_sum, bins = num_bins)
	# 	sort_ids = np.argsort(frequencies[noise_index:])
	# 	x_thresh = np.mean(avg_hist_values[noise_index+sort_ids[:remaining_mean]])

	# 	# x_thresh = avg_hist_values[10]# np.argmin(frequencies)

	# 	frequencies, avg_hist_values = np.histogram(y_sum, bins = num_bins)
	# 	sort_ids = np.argsort(frequencies[noise_index:])
	# 	y_thresh = np.mean(avg_hist_values[noise_index+sort_ids[:remaining_mean]])
	# else:
	# 	x_thresh = thresholds[0]
	# 	y_thresh = thresholds[1]

	# print x_thresh, y_thresh
	# # plt.hist(y_sum, bins = 20)
	# # plt.plot(y_sum)
	# # plt.show()	
	# # sys.exit(0)
	# x_sum, y_sum = x_sum > x_thresh, y_sum > y_thresh

	# x1, x2 = np.argmax(x_sum), x_sum.size - np.argmax(np.flip(x_sum, 0)) - 1
	# y1, y2 = np.argmax(y_sum), y_sum.size - np.argmax(np.flip(y_sum, 0)) - 1

	# if (draw):
	# 	after = cv2.rectangle(after,(x1,y1),(x2,y2),(0,255,0),4)
	# 	cv2.imshow('Frame', cv2.resize(after, None, fx=0.5, fy=0.5))
	# 	cv2.waitKey(0)

	# return (x1, y1, x2, y2)
"""
	Input Arguments:
		before, after: path to the image before right click, and after right click OR
		before, after: numpy image before right click, and after right click
		thresholds: tuple (x_thresh, y_thresh). thresholds in both x and y directions
		draw: True, display the bounding box. False, do not display
	Output Arguments:
		(x1, y1, x2, y2): where x1, y1 are top left corner and x2, y2 are bottom right corner
"""
def get_bbox(before, after, thresholds = None, draw = False):
	if (type(before) != type(after)):
		return ValueError('before and after should have same type')
	if (isinstance(before, str)):
		if (not os.path.isfile(before)):
			sys.exit(before + ' does NOT exist')
		if (not os.path.isfile(after)):
			sys.exit(after + ' does NOT exist')
		before = cv2.imread(before)
		after = cv2.imread(after)
	elif (isinstance(before, np.ndarray)):
		assert before.ndim == 3 and after.ndim == 3, 'before and after needs to be rgb arrays'
		assert (before.shape[0] == after.shape[0]) and (before.shape[1] == after.shape[1]),\
			 'before and after arrays should be of same dimension'

	dif = cv2.cvtColor(np.uint8(np.abs(after - before)), cv2.COLOR_BGR2GRAY)
	_, dif = cv2.threshold(dif,127,255,0)

	x_sum = np.mean(dif, axis = 0)
	y_sum = np.mean(dif, axis = 1)

	if (thresholds == None):
		x_thresh = np.mean(x_sum)
		#y_thresh = x_thresh
		y_thresh = np.mean(y_sum)
	else:
		x_thresh = thresholds[0]
		y_thresh = thresholds[1]

	x_sum, y_sum = x_sum > x_thresh, y_sum > y_thresh

	x1, x2 = np.argmax(x_sum), x_sum.size - np.argmax(np.flip(x_sum, 0)) - 1
	y1, y2 = np.argmax(y_sum), y_sum.size - np.argmax(np.flip(y_sum, 0)) - 1

	if (draw):
		after = cv2.rectangle(after,(x1,y1),(x2,y2),(0,255,0),4)
		cv2.imshow('Frame', cv2.resize(after, None, fx=0.5, fy=0.5))
		cv2.waitKey(0)

	return (x1, y1, x2, y2)

if (not os.path.exists(calibrationPath)):
	status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1],
		"rulers": {"len": 0}, "toUse": "Keyboard", "hold_action": None, "defaultCommand": None, "group1_command": None}
else:
	f = open(calibrationPath, "r")
	status = json.loads(" ".join([line.rstrip('\n') for line in f]))
	f.close()

def resetPanelMoves():
	status["firstW"] = (float(width) / (float(status["panel_dim"][1]) * 2.0))
	status["firstH"] = (float(height) / (float(status["panel_dim"][0]) * 2.0))
	status["jumpW"] = (status["firstW"] * 2.0 if status["panel_dim"][1] != 1 else 0)
	status["jumpH"] = (status["firstH"] * 2.0 if status["panel_dim"][0] != 1 else 0)
resetPanelMoves()

def moveToActivePanel():
	moveToX = status["firstW"] + (status["active_panel"][1] - 1) * (status["jumpW"])
	moveToY = status["firstH"] + (status["active_panel"][0] - 1) * (status["jumpH"])
	auto.moveTo(moveToX, moveToY)

openWindow(viewer)

class Calibration(object):
	def __init__(self):
		if (os.path.exists(calibrationPath)):
			self.topBarHeight = status["topBarHeight"]
			self.optionH = status["optionH"]
			self.rightHR = status["rightHR"]
			self.rightPlus = status["rightPlus"]
			self.rightIcons = status["rightIcons"]
			self.rightOffset = status["rightOffset"]
			self.rightBoxW = status["rightBoxW"]
			self.rightBoxH = status["rightBoxH"]
		else:
			self.resetAll()
			(status["topBarHeight"], status["optionH"], status["rightHR"], status["rightPlus"], status["rightIcons"],
				status["rightOffset"], status["rightBoxW"], status["rightBoxH"]) = self.getAll()
			f = open(calibrationPath, "w")
			f.write(json.dumps(status, indent=4, separators=(',', ': ')))
			f.close()

	def getAll(self):
		return (self.topBarHeight, self.optionH, self.rightHR, self.rightPlus, self.rightIcons, self.rightOffset,
			self.rightBoxW, self.rightBoxH)
	
	def resetAll(self):
		print "\nWarming up synapse system...\n"
		self.resetTopBarHeight()
		self.resetRightClick()
		self.resetRightOptions("presets", 8.5)
		self.resetRightOptions("scaleRotateFlip", 9.5)
		print "\nCompleted warm-up, make your gestures!\n"

	# Reset height of top bar and save it
	def resetTopBarHeight(self):
		moveToActivePanel()
		auto.click()
		ImageGrab.grab(bbox=(0, macH, nativeW, nativeH)).save(os.path.join("SCA_Images", "fullscreen.png"))
		auto.moveTo(auto.position()[0], 0)
		time.sleep(1)
		ImageGrab.grab(bbox=(0, macH, nativeW, nativeH)).save(os.path.join("SCA_Images", "afterTopBar.png"))
		topBarBox = get_bbox(os.path.join("SCA_Images", "fullscreen.png"), os.path.join("SCA_Images", "afterTopBar.png"))
		self.topBarHeight = topBarBox[3] - topBarBox[1] + 1
		ImageGrab.grab(bbox=(0, macH, nativeW, self.topBarHeight + macH)).save(os.path.join("SCA_Images", "topBar.png"))

	# Reset the right click
	def resetRightClick(self):
		moveToActivePanel()
		auto.click()
		beforeRightPath = os.path.join("SCA_Images", "RightClick", "beforeRight.png")
		ImageGrab.grab(bbox=boundBoxNoDash).save(beforeRightPath)
		auto.click(button='right')
		time.sleep(1)
		afterRightPath = os.path.join("SCA_Images", "RightClick", "afterRight.png")
		ImageGrab.grab(bbox=boundBoxNoDash).save(afterRightPath)
		rightBox = get_bbox(beforeRightPath, afterRightPath)
		print "rightBox: %s" % (rightBox,)
		(self.rightBoxW, self.rightBoxH) = (rightBox[2] - rightBox[0] + 1, rightBox[3] - rightBox[1] + 1)
		print "rightBox WxH: %s" % ((self.rightBoxW, self.rightBoxH),)

		self.optionH = (self.rightBoxH * 36.0 / 1000.0) / scale
		self.rightHR = (self.rightBoxH * 10.0 / 1000.0) / scale
		self.rightPlus = (self.rightBoxH * 8.0 / 1000.0) / scale
		self.rightIcons = (self.rightBoxH * 50.0 / 1000.0)
		self.rightOffset = (self.rightBoxH * 58.0 / 1000.0)

		(rightx1, righty1) = (rightBox[0] + boundBoxNoDash[0], rightBox[1] + boundBoxNoDash[1])
		(x1, y1) = (rightx1 + self.rightIcons, righty1 + self.rightOffset)
		(x2, y2) = (rightx1 + self.rightBoxW, righty1 + self.rightBoxH)
		ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(os.path.join("SCA_Images", "RightClick", "rightClick.png"))

		moveToActivePanel()
		auto.click()

	# Reset rightClick's presets or its scaleRotateFlip
	def resetRightOptions(self, option, offset):
		moveToActivePanel()
		auto.click()
		auto.click(button='right')
		located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "rightClick.png"))
		if (located is not None): (rightx1, righty1, w, h) = located
		else:
			print "Cannot find " + option + " on calibration reset. Attempting reset on rightClick."
			self.resetRightClick()
			located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "rightClick.png"))
			if (located is not None): (rightx1, righty1, w, h) = located
			else:
				print "Failed to reset " + option + "."
				return
		moveToX = (rightx1 + w / 2.0) / scale
		moveToY = (righty1 / scale) + (self.optionH * offset) + self.rightHR
		auto.moveTo(moveToX, moveToY)
		time.sleep(1)
		moveToActivePanel()
		auto.press("0")
		afterRightPath = os.path.join("SCA_Images", "RightClick", "afterRight.png")
		afterOptionPath = os.path.join("SCA_Images", "RightClick", "after" + option + ".png")
		ImageGrab.grab(bbox=boundBoxNoDash).save(afterOptionPath)
		box = get_bbox(afterRightPath, afterOptionPath)
		print option + " box: %s" % (box,)
		(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
		print option + " box WxH: %s" % ((boxW, boxH),)
		(x1, y1) = (box[0], box[1])
		optionPath = os.path.join("SCA_Images", "RightClick", option + ".png")
		ImageGrab.grab(bbox=(x1 + self.rightIcons, y1, x1 + boxW, y1 + boxH)).save(optionPath)
		auto.click()


calibration = Calibration()

actionList = [["Admin", "Quit", "Get Status", "Switch ToUse", "Reset"],
	["Scroll", "Up", "Down"],
	["Flip", "Horizontal", "Vertical"],
	["Rotate", "Clockwise", "Counter-Clockwise"],
	["Zoom", "In", "Out"],
	["Switch Panel", "Left", "Right", "Up", "Down"],
	["Pan", "Left", "Right", "Up", "Down"],
	["Ruler", "Measure", "Delete"],
	["Window", "Open", "Close"],
	["Manual Contrast", "Increase", "Decrease"],
	["Layout", "One-Panel", "Two-Panels", "Three-Panels", "Four-Panels"],
	["Contrast Presets", "I", "II"]]

# Report situation to command prompt, useful for debugging and for users understanding an issue.
def promptNotify(message, sleepAmt):
	openWindow(prompt)
	print message
	time.sleep(sleepAmt)

# Find Synapse's rightClick image
def findRightClick(offset):
	located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "rightClick.png"))
	if (located is not None):
		(x1, y1, w, h) = located
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, (y1 + (offset / 1000.0) * status["rightBoxH"]) / scale)
		return True
	else:
		print "Error when performing right click function."
		return False

# TODO: for window open, layout
# Windows: wo at (326, 78) and layout at (642, 80)
#	topBarHeight == 176
# Mac: wo at (435 / 2, 151 / 2) and layout at (857 / 2, 153 / 2), with macH
#	Mac: wo at (435 / 2, 107 / 2) and layout at (857 / 2, 109 / 2), without macH
#	topBarHeight == 224 (native)
# 224 / 176 == 14 / 11 == 1.2727272727
def gestureCommands(sequence):
	(commandID, actionID) = (-1, -1)
	commandAction = sequence
	if (sequence.find(" ") != -1):
		commandAction = sequence[:sequence.find(" ")]
		status["params"] = sequence[sequence.find(" ") + 1:]
	elif (status["hold_action"] is None): status["params"] = ""
	if (commandAction.find("_") != -1):
		try:
			commandID = int(commandAction[:commandAction.find("_")])
			actionID = int(commandAction[commandAction.find("_") + 1:])
			command = actionList[commandID][0]
			action = actionList[commandID][actionID]
		except ValueError:
			print "Unrecognized sequence of commands!\n"
			return False
		except IndexError:
			print "Incorrect commands!\n"
			return False
	else:
		print "Invalid command entered!\n"
		return False
	
	if (status["defaultCommand"] != command): status["defaultCommand"] = None
	if (status["group1_command"] != command): status["group1_command"] = None
	if (status["defaultCommand"] is None and status["group1_command"] is None): auto.mouseUp()

	if (command == "Admin" and action != "Admin"):
		if (action == "Quit"):
			removeImagesPrompt()
			sys.exit(0)
		elif (action == "Get Status"):
			print "------\nStatus\n------"
			print "Previous action: " + status["prev_action"]
			print "Panel Dimension: " + str(status["panel_dim"][0]) + 'x' + str(status["panel_dim"][1])
			print "Active panel: " + str(status["active_panel"][0]) + 'x' + str(status["active_panel"][1])
			print "Patient information window: " + ("opened" if status["window_open"] else "closed")
			print ""
		elif (action == "Switch ToUse"):
			status["toUse"] = ("key_shorts" if status["toUse"] == "img_recog" else "SCA_Images")
		elif (action == "Reset"):
			if (status["params"] == "All"):
				calibration.resetAll()
			if (status["params"] == "TopBar"):
				calibration.resetTopBarHeight()
			elif (status["params"] == "RightClick"):
				calibration.resetRightClick()
			elif (status["params"] == "Presets"):
				calibration.resetRightOptions("presets", 8.5)
			elif (status["params"] == "ScaleRotateFlip"):
				calibration.resetRightOptions("scaleRotateFlip", 9.5)
			(status["topBarHeight"], status["optionH"], status["rightHR"], status["rightPlus"], status["rightIcons"],
				status["rightOffset"], status["rightBoxW"], status["rightBoxH"]) = calibration.getAll()
			f = open(calibrationPath, "w")
			f.write(json.dumps(status, indent=4, separators=(',', ': ')))
			f.close()
			if (status["hold_action"] is not None):
				sequence = status["hold_action"]
				status["hold_action"] = "held"
				return gestureCommands(sequence)
	elif (command == "Scroll" and action != "Scroll"):
		moveToActivePanel()
		auto.click()
		scrollAmount = (50 if status["params"] == "" else int(status["params"]))
		auto.PAUSE = 0
		for i in range(scrollAmount): auto.press("right" if action == "Up" else "left")
		auto.PAUSE = 0.25
		auto.click()
	elif (command == "Flip" and action != "Flip"):
		moveToActivePanel()
		auto.click(button='right')
		if (status["toUse"] == "img_recog"):
			located = findRightClick(352)
			if (not located):
				if (status["hold_action"] != "held"):
					(status["hold_action"], status["params"]) = (commandAction, "RightClick")
					return gestureCommands("0_6")
				else: return False
			time.sleep(1)
			located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "scaleRotateFlip.png"))
			if (located is None):
				if (status["hold_action"] != "held"):
					(status["hold_action"], status["params"]) = (commandAction, "ScaleRotateFlip")
					return gestureCommands("0_8")
				else: return False
			(x1, y1, w, h) = located
			y1 = y1 / scale;
			y1 += (status["rightPlus"] + (status["optionH"] * 0.5) if action == "Horizontal" else status["rightPlus"] + (status["optionH"] * 1.5))
			auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
			auto.click()
		else:
			auto.PAUSE = 0.1
			#auto.press("0")
			auto.press("s")
			time.sleep(0.5)
			#auto.press("0")
			auto.press("h" if action == "Horizontal" else "v")
			auto.PAUSE = 0.25
	elif (command == "Rotate" and action != "Rotate"):
		moveToActivePanel()
		auto.click(button='right')
		if (status["toUse"] == "img_recog"):
			located = findRightClick(352)
			if (not located):
				if (status["hold_action"] != "held"):
					(status["hold_action"], status["params"]) = (commandAction, "RightClick")
					return gestureCommands("0_6")
				else: return False
			time.sleep(1)
			located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "scaleRotateFlip.png"))
			if (located is None):
				if (status["hold_action"] != "held"):
					(status["hold_action"], status["params"]) = (commandAction, "ScaleRotateFlip")
					return gestureCommands("0_8")
				else: return False
			(x1, y1, w, h) = located
			y1 = y1 / scale
			y1 += (status["rightPlus"] + (status["optionH"] * 2.5) if action == "Clockwise" else status["rightPlus"] + (status["optionH"] * 3.5))
			auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
			auto.click()
		else:
			auto.PAUSE = 0.1
			#auto.press("0")
			auto.press("s")
			time.sleep(0.5)
			#auto.press("0")
			auto.press("r")
			if (action != "Clockwise"): auto.press("down")
			auto.press("enter")
			auto.PAUSE = 0.25
	elif (command == "Zoom"):
		splitParams = status["params"].split("_")
		if (status["defaultCommand"] is None):
			if (status["group1_command"] is None):
				moveToActivePanel()
				auto.click()
				auto.click(button='right')
				if (status["toUse"] == "img_recog"):
					if (not findRightClick(54)):
						if (status["hold_action"] != "held"):
							(status["hold_action"], status["params"]) = (commandAction, "RightClick")
							return gestureCommands("0_6")
						else: return False
					auto.click()
					moveToActivePanel()
				else: auto.press("z")
			if (command == action):
				status["defaultCommand"] = command
				auto.mouseDown()
			else:
				if (len(splitParams) % 2 == 1 and status["params"] != ""):
					level = (-1 * int(splitParams[0]) if action == "In" else int(splitParams[0]))
				else: level = (-100 if action == "In" else 100)
				if (len(splitParams) <= 1): (moveToX, moveToY) = auto.position()
				else:
					(moveToX, moveToY) = (int(splitParams[len(splitParams) - 2]), int(splitParams[len(splitParams) - 1]))
				auto.moveTo(moveToX, moveToY)
				auto.mouseDown()
				auto.moveTo(moveToX, moveToY + level)
				#auto.mouseUp()
				status["group1_command"] = command
		else:
			(oldLocationX, oldLocationY) = auto.position()
			if (len(splitParams) == 1):
				if (status["params"] != ""):
					level = (-1 * int(splitParams[0]) if action == "In" else int(splitParams[0]))
				else: level = (-100 if action == "In" else 100)
			else:
				print "For " + command + ", you must pass a maximum of one argument."
				return False
			auto.moveTo(oldLocationX, oldLocationY + level)
	elif (command == "Switch Panel" and action != "Switch Panel"):
		ind = int(actionID / 3)
		status["active_panel"][ind] += (-1 if action == "Left" or action == "Up" else 1)
		status["active_panel"][ind] = max(1, status["active_panel"][ind])
		status["active_panel"][ind] = min(status["active_panel"][ind], status["panel_dim"])
		moveToActivePanel()
		auto.click()
	elif (command == "Pan"):
		splitParams = status["params"].split("_")
		if (status["defaultCommand"] is None):
			if (status["group1_command"] is None):
				moveToActivePanel()
				auto.click()
				auto.click(button='right')
				if (status["toUse"] == "img_recog"):
					if (not findRightClick(90)):
						if (status["hold_action"] != "held"):
							(status["hold_action"], status["params"]) = (commandAction, "RightClick")
							return gestureCommands("0_6")
						else: return False
					auto.click()
					moveToActivePanel()
				else: (auto.press(e) for e in ["p", "enter"])
			if (command == action):
				status["defaultCommand"] = command
				auto.mouseDown()
			else:
				if (len(splitParams) % 2 == 1 and status["params"] != ""):
					level = (int(splitParams[0]) if action == "Left" or action == "Up" else -1 * int(splitParams[0]))
				else: level = (20 if action == "Left" or action == "Up" else -20)
				if (len(splitParams) <= 1): (moveToX, moveToY) = auto.position()
				else:
					(moveToX, moveToY) = (int(splitParams[len(splitParams) - 2]), int(splitParams[len(splitParams) - 1]))
				if (action == "Left" or action == "Right"): (toMoveX, toMoveY) = (moveToX + level, moveToY)
				else: (toMoveX, toMoveY) = (moveToX, moveToY + level)
				auto.moveTo(moveToX, moveToY)
				auto.mouseDown()
				auto.moveTo(toMoveX, toMoveY)
				#auto.mouseUp()
				status["group1_command"] = command
		else:
			(oldLocationX, oldLocationY) = auto.position()
			if (len(splitParams) == 1):
				if (status["params"] != ""):
					level = (int(splitParams[0]) if action == "Left" or action == "Up" else -1 * int(splitParams[0]))
				else: level = (20 if action == "Left" or action == "Up" else -20)
			else:
				print "For " + command + ", you must pass a maximum of one argument."
				return False
			if (action == "Left" or action == "Right"): (toMoveX, toMoveY) = (oldLocationX + level, oldLocationY)
			else: (toMoveX, toMoveY) = (oldLocationX, oldLocationY + level)
			auto.moveTo(moveToX, moveToY)
	elif (command == "Ruler" and action != "Ruler"):
		if (action == "Measure"):
			openWindow(prompt)
			while (1):
				rawInput = raw_input("Enter coordinates separated by underscores (2 or 4 non-negative integers): ")
				try:
					if (len(rawInput.split("_")) == 2):
						moveToActivePanel()
						rawInput = "_".join(list(str(p) for p in auto.position())) + "_" + rawInput
						break
					elif (len(rawInput.split("_")) == 4): break
					else: promptNotify("Coordinates must have only 2 or 4 non-negative integers.", 0)
					#return False
				except ValueError:
					promptNotify("Coordinates must be non-negative integers.", 0)
					#return False
			status["params"] = rawInput
			points = status["params"].split("_")
			(x1, y1, x2, y2) = (int(points[0]), int(points[1]), int(points[2]), int(points[3]))
			openWindow(viewer)
			time.sleep(2)
			moveToActivePanel()
			auto.click(button='right')
			if (status["toUse"] == "img_recog"):
				located = findRightClick(126)
				if (not located):
					if (status["hold_action"] != "held"):
						(status["hold_action"], status["params"]) = (commandAction, "RightClick")
						return gestureCommands("0_6")
					else: return False
				auto.click()
				time.sleep(2)
			else: (auto.press(e) for e in ["r", "enter"])
			auto.moveTo(x1, y1)
			auto.mouseDown()
			auto.moveTo(x2, y2)
			auto.mouseUp()
			status["rulers"]["len"] += 1
			curr = 1
			while (curr <= status["rulers"]["len"]):
				if (curr not in status["rulers"]):
					status["rulers"][curr] = status["params"]
					break
				curr += 1
			print "ID of Ruler Measurement: " + str(curr)
		elif (action == "Delete"):
			if (status["params"] == ""):
				promptNotify("Ruler delete ID not specified.", 0)
				return False
			try:
				rulerID = int(status["params"])
				if (rulerID not in status["rulers"]):
					print "Ruler delete ID is not in the list of rulers."
					return False
			except ValueError:
				print "Ruler delete ID should be one positive integer value."
				return False
			points = status["rulers"][rulerID].split("_")
			status["rulers"].pop(rulerID, None)
			status["rulers"]["len"] -= 1
			auto.moveTo((int(points[2]) + int(points[0])) / 2.0, (int(points[3]) + int(points[1])) / 2.0)
			auto.click()
			beforeRCRuler = os.path.join("SCA_Images", "beforeRCRuler.png")
			ImageGrab.grab(bbox=boundBoxNoDash).save(beforeRCRuler)
			auto.click(button='right')
			if (status["toUse"] == "img_recog"):
				afterRCRuler = os.path.join("SCA_Images", "afterRCRuler.png")
				ImageGrab.grab(bbox=boundBoxNoDash).save(afterRCRuler)
				diffRCRuler = os.path.join("SCA_Images", "diffRCRuler.png")
				diffBox = get_bbox(beforeRCRuler, afterRCRuler)
				(x1, y1, x2, y2) = (diffBox[i] + boundBoxNoDash[(i % 2)] for i in range(4))
				print str((x1, y1))
				auto.moveTo(x1, y1)
				ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffRCRuler)
				moveToX = (x1 + status["rightIcons"] + x2) / (2.0 * scale)
				moveToY = (y1 / scale) + status["rightPlus"] + (status["optionH"] * 4.5)
				print str((moveToX, moveToY))
				auto.moveTo(moveToX, moveToY)
				auto.click()
				#os.remove(afterRCRuler)
				#os.remove(diffRCRuler)
			else:
				auto.PAUSE = 0.1
				auto.press("0")
				for i in range(5): auto.press("down")
				auto.press("enter")
				auto.pause = 0.25
			#os.remove(beforeRCRuler)
			"""auto.click()
			beforeMeasure = ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("SCA_Images", "beforeMeasure.png"))
			auto.click(button="right")
			afterMeasure = ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("SCA_Images", "afterMeasure.png"))
			(x1, y1, x2, y2) = get_bbox(os.path.join("SCA_Images", "beforeMeasure.png"), os.path.join("SCA_Images", "afterMeasure.png"))
			diffX = x2 - x1
			x1 += boundBoxNoDash[0] + (status["rightIcons"] / scale) + (diffX / 2.0)
			y1 += boundBoxNoDash[1] + status["rightPlus"] + (status["optionH"] * 4.5)
			#(moveToX, moveToY) = ((x1 + x2) / 2.0, status["rightPlus"] + (status["optionH"] * 4.5))
			#auto.moveTo(x1 + (79.0 / 1440.0) * width, y1 + (85.0 / 900.0) * height)
			auto.moveTo(x1, y1)
			auto.click()"""
	elif (command == "Window" and action != "Window"):
		if (action == "Open" and not status["window_open"]):
			auto.moveTo(width / 2.0, 0)
			time.sleep(1)
			box = (1.0 * scale, status["topBarHeight"] + 1.0 * scale, -1.0 * scale, -1.0 * scale)
			box = tuple(boundBoxNoDash[i] + box[i] for i in range(4))
			afterHoverPath = os.path.join("SCA_Images", "Window", "afterHover.png")
			ImageGrab.grab(bbox=box).save(afterHoverPath)
			# 219,53 on mac from topBar, without scale
			if (platform.system() == "Windows"): auto.moveTo(326.0 * width / 1920.0, 78.0 * height / 1080.0)
			else: auto.moveTo(435.0 / 2.0, (107.0 + 44.0) / 2.0)
			auto.click()
			time.sleep(5)
			seriesThumbnailPath = os.path.join("SCA_Images", "Window", "seriesThumbnail.png")
			ImageGrab.grab(bbox=box).save(seriesThumbnailPath)
			diffSeriesPath = os.path.join("SCA_Images", "Window", "diffSeries.png")
			diffBox = get_bbox(afterHoverPath, seriesThumbnailPath)
			(x1, y1, x2, y2) = (diffBox[i] + box[(i % 2)] for i in range(4))
			ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffSeriesPath)
			(tempX, tempY) = (x2, y1)
			auto.moveTo(tempX, tempY)
			(x1, y1) = (tempX + ((-14.0 - 90.0) * scale / 2.0), tempY + (3.0) * scale / 2.0)
			(x2, y2) = (tempX + (-14.0) * scale / 2.0, tempY + (43.0) * scale / 2.0)
			seriesClosePath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose.png")
			seriesClose_RedPath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose_Red.png")
			seriesClose_GrayPath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose_Gray.png")
			ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClosePath)
			auto.moveTo((x1 + x2) / (scale * 2.0), (y1 + y2) / (scale * 2.0))
			ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClose_RedPath)
			auto.moveTo(0, (y1 + y2) / (scale * 2.0))
			auto.click()
			ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClose_GrayPath)
			status["window_open"] = (not status["window_open"])
		elif (action == "Close" and status["window_open"]):
			for file in os.listdir(os.path.join("SCA_Images", "Window", "Closes")):
				if (not file.endswith(".png")): continue
				close = auto.locateOnScreen(os.path.join("SCA_Images", "Window", "Closes", file))
				if (close is not None):
					(x1, y1, w, h) = close
					auto.moveTo((2 * x1 + w) / (scale * 2.0), (2 * y1 + h) / (scale * 2.0))
					auto.click()
					status["window_open"] = (not status["window_open"])
					break
	elif (command == "Manual Contrast"):
		splitParams = status["params"].split("_")
		if (status["defaultCommand"] is None):
			if (status["group1_command"] is None):
				moveToActivePanel()
				auto.click(button='right')
				if (status["toUse"] == "img_recog"):
					located = findRightClick(18)
					if (not located):
						(status["raw_input"], status["hold_action"]) = ("0_6", commandAction)
						return False
					auto.click()
					moveToActivePanel()
				else: (auto.press(e) for e in ["0", "w"])
			if (command == action):
				status["defaultCommand"] = command
				auto.mouseDown()
			else:
				if (splitParams[0] != ""):
					level = (-1 * int(splitParams[0]) if action == "Decrease" else int(splitParams[0]))
				else: level = (-50 if action == "Decrease" else 50)
				(oldLocationX, oldLocationY) = auto.position()
				auto.mouseDown()
				auto.moveTo(oldLocationX, oldLocationY + level)
				#auto.mouseUp()
				status["group1_command"] = command
		else:
			(oldLocationX, oldLocationY) = auto.position()
			if (len(splitParams) == 1):
				if (status["params"] != ""):
					level = (-1 * int(splitParams[0]) if action == "Decrease" else int(splitParams[0]))
				else: level = (-50 if action == "Decrease" else 50)
			else:
				print "For " + command + ", you must pass a maximum of one argument."
				return False
			auto.moveTo(oldLocationX, oldLocationY + level)
	elif (command == "Layout" and action != "Layout"):
		(oldLocationX, oldLocationY) = auto.position()
		auto.moveTo(oldLocationX, 0)
		time.sleep(1)
		box = (1.0 * scale, status["topBarHeight"], -1.0 * scale, -1.0 * scale)
		box = tuple(boundBoxNoDash[i] + box[i] for i in range(4))
		afterHoverPath = os.path.join("SCA_Images", "Layout", "afterHover.png")
		ImageGrab.grab(bbox=box).save(afterHoverPath)
		# 429,54 on mac from topBar, without scale
		if (platform.system() == "Windows"): auto.moveTo(642.0 * width / 1920.0, 80.0 * height / 1080.0)
		else: auto.moveTo(857.0 / 2.0, (109.0 + 44.0) / 2.0)
		auto.click()
		time.sleep(5)
		windowPath = os.path.join("SCA_Images", "Layout", "window.png")
		ImageGrab.grab(bbox=box).save(windowPath)
		diffLayoutPath = os.path.join("SCA_Images", "Layout", "diffLayout.png")
		diffBox = get_bbox(afterHoverPath, windowPath)
		(x1, y1, x2, y2) = (diffBox[i] + box[(i % 2)] for i in range(4))
		ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffLayoutPath)
		auto.moveTo(x1, y1)
		time.sleep(2)
		auto.moveTo(x1 / scale, y1 / scale)
		time.sleep(2)
		(x1, y1) = ((x1 + 91.0) / 2.0, (y1 + 127.0) / 2.0)
		jumpX = (122.0 / 2.0)
		(status["panel_dim"][0], status["panel_dim"][1]) = (1, actionID)
		#(x1, y1) = (472.0 + (actionID - 1) * 62.0, 217.0)
		x1 += (status["panel_dim"][1] - 1) * jumpX
		auto.moveTo(x1, y1)
		auto.click()
		resetPanelMoves()
		moveToActivePanel()
		auto.click()
	elif (command == "Contrast Presets" and action != "Contrast Presets"):
		moveToActivePanel()
		auto.click()
		auto.click(button='right')
		if (status["toUse"] == "img_recog"):
			located = findRightClick(316)
			if (not located):
				if (status["hold_action"] != "held"):
					(status["hold_action"], status["params"]) = (commandAction, "RightClick")
					return gestureCommands("0_6")
				else: return False
			located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "presets.png"))
			if (located is None):
				if (status["hold_action"] != "held"):
					(status["hold_action"], status["params"]) = (commandAction, "Presets")
					return gestureCommands("0_7")
				else: return False
			(x1, y1, w, h) = located
			y1 = y1 / scale
			y1 += status["rightPlus"] + (status["optionH"] * (actionID + 0.5))
			auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
			auto.click()
		else:
			auto.PAUSE = 0.1
			auto.press("0")
			auto.press("i")
			auto.press("right")
			time.sleep(0.5)
			auto.press("0")
			for i in range(actionID + 1): auto.press("down")
			auto.press("enter")
			auto.PAUSE = 0.25
		time.sleep(1)

	if (command != "Admin"): status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)
	status["hold_action"] = None
	
	return True

