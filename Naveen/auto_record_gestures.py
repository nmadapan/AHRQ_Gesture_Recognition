import os, time, re, sys
import pyautogui as auto
from glob import glob
from threading import Thread
from XefParser import Parser
from datetime import datetime
from helpers import *
from KinectReader import kinect_reader

#####################
#
# Description:
#
# How to use:
#
#####################

# Initialization

# Default settings
base_write_folder = '..\\Data' # Where to write the files
images_folder = os.path.join('.', 'Images_AHRQPC')
kinect_studio_open_time = 3 # 'in seconds
fixed_num_gestures = 20

## Flags
global record_active, gest_count, xef_flag, gui_flag, gc_flag 
xef_flag = False
gui_flag = False
gc_flag = False
gest_count = 0
record_active = True

xef_rex = re.compile('Microsoft\\xae Kinect Studio', re.IGNORECASE)

class XEF(Thread):
	def __init__(self):
		super(XEF, self).__init__(name = 'xef')
		self.kstudio_path = 'kstudio'

	def run(self): 
		global record_active, gest_count, xef_flag, gui_flag, gc_flag 
		xef_flag = True
		try:
			os.system(self.kstudio_path)
			xef_flag = False
		except Exception as exp:
			print(exp)

class GUI():
	def __init__(self):
		auto.FAILSAFE = True # Drag the mouse to top left to stop autogui
		auto.PAUSE = 2 # Pause for 2 seconds after every autogui operation
		self.width, self.height = auto.size()

	def run_gui(self):
		global record_active, gest_count, xef_flag, gui_flag, gc_flag 
		rex = re.compile('Microsoft\\xae Kinect Studio', re.IGNORECASE)

		## Waiting for Kinect Studio to open
		while(True):
			window_names = auto.getWindows().keys()
			matched_keys = [window_name for window_name in window_names if rex.search(window_name) is not None]
			if(len(matched_keys) != 0): 
				xef_window_name = matched_keys[0]
				break
			time.sleep(0.2)

		xef_window = auto.getWindow(xef_window_name)
		xef_window.maximize()

		## Go to RECORD window
		while(True):
			res = auto.locateCenterOnScreen(os.path.join(images_folder, 'record.PNG'))
			res_act = auto.locateCenterOnScreen(os.path.join(images_folder, 'record_activated.PNG'))
			if(res is None or res_act is None): 
				time.sleep(0.2)
				# print 'record.PNG not found'
			if res is not None:
				cx, cy = res
				auto.click(cx, cy)
				auto.moveTo(self.width/2, self.height/2)
				break
			if res_act is not None:
				cx, cy = res_act
				auto.click(cx, cy)
				auto.moveTo(self.width/2, self.height/2)			
				break

		## Connect Kinect Studio
		res = auto.locateCenterOnScreen(os.path.join(images_folder, 'record_connect.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		else:
			print 'record_connect.PNG is not found'
			sys.exit(0)

		gui_flag = True
		while(not xef_flag): time.sleep(0.1)
		while(not gc_flag): time.sleep(0.1)

		## Record
		res = auto.locateCenterOnScreen(os.path.join(images_folder, 'record_record.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		else:
			print 'record_record.PNG not found'

		xef_window.close()

		# XEF stopping condition
		while(True):
			if(gest_count > fixed_num_gestures):
				xef_window.maximize()
				res = auto.locateCenterOnScreen(os.path.join(images_folder, 'record_stop.PNG'))
				if res is not None:
					cx, cy = res
					auto.click(cx, cy)
					record_active = False
					auto.moveTo(self.width/2, self.height/2)
					break
				# else:
				# 	print 'record_stop.PNG not found'
			time.sleep(0.1)

		xef_window.maximize()
		# XEF shutting condition
		while(True):
			res = auto.locateCenterOnScreen(os.path.join(images_folder, 'buffer.PNG'))
			if res is not None:
				time.sleep(0.1)
				continue
			else:
				# Close kinect studio if they are open
				matched_keys = [window_name for window_name in auto.getWindows().keys() if xef_rex.search(window_name) is not None]
				if(len(matched_keys) != 0): 
					os.system('taskkill /f /im kstudio.exe') # Works only on windows
					break

		gui_flag = False

## Global parameters
torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2
base_id = torso_id

def get_gest_count(kr):
	global record_active, gest_count, xef_flag, gui_flag, gc_flag 
	start_flag = False
	frame_count = 0
	while(not gui_flag): time.sleep(0.1)
	
	wait_for_kinect(kr)
	gc_flag = True

	while(record_active):
		try:
			body_flag = kr.update_body()
			if(body_flag):
				skel_pts = kr.skel_pts.tolist()
				start_y_coo = thresh_level * (skel_pts[3*neck_id+1] - skel_pts[3*base_id+1])
				left_y = skel_pts[3*left_hand_id+1] - skel_pts[3*base_id+1]
				right_y = skel_pts[3*right_hand_id+1] - skel_pts[3*base_id+1]
				if (left_y >= start_y_coo or right_y >= start_y_coo) and (not start_flag): 
					start_flag = True
					frame_count = 0
				if (left_y < start_y_coo and right_y < start_y_coo) and start_flag: 
					start_flag = False
				if(start_flag):
					frame_count += 1
			if(frame_count!=0 and (not start_flag) ):
				frame_count = 0
				gest_count += 1
				print gest_count
				start_flag = False
			time.sleep(0.1)
		except Exception as exp:
			print exp

# Initialize Kinect
kr = kinect_reader()

# Close kinect studio if they are open
matched_keys = [window_name for window_name in auto.getWindows().keys() if xef_rex.search(window_name) is not None]
if(len(matched_keys) != 0): os.system('taskkill /f /im kstudio.exe') # Works only on windows
time.sleep(kinect_studio_open_time)

# Initialize the function that opens and holds the XEF File
xef_thread = XEF()

# Open the XEF File. This line is non blocking call. 
xef_thread.start()
time.sleep(kinect_studio_open_time)

# Initialize auto clicking thread
gui = GUI()
gui_thread = Thread(name = 'clicks_on_gui', target = gui.run_gui)

gui_thread.start()	

gc_thread = Thread(name = 'gest_count', target = get_gest_count, args = (kr, ))
gc_thread.start()

# Wait for all threads to join
# parse_thread.join()
xef_thread.join()
gui_thread.join()

time.sleep(1)