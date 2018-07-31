import time
import pyautogui as auto
"""import pyscreenshot as ImageGrab
from PIL import Image
from PIL import ImageChops"""
from PIL import ImageGrab
from PIL import ImageChops

window_names = auto.getWindows().keys()

auto.FAILSAFE = True
auto.PAUSE = 2

status = {"prev_action": "", "number_of_panels": 1}

def rightClick():
	#(locationX, locationY) = auto.position()
	#(width, height) = auto.size()
	beforeRight = ImageGrab.grab(bbox=None)
	auto.click(button='right')
	afterRight = ImageGrab.grab(bbox=None)
	(x1, y1, x2, y2) = ImageChops.difference(beforeRight, afterRight).getbbox()
	return (x1, y1, x2, y2, (x1 + x2) / 2.0, y1 + (0.076 * boxHeight), y2 - y1)
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

def get_status():
	print "Status\n------"
	print "Previous action: " + status["prev_action"] + "\n"
	print "No. of panels: " + status["number_of_panels"] + "\n"

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
		except ValueError:
			print "Unrecognized sequence of commands!\n"
			continue
	else:
		print "Invalid command entered!\n"
		continue
	command = actionList[commandID][0]
	action = actionList[commandID][actionID]
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
			(x1, y1, x2, y2, moveToX, moveToY, boxHeight) = rightClick()
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
		(x1, y1, x2, y2, moveToX, moveToY, boxHeight) = rightClick()
		moveToY += 0.036 * boxHeight
		auto.moveTo(moveToX, moveToY)
		auto.click()
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
	elif (command == "Switch"):
		auto.click(button='right')
		auto.click()
	elif (command == "Pan"):
		(x1, y1, x2, y2, moveToX, moveToY, boxHeight) = rightClick()
		moveToY += (0.036 * 2) * boxHeight
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
		(x1, y1, x2, y2, moveToX, moveToY, boxHeight) = rightClick()
		moveToY += (0.036 * 3) * boxHeight
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
		if (actionID == "Open"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "Close"):
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
	auto.moveTo(self.width / 2, self.height / 2)
	status["prev_action"] = command + " " + action










