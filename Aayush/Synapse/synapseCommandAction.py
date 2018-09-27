import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import ImageGrab
#from PIL import ImageChops
import signal
import sys

#Remove images already saved (avoids issues with git)
def removeImages():
	for file in os.listdir(os.path.join("Images")):
		if file.endswith(".png"):
			os.remove(os.path.join(os.path.join("Images"), file))
	for file in os.listdir(os.path.join("Images", "RightClick")):
		if file.endswith(".png"):
			os.remove(os.path.join(os.path.join("Images", "RightClick"), file))

# If exiting the synapse program, remove all images before closing synapse.
def signal_handler(sig, frame):
	removeImages()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

auto.FAILSAFE = True
auto.PAUSE = 0.75

(width, height) = auto.size()
(nativeW, nativeH) = ImageGrab.grab().size
scale = nativeW / width
print "WxH: %s" % ((width, height),)
print "nativeW, nativeH: %s" % ((nativeW, nativeH),)
print str(scale)

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
		y_thresh = x_thresh
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


if (platform.system() == "Windows"):
	(macHeader, viewer, prompt) = (0, "\\\\Remote", "Command Prompt")
else:
	(macHeader, viewer, prompt) = ((44.0 / 2880.0) * (nativeH), "Citrix Viewer", "Teminal")

def openWindow(toOpen):
	window_names = auto.getWindows().keys()
	for window_name in window_names:
		auto.getWindow(window_name).close()
		if (toOpen in window_name):
			xef_window_name = window_name
	xef_window = auto.getWindow(xef_window_name)
	xef_window.maximize()


class Calibration(object):
	def __init__(self):
		self.resetTopBarHeight()
		self.resetBoundBoxNoDash()
		self.resetRightClick()
		self.resetRightOptions("presets", 8.5)
		self.resetRightOptions("scaleRotateFlip", 9.5)

	def getAll(self):
		return (self.topBarHeight, self.boundBoxNoDash, self.optionH, self.rightHR, self.rightPlus, self.rightIcons,
			self.rightOffset, self.rightBoxW, self.rightBoxH)

	# Reset height of top bar and save it
	def resetTopBarHeight(self):
		auto.moveTo(width / 2.0, height / 2.0)
		auto.click()
		ImageGrab.grab().save(os.path.join("Images", "fullscreen.png"))
		auto.moveTo(width / 2.0, 0)
		time.sleep(1)
		ImageGrab.grab().save(os.path.join("Images", "afterTopBar.png"))
		topBarBox = get_bbox(os.path.join("Images", "fullscreen.png"), os.path.join("Images", "afterTopBar.png"))
		self.topBarHeight = topBarBox[3] - topBarBox[1] + 1
		ImageGrab.grab(bbox=(0, 0, nativeW, self.topBarHeight)).save(os.path.join("Images", "topBar.png"))

	# Reset border inside dashed region
	def resetBoundBoxNoDash(self):
		auto.moveTo(width / 2.0, height / 2.0)
		auto.click()
		auto.click(button='right')
		ImageGrab.grab().save(os.path.join("Images", "noDash.png"))
		box = get_bbox(os.path.join("Images", "fullscreen.png"), os.path.join("Images", "noDash.png"))
		(x1, y1, x2, y2) = (box[0] + (10 * scale), box[1] + (10 * scale), box[2] - (10 * scale), box[3] - (10 * scale))
		(bbndW, bbndH) = ((x2 - x1) / scale, (y2 - y1) / scale)
		self.boundBoxNoDash = (x1, y1, x2, y2)
		print "boundBoxNoDash: %s" % (self.boundBoxNoDash,)
		print "boundBoxNoDash WxH: %s" % ((bbndW, bbndH),)
		auto.press("esc")

	# Reset the right click
	def resetRightClick(self):
		auto.moveTo(width / 2.0, height / 2.0)
		auto.click()
		beforeRightPath = os.path.join("Images", "RightClick", "beforeRight.png")
		ImageGrab.grab(bbox=self.boundBoxNoDash).save(beforeRightPath)
		auto.click(button='right')
		time.sleep(1)
		afterRightPath = os.path.join("Images", "RightClick", "afterRight.png")
		ImageGrab.grab(bbox=self.boundBoxNoDash).save(afterRightPath)
		rightBox = get_bbox(beforeRightPath, afterRightPath)
		print "rightBox: %s" % (rightBox,)
		(self.rightBoxW, self.rightBoxH) = (rightBox[2] - rightBox[0] + 1, rightBox[3] - rightBox[1] + 1)
		print "rightBox WxH: %s" % ((self.rightBoxW, self.rightBoxH),)

		self.optionH = ((self.rightBoxH / 1000.0) * 36.0) / scale
		self.rightHR = ((self.rightBoxH / 1000.0) * 10.0) / scale
		self.rightPlus = ((self.rightBoxH / 1000.0) * 8.0) / scale
		self.rightIcons = ((self.rightBoxH / 1000.0) * 50.0)
		self.rightOffset = ((self.rightBoxH / 1000.0) * 58.0)

		(self.rightx1, self.righty1) = (rightBox[0] + self.boundBoxNoDash[0], rightBox[1] + self.boundBoxNoDash[1])
		(x1, y1) = (self.rightx1 + self.rightIcons, self.righty1 + self.rightOffset)
		(x2, y2) = (self.rightx1 + self.rightBoxW, self.righty1 + self.rightBoxH)
		ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(os.path.join("Images", "RightClick", "rightClick.png"))

		auto.moveTo(x1, y1)
		auto.moveTo(x2, y2)
		auto.press("esc")

	# Reset rightClick's presets/scaleRotateFlip
	def resetRightOptions(self, option, offset):
		auto.moveTo(width / 2.0, height / 2.0)
		auto.click(button='right')
		moveToX = (self.rightx1 + self.rightBoxW / 2.0) / scale
		moveToY = ((self.righty1 + self.rightOffset) / scale) + (self.optionH * offset) + self.rightHR
		auto.moveTo(moveToX, moveToY)
		time.sleep(1)
		auto.moveTo(self.rightx1 / scale, (self.righty1 + self.rightOffset) / scale)
		afterRightPath = os.path.join("Images", "RightClick", "afterRight.png")
		afterOptionPath = os.path.join("Images", "RightClick", "after" + option + ".png")
		ImageGrab.grab(bbox=self.boundBoxNoDash).save(afterOptionPath)
		box = get_bbox(afterRightPath, afterOptionPath)
		print option + " box: %s" % (box,)
		(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
		print option + " box WxH: %s" % ((boxW, boxH),)
		(x1, y1) = (box[0] + self.boundBoxNoDash[0], box[1] + self.boundBoxNoDash[1])
		optionPath = os.path.join("Images", "RightClick", option + ".png")
		ImageGrab.grab(bbox=(x1 + self.rightIcons, y1, x1 + boxW, y1 + boxH)).save(optionPath)
		auto.press("esc")


print "Warming up synapse system...\n"
openWindow(viewer)

Calibration = Calibration()
(topBarHeight, boundBoxNoDash, optionH, rightHR, rightPlus, rightIcons, rightOffset,
	rightBoxW, rightBoxH) = Calibration.getAll()

openWindow(prompt)
print "\nCompleted warm-up, make your gestures!\n"


status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1], "params": "", "rulers": {"len": 0}}

def resetPanelMoves():
	status["firstW"] = (float(width) / (float(status["panel_dim"][1]) * 2.0))
	status["firstH"] = (float(height) / (float(status["panel_dim"][0]) * 2.0))
	status["jumpW"] = (status["firstW"] * 2.0 if status["panel_dim"][1] != 1 else 0)
	status["jumpH"] = (status["firstH"] * 2.0 if status["panel_dim"][0] != 1 else 0)

	print "Reset Panel: " + str(status["firstW"]) + " " + str(status["firstH"]) + " " + str(status["jumpW"]) + " " + str(status["jumpH"])

resetPanelMoves()

def moveToActivePanel():
	moveToX = status["firstW"] + (status["active_panel"][1] - 1) * (status["jumpW"])
	moveToY = status["firstH"] + (status["active_panel"][0] - 1) * (status["jumpH"])
	auto.moveTo(moveToX, moveToY)

actionList = [["Admin", "Quit", "Get Status", "Reset 0", "Reset 1", "Reset 2", "Reset 3", "Reset 4", "Reset 5"],
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

def defaultAction(commandID, paramSizes):
	auto.hotkey("command", "tab")
	try:
		command = actionList[commandID][0]
		commandLen = len(actionList[commandID])
		rawInput = raw_input("Enter parameters for " + command + " <1-" + str(commandLen - 1) + "> <param1_param2_...>: ")
		auto.hotkey("command", "tab")
		params = rawInput.split(" ")
		if (len(params) == 2 or len(params) == 1):
			if (int(params[0]) >= commandLen):
				auto.hotkey("command", "tab")
				print "Invalid action type given: <1-" + str(commandLen) + ">"
				return (False, actionList[commandID][0])
			invalidSize = True
			for paramSize in paramSizes:
				if (len(params[1].split("_")) == paramSize):
					invalidSize = False
			if (invalidSize):
				auto.hotkey("command", "tab")
				print "Invalid parameter size given for " + command
				return (False, actionList[commandID][0])
			status["params"] = params[1]
			return (True, actionList[commandID][int(params[0])])
		else:
			auto.hotkey("command", "tab")
			print "Invalid parameters given"
			return (False, actionList[commandID][0])
	except ValueError:
		auto.hotkey("command", "tab")
		print "Unrecognized parameters given for " + command
		return (False, actionList[commandID][0])

def rightClick(offset):
	auto.click(button='right')
	located = auto.locateOnScreen(os.path.join("Images", "RightClick", "rightClick.png"))
	if (located is not None):
		(x1, y1, w, h) = located
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, (y1 + (offset / 1000.0) * rightBoxH) / scale)
		return True
	else:
		print "Error when performing right click function."
		return False
	
def get_status():
	print "\nStatus\n------"
	print "Previous action: " + status["prev_action"]
	print "Panel Dimension: " + str(status["panel_dim"][0]) + 'x' + str(status["panel_dim"][1])
	print "Active panel: " + str(status["active_panel"][0]) + 'x' + str(status["active_panel"][1])
	print "Patient information window: " + ("opened" if status["window_open"] else "closed")


while (True):
	(commandID, actionID) = (-1, -1)
	sequence = raw_input("Gesture Command -> ")
	commandAction = sequence
	if (sequence.find(" ") != -1):
		commandAction = sequence[:sequence.find(" ")]
		status["params"] = sequence[sequence.find(" ") + 1:]
	if (commandAction.find("_") != -1):
		try:
			commandID = int(commandAction[:commandAction.find("_")])
			actionID = int(commandAction[commandAction.find("_") + 1:])
			command = actionList[commandID][0]
			action = actionList[commandID][actionID]
		except ValueError:
			print "Unrecognized sequence of commands!\n"
			continue
		except IndexError:
			print "Incorrect commands!\n"
			continue
	else:
		print "Invalid command entered!\n"
		continue

	openWindow(viewer)


	if (command == "Admin"):
		if (action == "Quit"):
			openWindow(prompt)
			break
		elif (action == "Get Status"):
			get_status()
		elif ("Reset" in action):
			actionNum = actionID - 3
			if (actionNum == 0):
				Calibration = Calibration()
			elif (actionNum == 1):
				Calibration.resetTopBarHeight()
			elif (actionNum == 2):
				Calibration.resetBoundBoxNoDash()
			elif (actionNum == 3):
				Calibration.resetRightClick()
			elif (actionNum == 4):
				Calibration.resetRightOptions("presets", 8.5)
			elif (actionNum == 5):
				Calibration.resetRightOptions("scaleRotateFlip", 9.5)
			(topBarHeight, boundBoxNoDash, optionH, rightHR, rightPlus, rightIcons, rightOffset,
				rightBoxW, rightBoxH) = Calibration.getAll()
	elif (command == "Scroll" and action != "Scroll"):
		moveToActivePanel()
		auto.click()
		scrollAmount = (10 if status["params"] == "" else int(status["params"]))
		nums = scrollAmount
		scrollAmount = (-1 * scrollAmount if action == "Up" else scrollAmount)
		#auto.scroll(scrollAmount)
		auto.PAUSE = 0
		print str(nums)
		toPress = ("right" if action == "Up" else "left")
		print toPress
		for i in range(nums):
			auto.press(toPress)
		auto.PAUSE = 0.75
		time.sleep(1)
	elif (command == "Flip" and action != "Flip"):
		moveToActivePanel()
		located = rightClick(352)
		if (not located):
			openWindow(prompt)
			continue
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))
		y1 = y1 / scale;
		y1 += (rightPlus + (optionH * 0.5) if action == "Horizontal" else rightPlus + (optionH * 1.5))
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
		auto.click()
	elif (command == "Rotate" and action != "Rotate"):
		moveToActivePanel()
		located = rightClick(352)
		if (not located):
			openWindow(prompt)
			continue
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))
		y1 = y1 / scale
		y1 += (rightPlus + (optionH * 2.5) if action == "Clockwise" else rightPlus + (optionH * 3.5))
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
		auto.click()
	elif (command == "Zoom"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			(oldLocationX, oldLocationY) = auto.position()
			moveToActivePanel()
			located = rightClick(54)
			if (not located):
				openWindow(prompt)
				continue
			auto.click()
			time.sleep(1)
			auto.moveTo(oldLocationX, oldLocationY)
			if (status["params"] != ""):
				level = (-1 * int(status["params"]) if action == "In" else int(status["params"]))
			else:
				level = (-20 if action == "In" else 20)
			auto.mouseDown()
			auto.moveTo(oldLocationX, oldLocationY + level)
			auto.mouseUp()
	elif (command == "Switch Panel" and action != "Switch Panel"):
		status["active_panel"][1] += (1 if action == "Right" else -1)
		status["active_panel"][0] += (1 if action == "Down" else -1)
		if (status["active_panel"][0] < 1):
			status["active_panel"][0] = 1
		if (status["active_panel"][1] < 1):
			status["active_panel"][1] = 1
		moveToActivePanel()
		auto.click()
	elif (command == "Pan"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			(oldLocationX, oldLocationY) = auto.position()
			moveToActivePanel()
			located = rightClick(90)
			if (not located):
				openWindow(prompt)
				continue
			auto.click()
			time.sleep(1)
			auto.moveTo(oldLocationX, oldLocationY)
			if (status["params"] != ""):
				level = (-1 * int(status["params"]) if action == "Up" or action == "Left" else int(status["params"]))
			else:
				level = (-20 if action == "Up" or action == "Left" else 20)
			auto.mouseDown()
			oldLocationX += (level if action == "Left" or action == "Right" else 0)
			oldLocationY += (level if action == "Up" or action == "Down" else 0)
			auto.moveTo(oldLocationX, oldLocationY)
			auto.mouseUp()
	elif (command == "Ruler"):
		if (action == "Measure"):
			(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [2, 4]))
			if (isValid):
				moveToActivePanel()
				located = rightClick(126)
				if (not located):
					openWindow(prompt)
					continue
				auto.click()
				time.sleep(2)
				points = status["params"].split("_")
				try:
					if (len(points) == 4):
						(x1, y1, x2, y2) = (int(points[0]), int(points[1]), int(points[2]), int(points[3]))
					elif (len(points) == 2):
						(x1, y1) = auto.position()
						(x2, y2) = (int(points[0]), int(points[1]))
				except ValueError:
					print "Ruler measure parameters should only include non-negative integers separated by underscores."
					continue
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
		elif (action == "Delete"):
			try:
				popped = status["rulers"][int(status["params"])]
				status["rulers"].pop(int(status["params"]), None)
				print str(popped)
				points = popped.split("_")
				status["rulers"]["len"] -= 1
				(moveToX, moveToY) = ((int(points[2]) + int(points[0])) / 2.0, (int(points[3]) + int(points[1])) / 2.0)
				auto.moveTo(moveToX, moveToY)
			except ValueError:
				print "Ruler delete parameter should only be a positive integer value."
				continue
			auto.click()
			beforeMeasure = ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("Images", "beforeMeasure.png"))
			auto.click(button="right")
			afterMeasure = ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("Images", "afterMeasure.png"))
			(x1, y1, x2, y2) = get_bbox(os.path.join("Images", "beforeMeasure.png"), os.path.join("Images", "afterMeasure.png"))
			diffX = x2 - x1 + 1
			x1 += boundBoxNoDash[0] + (rightIcons / scale) + (diffX / 2.0)
			y1 += boundBoxNoDash[1] + rightPlus + (optionH * 4.5)
			#(moveToX, moveToY) = ((x1 + x2) / 2.0, rightPlus + (optionH * 4.5))
			#auto.moveTo(x1 + (79.0 / 1440.0) * width, y1 + (85.0 / 900.0) * height)
			auto.moveTo(x1, y1)
			auto.click()
	elif (command == "Window" and action != "Window"):
		(oldLocationX, oldLocationY) = auto.position()
		if (action == "Open" and not status["window_open"]):
			auto.moveTo(oldLocationX, 0)
			time.sleep(1)
			auto.moveTo(oldLocationX, macHeader)
			afterHover = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
			afterHover.save(os.path.join("Images", "window_afterHover.png"))
			auto.moveTo((329.0 / 1920.0) * width, (82.0 / 1080.0) * height)
			#auto.moveTo((219.0 / 1440.0) * width, (77.0 / 900.0) * height)
			#auto.moveTo((326.0 / 1920.0) * width, (78.0 / 1080.0) * height)
			auto.click()
			time.sleep(6)
			seriesThumbnail = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
			seriesThumbnail.save(os.path.join("Images", "window_seriesThumbnail.png"))
			(x1, y1, x2, y2) = get_bbox(os.path.join("Images", "window_afterHover.png"), os.path.join("Images", "window_seriesThumbnail.png"))
			(diffW, diffH) = (x2 - x1 + 1, y2 - y1 + 1)
			x1 += boundBoxNoDash[0] + (1 * scale)
			y1 += boundBoxNoDash[1] + topBarHeight + (1 * scale)
			(x2, y2) = (x1 + diffW, y1 + diffH)
			ImageGrab.grab(bbox=(x1, y1, x2, y2)).save("diffSeries.png")
			#(x1, y1) = (x2 - (83.0 / 2880.0) * nativeW,  y1 + (2.0 / 2880.0) * nativeW)
			#(x2, y2) = (x1 + (90.0 / 2880.0) * nativeW, y1 + (40.0 / 2880.0) * nativeW)
			(x1, y1) = (x2 - (10.0 * scale) - (90.0 / 2880.0) * nativeW, y1 + (2.0 * scale))
			(x2, y2) = (x2 - (10.0 * scale), y1 + (2.0 * scale) + (40.0 / 2880.0) * nativeW)
			close = ImageGrab.grab(bbox=(x1, y1, x2, y2))
			close.save(os.path.join("Images", "window_seriesThumbnailClose.png"))
			auto.moveTo((x1 + x2) / (scale * 2.0), (y1 + y2) / (scale * 2.0))
			close = ImageGrab.grab(bbox=(x1, y1, x2, y2))
			close.save(os.path.join("Images", "window_seriesThumbnailClose_Red.png"))
			auto.moveTo(0, (y1 + y2) / (scale * 2.0))
			auto.click()
			close = ImageGrab.grab(bbox=(x1, y1, x2, y2))
			close.save(os.path.join("Images", "window_seriesThumbnailClose_Gray.png"))
			status["window_open"] = (not status["window_open"])
		elif (action == "Close" and status["window_open"]):
			close = auto.locateOnScreen(os.path.join("Images", "window_seriesThumbnailClose.png"))
			if (close is None):
				close = auto.locateOnScreen(os.path.join("Images", "window_seriesThumbnailClose_Red.png"))
			if (close is None):
				close = auto.locateOnScreen(os.path.join("Images", "window_seriesThumbnailClose_Gray.png"))
			(x1, y1, w, h) = close
			(x2, y2) = (x1 + w, y1 + h)
			auto.moveTo((x1 + x2) / (scale * 2.0), (y1 + y2) / (scale * 2.0))
			auto.click()
			status["window_open"] = (not status["window_open"])
	elif (command == "Manual Contrast"):
		moveToActivePanel()
		(oldLocationX, oldLocationY) = auto.position()
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			moveToActivePanel()
			located = rightClick(18)
			if (not located):
				openWindow(prompt)
				continue
			auto.click()
			time.sleep(1)
			moveToActivePanel()
			auto.mouseDown()
			if (status["params"] != ""):
				level = (int(status["params"]) if action == "Increase" else -1 * int(status["params"]))
			else:
				level = (20 if action == "Increase" else -20)
			auto.moveTo(oldLocationX, oldLocationY + level)
			auto.mouseUp()
	elif (command == "Layout" and action != "Layout"):
		(oldLocationX, oldLocationY) = auto.position()
		auto.moveTo(oldLocationX, 0)
		time.sleep(1)
		afterHover = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
		afterHover.save(os.path.join("Images", "layout_afterHover.png"))
		#auto.moveTo((329.0 / 1920.0) * width, (82.0 / 1080.0) * height)
		auto.moveTo((643.0 / 1920.0) * width, (82.0 / 1080.0) * height)
		#auto.moveTo((428.0 / 1920.0) * width, (77.0 / 1080.0) * height)
		auto.click()
		time.sleep(5)
		seriesThumbnail = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
		seriesThumbnail.save(os.path.join("Images", "layout_seriesThumbnail.png"))
		(x1, y1, x2, y2) = get_bbox(os.path.join("Images", "layout_afterHover.png"), os.path.join("Images", "layout_seriesThumbnail.png"))
		(diffW, diffH) = (x2 - x1 + 1, y2 - y1 + 1)
		x1 += boundBoxNoDash[0] + (1 * scale)
		y1 += boundBoxNoDash[1] + topBarHeight + (1 * scale)
		ImageGrab.grab(bbox=(x1, y1, x1 + diffW, y1 + diffH)).save(os.path.join("Images", "layout_diff.png"))
		(x2, y2) = (x1 + diffW, y1 + diffH)
		ImageGrab.grab(bbox=(x1, y1, x2, y2)).save("diffLayout.png")
		status["panel_dim"][0] = 1
		y1 += (95.0 / 1080.0) * height
		jumpX = (91.0 / 1920.0) * width
		if (action == "One-Panel"):
			x1 += (68.0 / 1920.0) * width
			status["panel_dim"][1] = 1
		elif (action == "Two-Panels"):
			x1 += (68.0 / 1920.0) * width
			status["panel_dim"][1] = 2
		elif (action == "Three-Panels"):
			x1 += (68.0 / 1920.0) * width
			status["panel_dim"][1] = 3
		elif (action == "Four-Panels"):
			x1 += (68.0 / 1920.0) * width
			status["panel_dim"][1] = 4
		x1 += (status["panel_dim"][1] - 1) * jumpX
		auto.moveTo(x1, y1)
		auto.click()
		resetPanelMoves()
		moveToActivePanel()
		auto.click()
	elif (command == "Contrast Presets" and action != "Contrast Presets"):
		moveToActivePanel()
		located = rightClick(316)
		if (not located):
			openWindow(prompt)
			continue
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "presets.png"))
		y1 = y1 / scale
		y1 += rightPlus + (optionH * 0.5)
		if (action == "I"):
			y1 += optionH
		elif (action == "II"):
			y1 += optionH * 2
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
		auto.click()
	
	if (command != "Admin"):
		status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)
		status["params"] = ""


	openWindow(prompt)


# When quitting program, remove anything saved
removeImages()
