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

macHeader = (44.0 / 2880.0) * (nativeH)
(viewer, prompt) = ("Citrix Viewer", "Teminal")

def openWindow(toOpen):
	window_names = auto.getWindows().keys()
	print "window_names: "
	print window_names
	print ""
	for window_name in window_names:
		auto.getWindow(window_name).close()
		if (toOpen in window_name):
			xef_window_name = window_name
			print "xef_window_name:"
			print xef_window_name
			print ""
	#matched_keys = [window_name for window_name in window_names if toOpen in window_name]
	#if (len(matched_keys) != 0):
		#xef_window_name = matched_keys[0]
	xef_window = auto.getWindow(xef_window_name)
	xef_window.maximize()


print "Warming up osirix system...\n"
openWindow(viewer)


status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1], "params": ""}

def resetPanelMoves():
	status["firstW"] = ((float(width) - 110.0) / (float(status["panel_dim"][1]) * 2.0))
	status["firstH"] = ((float(height) - 100.0 - float(status["panel_dim"][0]) * 38.0) / (float(status["panel_dim"][0]) * 2.0))
	status["jumpW"] = (status["firstW"] * 2.0 if status["panel_dim"][1] != 1 else 0)
	status["jumpH"] = (status["firstH"] * 2.0 if status["panel_dim"][0] != 1 else 0)

resetPanelMoves()

def moveToActivePanel():
	moveToX = 110.0 + status["firstW"] + (status["active_panel"][1] - 1) * (status["jumpW"])
	moveToY = 100.0 + status["firstH"] + (status["active_panel"][0] - 1) * (status["jumpH"]) + float(status["panel_dim"][0]) * 38.0
	auto.moveTo(moveToX, moveToY)

actionList = [["Admin", "Quit", "Get Status"],
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
			#invalidSize = (invalidSize | (len(params[1].split("_")) != paramSize) for paramSize in paramSizes)
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
	(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/rightClick.png")
	auto.moveTo((2 * x1 + w) / 4, (y1 + (offset / 1000.0) * rightBoxH) / 2)

def get_status():
	print "\nStatus\n------"
	print "Previous action: " + status["prev_action"]
	print "Panel Dimension: " + str(status["panel_dim"][0]) + 'x' + str(status["panel_dim"][1])
	print "Active panel: " + str(status["active_panel"][0]) + 'x' + str(status["active_panel"][1])
	print "Patient information window: " + ("opened" if status["window_open"] else "closed")


openWindow(prompt)
print "\nCompleted warm-up, make your gestures!\n"


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
	elif (command == "Scroll" and action != "Scroll"):
		scrollAmount = (10 if status["params"] == "" else int(status["params"]))
		auto.scroll((-1 * scrollAmount if action == "Up" else scrollAmount))
	elif (command == "Flip" and action != "Flip"):
		moveToActivePanel()
		auto.click()
		toPress = ("h" if action == "Horizontal" else "v")
		auto.press(toPress)
	elif (command == "Rotate" and action != "Rotate"):
		moveToActivePanel()
		auto.click()
		auto.moveTo(794.0 / scale, macHeader / (2.0 * scale))
		auto.click()
		(moveToX, moveToY) = (1089.0, (macHeader / 2.0) + (7.0 + (38.0 * 5.0) + 24.0 + (38.0) + 24.0 + (38.0 * 4.5)))
		auto.moveTo(moveToX / scale, moveToY / scale)
		moveToX = (1468.0 + (482.0 / 2.0))
		auto.moveTo(moveToX / scale, moveToY / scale)
		moveToY += (-1.0 * (38.0 * 0.5) + (64.0 * 2.0) + 22.0 + 92.0)
		moveToY += ((106.0 * 0.5) if action == "Clockwise" else 106.0 + (96.0 * 0.5))
		auto.moveTo(moveToX / scale, moveToY / scale)
		auto.click()
	elif (command == "Zoom"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			(oldLocationX, oldLocationY) = auto.position()
			#moveToActivePanel()
			auto.press("z")
			#auto.mouseDown()
			if (status["params"] != ""):
				level = (-1 * int(status["params"]) if action == "In" else int(status["params"]))
			else:
				level = (-20 if action == "In" else 20)
			auto.PAUSE = 0
			auto.mouseDown()
			auto.moveTo(oldLocationX, oldLocationY + level)
			auto.mouseUp()
			auto.PAUSE = 0.75
	elif (command == "Switch Panel" and action != "Switch Panel"):
		if (action == "Right" or action == "Left"):
			status["active_panel"][1] += (-1 if action == "Left" else 1)
			if (status["active_panel"][1] < 1):
				status["active_panel"][1] = 1
		else:
			status["active_panel"][0] += (-1 if action == "Up" else 1)
			if (status["active_panel"][0] < 1):
				status["active_panel"][0] = 1
		moveToActivePanel()
		auto.click()
	elif (command == "Pan"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			moveToActivePanel()
			(oldLocationX, oldLocationY) = auto.position()
			auto.press("m")
			auto.mouseDown()
			if (status["params"] != ""):
				level = (-1 * int(status["params"]) if action == "Up" or action == "Left" else int(status["params"]))
			else:
				level = (-20 if action == "Up" or action == "Left" else 20)
			oldLocationX += (0 if action == "Up" or action == "Down" else level)
			oldLocationY += (level if action == "Up" or action == "Down" else 0)
			auto.moveTo(oldLocationX, oldLocationY)
			auto.mouseUp()
	elif (command == "Ruler"):
		if (action == "Measure"):
			(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [2, 4]))
			if (isValid):
				moveToActivePanel()
				auto.click()
				auto.press("l")
				points = status["params"].split("_")
				try:
					if (len(points) == 4):
						(x1, y1, x2, y2) = (int(points[0]), int(points[1]), int(points[2]), int(points[3]))
					elif (len(points) == 2):
						(x1, y1) = auto.position()
						(x2, y2) = (int(points[0]), int(points[1]))
				except ValueError:
					print "Ruler parameters should only include non-negative integers separated by underscores."
					continue
				auto.moveTo(x1, y1)
				auto.click()
				auto.mouseDown()
				auto.moveTo(x2, y2)
				auto.mouseUp()
		elif (action == "Delete"):
			(x, y) = auto.position()
			auto.click()
			auto.click(button="right")
			auto.moveTo(x + 79, y + 85)
			auto.click()
	elif (command == "Window" and action != "Window"):
		(oldLocationX, oldLocationY) = auto.position()
		if (action == "Open" and not status["window_open"]):
			"""auto.moveTo(oldLocationX, 0)
			time.sleep(1)
			auto.moveTo(oldLocationX, macHeader)
			afterHover = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
			afterHover.save(os.path.join("Images", "window_afterHover.png"))
			auto.moveTo((326.0 / 1920.0) * width, (78.0 / 1080.0) * height)
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
			close.save(os.path.join("Images", "window_seriesThumbnailClose_Gray.png"))"""
			status["window_open"] = (not status["window_open"])
		elif (action == "Close" and status["window_open"]):
			"""close = auto.locateOnScreen(os.path.join("Images", "window_seriesThumbnailClose.png"))
			if (close is None):
				close = auto.locateOnScreen(os.path.join("Images", "window_seriesThumbnailClose_Red.png"))
			if (close is None):
				close = auto.locateOnScreen(os.path.join("Images", "window_seriesThumbnailClose_Gray.png"))
			(x1, y1, w, h) = close
			(x2, y2) = (x1 + w, y1 + h)
			auto.moveTo((x1 + x2) / (scale * 2.0), (y1 + y2) / (scale * 2.0))
			auto.click()"""
			status["window_open"] = (not status["window_open"])
	elif (command == "Manual Contrast"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			moveToActivePanel()
			auto.press("w")
			auto.mouseDown()
			if (status["params"] != ""):
				level = (int(status["params"]) if action == "Increase" else -1 * int(status["params"]))
			else:
				level = (20 if action == "Increase" else -20)
			auto.moveTo(moveToX, moveToY + level)
			auto.mouseUp()
	elif (command == "Layout" and action != "Layout"):
		auto.moveTo(194.0 / scale, 105.0 / scale)
		auto.scroll(200)
		status["panel_dim"][0] = 1
		if (action == "One-Panel"):
			status["panel_dim"][1] = 1
		elif (action == "Two-Panels"):
			status["panel_dim"][1] = 2
		elif (action == "Three-Panels"):
			status["panel_dim"][1] = 3
		elif (action == "Four-Panels"):
			status["panel_dim"][1] = 4
		auto.moveTo(225.0 / scale, (20.0 + 126 * (status["panel_dim"][1] - 0.5)) / scale)
		auto.click()
		resetPanelMoves()
		(status["active_panel"][0], status["active_panel"][1]) = (1, 1)
		moveToActivePanel()
		auto.click()
	elif (command == "Contrast Presets" and action != "Contrast Presets"):
		# much easier if contrast presets parameters were just the numbers, not the Roman numerals
		if (action == "I"):
			toPress = "1"
		elif (action == "II"):
			toPress = "2"
		auto.press(toPress)

	if (command != "Admin"):
		status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)
		status["params"] = ""

	openWindow(prompt)



# When quitting program, remove anything saved
removeImages()
