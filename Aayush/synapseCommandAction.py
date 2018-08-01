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

def rightClick():
	(oldLocationX, oldLocationY) = auto.position()
	#(width, height) = auto.size()
	#auto.moveTo(width / 2.0, height / 2.0)
	auto.moveTo(400, 100)
	
	"""beforeRight = ImageGrab.grab(bbox=(316 * 2, 35 * 2, 1124 * 2, 811 * 2))
	beforeRight.save("Images/beforeRight.png")
	auto.click(button='right')
	afterRight = ImageGrab.grab(bbox=(316 * 2, 35 * 2, 1124 * 2, 811 * 2))
	afterRight.save("Images/afterRight.png")
	(x1, y1, x2, y2) = ImageChops.difference(beforeRight, afterRight).getbbox()
	print "dimensions: " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2)
	x1 += 316 * 2
	y1 += 35 * 2
	x2 += 316 * 2
	y2 += 35 * 2
	print "beforeAfterRight box: " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2)
	diff = ImageGrab.grab(bbox=(int(x1), int(y1), int(x2), int(y2)))
	diff.save("Images/diff_beforeAfterRight.png")
	#return (x1, y1, x2, y2, (x1 + x2) / 2.0, y1 + (0.076 * boxHeight), y2 - y1, afterRight)"""
	return (x1, y1, x2, y2, afterRight)
	"""
		moveToX = (x1 + x2) / 2.0
		moveToY = y1 + (0.076 * boxHeight)
		boxHeight = y2 - y1
		if (command == "Zoom"):
			moveToY += 0.036 * boxHeight
		elif (command == "Pan"):
			moveToY += (0.036 * 2) * boxHeight
		elif (command == "Ruler"):
			moveToY += (0.036 * 3) * boxHeight
		elif (command == "Flip" or command == "Rotate"):
			moveToY += ((0.036 * 9) + 0.010) * boxHeight
			auto.moveTo(moveToX, moveToY)
			time.sleep(0.5)
			scaleRotateFlip = ImageGrab.grab(bbox=None)
			(x1, y1, x2, y2) = ImageChops.difference(afterRight, scaleRotateFlip).getbbox()
			moveToX = (x1 + x2) / 2.0
			moveToY = y1 + ((25 / 268) * boxHeight)
			boxHeight = y2 - y1
			if (command == "Flip" and action == "Vertical"):
				moveToY += (36 / 268) * boxHeight
			elif (command == "Rotate" and action == "Clockwise"):
				moveToY += (36 * 2 / 268) * boxHeight
			elif (command == "Rotate" and action == "Counter-Clockwise"):
				moveToY += (36 * 3 / 268) * boxHeight
			auto.moveTo(moveToX, moveToY)
		auto.click()
	"""

"""
def moveToImage(image):
	newLocationX, newLocationY = auto.center(auto.locateOnScreen(image))
	auto.moveTo(newLocationX, newLocationY)
"""

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
	print "No. of panels: " + status["number_of_panels"] + "\n"
	print "Patient information window: " + status["window"] + "\n"

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
			(x1, y1, x2, y2, afterRight) = rightClick()
			#moveToY += ((0.036 * 9) + 0.010) * boxHeight
			moveToX = (x1 + x2) / 2
			moveToY = y1 + 410
			auto.moveTo(moveToX, moveToY)
			time.sleep(0.5)
			scaleRotateFlip = ImageGrab.grab(bbox=(316 * 2, 35 * 2, 1124 * 2, 811 * 2))
			scaleRotateFlip.save("Images/scaleRotateFlip.png")
			im = ImageChops.difference(afterRight, scaleRotateFlip)
			if (im is None or im.getbbox() is None):
				print "moveToX: " + str(moveToX)
				print "moveToY: " + str(moveToY)
			else:
				(x1, y1, x2, y2) = im.getbbox()
				x1 += 316 * 2
				y1 += 35 * 2
				x2 += 316 * 2
				y2 += 35 * 2
				#moveToY = y1 + ((25 / 268) * boxHeight)
				moveToY = y1 + 25
				boxHeight = y2 - y1
				if (command == "Flip" and action == "Vertical"):
					#moveToY += (36 / 268) * boxHeight
					moveToY += 36
				elif (command == "Rotate" and action == "Clockwise"):
					#moveToY += (36 * 2 / 268) * boxHeight
					moveToY += 36 * 2
				elif (command == "Rotate" and action == "Counter-Clockwise"):
					#moveToY += (36 * 3 / 268) * boxHeight
					moveToY += 36 * 3
				auto.moveTo(moveToX, moveToY)
			"""
				if (command == "Flip" and action == "Horizontal"):
					rightClick("Scale_rotate_flip", command, action)
				elif (command == "Flip" and action == "Vertical"):
					rightClick("Scale_rotate_flip", command, action)
					#moveToImage('Images/flip-vertical.png')
				elif (command == "Rotate" and action == "Clockwise"):
					rightClick("Scale_rotate_flip", command, action)
					#moveToImage('Images/rotate-clockwise.png')
				elif (command == "Zoom" and action == "Counter-Clockwise"):
					rightClick("Scale_rotate_flip", command, action)
					#moveToImage('Images/rotate-anticlockwise.png')
			"""
		auto.click()
	elif (command == "Zoom"):
		(oldLocationX, oldLocationY) = auto.position()
		(x1, y1, x2, y2, afterRight) = rightClick()
		#moveToY += 0.036 * boxHeight
		moveToY = y1 + 36
		auto.moveTo(moveToX, moveToY)
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		auto.mouseDown()
		if (actionID == 0):
			auto.scroll(10)
			"""
				oldLocationX, oldLocationY = auto.position()
				auto.click(button='right')
				moveToImage('Images/zoom.png')
				auto.click()
				auto.moveTo(oldLocationX, oldLocationY)
			"""
		else:
			if (params.find("-") != -1):
				auto.scroll(-1 * int(params[params.find("-") + 1:]))
			else:
				auto.scroll(int(params))
		"""
			elif (action == "In"):
				auto.moveDown()
				auto.scroll(scrollAmount)
			elif (action == "Out"):
				auto.moveDown()
				auto.scroll(-1 * scrollAmount)
		"""
		auto.mouseUp()
	elif (command == "Switch"):
		auto.click(button='right')
		auto.click()
	elif (command == "Pan"):
		(x1, y1, x2, y2, afterRight) = rightClick()
		#moveToY += (0.036 * 2) * boxHeight
		moveToY = y1 + (36 * 2)
		auto.moveTo(moveToX, moveToY)
		auto.click()
		"""oldLocationX, oldLocationY = auto.position()
		auto.click(button='right')
		moveToImage('Images/pan.png')
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		dragAmount = 100
		if (action == "Left"):
			auto.dragTo(dragAmount, 0, button='left')
		elif (action == "Right"):
			auto.dragTo(-1 * dragAmount, 0, button='left')
		elif (action == "Up"):
			auto.dragTo(0, dragAmount, button='left')
		elif (action == "Down"):
			auto.dragTo(0, -1 * dragAmount, button='left')"""
	elif (command == "Ruler"):
		(x1, y1, x2, y2, afterRight) = rightClick()
		#moveToY += (0.036 * 3) * boxHeight
		moveToY = y1 + (36 * 3)
		auto.moveTo(moveToX, moveToY)
		auto.click()
		"""oldLocationX, oldLocationY = auto.position()
		auto.click(button='right')
		moveToImage('Images/ruler.png')
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		newLocationX, newLocationY = oldLocationX, oldLocationY
		if (actionID == "Measure"):
			auto.dragTo(newLocationX, newLocationY, button='left')
		elif (actionID == "Delete"):
			auto.click(button='right')
			moveToImage('Images/ruler-delete.png')
			auto.click()"""
	elif (command == "Window"):
		(oldLocationX, oldLocationY) = auto.position()
		if (actionID == "Open" and not status["window_open"]):
			beforeOpen = ImageGrab.grab(bbox=None)
			auto.moveTo(oldLocationX, 0)
			time.sleep(0.5)
			#auto.moveTo((435 / 573) * (x2 - x1), (150 / 228) * (y2 - y1))
			auto.moveTo(435, 150)
			auto.click()
			time.sleep(5)
			afterOpen = ImageGrab.grab(bbox=None)
			(x1, y1, x2, y2) = ImageChops.difference(beforeOpen, afterOpen).getbbox()
			x1 += 316 * 2
			y1 += 35 * 2
			x2 += 316 * 2
			y2 += 35 * 2
			x2 -= 14
			y1 -= 23
			x1 = x2 - 45
			y2 = y2 + 40
			seriesThumbnail = auto.screenshot(region=(x1, y1, x2, y2))
			seriesThumbnail.save("Images/series-thumbnail-close.png")
		elif (actionID == "Close" and status["window_open"]):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	elif (command == "Manual Contrast"):
		if (actionID == "Increase"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "Decrease"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
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
import os
if os.path.exists("Images/series-thumbnail-close.png"):
	os.remove("Images/series-thumbnail-close.png")






