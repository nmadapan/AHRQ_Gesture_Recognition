import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import ImageGrab
#from PIL import ImageChops

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
	macHeader = 44
	#borderDash = 22
	navType = "command"

auto.FAILSAFE = True
auto.PAUSE = 0.75

(width, height) = auto.size()
(nativeW, nativeH) = ImageGrab.grab().size
scale = nativeW / width

borderDash = (20 + 2) * scale

auto.hotkey(navType, "tab")

"""auto.moveTo(width / 2, height / 2)
beforeDashed = ImageGrab.grab()
beforeDashed.save(os.path.join("Images", "beforeDashed.png"))
auto.click(button='right')
afterDashed = ImageGrab.grab()
afterDashed.save(os.path.join("Images", "afterDashed.png"))
dashed = get_bbox(os.path.join("Images", "beforeDashed.png"), os.path.join("Images", "afterDashed.png"))
ImageGrab.grab(bbox=dashed).save(os.path.join("Images", "dashed.png"))
boundBoxNoDash = (dashed[0] + 3, dashed[1] + 3, dashed[2] + 3, dashed[3] + 3)"""
boundBoxNoDash = (0 + borderDash, 0 + borderDash, nativeW - borderDash, nativeH - borderDash)
(bbndW, bbndH) = ((boundBoxNoDash[2] - boundBoxNoDash[0]) / scale, (boundBoxNoDash[3] - boundBoxNoDash[1]) / scale)

#print "WxH: %s" % ((width, height),)
#boundBox = (0, offsetY1, width * scale, (height - offsetY2) * scale)
#print "%s" % (boundBox,)
#(boundBoxW, boundBoxH) = ((boundBox[2] - boundBox[0]) * scale / 2.0, (boundBox[3] - boundBox[1]) * scale / 2.0)
#print "%s" % ((boundBoxW, boundBoxH),)
#boundBoxNoTopBar = (0, 272, width * 2, (height - offsetY2) * 2)
#boundBoxNoDash = (borderDash, macHeader + borderDash, width * scale - borderDash, (height - offsetY2) * scale - borderDash)
#ImageGrab.grab(bbox=boundBoxNoDash).save(os.path.join("Images", "boundBoxNoDash.png"))
#print "boundBoxNoDash: %s" % (boundBoxNoDash,)

auto.moveTo(width / 2.0, height / 2.0)
time.sleep(1)
beforeTopBar = ImageGrab.grab()
beforeTopBar.save(os.path.join("Images", "beforeTopBar.png"))
auto.moveTo(width / 2.0, 0)
time.sleep(1)
auto.moveTo(width / 2.0, macHeader)
time.sleep(1)
afterTopBar = ImageGrab.grab()
afterTopBar.save(os.path.join("Images", "afterTopBar.png"))
topBarBox = get_bbox(os.path.join("Images", "beforeTopBar.png"), os.path.join("Images", "afterTopBar.png"))
topBarHeight = topBarBox[3]
topBarBox = (0, 0, nativeW, topBarHeight)
ImageGrab.grab(bbox=topBarBox).save(os.path.join("Images", "topBarBox.png"))
#print "topBarBox: %s" % (topBarBox,)

#boundBoxNoTopBarDash = (borderDash, topBarBox[3] - topBarBox[1], width * scale - borderDash, (height - offsetY2) * scale - borderDash)
"""boundBoxNoTopBarDash = (boundBoxNoDash[0], topBarBox[1], boundBoxNoDash[2], boundBoxNoDash[3])
ImageGrab.grab(bbox=boundBoxNoTopBarDash).save(os.path.join("Images", "boundBoxNoTopBarDash.png"))
print "boundBoxNoTopBarDash: %s" % (boundBoxNoTopBarDash,)"""

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

# Get and store the right click
auto.moveTo(bbndW / 2.0, bbndH / 2.0)
beforeRight = ImageGrab.grab(bbox=boundBoxNoDash)
beforeRight.save(os.path.join("Images", "RightClick", "beforeRight.png"))
auto.click(button='right')
afterRight = ImageGrab.grab(bbox=boundBoxNoDash)
afterRight.save(os.path.join("Images", "RightClick", "afterRight.png"))
rightBox = get_bbox(os.path.join("Images", "RightClick", "beforeRight.png"), os.path.join("Images", "RightClick", "afterRight.png"))
#print "rightBox: %s" % (rightBox,)
(rightBoxW, rightBoxH) = (rightBox[2] - rightBox[0] + 1, rightBox[3] - rightBox[1] + 1)
#print "rightBox WxH: %s" % ((rightBoxW, rightBoxH),)

optionH = ((rightBoxH / 1000.0) * 36) / scale
rightHR = ((rightBoxH / 1000.0) * 10) / scale

rightIcons = ((rightBoxH / 1000.0) * 50)
rightOffset = ((rightBoxH / 1000.0) * 58)

#(rightBoxW, rightBoxH) = (382, 1000)
"""(x1, y1) = ((rightBox[0] + boundBoxNoDash[0]) * scale / 2.0, (rightBox[1] + boundBoxNoDash[1]) * scale / 2.0)
rightClick = ImageGrab.grab(bbox=((x1) * scale, (y1) * scale, (x1) * scale + rightBoxW, (y1) * scale + rightBoxH))
rightClick.save(os.path.join("Images", "RightClick", "rightClick.png"))"""
(rightx1, righty1) = (rightBox[0] + boundBoxNoDash[0], rightBox[1] + boundBoxNoDash[1])
rightClick = ImageGrab.grab(bbox=(rightx1 + rightIcons, righty1 + rightOffset, rightx1 + rightBoxW, righty1 + rightBoxH))
rightClick.save(os.path.join("Images", "RightClick", "rightClick.png"))

# Get and store image presets
#auto.moveTo(((x1) * scale + rightBoxW / 2.0) / 2, ((y1) * scale + 374) / 2)
auto.moveTo((rightx1 / scale + (rightx1 + rightBoxW) / scale) / 2.0, ((righty1 + rightOffset) / scale + (optionH * 8.5) + (rightHR)))
time.sleep(1)
auto.moveTo(rightx1 / scale, righty1 / scale)
afterPresets = ImageGrab.grab(bbox=boundBoxNoDash)
afterPresets.save(os.path.join("Images", "RightClick", "afterPresets.png"))
box = get_bbox(os.path.join("Images", "RightClick", "afterRight.png"), os.path.join("Images", "RightClick", "afterPresets.png"))
(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
(x1, y1) = (box[0] + boundBoxNoDash[0], box[1] + boundBoxNoDash[1])
#boxH = 8 * 2 + 36 * 21
#presets = ImageGrab.grab(bbox=(((x1) + 180 + 25) * scale, ((y1) + 187 - 9) * scale, ((x1) + 180) * scale + boxW, ((y1) + 187 - 9) * scale + boxH))
presetsW = boxW
presets = ImageGrab.grab(bbox=(x1 + rightIcons, y1, x1 + boxW, y1 + boxH))
presets.save(os.path.join("Images", "RightClick", "presets.png"))

# Get and store scale-rotate-flip
#auto.moveTo(((x1) * scale + rightBoxW / 2.0) / 2, ((y1 + 1) * scale + 410) / 2)
auto.moveTo((rightx1 / scale + (rightx1 + rightBoxW) / scale) / 2.0, ((righty1 + rightOffset) / scale + (optionH * 9.5) + (rightHR)))
time.sleep(1)
auto.moveTo(rightx1 / scale, righty1 / scale)
afterSRF = ImageGrab.grab(bbox=boundBoxNoDash)
afterSRF.save(os.path.join("Images", "RightClick", "afterSRF.png"))
box = get_bbox(os.path.join("Images", "RightClick", "afterRight.png"), os.path.join("Images", "RightClick", "afterSRF.png"))
(boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
(x1, y1) = (box[0] + boundBoxNoDash[0], box[1] + boundBoxNoDash[1])
#boxH = 8 * 2 + 36 * 7
#scaleRotateFlip = ImageGrab.grab(bbox=(((x1) + 180 + 25) * scale, ((y1) + 205 - 9) * scale, ((x1) + 180) * scale + boxW, ((y1) + 205 - 9) * scale + boxH))
scaleRotateFlipW = boxW
scaleRotateFlip = ImageGrab.grab(bbox=(x1 + rightIcons, y1, x1 + boxW, y1 + boxH))
scaleRotateFlip.save(os.path.join("Images", "RightClick", "scaleRotateFlip.png"))

os.remove(os.path.join("Images", "RightClick", "beforeRight.png"))
os.remove(os.path.join("Images", "RightClick", "afterRight.png"))
os.remove(os.path.join("Images", "RightClick", "afterPresets.png"))
os.remove(os.path.join("Images", "RightClick", "afterSRF.png"))

auto.click()
auto.hotkey(navType, "tab")



status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1], "params": ""}

def resetPanelMoves():
	status["firstW"] = (float(boundBoxNoDash[2] - boundBoxNoDash[0]) / (float(status["panel_dim"][1]) * 4.0))
	status["firstH"] = (float(height) / (float(status["panel_dim"][0]) * 2.0))
	status["jumpW"] = (status["firstW"] * 2.0 if status["panel_dim"][1] != 1 else 0)
	status["jumpH"] = (status["firstH"] * 2.0 if status["panel_dim"][0] != 1 else 0)

resetPanelMoves()


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
		auto.scroll((-1 * scrollAmount if action == "Up" else scrollAmount))
	elif (command == "Flip" and action != "Flip"):
		rightClick(410)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/scaleRotateFlip.png")
		y1 += (8 + (optionH / 2.0) if action == "Horizontal" else 8 + (optionH * 1.5))
		auto.moveTo(x1 / 2 + w / 4, y1 / 2)
		auto.click()
	elif (command == "Rotate" and action != "Rotate"):
		rightClick(410)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/scaleRotateFlip.png")
		y1 += (8 + (optionH * 2.5) if action == "Clockwise" else 8 + (optionH * 3.5))
		auto.moveTo(x1 / 2 + w / 4, y1 / 2)
		auto.click()
	elif (command == "Zoom"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			(oldLocationX, oldLocationY) = auto.position()
			rightClick(112)
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
		status["active_panel"][1] += (1 if (action == "Left" and status["active_panel"][1] > 1) else -1)
		status["active_panel"][0] += (1 if (action == "Up" and status["active_panel"][0] > 1) else -1)
		auto.click()
	elif (command == "Pan"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			(oldLocationX, oldLocationY) = auto.position()
			rightClick(148)
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
				rightClick(184)
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
			afterHover = ImageGrab.grab(bbox=(borderDash, topBarHeight + borderDash, nativeW - borderDash, nativeH - borderDash))
			afterHover.save(os.path.join("Images", "window_afterHover.png"))
			auto.moveTo((219.0 / 1440.0) * width, (77.0 / 900.0) * height)
			auto.click()
			time.sleep(5)
			afterHover = ImageGrab.grab(bbox=(borderDash, topBarHeight + borderDash, nativeW - borderDash, nativeH - borderDash))
			seriesThumbnail.save(os.path.join("Images", "window_seriesThumbnail.png"))
			(x1, y1, x2, y2) = get_bbox("Images/window_afterHover.png", "Images/window_seriesThumbnail.png")
			x1 += (20.0 / 1440.0) * width
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
			close.save(os.path.join("Images", "window_seriesThumbnailClose_Gray.png"))
			status["window_open"] = (not status["window_open"])
		elif (action == "Close" and status["window_open"]):
			close = auto.locateOnScreen("Images/window_seriesThumbnailClose.png")
			if (close is None):
				close = auto.locateOnScreen("Images/window_seriesThumbnailClose_Red.png")
			if (close is None):
				close = auto.locateOnScreen("Images/window_seriesThumbnailClose_Gray.png")
			(x1, y1, w, h) = close
			x2 = x1 + w
			y2 = y1 + h
			auto.moveTo((x1 + x2) / 4, (y1 + y2) / 4)
			auto.click()
			status["window_open"] = (not status["window_open"])
	elif (command == "Manual Contrast"):
		(isValid, action) = ((True, action) if command != action else defaultAction(commandID, [0, 1]))
		if (isValid):
			rightClick(76)
			auto.click()
			moveToActivePanel()
			auto.mouseDown()
			if (status["params"] != ""):
				level = (int(status["params"]) if action == "Increase" else -1 * int(status["params"]))
			else:
				level = (20 if action == "Increase" else -20)
			auto.moveTo(moveToX, moveToY + level)
			auto.mouseUp()
	elif (command == "Layout" and action != "Layout"):
		noDash = ImageGrab.grab(bbox=(borderDash, topBarHeight + borderDash, nativeW - borderDash, nativeH - borderDash))
		noDash.save(os.path.join("Images", "layout_noDash.png"))
		(oldLocationX, oldLocationY) = auto.position()
		auto.moveTo(oldLocationX, 0)
		time.sleep(1)
		afterHover = ImageGrab.grab(bbox=(borderDash, topBarHeight + borderDash, nativeW - borderDash, nativeH - borderDash))
		afterHover.save(os.path.join("Images", "layout_afterHover.png"))
		auto.moveTo(428, 77)
		auto.click()
		seriesThumbnail = ImageGrab.grab(bbox=(borderDash, topBarHeight + borderDash, nativeW - borderDash, nativeH - borderDash))
		seriesThumbnail.save(os.path.join("Images", "layout_seriesThumbnail.png"))
		(x1, y1, x2, y2) = get_bbox("Images/layout_afterHover.png", "Images/layout_seriesThumbnail.png")
		status["panel_dim"][0] = 1
		if (action == "One-Panel"):
			auto.moveTo((x1 + 20) / 2 + 45, y1 / 2 + 200)
			status["panel_dim"][1] = 1
		elif (action == "Two-Panels"):
			auto.moveTo((x1 + 20) / 2 + 107, y1 / 2 + 200)
			status["panel_dim"][1] = 2
		elif (action == "Three-Panels"):
			auto.moveTo((x1 + 20) / 2 + 169, y1 / 2 + 200)
			status["panel_dim"][1] = 3
		elif (action == "Four-Panels"):
			auto.moveTo((x1 + 20) / 2 + 231, y1 / 2 + 200)
			status["panel_dim"][1] = 4
		auto.click()
		resetPanelMoves()
		auto.moveTo(status["firstW"], status["firstH"])
		auto.click()
	elif (command == "Contrast Presets" and action != "Contrast Presets"):
		rightClick(374)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/presets.png")
		y1 += 8 + (optionH / 2.0)
		if (action == "I"):
			y1 += optionH
		elif (action == "II"):
			y1 += optionH * 2
		auto.moveTo(x1 / 2 + w / 4, y1 / 2)
		auto.click()
	status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)
	status["params"] = ""
	auto.hotkey(navType, "tab")


# When quitting program, remove anything saved
