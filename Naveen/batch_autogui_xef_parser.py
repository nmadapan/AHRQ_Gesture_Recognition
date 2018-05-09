import os, time, re, sys
import pyautogui as auto
from glob import glob
from threading import Thread
from XefParser import Parser

#####################
#
# Description:
# 	This file AUTOMATICALLY BATCH parses .xef files into RGB video, depth video, and skeletal data.
#	You DO NOT need to manually open any .xef file. In fact, close Kinect Studio if it is opened. 
#	Give the full path to the folder containing .xef files, it AUTOMATICALLY opens each .xef file, 
#		do auto clicking and parses the data. 
# 	This file does BATCH PROCESSING.
#
# How to use:
#
#	xef_folder_path: The path to the folder containing more than one XEF files. Change this path accordingly.
#	Thats it. Run this file. 
#
#####################

# Initialization
xef_folder_path = 'E:\\AHRQ\\Study_4_Training_Videos\\S2_L6'
error_log_filename = 'error_log.txt'

# Default settings
base_write_folder = '..\\Data' # Where to write the files
compress_flag = False # Do not compress the RGB and Depth videos
thresh_empty_cycles = 200 # No. of cycles to wait before obtaining the RGB image. Quit after 200 cycles. 
in_format_flag = True # True since the filename is in the correct format

# Get all xef files paths
xef_files_paths = glob(os.path.join(xef_folder_path, '*.xef'))

class XEF(Thread):
	def __init__(self, xef_file_path):
		super(XEF, self).__init__(name = xef_file_path)
		self.xef_file_path = xef_file_path

	def run(self): 
		try:
			os.system(self.xef_file_path)
		except Exception as exp:
			print(exp)
			with open(error_log_filename, 'a') as fp:
				fp.write(self.xef_file_name); fp.write('\n')			

class GUI():
	def __init__(self, xef_file_name):
		auto.FAILSAFE = True
		auto.PAUSE = 2
		self.width, self.height = auto.size()
		self.xef_file_name = os.path.basename(xef_file_name) # convert absolute path to just the filename

		# Add extension if it is not added
		if(self.xef_file_name[-4:] != '.xef'): self.xef_file_name = self.xef_file_name + '.xef'

	def run_gui(self):
		window_names = auto.getWindows().keys()
		rex = re.compile(self.xef_file_name + ' - Microsoft\\xae Kinect Studio', re.IGNORECASE)

		matched_keys = [window_name for window_name in window_names if rex.search(window_name) is not None]
		xef_window_name = matched_keys[0]

		xef_window = auto.getWindow(xef_window_name)
		xef_window.maximize()

		## Connect Kinect Studio
		res = auto.locateCenterOnScreen(os.path.join('.', 'Images', 'connect.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		else:
			print('Kinect Studio already connected')

		## Enable color stream
		res = auto.locateCenterOnScreen(os.path.join('.', 'Images', 'activate.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		else:
			print('Color stream already connected')

		## Play video
		res = auto.locateCenterOnScreen(os.path.join('.', 'Images', 'play.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		else:
			print('Play button not found')
			with open(error_log_filename, 'a') as fp:
				fp.write(self.xef_file_name); fp.write('\n')

		while True:
			## Closing condition
			_res = auto.locateCenterOnScreen(os.path.join('.', 'Images', 'stop_cond.PNG'))
			if _res is None:
				cx, cy = auto.locateCenterOnScreen(os.path.join('.', 'Images', 'close_button.PNG'))
				auto.click(cx, cy)
				auto.moveTo(self.width/2, self.height/2)
				break
			else:
				# print '. ',
				time.sleep( 0.1)

for file_path in xef_files_paths:
	## Initialize XEF Parser
	parser = Parser(os.path.basename(file_path), base_write_folder, compress_flag, thresh_empty_cycles, in_format_flag = in_format_flag)
	parse_thread = Thread(name = 'parse_thread', target = parser.parse)

	# Initialize auto clicking thread
	gui = GUI(os.path.basename(file_path))
	gui_thread = Thread(name = 'clicks_on_gui', target = gui.run_gui)

	# Initialize the function that opens and holds the XEF File
	xef_thread = XEF(file_path)

	# Run the threads in parallel
	parse_thread.start(); 
	time.sleep(1)

	xef_thread.start()
	time.sleep(3)

	gui_thread.start()	

	# Wait for all threads to join
	parse_thread.join()
	xef_thread.join()
	gui_thread.join()

	time.sleep(1)