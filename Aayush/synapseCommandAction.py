import numpy as np
import cv2
import os
import time
import pyautogui as auto
from PIL import ImageGrab
from PIL import ImageChops

#window_names = auto.getWindow("Citrix Viewer")

auto.FAILSAFE = True
auto.PAUSE = 2

(width, height) = auto.size()
boundBox = (0, 44, width * 2, (height - 51) * 2)
boundBoxNoTopBar = (0, 272, width * 2, (height - 51) * 2)
boundBoxNoDash = (20, 66, width * 2 - 20, (height - 51) * 2 - 22)
boundBoxNoTopBarDash = (20, 272, width * 2 - 10, (height - 51) * 2 - 12)

status = {"prev_action": "", "panel_dim": 1, "window_open": False, "active_panel": [0, 0], "params": ""}

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

# Get and store the right click, will be used to later find where a rightClick has been made
auto.moveTo(400, 100)
auto.click(button='right')
rightClick = ImageGrab.grab(bbox=(401 * 2, 101 * 2, (401 * 2 + 382), (101 * 2 + 1000)))
rightClick.save("Images/RightClick/rightClick.png")
auto.click()

auto.hotkey("command", "tab")

def rightClick():
	auto.click(button='right')
	(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/rightClick.png")
	return (x1, y1, x1 + w, y1 + h)

def get_status():
	print "Status\n------"
	print "Previous action: " + status["prev_action"] + "\n"
	print "Panel Dimension: " + 'x'.join(status["panel_dim"]) + "\n"
	print "Patient information window: " + ("opened" if status["window_open"] else "closed") + "\n"

while (True):
	(commandID, actionID) = (-1, -1)
	sequence = raw_input("Gesture Command -> ")
	(commandAction, status["params"]) = (sequence, "")
	if (sequence.find(" ") != -1):
		commandAction = sequence[:sequence.find(" ")]
		status["params"] = sequence[sequence.find(" ") + 1:]
	if (commandAction.find("_") != -1):
		try:
			commandID = int(commandAction[:commandAction.find("_")])
			actionID = int(commandAction[commandAction.find("_") + 1:])
			command = actionList[commandID][0]
			action = actionList[commandID][actionID]
			status["prev_action"] = str(commandID) + "_" + str(actionID)
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
		scrollAmount = 10
		if (status["params"] != ""):
			scrollAmount = int(status["params"])
		if (action == "Up"):
			auto.scroll(scrollAmount)
		elif (action == "Down"):
			auto.scroll(-1 * scrollAmount)
		else:
			auto.click()
	elif (command == "Flip" or command == "Rotate"):
		if (actionID != 0):
			(x1, y1, x2, y2) = rightClick()
			#moveToY += ((0.036 * 9) + 0.010) * boxHeight
			moveToX = (x1 + x2) / 4
			moveToY = (y1 + 410) / 2
			auto.moveTo(moveToX, moveToY)
			time.sleep(1)
			moveToX += (382 + 434) / 4
			if (command == "Flip" and action == "Vertical"):
				moveToY += 36 / 2
			elif (command == "Rotate" and action == "Clockwise"):
				moveToY += 36 * 2 / 2
			elif (command == "Rotate" and action == "Counter-Clockwise"):
				moveToY += 36 * 3 / 2
			auto.moveTo(moveToX, moveToY)
		auto.click()
	elif (command == "Zoom"):
		(oldLocationX, oldLocationY) = auto.position()
		(x1, y1, x2, y2) = rightClick()
		#moveToY += 0.036 * boxHeight
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 112) / 2
		auto.moveTo(moveToX, moveToY)
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		auto.mouseDown()
		try:
			if (actionID == 0):
				while (True):
					zoomLevel = raw_input("Enter Zoom Level (negative value to zoom out) -> ")
					if (zoomLevel.find("-") != -1):
						auto.moveTo(oldLocationX, oldLocationY - int(zoomLevel[zoomLevel.find("-") + 1:]))
					else:
						auto.moveTo(oldLocationX, oldLocationY - int(zoomLevel))
				#auto.moveTo(oldLocationX, oldLocationY + 100)
			elif ((actionID == 1 or actionID == 2) and status["params"] != ""):
				if (status["params"].find("-") != -1):
					auto.moveTo(oldLocationX, oldLocationY - int(status["params"][status["params"].find("-") + 1:]))
				else:
					auto.moveTo(oldLocationX, oldLocationY + int(status["params"]))
		except ValueError:
			print "Unrecognized parameter for zooming!\n"
			continue
		auto.mouseUp()
	elif (command == "Switch"):
		#auto.click(button='right')
		auto.click()
	elif (command == "Pan"):
		(oldLocationX, oldLocationY) = auto.position()
		(x1, y1, x2, y2) = rightClick()
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 148) / 2
		auto.moveTo(moveToX, moveToY)
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		(width, height) = auto.size()
		auto.dragTo(width / 2, height / 2, button="left")
	elif (command == "Ruler"):
		if (action == "Ruler" or action == "Measure"):
			(x1, y1, x2, y2) = rightClick()
			#moveToY += (0.036 * 3) * boxHeight
			moveToX = (x1 + x2) / 4
			moveToY = (y1 + 148 + 36) / 2
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
			(x1, y1, w, h)
			x2 = x1 + w
			y2 = y1 + h
			auto.moveTo((x1 + x2) / 4, (y1 + y2) / 4)
			auto.click()
			status["window_open"] = (not status["window_open"])
	elif (command == "Manual Contrast"):
		(oldLocationX, oldLocationY) = auto.position()
		(x1, y1, x2, y2) = rightClick()
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 76) / 2
		auto.moveTo(moveToX, moveToY)
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		auto.mouseDown()
		#if (actionID == 0):
		#	auto.dragTo(oldLocationX, moveToY)
		if (action == "Increase"):
			auto.scroll(int(status["params"]))
		elif (action == "Decrease"):
			auto.scroll(-1 * int(status["params"]))
		else:
			auto.scroll(20)
		auto.mouseUp()
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
			auto.click()
		elif (action == "Two-Panels"):
			auto.moveTo(x1 / 2 + 107, y1 / 2 + 64)
			auto.click()
		elif (action == "Three-Panels"):
			auto.moveTo(x1 / 2 + 169, y1 / 2 + 64)
			auto.click()
		elif (action == "Four-Panels"):
			auto.moveTo(x1 / 2 + 231, y1 / 2 + 64)
			auto.click()
	elif (command == "Contrast Presets"):
		(x1, y1, x2, y2) = rightClick()
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 374) / 2
		before1 = ImageGrab.grab(bbox=(x2, 44, width * 2, moveToY * 2 - 18))
		before1.save("Images/contrast_before1.png")
		before2 = ImageGrab.grab(bbox=(x2, moveToY * 2 + 18, width * 2, (height - 51) * 2))
		before2.save("Images/contrast_before2.png")
		auto.moveTo(moveToX, moveToY)
		time.sleep(1)
		after1 = ImageGrab.grab(bbox=(x2, 44, width * 2, moveToY * 2 - 18))
		after1.save("Images/contrast_after1.png")
		after2 = ImageGrab.grab(bbox=(x2, moveToY * 2 + 18, width * 2, (height - 51) * 2))
		after2.save("Images/contrast_after2.png")
		(x1, y1, x2, y2) = get_bbox("Images/contrast_before1.png", "Images/contrast_after1.png")
		if (y2 - y1 + 1 == (moveToY * 2 - 18) - 44 and x2 - x1 + 1 == width * 2):
			(x1, y1, x2, y2) = get_bbox("Images/contrast_before2.png", "Images/contrast_after2.png")
			moveToY = y1 + 53
		else:
			moveToY -= 18
		diff = ImageGrab.grab(bbox=(x1, moveToY, x2, y2))
		diff.save("Images/contrast_diff.png")
		moveToX = (x1 + x2) / 4
		if (action == "I"):
			moveToY += 24
		elif (action == "II"):
			moveToY += 42
		auto.moveTo(moveToX, moveToY)
		auto.click()
	auto.hotkey("command", "tab")


# When quitting program, remove anything saved
if os.path.exists("Images/series-thumbnail-close.png"):
	os.remove("Images/series-thumbnail-close.png")


