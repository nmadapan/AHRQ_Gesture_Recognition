import pyautogui as auto

window_names = auto.getWindows().keys()
auto.FAILSAFE = True
auto.PAUSE = 2

def moveToImage(image):
	newLocationX, newLocationY = auto.center(auto.locateOnScreen(image))
	auto.moveTo(newLocationX, newLocationY)

status = {"prev_action": "", "number_of_panels": 1}

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
	commandID = -1
	actionID = -1
	sequence = raw_input("Gesture Command -> ")
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
	nameType = actionList[commandID][0]
	action = actionList[commandID][actionID]
	if (nameType == "Admin"):
		if (action == "Quit"):
			break
		elif (action == "Get Status"):
			get_status()
	elif (nameType == "Scroll"):
		scrollAmount = 10
		if (action == "Up"):
			auto.scroll(scrollAmount)
		elif (action == "Down"):
			auto.scroll(-1 * scrollAmount)
		else:
			auto.click()
	elif (nameType == "Flip" or nameType == "Rotate"):
		if (actionID != 0):
			auto.click(button='right')
			moveToImage('Images/scale-rotate-flip.png')
			moveToImage('Images/flip-horizontal.png')
			if (nameType == "Flip" and action == "Vertical"):
				moveToImage('Images/flip-vertical.png')
			elif (nameType == "Rotate" and action == "Clockwise"):
				moveToImage('Images/rotate-clockwise.png')
			elif (nameType == "Zoom" and action == "Counter-Clockwise"):
				moveToImage('Images/rotate-anticlockwise.png')
		auto.click()
	elif (nameType == "Zoom"):
		scrollAmount = 10
		if (actionID == 0):
			oldLocationX, oldLocationY = auto.position()
			auto.click(button='right')
			moveToImage('Images/zoom.png')
			auto.click()
			auto.moveTo(oldLocationX, oldLocationY)
		elif (action == "In"):
			auto.moveDown()
			auto.scroll(scrollAmount)
		elif (action == "Out"):
			auto.moveDown()
			auto.scroll(-1 * scrollAmount)
	elif (nameType == "Switch"):
		auto.click(button='right')
		auto.click()
	elif (nameType == "Pan"):
		oldLocationX, oldLocationY = auto.position()
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
			auto.dragTo(0, -1 * dragAmount, button='left')
	elif (nameType == "Ruler"):
		oldLocationX, oldLocationY = auto.position()
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
			auto.click()
	elif (nameType == "Window"):
		if (actionID == "Open"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "Close"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	elif (nameType == "Manual Contrast"):
		if (actionID == "Increase"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "Decrease"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	elif (nameType == "Layout"):
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
	elif (nameType == "Contrast Presets"):
		if (actionID == "I"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (actionID == "II"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	auto.moveTo(self.width / 2, self.height / 2)
	status["prev_action"] = nameType + " " + action


