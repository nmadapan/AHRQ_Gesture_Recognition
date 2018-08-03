import numpy as np
import cv2
import os
import time
import pyautogui as auto
"""import pyscreenshot as ImageGrab
from PIL import Image
from PIL import ImageChops"""
from PIL import ImageGrab
from PIL import ImageChops

#window_names = auto.getWindow("Citrix Viewer")

auto.FAILSAFE = True
auto.PAUSE = 2

(width, height) = auto.size()
boundBox = (0, 44, width * 2, (height - 51) * 2)

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

# Get and store the right click, will be used to later find where a rightClick has been made
auto.hotkey("command", "tab")
auto.moveTo(400, 100)
auto.click(clicks=2)
#before = ImageGrab.grab(bbox=(400 * 2, 100 * 2, (400 * 2 + 382), (100 * 2 + 1000)))
#before.save("Images/RightClick/before.png")
auto.click(button='right')
#after = ImageGrab.grab(bbox=(400 * 2, 100 * 2, (400 * 2 + 382), (100 * 2 + 1000)))
#after.save("Images/RightClick/after.png")
rightClick = ImageGrab.grab(bbox=(401 * 2, 101 * 2, (401 * 2 + 382), (101 * 2 + 1000)))
rightClick.save("Images/RightClick/rightClick.png")
auto.hotkey("command", "tab")

"""
def rightClick():
	(width, height) = auto.size()
	before = ImageGrab.grab(bbox=(0, 22 * 2, width * 2, (height - 51) * 2))
	before.save("Images/before.png")
	#auto.moveTo(400, 100)
	auto.click(button='right')
	#after = ImageGrab.grab(bbox=(400 * 2, 100 * 2, 800 + 382, 1200))
	after = ImageGrab.grab(bbox=(0, 22 * 2, width * 2, (height - 51) * 2))
	after.save("Images/after.png")
	(x1, y1, x2, y2) = get_bbox("Images/before.png", "Images/after.png")
	x1 = 800
	y1 = 200
	x2 = 1182
	y2 = 1200
	return (x1, y1, x2, y2)
"""
def rightClick():
	auto.click(button='right')
	(x1, y1, w, h) = auto.locateOnScreen("Images/RightClick/rightClick.png")
	return (x1, y1, x1 + w, y1 + h)

status = {"prev_action": "", "number_of_panels": 1, "window_open": False, "active_panel": [0, 0]}

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

def get_status():
	print "Status\n------"
	print "Previous action: " + status["prev_action"] + "\n"
	print "No. of panels: " + str(status["number_of_panels"]) + "\n"
	#print "Patient information window: " + status["window"] + "\n"

while (True):
	(commandID, actionID) = (-1, -1)
	sequence = raw_input("Gesture Command -> ")
	(commandAction, params) = (sequence, "")
	if (sequence.find(" ") != -1):
		commandAction = sequence[:sequence.find(" ")]
		params = sequence[sequence.find(" ") + 1:]
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
		scrollAmount = 10
		if (params != ""):
			scrollAmount = int(params)
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
			elif ((actionID == 1 or actionID == 2) and params != ""):
				if (params.find("-") != -1):
					auto.moveTo(oldLocationX, oldLocationY - int(params[params.find("-") + 1:]))
				else:
					auto.moveTo(oldLocationX, oldLocationY + int(params))
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
		(x1, y1, x2, y2) = rightClick()
		#moveToY += (0.036 * 3) * boxHeight
		moveToX = (x1 + x2) / 4
		moveToY = (y1 + 148 + 36) / 2
		auto.moveTo(moveToX, moveToY)
		auto.click()
	elif (command == "Window"):
		(oldLocationX, oldLocationY) = auto.position()
		if (action == "Open" and not status["window_open"]):
			beforeHover = ImageGrab.grab(bbox=boundBox)
			beforeHover.save("Images/beforeHover.png");
			auto.moveTo(oldLocationX, 0)
			time.sleep(1)
			afterHover = ImageGrab.grab(bbox=boundBox)
			afterHover.save("Images/afterHover.png");
			auto.moveTo(219, 77)
			auto.click()
			time.sleep(5)
			#(x1, y1, x2, y2) = get_bbox("Images/beforeWindow.png", "Images/afterWindow.png")
			seriesThumbnail = ImageGrab.grab(bbox=boundBox)
			seriesThumbnail.save("Images/seriesThumbnail.png")
			(x1, y1, x2, y2) = get_bbox("Images/afterHover.png", "Images/seriesThumbnail.png")
			# 136, 2, 226, 42
			print "dimensions: " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2)
			close = ImageGrab.grab(bbox=((x2 - 80) / 2, (y1 + 50) / 2, (x2 - 80) / 2 - 59, (y1 + 50) / 2 + 22))
			auto.moveTo((x2 - 80) / 2, (y1 + 50) / 2)
			close.save("Images/seriesThumbnailClose.png")
		elif (action == "Close" and status["window_open"]):
			#moveToImage('Images/seriesThumbnailClose.png')
			(x1, y1, w, h) = auto.locateOnScreen("Images/seriesThumbnailClose.png")
			auto.moveTo(x1 + w / 2, y1 + h / 2)
			auto.click()
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
			auto.scroll(int(params))
		elif (action == "Decrease"):
			auto.scroll(-1 * int(params))
		else:
			auto.scroll(20)
		auto.mouseUp()
	elif (command == "Layout"):
		if (actionID == "One-Panel"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "Two-Panels"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
		elif (actionID == "Three-Panels"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
		elif (actionID == "Four-Panels"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	elif (command == "Contrast Presets"):
		if (actionID == "I"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "II"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	status["prev_action"] = command + " " + action
	auto.hotkey("command", "tab")


# When quitting program, remove anything saved
if os.path.exists("Images/series-thumbnail-close.png"):
	os.remove("Images/series-thumbnail-close.png")






