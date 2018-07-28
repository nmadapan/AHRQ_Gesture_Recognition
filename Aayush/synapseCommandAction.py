import pyautogui as auto

window_names = auto.getWindows().keys()

def moveToImage(image):
	newLocationX, newLocationY = auto.center(auto.locateOnScreen(image))
	auto.moveTo(newLocationX, newLocationY)

status = {prev_action: "", number_of_panels: ""}

def get_status():
	print "Status\n------"
	print "Previous action: " + status[prev_action] + "\n"
	print "No. of panels: " + status[number_of_panels] + "\n"

commandSeq = ""
while (True):
	commandType = "-1"
	commandID = "-1"
	commandSeq = raw_input("Gesture Command -> ")
	command = commandSeq[:commandSeq.find(" ")]
	params = commandSeq[commandSeq.find(" ") + 1:]
	if (command == "0_0"):
		break
	elif (command.find("_") != -1):
		commandType = command[:command.find("_")]
		commandID = command[command.find("_") + 1:]
	else:
		print "Unrecognized command!\n"
		continue
	if (commandType == "1"):
		scrollAmount = 10
		if (commandID == "1"):
			auto.scroll(scrollAmount)
		elif (commandID == "2"):
			auto.scroll(-1 * scrollAmount)
		else:
			auto.click()
	elif (commandType == "2" or commandType == "3"):
		if (commandType != "0"):
			auto.click(button='right')
			moveToImage('Images/scale-rotate-flip.png')
			moveToImage('Images/flip-horizontal.png')
			if (commandType == "2" and commandID == "2"):
				moveToImage('Images/flip-vertical.png')
			elif (commandType == "3" and commandID == "3"):
				moveToImage('Images/rotate-clockwise.png')
			elif (commandType == "3" and commandID == "4"):
				moveToImage('Images/rotate-anticlockwise.png')
		auto.click()
	elif (commandType == "4"):
		scrollAmount = 10
		if (commandID == "0"):
			oldLocationX, oldLocationY = auto.position()
			auto.click(button='right')
			moveToImage('Images/zoom.png')
			auto.click()
			auto.moveTo(oldLocationX, oldLocationY)
		elif (commandID == "1"):
			auto.moveDown()
			auto.scroll(scrollAmount)
		elif (commandID == "2"):
			auto.moveDown()
			auto.scroll(-1 * scrollAmount)
	elif (commandType == "5"):
		auto.click(button='right')
		auto.click()
	elif (commandType == "6"):
		oldLocationX, oldLocationY = auto.position()
		auto.click(button='right')
		moveToImage('Images/pan.png')
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		dragAmount = 100
		if (commandID == "1"):
			auto.dragTo(dragAmount, 0, button='left')
		elif (commandID == "2"):
			auto.dragTo(-1 * dragAmount, 0, button='left')
		elif (commandID == "3"):
			auto.dragTo(0, dragAmount, button='left')
		elif (commandID == "4"):
			auto.dragTo(0, -1 * dragAmount, button='left')
	elif (commandType == "7"):
		oldLocationX, oldLocationY = auto.position()
		auto.click(button='right')
		moveToImage('Images/ruler.png')
		auto.click()
		auto.moveTo(oldLocationX, oldLocationY)
		newLocationX, newLocationY = oldLocationX, oldLocationY
		if (commandID == "1"):
			auto.dragTo(newLocationX, newLocationY, button='left')
		elif (commandID == "2"):
			auto.click(button='right')
			moveToImage('Images/ruler-delete.png')
			auto.click()
	elif (commandType == "8"):
		if (commandID == "1"):
			moveToImage('Images/series-thumbnail.png')
			auto.click()
		elif (commandID == "2"):
			moveToImage('Images/series-thumbnail-close.png')
			auto.click()
	elif (commandID == "21" or commandID == "22"):
		# manual contrast increase/decrease
		auto.click(button='right')
		auto.click()
	elif (commandID == "23" or commandID == "24" or commandID == "25" or commandID == "26"):
		# layout with x panels
		auto.click(button='right')
		auto.click()
	elif (commandID == "27" or commandID == "28"):
		# contrast presets std 1/2
		auto.click(button='right')
		auto.click()