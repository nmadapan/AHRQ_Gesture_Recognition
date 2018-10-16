import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import ImageGrab
import signal
import sys


auto.FAILSAFE = True
auto.PAUSE = 0.75

(width, height) = auto.size()
(nativeW, nativeH) = ImageGrab.grab().size
scale = nativeW / width
print "WxH: %s" % ((width, height),)
print "nativeW, nativeH: %s" % ((nativeW, nativeH),)
print str(scale)

(macH, viewer, prompt) = ((0, "\\\\Remote", "Command Prompt") if platform.system() == "Windows" else (44.0 * nativeW / 2880.0, "Citrix Viewer", "Terminal"))

border = (20.0 * nativeW / 2880.0) + (4.0 * scale)
boundBoxNoDash = (border, macH + border, nativeW - border, nativeH - border)


# Close all other windows and open either command prompt or the Citrix Viewer
def openWindow(toOpen):
	if (platform.system() == "Windows"):
		window_names = auto.getWindows().keys()
		for window_name in window_names:
			auto.getWindow(window_name).minimize()
			if (toOpen in window_name):
				xef_window_name = window_name
		xef_window = auto.getWindow(xef_window_name)
		xef_window.maximize()
	else:
		auto.hotkey("command", "space")
		auto.typewrite(toOpen)
		auto.press("enter")
		#auto.hotkey("command", "tab")

#Remove images already saved (avoids issues with git)
def removeImages():
	paths = [os.path.join("Images", "RightClick"), os.path.join("Images", "Window", "Closes"),
		os.path.join("Images", "Window"), os.path.join("Images", "Layout"), os.path.join("Images")]
	for path in paths:
		if (not os.path.exists(path)):
			continue
		for file in os.listdir(path):
			if file.endswith(".png"):
				os.remove(os.path.join(path, file))

# Prompt notification if choosing to remove the images
def removeImagesPrompt():
	openWindow(prompt)
	while True:
		ans = raw_input("Do you want to remove the images saved in the folder? (y/n)")
		if (len(ans) == 1 and ans.lower() == "y"):
			removeImages()
			break
		elif (len(ans) != 1 or ans.lower() != "n"):
			print "Unrecognized request, please enter either 'y' or 'n'"
		else:
			break
	print ""

# If exiting the synapse program, remove all images before closing synapse.
def signal_handler(sig, frame):
	removeImagesPrompt()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


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


status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1], "rulers": {"len": 0}, "toUse": "Keyboard"}

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


class Calibration(object):
	def __init__(self):
		if (os.path.exists("calibration.txt")):
			f = open("calibration.txt", "r")
			#self.boundBoxNoDash = tuple(float(e) for e in f.readline()[1:-2].split(", "))
			(self.topBarHeight, self.optionH, self.rightHR, self.rightPlus, self.rightIcons, self.rightOffset,
				self.rightBoxW, self.rightBoxH) = tuple(float(f.readline()) for i in range(8))
			f.close()
		else:
			(self.topBarHeight, self.optionH, self.rightHR, self.rightPlus, self.rightIcons,
				self.rightOffset, self.rightBoxW, self.rightBoxH) = (0 for i in range(8))

	def getAll(self):
		return (self.topBarHeight, self.optionH, self.rightHR, self.rightPlus, self.rightIcons,
			self.rightOffset, self.rightBoxW, self.rightBoxH)
	
	def resetAll(self):
		print "\nWarming up synapse system...\n"
		self.resetTopBarHeight()
		self.resetRightClick()
		self.resetRightOptions("presets", 8.5)
		self.resetRightOptions("scaleRotateFlip", 9.5)
		f = open("calibration.txt", "w")
		f.write("\n".join(list(str(e) for e in self.getAll())))
		f.close()
		print "\nCompleted warm-up, make your gestures!\n"

	"""
	# Reset border inside dashed region
	def resetBoundBoxNoDash(self):
		moveToActivePanel()
		auto.click()
		border = (16.0 * nativeW / 2880.0) + (4.0 * scale)
		self.boundBoxNoDash = (border, macH + border, nativeW - border, nativeH - border)
		ImageGrab.grab(bbox=self.boundBoxNoDash).save(os.path.join("Images", "boundBoxNoDash.png"))
		print "boundBoxNoDash: %s" % (self.boundBoxNoDash,)
		auto.click()
	"""

	# Reset height of top bar and save it
	def resetTopBarHeight(self):
		moveToActivePanel()
		auto.click()
		ImageGrab.grab(bbox=(0, macH, nativeW, nativeH)).save(os.path.join("Images", "fullscreen.png"))
		auto.moveTo(auto.position()[0], 0)
		time.sleep(1)
		ImageGrab.grab(bbox=(0, macH, nativeW, nativeH)).save(os.path.join("Images", "afterTopBar.png"))
		topBarBox = get_bbox(os.path.join("Images", "fullscreen.png"), os.path.join("Images", "afterTopBar.png"))
		self.topBarHeight = topBarBox[3] - topBarBox[1] + 1
		ImageGrab.grab(bbox=(0, macH, nativeW, self.topBarHeight + macH)).save(os.path.join("Images", "topBar.png"))

	# Reset the right click
	def resetRightClick(self):
		moveToActivePanel()
		auto.click()
		beforeRightPath = os.path.join("Images", "RightClick", "beforeRight.png")
		ImageGrab.grab(bbox=boundBoxNoDash).save(beforeRightPath)
		auto.click(button='right')
		time.sleep(1)
		afterRightPath = os.path.join("Images", "RightClick", "afterRight.png")
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

		(self.rightx1, self.righty1) = (rightBox[0] + boundBoxNoDash[0], rightBox[1] + boundBoxNoDash[1])
		(x1, y1) = (self.rightx1 + self.rightIcons, self.righty1 + self.rightOffset)
		(x2, y2) = (self.rightx1 + self.rightBoxW, self.righty1 + self.rightBoxH)
		ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(os.path.join("Images", "RightClick", "rightClick.png"))

		moveToActivePanel()
		auto.click()

	# Reset rightClick's presets/scaleRotateFlip
	def resetRightOptions(self, option, offset):
		moveToActivePanel()
		auto.click()
		auto.click(button='right')
		"""located = auto.locateOnScreen(os.path.join("Images", "RightClick", "rightClick.png"))
		if (located is not None):
			(rightx1, righty1, w, h) = located
		else:
			print "Cannot find rightClick image, resetting."
			return"""
		moveToX = (self.rightx1 + self.rightBoxW / 2.0) / scale
		moveToY = ((self.righty1 + self.rightOffset) / scale) + (self.optionH * offset) + self.rightHR
		auto.moveTo(moveToX, moveToY)
		time.sleep(1)
		moveToActivePanel()
		auto.press("0")
		afterRightPath = os.path.join("Images", "RightClick", "afterRight.png")
		afterOptionPath = os.path.join("Images", "RightClick", "after" + option + ".png")
		ImageGrab.grab(bbox=boundBoxNoDash).save(afterOptionPath)
		box = get_bbox(afterRightPath, afterOptionPath)
		print option + " box: %s" % (box,)
		(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
		print option + " box WxH: %s" % ((boxW, boxH),)
		(x1, y1) = (box[0] + boundBoxNoDash[0], box[1] + boundBoxNoDash[1])
		optionPath = os.path.join("Images", "RightClick", option + ".png")
		ImageGrab.grab(bbox=(x1 + self.rightIcons, y1, x1 + boxW, y1 + boxH)).save(optionPath)
		auto.click()

calibration = Calibration()
(topBarHeight, optionH, rightHR, rightPlus, rightIcons, rightOffset, rightBoxW, rightBoxH) = calibration.getAll()


actionList = [["Admin", "Quit", "Get Status", "Switch Fetch", "Reset All", "Reset TopBar", "Reset RightClick", "Reset Presets", "Reset ScaleRotateFlip"],
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

# If the command and action are the same, meaning if a "#_0" command has been entered.
def defaultAction(commandID, paramSizes):
	openWindow(prompt)
	try:
		command = actionList[commandID][0]
		commandLen = len(actionList[commandID])
		rawInput = raw_input("Enter parameters for " + command + " <1-" + str(commandLen - 1) + "> <param1_param2_...>: ")
		openWindow(viewer)
		params = rawInput.split(" ")
		if (len(params) == 2 or len(params) == 1):
			if (int(params[0]) >= commandLen):
				promptNotify("Invalid action type given: <1-" + str(commandLen) + ">", 3)
				return (False, command)
			if (len(params[1].split("_")) not in paramSizes):
				promptNotify("Invalid parameter size given for " + command, 3)
				return (False, command)
			status["params"] = params[1]
			return (True, actionList[commandID][int(params[0])])
		else:
			promptNotify("Invalid parameters given", 3)
			return (False, command)
	except ValueError:
		promptNotify("Unrecognized parameters given for " + command, 3)
		return (False, command)

# Find Synapse's rightClick image
def findRightClick(offset):
	#auto.click(button='right')
	located = auto.locateOnScreen(os.path.join("Images", "RightClick", "rightClick.png"))
	if (located is not None):
		(x1, y1, w, h) = located
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, (y1 + (offset / 1000.0) * rightBoxH) / scale)
		return True
	else:
		print "Error when performing right click function."
		return False


openWindow(viewer)

def gestureCommands(sequence):
	(commandID, actionID) = (-1, -1)
	commandAction = sequence
	if (sequence.find(" ") != -1):
		commandAction = sequence[:sequence.find(" ")]
		status["params"] = sequence[sequence.find(" ") + 1:]
	else:
		status["params"] = ""
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


	if (command == "Admin"):
		if (action == "Quit"):
			removeImagesPrompt()
			sys.exit(0)
		elif (action == "Get Status"):
			print "------\nStatus\n------"
			print "Previous action: " + status["prev_action"]
			print "Panel Dimension: " + str(status["panel_dim"][0]) + 'x' + str(status["panel_dim"][1])
			print "Active panel: " + str(status["active_panel"][0]) + 'x' + str(status["active_panel"][1])
			print "Patient information window: " + ("opened" if status["window_open"] else "closed")
			print "Rulers: " + ("\n\t" + str(c) + ": " + status["rulers"][c] for c in status["rulers"] if c != "len")
			print "(topBarHeight, optionH, rightHR, rightPlus, rightIcons, rightOffset, rightBoxW, rightBoxH)",str(calibration.getAll())
			print ""
		elif (action == "Switch Fetch"):
			status["toUse"] = ("Keyboard" if status["toUse"] == "Images" else "Images")
		elif ("Reset " in action):
			action = action[6:]
			calibration = Calibration()
			if (action == "All"):
				calibration.resetAll()
			if (action == "TopBar"):
				calibration.resetTopBarHeight()
			elif (action == "RightClick"):
				calibration.resetRightClick()
			elif (action == "Presets"):
				calibration.resetRightOptions("presets", 8.5)
			elif (action == "ScaleRotateFlip"):
				calibration.resetRightOptions("scaleRotateFlip", 9.5)
			(topBarHeight, optionH, rightHR, rightPlus, rightIcons, rightOffset, rightBoxW, rightBoxH) = calibration.getAll()
			if ("hold_action" in status):
				sequence = status["hold_action"]
				status.pop("hold_action", None)
				return gestureCommands(sequence)
	elif (command == "Scroll" and action != "Scroll"):
		moveToActivePanel()
		auto.click()
		scrollAmount = (10 if status["params"] == "" else int(status["params"]))
		if (status["toUse"] != "Keyboard" and platform.system() != "Windows"):
			scrollAmount = (-1 * scrollAmount if action == "Up" else scrollAmount)
			auto.scroll(scrollAmount)
		else:
			auto.PAUSE = 0.1
			toPress = ("right" if action == "Up" else "left")
			for i in range(scrollAmount):
				auto.press(toPress)
			auto.PAUSE = 0.75
			auto.click()
	elif (command == "Flip" and action != "Flip"):
		moveToActivePanel()
		auto.click(button='right')
		if (status["toUse"] == "Images"):
			located = findRightClick(352)
			if (not located):
				status["hold_action"] = commandAction
				return gestureCommands("0_6")
			time.sleep(1)
			located = auto.locateOnScreen(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))
			if (located is None):
				status["hold_action"] = commandAction
				return gestureCommands("0_8")
			(x1, y1, w, h) = located
			y1 = y1 / scale;
			y1 += (rightPlus + (optionH * 0.5) if action == "Horizontal" else rightPlus + (optionH * 1.5))
			auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
			auto.click()
		else:
			auto.PAUSE = 0.2
			auto.press("0")
			for i in range(10):
				auto.press("down")
			auto.press("right")
			time.sleep(0.5)
			auto.press("0")
			if (action == "Horizontal"):
				auto.press("down")
			else:
				auto.press("down")
				auto.press("down")
			auto.press("enter")
			auto.PAUSE = 0.75
	elif (command == "Rotate" and action != "Rotate"):
		moveToActivePanel()
		auto.click(button='right')
		if (status["toUse"] == "Images"):
			located = findRightClick(352)
			if (not located):
				status["hold_action"] = commandAction
				return gestureCommands("0_6")
			time.sleep(1)
			located = auto.locateOnScreen(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))
			if (located is None):
				status["hold_action"] = commandAction
				return gestureCommands("0_8")
			(x1, y1, w, h) = located
			y1 = y1 / scale
			y1 += (rightPlus + (optionH * 2.5) if action == "Clockwise" else rightPlus + (optionH * 3.5))
			auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
			auto.click()
		else:
			auto.PAUSE = 0.2
			auto.press("0")
			for i in range(10):
				auto.press("down")
			auto.press("right")
			time.sleep(0.5)
			auto.press("0")
			if (action == "Clockwise"):
				auto.press("down")
				auto.press("down")
				auto.press("down")
			else:
				auto.press("down")
				auto.press("down")
				auto.press("down")
				auto.press("down")
			auto.PAUSE = 0.75
			auto.press("enter")
	elif (command == "Zoom"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1, 2, 3]))
		if (not isValid):
			return False
		else:
			splitParams = status["params"].split("_")
			if (len(splitParams) % 2 == 1 and status["params"] != ""):
				level = (-1 * int(splitParams[0]) if action == "Out" else int(splitParams[0]))
			else:
				level = (-20 if action == "Out" else 20)
			moveToActivePanel()
			auto.click()
			auto.click(button='right')
			if (status["toUse"] == "Images"):
				if (not findRightClick(54)):
					status["hold_action"] = commandAction
					return gestureCommands("0_6")
				auto.click()
			else:
				auto.press("z")
			if (len(splitParams) >= 2):
				(moveToX, moveToY) = auto.position()
			else:
				(moveToX, moveToY) = (int(splitParams[len(splitParams) - 2]), int(splitParams[len(splitParams) - 1]))
			auto.moveTo(moveToX, moveToY)
			auto.mouseDown()
			auto.moveTo(moveToX, moveToY + level)
			auto.mouseUp()
	elif (command == "Switch Panel" and action != "Switch Panel"):
		status["active_panel"][1] += (1 if action == "Right" else -1)
		status["active_panel"][0] += (1 if action == "Down" else -1)
		status["active_panel"][1] = (1 if status["active_panel"][0] < 1 else status["active_panel"][1])
		status["active_panel"][0] = (1 if status["active_panel"][0] < 1 else status["active_panel"][0])
		moveToActivePanel()
		auto.click()
	elif (command == "Pan"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1, 2, 3]))
		if (not isValid):
			return False
		else:
			splitParams = status["params"].split("_")
			if (len(splitParams) % 2 == 1 and status["params"] != ""):
				level = (-1 * int(splitParams[0]) if action == "Left" or action == "Up" else int(splitParams[0]))
			else:
				level = (-20 if action == "Left" or action == "Up" else 20)
			moveToActivePanel()
			auto.click()
			auto.click(button='right')
			if (status["toUse"] == "Images"):
				if (not findRightClick(54)):
					status["hold_action"] = commandAction
					return gestureCommands("0_6")
				auto.click()
			else:
				auto.press("p")
				auto.press("enter")
			if (len(splitParams) >= 2 or status["params"] == ""):
				(moveToX, moveToY) = auto.position()
			else:
				(moveToX, moveToY) = (int(splitParams[len(splitParams) - 2]), int(splitParams[len(splitParams) - 1]))
			auto.moveTo(moveToX, moveToY)
			auto.mouseDown()
			auto.moveTo(moveToX, moveToY + level)
			auto.mouseUp()
	elif (command == "Ruler"):
		if (action == "Measure"):
			(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [2, 4]))
			if (not isValid):
				return False
			else:
				moveToActivePanel()
				auto.click(button='right')
				if (status["toUse"] == "Images"):
					located = findRightClick(126)
					if (not located):
						status["hold_action"] = commandAction
						return gestureCommands("0_6")
					auto.click()
					time.sleep(2)
				else:
					auto.press("r")
					auto.press("enter")
				points = status["params"].split("_")
				try:
					if (len(points) == 4):
						(x1, y1, x2, y2) = (int(points[0]), int(points[1]), int(points[2]), int(points[3]))
					elif (len(points) == 2):
						(x1, y1) = auto.position()
						(x2, y2) = (int(points[0]), int(points[1]))
					else:
						print "Ruler measure parameters should include 2 or 4 non-negative integers separated by underscores."
				except ValueError:
					print "Ruler measure parameters should only include non-negative integers separated by underscores."
					return False
				auto.moveTo(x1, y1)
				auto.mouseDown()
				auto.moveTo(x2, y2)
				auto.mouseUp()
				status["rulers"]["len"] += 1
				curr = 1
				while (curr <= status["rulers"]["len"]):
					if (curr not in status["rulers"]):
						status["rulers"][curr] = str(x1) + "_" + str(y1) + "_" + str(x2) + "_" + str(y2)
						break
					curr += 1
				print "ID of Ruler Measurement: " + str(curr)
		elif (action == "Delete"):
			if (status["params"] == ""):
				print "Ruler delete ID not specified."
				openWindow(prompt)
				return False
			elif (len(status["params"].split("_")) != 1):
				print "Ruler delete ID must only be one positive integer."
				openWindow(prompt)
				return False
			try:
				rulerID = int(status["params"])
				if (rulerID not in status["rulers"]):
					print "Ruler delete ID is not in the list of rulers."
					openWindow(prompt)
					return False
			except ValueError:
				print "Ruler delete ID should be a positive integer value."
				openWindow(prompt)
				return False
			points = status["rulers"][rulerID].split("_")
			status["rulers"].pop(rulerID, None)
			status["rulers"]["len"] -= 1
			auto.moveTo((int(points[2]) + int(points[0])) / 2.0, (int(points[3]) + int(points[1])) / 2.0)
			auto.click(button='right')
			auto.PAUSE = 0.1
			auto.press("0")
			for i in range(5):
				auto.press("down")
			auto.press("enter")
			auto.pause = 0.75
			"""auto.click()
			beforeMeasure = ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("Images", "beforeMeasure.png"))
			auto.click(button="right")
			afterMeasure = ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("Images", "afterMeasure.png"))
			(x1, y1, x2, y2) = get_bbox(os.path.join("Images", "beforeMeasure.png"), os.path.join("Images", "afterMeasure.png"))
			diffX = x2 - x1
			x1 += boundBoxNoDash[0] + (rightIcons / scale) + (diffX / 2.0)
			y1 += boundBoxNoDash[1] + rightPlus + (optionH * 4.5)
			#(moveToX, moveToY) = ((x1 + x2) / 2.0, rightPlus + (optionH * 4.5))
			#auto.moveTo(x1 + (79.0 / 1440.0) * width, y1 + (85.0 / 900.0) * height)
			auto.moveTo(x1, y1)
			auto.click()"""
	elif (command == "Window" and action != "Window"):
		if (action == "Open" and not status["window_open"]):
			auto.moveTo(width / 2.0, 0)
			time.sleep(1)
			box = (1.0 * scale, topBarHeight, -1.0 * scale, -1.0 * scale)
			box = tuple(boundBoxNoDash[i] + box[i] for i in range(4))
			afterHoverPath = os.path.join("Images", "Window", "afterHover.png")
			if (not os.path.exists(afterHoverPath)):
				ImageGrab.grab(bbox=box).save(afterHoverPath)
			#auto.moveTo((329.0 / 1920.0) * nativeW, (82.0 / 1080.0) * nativeH + macH / scale)
			#auto.moveTo((218.0 / 1440.0) * width, (75.5.0 / 900.0) * height)
			#auto.moveTo((326.0 / 1920.0) * width, (78.0 / 1080.0) * height)
			auto.moveTo((435.0 / 2880.0) * nativeW / scale, ((107.0 + macH) / 1800.0) * nativeH / scale)
			auto.click()
			time.sleep(6)
			seriesThumbnailPath = os.path.join("Images", "Window", "seriesThumbnail.png")
			if (not os.path.exists(seriesThumbnailPath)):
				ImageGrab.grab(bbox=box).save(seriesThumbnailPath)
			diffSeriesPath = os.path.join("Images", "Window", "diffSeries.png")
			if (not os.path.exists(diffSeriesPath)):
				diffBox = get_bbox(afterHoverPath, seriesThumbnailPath)
				(x1, y1, x2, y2) = (diffBox[i] + box[(i % 2)] for i in range(4))
				ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffSeriesPath)
			else:
				(x1, y1, w, h) = auto.locateOnScreen(diffSeriesPath)
				(x2, y2) = (x1 + w, y1 + h)
			#(x1, y1) = (x2 - (83.0 / 2880.0) * nativeW,  y1 + (2.0 / 2880.0) * nativeW)
			#(x2, y2) = (x1 + (90.0 / 2880.0) * nativeW, y1 + (40.0 / 2880.0) * nativeW)
			(x1, y1) = (x2 - (10.0 * scale) - (90.0 / 2880.0) * nativeW, y1 + (2.0 * scale))
			(x2, y2) = (x2 - (10.0 * scale), y1 + (2.0 * scale) + (40.0 / 1800.0) * nativeH)
			seriesClosePath = os.path.join("Images", "Window", "Closes", "seriesClose.png")
			seriesClose_RedPath = os.path.join("Images", "Window", "Closes", "seriesClose_Red.png")
			seriesClose_GrayPath = os.path.join("Images", "Window", "Closes", "seriesClose_Gray.png")
			if (not os.path.exists(seriesClosePath)):
				ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClosePath)
			if (not os.path.exists(seriesClose_RedPath)):
				auto.moveTo((x1 + x2) / (scale * 2.0), (y1 + y2) / (scale * 2.0))
				ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClose_RedPath)
			if (not os.path.exists(seriesClose_GrayPath)):
				auto.moveTo(0, (y1 + y2) / (scale * 2.0))
				auto.click()
				ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClose_GrayPath)
			status["window_open"] = (not status["window_open"])
		elif (action == "Close" and status["window_open"]):
			for file in os.listdir(os.path.join("Images", "Window", "Closes")):
				close = auto.locateOnScreen(os.path.join("Images", "Window", "Closes", file))
				if (close is not None):
					(x1, y1, w, h) = close
					auto.moveTo((2 * x1 + w) / (scale * 2.0), (2 * y1 + h) / (scale * 2.0))
					auto.click()
					status["window_open"] = (not status["window_open"])
					break
	elif (command == "Manual Contrast"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (not isValid):
			return False
		else:
			splitParams = status["params"].split("_")
			if (splitParams[0] != ""):
				level = (-1 * int(splitParams[0]) if action == "Decrease" else int(splitParams[0]))
			else:
				level = (-20 if action == "Decrease" else 20)
			moveToActivePanel()
			auto.click(button='right')
			if (status["toUse"] == "Images"):
				located = findRightClick(18)
				if (not located):
					(status["raw_input"], status["hold_action"]) = ("0_6", commandAction)
					return False
				auto.click()
			else:
				auto.press("0")
				auto.press("down")
				auto.press("enter")
			moveToActivePanel()
			(oldLocationX, oldLocationY) = auto.position()
			auto.mouseDown()
			auto.moveTo(oldLocationX, oldLocationY + level)
			auto.mouseUp()
	elif (command == "Layout" and action != "Layout"):
		(oldLocationX, oldLocationY) = auto.position()
		auto.moveTo(oldLocationX, 0)
		time.sleep(1)
		box = (1.0 * scale, topBarHeight, -1.0 * scale, -1.0 * scale)
		box = tuple(boundBoxNoDash[i] + box[i] for i in range(4))
		afterHoverPath = os.path.join("Images", "Layout", "afterHover.png")
		if (not os.path.exists(afterHoverPath)):
			ImageGrab.grab(bbox=box).save(os.path.join("Images", "Layout", "afterHover.png"))
		#auto.moveTo((329.0 / 1920.0) * width, (82.0 / 1080.0) * height)
		#auto.moveTo((643.0 / 1920.0) * nativeW, (82.0 / 1080.0) * nativeH)
		#auto.moveTo((428.0 / 1920.0) * width, (77.0 / 1080.0) * height)
		#auto.moveTo((435.0 / 2880.0) * nativeW / scale, ((107.0 + macH) / 1800.0) * nativeH / scale)
		#moveToY = (61.0 * nativeW / 2880.0)
		auto.moveTo((857.0 / 2880.0) * nativeW / scale, ((109.0 + macH) / 1800.0) * nativeH / scale)
		auto.click()
		time.sleep(5)
		windowPath = os.path.join("Images", "Layout", "window.png")
		if (not os.path.exists(windowPath)):
			ImageGrab.grab(bbox=box).save(os.path.join("Images", "Layout", "window.png"))
		diffBox = get_bbox(afterHoverPath, windowPath)
		(x1, y1, x2, y2) = (diffBox[i] + box[(i % 2)] for i in range(4))
		diffLayoutPath = os.path.join("Images", "Layout", "diffLayout.png")
		if (not os.path.exists(diffLayoutPath)):
			ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffLayoutPath)
		x1 += (68.0 / 1920.0) * nativeW
		y1 += (95.0 / 1080.0) * nativeH
		jumpX = (91.0 / 1920.0) * nativeW
		(status["panel_dim"][0], status["panel_dim"][1]) = (1, actionID)
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
		if (status["toUse"] == "Images"):
			located = findRightClick(316)
			if (not located):
				status["hold_action"] = commandAction
				return gestureCommands("0_6")
			located = auto.locateOnScreen(os.path.join("Images", "RightClick", "presets.png"))
			if (located is None):
				status["hold_action"] = commandAction
				return gestureCommands("0_7")
			(x1, y1, w, h) = located
			y1 = y1 / scale
			y1 += rightPlus + (optionH * (actionID + 0.5))
			auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
			auto.click()
		else:
			auto.PAUSE = 0.1
			auto.press("0")
			for i in range(9):
				auto.press("down")
			auto.press("right")
			time.sleep(0.5)
			auto.press("0")
			auto.press("down")
			for i in range(actionID):
				auto.press("down")
			auto.press("enter")
			auto.PAUSE = 0.75

	if (command != "Admin"):
		status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)


	#openWindow(prompt)
	
	return True

# When quitting program, remove anything saved
#removeImages()
