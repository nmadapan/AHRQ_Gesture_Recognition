import numpy as np
import cv2
import os
import time
import pyautogui as auto
from PIL import ImageGrab
from PIL import ImageChops

#window_names = auto.getWindow("Citrix Viewer")

auto.FAILSAFE = True
auto.PAUSE = 0.75

(width, height) = auto.size()
boundBox = (0, 44, width * 2, (height - 51) * 2)
boundBoxNoTopBar = (0, 272, width * 2, (height - 51) * 2)
boundBoxNoDash = (20, 66, width * 2 - 20, (height - 51) * 2 - 22)
boundBoxNoTopBarDash = (20, 272, width * 2 - 10, (height - 51) * 2 - 12)

status = {"prev_action": "", "panel_dim": [1, 1], "window_open": False, "active_panel": [1, 1], "params": ""}

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

rightOptionHeight = 36

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

auto.hotkey("command", "tab")

# Get and store the right click
auto.moveTo(400, 100)
beforeRight = ImageGrab.grab(bbox=boundBoxNoDash)
beforeRight.save("Images/RightClick/beforeRight.png")
auto.click(button='right')
afterRight = ImageGrab.grab(bbox=boundBoxNoDash)
afterRight.save("Images/RightClick/afterRight.png")
rightBox = get_bbox("Images/RightClick/beforeRight.png", "Images/RightClick/afterRight.png")
rightBoxW = rightBox[2] - rightBox[0] + 1
rightBoxH = rightBox[3] - rightBox[1] + 1
rightClick = ImageGrab.grab(bbox=(401 * 2, 101 * 2, 401 * 2 + rightBoxW, 101 * 2 + rightBoxH))
rightClick.save("Images/RightClick/rightClick.png")

# Get and store image presets
auto.moveTo((401 * 2 + rightBoxW / 2) / 2, (101 * 2 + 374) / 2)
time.sleep(1)
auto.moveTo(400, 100)
afterPresets = ImageGrab.grab(bbox=boundBoxNoDash)
afterPresets.save("Images/RightClick/afterPresets.png")
box = get_bbox("Images/RightClick/afterRight.png", "Images/RightClick/afterPresets.png")
boxW = box[2] - box[0] + 1
boxH = box[3] - box[1] + 1
boxH = 8 * 2 + 36 * 21
presets = ImageGrab.grab(bbox=((401 + 180 + 25) * 2, (101 + 187 - 9) * 2, (401 + 180) * 2 + boxW, (101 + 187 - 9) * 2 + boxH))
presets.save("Images/RightClick/presets.png")

# Get and store scale-rotate-flip
auto.moveTo((401 * 2 + rightBoxW / 2) / 2, (101 * 2 + 410) / 2)
time.sleep(1)
auto.moveTo(400, 100)
afterSRF = ImageGrab.grab(bbox=boundBoxNoDash)
afterSRF.save("Images/RightClick/afterSRF.png")
box = get_bbox("Images/RightClick/afterRight.png", "Images/RightClick/afterSRF.png")
boxW = box[2] - box[0] + 1
boxH = box[3] - box[1] + 1
boxH = 8 * 2 + 36 * 7
scaleRotateFlip = ImageGrab.grab(bbox=((401 + 180 + 25) * 2, (101 + 205 - 9) * 2, (401 + 180) * 2 + boxW, (101 + 205 - 9) * 2 + boxH))
scaleRotateFlip.save("Images/RightClick/scaleRotateFlip.png")

os.remove("Images/RightClick/beforeRight.png")
os.remove("Images/RightClick/afterRight.png")
os.remove("Images/RightClick/afterPresets.png")
os.remove("Images/RightClick/afterSRF.png")

auto.click()
auto.hotkey("command", "tab")

def rightClick():
	auto.click(button='right')
	(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/rightClick.png")
	return (x1, y1, x1 + w, y1 + h)

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
	auto.hotkey("command", "tab")
	if (command == "Admin"):
		if (action == "Quit"):
			break
		elif (action == "Get Status"):
			get_status()
	elif (command == "Scroll"):
		scrollAmount = (10 if status["params"] == "" else int(status["params"]))
		if (action == "Up"):
			auto.scroll(-1 * scrollAmount)
		elif (action == "Down"):
			auto.scroll(scrollAmount)
		else:
			auto.click()
	elif (command == "Flip" or command == "Rotate"):
		if (actionID != 0):
			(x1, y1, x2, y2) = rightClick()
			auto.moveTo(((x1 + x2) / 4, (y1 + 410) / 2))
			time.sleep(1)
			(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/scaleRotateFlip.png")
			y1 += 8 + 18
			if (command == "Flip" and action == "Vertical"):
				y1 += 36
			elif (command == "Rotate" and action == "Clockwise"):
				y1 += 36 * 2
			elif (command == "Rotate" and action == "Counter-Clockwise"):
				y1 += 36 * 3
			auto.moveTo(x1 / 2 + w / 4, y1 / 2)
		auto.click()
	elif (command == "Zoom"):
		(oldLocationX, oldLocationY) = auto.position()
		(x1, y1, x2, y2) = rightClick()
		auto.moveTo((x1 + x2) / 4, (y1 + 112) / 2)
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		auto.mouseDown()
		try:
			if (action == "Zoom"):
				auto.hotkey("command", "tab")
				invalidFormat = True
				while (invalidFormat):
					rawInput = raw_input("Enter Zoom Level <In/Out> <level> -> ")
					if (rawInput.find(" ") != -1):
						direction = rawInput[:rawInput.find(" ")]
						level = int(rawInput[rawInput.find(" ") + 1:])
						invalidFormat = False
						auto.hotkey("command", "tab")
					else:
						print "The zoom parameters you entered are incorrectly formatted: <In/Out> <level>\n"
			else:
				if (status["params"] != ""):
					level = (-1 * int(status["params"]) if action == "In" else int(status["params"]))
				else:
					level = (-20 if action == "In" else 20)
			auto.moveTo(oldLocationX, oldLocationY + level)
		except ValueError:
			print "Unrecognized parameter for zooming!\n"
			continue
		auto.mouseUp()
	elif (command == "Switch Panel"):
		firstW = (float(boundBox[2] - boundBox[0]) / (float(status["panel_dim"][1]) * 4.0))
		firstH = (float(height) / (float(status["panel_dim"][0]) * 2.0))
		jumpW = (firstW * 2.0 if status["panel_dim"][1] != 1 else 0)
		jumpH = (firstH * 2.0 if status["panel_dim"][0] != 1 else 0)
		if (action == "Left" and status["active_panel"][1] > 1):
			status["active_panel"][1] -= 1
		elif (action == "Right" and status["active_panel"][1] < status["panel_dim"][1]):
			status["active_panel"][1] += 1
		elif (action == "Up" and status["active_panel"][0] > 1):
			status["active_panel"][0] -= 1
		elif (action == "Down" and status["active_panel"][0] < status["panel_dim"][0]):
			status["active_panel"][0] += 1
		moveToX = firstW + (jumpW * (status["active_panel"][1] - 1))
		moveToY = firstH + (jumpH * (status["active_panel"][0] - 1))
		auto.moveTo(moveToX, moveToY)
		auto.click()
	elif (command == "Pan"):
		(oldLocationX, oldLocationY) = auto.position()
		(x1, y1, x2, y2) = rightClick()
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 148) / 2
		auto.moveTo(moveToX, moveToY)
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		panAmount = 20
		(dragToX, dragToY) = (oldLocationX, oldLocationY)
		try:
			if (action == "Pan"):
				auto.hotkey("command", "tab")
				invalidFormat = True
				while (invalidFormat):
					rawInput = raw_input("Enter for Pan: <direction> <level> -> ")
					if (rawInput.find(" ") != -1):
						direction = rawInput[:rawInput.find(" ")]
						level = str(rawInput[rawInput.find(" ") + 1:])
						invalidFormat = False
						auto.hotkey("command", "tab")
					else:
						print "The pan parameters you entered are incorrectly formatted: <direction> <level>\n"
			else:
				if (status["params"] != ""):
					level = (int(status["params"]) if action == "Increase" else -1 * int(status["params"]))
				else:
					level = (20 if action == "Increase" else -20)
			auto.moveTo(moveToX, moveToY + level)
		except ValueError:
			print "Unrecognized parameter for zooming!\n"
			continue
		(width, height) = auto.size()
		auto.dragTo(width / 2, height / 2, button="left")
	elif (command == "Ruler"):
		if (action == "Ruler" or action == "Measure"):
			(x1, y1, x2, y2) = rightClick()
			moveToX = (x1 + x2) / 4
			moveToY = (y1 + 184) / 2
			auto.moveTo(moveToX, moveToY)
			auto.click()
		if (action == "Measure"):
			points = status["params"].split("_")
			try:
				if (len(points) == 4):
					(x1, y1, x2, y2) = (int(points[0]), int(points[1]), int(points[2]), int(points[3]))
				elif (len(points) == 2):
					(x1, y1) = auto.position()
					(x2, y2) = (int(points[0]), int(points[1]))
				else:
					print "There aren't enough parameters to create a ruler!"
					continue
			except ValueError:
				print "Parameters should only include non-negative integers separated by underscores."
				continue
			auto.moveTo(x1, y1)
			auto.mouseDown()
			auto.moveTo(x2, y2)
			auto.mouseUp()
		elif (action == "Delete"):
			(x, y) = auto.position()
			auto.click(button="right")
			auto.moveTo(x + 79, y + 85)
			auto.click()
			#rulerBox = ImageGrab.grab(x * 2 + 1, y * 2 + 1, (x * 2 + 1 + 304), (y * 2 + 1 + 278))
	elif (command == "Window"):
		(oldLocationX, oldLocationY) = auto.position()
		if (action == "Open" and not status["window_open"]):
			auto.moveTo(oldLocationX, 0)
			time.sleep(1)
			afterHover = ImageGrab.grab(bbox=boundBoxNoTopBarDash)
			afterHover.save("Images/window_afterHover.png")
			auto.moveTo(219, 77)
			auto.click()
			time.sleep(5)
			seriesThumbnail = ImageGrab.grab(bbox=boundBoxNoTopBarDash)
			seriesThumbnail.save("Images/window_seriesThumbnail.png")
			(x1, y1, x2, y2) = get_bbox("Images/window_afterHover.png", "Images/window_seriesThumbnail.png")
			x1 += 20
			y1 += 272
			diff = ImageGrab.grab(bbox=(x1, y1, x2, y2))
			diff.save("Images/window_diff.png")
			close = ImageGrab.grab(bbox=((x2 - 83), (y1 + 2), (x2 - 83) + 90, (y1 + 2) + 40))
			close.save("Images/window_seriesThumbnailClose.png")
			auto.moveTo((2 * (x2 - 83) + 90) / 4, (2 * (y1 + 2) + 40) / 4)
			close = ImageGrab.grab(bbox=((x2 - 83), (y1 + 2), (x2 - 83) + 90, (y1 + 2) + 40))
			close.save("Images/window_seriesThumbnailClose_Red.png")
			auto.moveTo(x2 + 1, (2 * (y1 + 2) + 40) / 4)
			auto.click()
			close = ImageGrab.grab(bbox=((x2 - 83), (y1 + 2), (x2 - 83) + 90, (y1 + 2) + 40))
			close.save("Images/window_seriesThumbnailClose_Gray.png")
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
		(x1, y1, x2, y2) = rightClick()
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 76) / 2
		auto.moveTo(moveToX, moveToY)
		auto.click()
		firstW = (float(boundBox[2] - boundBox[0]) / (float(status["panel_dim"][1]) * 4.0))
		firstH = (float(height) / (float(status["panel_dim"][0]) * 2.0))
		jumpW = (firstW * 2.0 if status["panel_dim"][1] != 1 else 0)
		jumpH = (firstH * 2.0 if status["panel_dim"][0] != 1 else 0)
		moveToX = firstW + (jumpW * (status["active_panel"][1] - 1))
		moveToY = firstH + (jumpH * (status["active_panel"][0] - 1))
		auto.moveTo(moveToX, moveToY)
		auto.mouseDown()
		try:
			if (action == "Manual Contrast"):
				auto.hotkey("command", "tab")
				contrastLevel = raw_input("Enter Contrast Level (negative value to decrease) -> ")
				auto.hotkey("command", "tab")
				if (contrastLevel.find("-") != -1):
					level = -1 * int(contrastLevel[contrastLevel.find("-") + 1:])
				else:
					level = int(contrastLevel)
			else:
				if (status["params"] != ""):
					level = (int(status["params"]) if action == "Increase" else -1 * int(status["params"]))
				else:
					level = (20 if action == "Increase" else -20)
			auto.moveTo(moveToX, moveToY + level)
		except ValueError:
			print "Unrecognized parameter for zooming!\n"
			continue
		auto.mouseUp()
		auto.moveTo(moveToX, moveToY)
	elif (command == "Layout"):
		noDash = ImageGrab.grab(bbox=boundBoxNoTopBarDash)
		noDash.save("Images/layout_noDash.png")
		(oldLocationX, oldLocationY) = auto.position()
		auto.moveTo(oldLocationX, 0)
		time.sleep(1)
		afterHover = ImageGrab.grab(bbox=boundBoxNoTopBarDash)
		afterHover.save("Images/layout_afterHover.png")
		auto.moveTo(428, 77)
		auto.click()
		seriesThumbnail = ImageGrab.grab(bbox=boundBoxNoTopBarDash)
		seriesThumbnail.save("Images/layout_seriesThumbnail.png")
		(x1, y1, x2, y2) = get_bbox("Images/layout_afterHover.png", "Images/layout_seriesThumbnail.png")
		x1 += 20
		y1 += 272
		if (action == "One-Panel"):
			auto.moveTo(x1 / 2 + 45, y1 / 2 + 64)
			status["panel_dim"][0] = 1
			status["panel_dim"][1] = 1
		elif (action == "Two-Panels"):
			auto.moveTo(x1 / 2 + 107, y1 / 2 + 64)
			status["panel_dim"][0] = 1
			status["panel_dim"][1] = 2
		elif (action == "Three-Panels"):
			auto.moveTo(x1 / 2 + 169, y1 / 2 + 64)
			status["panel_dim"][0] = 1
			status["panel_dim"][1] = 3
		elif (action == "Four-Panels"):
			auto.moveTo(x1 / 2 + 231, y1 / 2 + 64)
			status["panel_dim"][0] = 1
			status["panel_dim"][1] = 4
		auto.click()
	elif (command == "Contrast Presets"):
		(x1, y1, x2, y2) = rightClick()
		auto.moveTo((x1 + x2) / 4, (y1 + 374) / 2)
		time.sleep(1)
		(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/presets.png")
		y1 += 8 + 18
		if (action == "I"):
			y1 += 36
		elif (action == "II"):
			y1 += 36 * 2
		auto.moveTo(x1 / 2 + w / 4, y1 / 2)
		auto.click()
	status["prev_action"] = str(commandID) + "_" + str(actionID) + ", " + str(command) + " " + str(action)
	status["params"] = ""
	auto.hotkey("command", "tab")


# When quitting program, remove anything saved
if os.path.exists("Images/series-thumbnail-close.png"):
	os.remove("Images/series-thumbnail-close.png")























