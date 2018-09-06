import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import ImageGrab
#from PIL import ImageChops

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

#window_names = auto.getWindow("Citrix Viewer")

if (platform.system() == "Windows"):
	#(offsetY1, offsetY2) = (0, 0)
	macHeader = 0
	#borderDash = 16
	navType = "alt"
else:
	#(offsetY1, offsetY2) = (44, 84)
	macHeader = (44.0 / 2880.0) * (nativeH)
	#borderDash = 22
	navType = "command"


print "Warming up synapse system...\n"
auto.hotkey(navType, "tab")


# Get height of top bar and save it
auto.moveTo(width / 2.0, height / 2.0)
fullscreen = ImageGrab.grab()
fullscreen.save(os.path.join("Images", "fullscreen.png"))
auto.moveTo(width / 2.0, 0)
time.sleep(1)
auto.moveTo(width / 2.0, macHeader)
time.sleep(1)
afterTopBar = ImageGrab.grab()
afterTopBar.save(os.path.join("Images", "afterTopBar.png"))
topBarBox = get_bbox(os.path.join("Images", "fullscreen.png"), os.path.join("Images", "afterTopBar.png"))
topBarHeight = topBarBox[3]
os.remove(os.path.join("Images", "afterTopBar.png"))


# Get border of dashed region
auto.moveTo(width / 2.0, height / 2.0)
auto.click(button='right')
noDash = ImageGrab.grab()
noDash.save(os.path.join("Images", "noDash.png"))
boundBoxNoDash = get_bbox(os.path.join("Images", "fullscreen.png"), os.path.join("Images", "noDash.png"))
print "boundBoxNoDash: %s" % (boundBoxNoDash,)
boundBoxNoDash = (boundBoxNoDash[0] + (10 * scale), boundBoxNoDash[1] + (10 * scale), boundBoxNoDash[2] - (10 * scale), boundBoxNoDash[3] - (10 * scale))
#borderDash = topBarHeight / 2.0
#boundBoxNoDash = (borderDash, borderDash, nativeW - borderDash, nativeH - borderDash)
(bbndW, bbndH) = ((boundBoxNoDash[2] - boundBoxNoDash[0]) / scale, (boundBoxNoDash[3] - boundBoxNoDash[1]) / scale)
print "boundBoxNoDash: %s" % (boundBoxNoDash,)
print "boundBoxNoDash WxH: %s" % ((bbndW, bbndH),)
os.remove(os.path.join("Images", "noDash.png"))
os.remove(os.path.join("Images", "fullscreen.png"))
#os.remove(os.path.join("Images", "boundBoxNoDash.png"))
auto.click()


# Get and store the right click
auto.moveTo(width / 2.0, height / 2.0)
beforeRight = ImageGrab.grab(bbox=boundBoxNoDash)
beforeRight.save(os.path.join("Images", "RightClick", "beforeRight.png"))
auto.click(button='right')
afterRight = ImageGrab.grab(bbox=boundBoxNoDash)
afterRight.save(os.path.join("Images", "RightClick", "afterRight.png"))
rightBox = get_bbox(os.path.join("Images", "RightClick", "beforeRight.png"), os.path.join("Images", "RightClick", "afterRight.png"))
print "rightBox: %s" % (rightBox,)
(rightBoxW, rightBoxH) = (rightBox[2] - rightBox[0] + 1, rightBox[3] - rightBox[1] + 1)
print "rightBox WxH: %s" % ((rightBoxW, rightBoxH),)

optionH = ((rightBoxH / 1000.0) * 36) / scale
rightHR = ((rightBoxH / 1000.0) * 10) / scale
rightIcons = ((rightBoxH / 1000.0) * 50)
rightOffset = ((rightBoxH / 1000.0) * 58)

(rightx1, righty1) = (rightBox[0] + boundBoxNoDash[0], rightBox[1] + boundBoxNoDash[1])
rightClick = ImageGrab.grab(bbox=(rightx1 + rightIcons, righty1 + rightOffset, rightx1 + rightBoxW, righty1 + rightBoxH))
rightClick.save(os.path.join("Images", "RightClick", "rightClick.png"))


# Get and store image presets
auto.moveTo((rightx1 + rightBoxW / 2.0) / scale, (((righty1 + rightOffset) / scale) + (optionH * 8.5) + rightHR))
time.sleep(1)
auto.moveTo(rightx1 / scale, righty1 / scale)
afterPresets = ImageGrab.grab(bbox=boundBoxNoDash)
afterPresets.save(os.path.join("Images", "RightClick", "afterPresets.png"))
box = get_bbox(os.path.join("Images", "RightClick", "afterRight.png"), os.path.join("Images", "RightClick", "afterPresets.png"))
print "presets box: %s" % (box,)
(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
print "presets box WxH: %s" % ((boxW, boxH),)
(x1, y1) = (box[0] + boundBoxNoDash[0], box[1] + boundBoxNoDash[1])
presets = ImageGrab.grab(bbox=(x1 + rightIcons, y1, x1 + boxW, y1 + boxH))
presets.save(os.path.join("Images", "RightClick", "presets.png"))


# Get and store scale-rotate-flip
auto.moveTo((rightx1 + rightBoxW / 2.0) / scale, (((righty1 + rightOffset) / scale) + (optionH * 9.5) + rightHR))
time.sleep(1)
auto.moveTo(rightx1 / scale, righty1 / scale)
afterSRF = ImageGrab.grab(bbox=boundBoxNoDash)
afterSRF.save(os.path.join("Images", "RightClick", "afterSRF.png"))
box = get_bbox(os.path.join("Images", "RightClick", "afterRight.png"), os.path.join("Images", "RightClick", "afterSRF.png"))
print "srf box: %s" % (box,)
(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
print "srf box WxH: %s" % ((boxW, boxH),)
(x1, y1) = (box[0] + boundBoxNoDash[0], box[1] + boundBoxNoDash[1])
scaleRotateFlip = ImageGrab.grab(bbox=(x1 + rightIcons, y1, x1 + boxW, y1 + boxH))
scaleRotateFlip.save(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))

os.remove(os.path.join("Images", "RightClick", "beforeRight.png"))
os.remove(os.path.join("Images", "RightClick", "afterRight.png"))
os.remove(os.path.join("Images", "RightClick", "afterPresets.png"))
os.remove(os.path.join("Images", "RightClick", "afterSRF.png"))

auto.click()
auto.hotkey(navType, "tab")
print "Completed warm-up, make your gestures!\n"


status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1], "params": ""}

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
	(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "rightClick.png"))
	#print "rightClick function: %s" % ((x1, y1, w, h),)
	#auto.moveTo((2 * x1 + w) / 4.0, (y1 + (offset / 1000.0) * rightBoxH) / 2.0)
	auto.moveTo((x1 / scale) + (w / 2.0) * scale, (y1 + (offset / 1000.0) * rightBoxH) / scale)
	
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
	auto.hotkey(navType, "tab")
	if (command == "Admin"):
		if (action == "Quit"):
			break
		elif (action == "Get Status"):
			get_status()
	elif (command == "Scroll" and action != "Scroll"):
		scrollAmount = (10 if status["params"] == "" else int(status["params"]))
		scrollAmount = (-1 * scrollAmount if action == "Up" else scrollAmount)
		auto.scroll(scrollAmount)
	elif (command == "Flip" and action != "Flip"):
		rightClick(352)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))
		y1 = y1 / scale;
		y1 += (8 + (optionH * 0.5) if action == "Horizontal" else 8 + (optionH * 1.5))
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
		auto.click()
	elif (command == "Rotate" and action != "Rotate"):
		rightClick(352)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))
		y1 = y1 / scale
		y1 += (8 + (optionH * 2.5) if action == "Clockwise" else 8 + (optionH * 3.5))
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
		auto.click()
	elif (command == "Zoom"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			(oldLocationX, oldLocationY) = auto.position()
			rightClick(54)
			auto.click()
			auto.moveTo(oldLocationX, oldLocationY)
			auto.mouseDown()
			if (status["params"] != ""):
				level = (-1 * int(status["params"]) if action == "In" else int(status["params"]))
			else:
				level = (-20 if action == "In" else 20)
			auto.moveTo(oldLocationX, oldLocationY + level)
			auto.mouseUp()
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
			(oldLocationX, oldLocationY) = auto.position()
			rightClick(90)
			auto.click()
			auto.moveTo(oldLocationX, oldLocationY)
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
				rightClick(126)
				auto.click()
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
			auto.moveTo(oldLocationX, 0)
			time.sleep(1)
			auto.moveTo(oldLocationX, macHeader)
			afterHover = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
			afterHover.save(os.path.join("Images", "window_afterHover.png"))
			#auto.moveTo((219.0 / 1440.0) * width, (77.0 / 900.0) * height)
			auto.moveTo((326.0 / 1920.0) * width, (78.0 / 1080.0) * height)
			auto.click()
			time.sleep(6)
			seriesThumbnail = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
			seriesThumbnail.save(os.path.join("Images", "window_seriesThumbnail.png"))
			(x1, y1, x2, y2) = get_bbox(os.path.join("Images", "window_afterHover.png"), os.path.join("Images", "window_seriesThumbnail.png"))
			"""x1 += (20.0 / 1440.0) * width
			y1 += (272.0 / 900.0) * height
			diff = ImageGrab.grab(bbox=(x1, y1, x2, y2))
			diff.save(os.path.join("Images", "window_diff.png"))
			close = ImageGrab.grab(bbox=((x2 - 83), (y1 + 2), (x2 - 83) + 90, (y1 + 2) + 40))
			close.save(os.path.join("Images", "window_seriesThumbnailClose.png"))
			auto.moveTo((2 * (x2 - 83) + 90) / 4, (2 * (y1 + 2) + 40) / 4)
			close = ImageGrab.grab(bbox=((x2 - 83), (y1 + 2), (x2 - 83) + 90, (y1 + 2) + 40))
			close.save(os.path.join("Images", "window_seriesThumbnailClose_Red.png"))
			auto.moveTo(x2 + 1, (2 * (y1 + 2) + 40) / 4)
			auto.click()
			close = ImageGrab.grab(bbox=((x2 - 83), (y1 + 2), (x2 - 83) + 90, (y1 + 2) + 40))
			close.save(os.path.join("Images", "window_seriesThumbnailClose_Gray.png"))"""
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
			rightClick(18)
			auto.click()
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
		#auto.moveTo((428.0 / 2880.0) * nativeW, (77.0 / 2880.0) * nativeW)
		auto.moveTo((642.0 / 1920.0) * width, (80.0 / 1080.0) * height)
		auto.click()
		seriesThumbnail = ImageGrab.grab(bbox=(boundBoxNoDash[0] + (1 * scale), boundBoxNoDash[1] + topBarHeight + (1 * scale), boundBoxNoDash[2] + (1 * scale), boundBoxNoDash[3] + (1 * scale)))
		seriesThumbnail.save(os.path.join("Images", "layout_seriesThumbnail.png"))
		(x1, y1, x2, y2) = get_bbox(os.path.join("Images", "layout_afterHover.png"), os.path.join("Images", "layout_seriesThumbnail.png"))
		(diffW, diffH) = (x2 - x1 + 1, y2 - y1 + 1)
		x1 += boundBoxNoDash[0] + (1 * scale)
		y1 += boundBoxNoDash[1] + topBarHeight + (1 * scale)
		(x2, y2) = (x1 + diffW, y1 + diffH)
		ImageGrab.grab(bbox=(x1, y1, x2, y2)).save("diffLayout.png")
		status["panel_dim"][0] = 1
		if (action == "One-Panel"):
			#auto.moveTo((x1 + 20) / 2 + 45, y1 / 2 + 200)
			auto.moveTo((x1 + (68.0 / 1920.0) * nativeW) / scale, (y1 + (95.0 / 1920.0) * nativeW) / scale)
			status["panel_dim"][1] = 1
		elif (action == "Two-Panels"):
			#auto.moveTo((x1 + 20) / 2 + 107, y1 / 2 + 200)
			auto.moveTo((x1 + (160.0 / 1920.0) * nativeW) / scale, (y1 + (95.0 / 1920.0) * nativeW) / scale)
			status["panel_dim"][1] = 2
		elif (action == "Three-Panels"):
			#auto.moveTo((x1 + 20) / 2 + 169, y1 / 2 + 200)
			auto.moveTo((x1 + (252.0 / 1920.0) * nativeW) / scale, (y1 + (95.0 / 1920.0) * nativeW) / scale)
			status["panel_dim"][1] = 3
		elif (action == "Four-Panels"):
			#auto.moveTo((x1 + 20) / 2 + 231, y1 / 2 + 200)
			auto.moveTo((x1 + (344.0 / 1920.0) * nativeW) / scale, (y1 + (95.0 / 1920.0) * nativeW) / scale)
			status["panel_dim"][1] = 4
		auto.click()
		resetPanelMoves()
		moveToActivePanel()
		auto.click()
	elif (command == "Contrast Presets" and action != "Contrast Presets"):
		moveToActivePanel()
		rightClick(316)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen(os.path.join("Images", "RightClick", "presets.png"))
		y1 = y1 / scale
		y1 += 8 + (optionH * 0.5)
		if (action == "I"):
			y1 += optionH
		elif (action == "II"):
			y1 += optionH * 2
		auto.moveTo((x1 / scale) + (w / 2.0) * scale, y1)
		auto.click()
	status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)
	status["params"] = ""
	if (platform.system() == "Windows" and command == "Windows" and action == "Open"):
		auto.keyDown(navType)
		auto.press("tab")
		auto.press("tab")
		auto.keyUp(navType)
	else:
		auto.hotkey(navType, "tab")


# When quitting program, remove anything saved
#if ()