import os, time, re, sys
import pyautogui as auto
from glob import glob
from threading import Thread
from XefParser import Parser
from datetime import datetime
from helpers import *

#####################
#
# Description:
# 	This file AUTOMATICALLY BATCH parses .xef files into RGB video, depth video, and skeletal data.
#	You DO NOT need to manually open any .xef file. 
#	Give the full path to the folder containing .xef files, it AUTOMATICALLY opens each .xef file, 
#		do auto clicking and parses the data. 
# 	This file does BATCH PROCESSING.
#
# How to use:
#
#	xef_folder_path: The path to the folder containing more than one XEF files. Change this path accordingly.
#	error_log_filename: This script writes the status to this file. It will make it easy to back track.
#	Thats it. Run this file. 
#
#####################

# Initialization
xef_folder_paths = [r'E:\AHRQ\Study_IV\XEF_Files\*']
in_format_flag = True # True since the filename is in the correct format
enable_repeat = False # If True, all xef files will be executed, Otherwise, only the files that werent read previously or the files that were incompletely read
xef_rgb_factor = 3.2 # Max is 3.8
print_fnames = False
images_folder = '.\\Images_Rahul'

error_log_folder = r'E:\AHRQ\Study_IV\XEF_Files\Logfiles'
error_log_filename = os.path.join(error_log_folder, 'error_log_'+datetime.now().strftime("%Y_%m_%d_%H_%M")+'.txt')

# Default settings
base_write_folder = r'E:\AHRQ\Study_IV\XEF_Files\Data' # Where to write the files
kinect_studio_open_time = 3 # in seconds
thresh_empty_cycles = 200 # No. of cycles to wait before obtaining the first RGB image. Quit after 200 cycles. 
dynamic_thresh_fac = 10 # How long to wait later for the arrival of RGB frame 

## Flags
global parse_flag, xef_flag, gui_flag, file_active
xef_flag = False
gui_flag = False
parse_flag = False
file_active = False

# # Check consistencies in the xef folder path
if(in_format_flag):
	print 'Checking consistencies: ', 
	for xef_folder_path in xef_folder_paths:
		flag, error_strs = check_consis(xef_folder_path)
		if(not flag): raise IOError(error_strs)
	print 'All Good.'

## Get all xef files paths
xef_files_paths = []
for xef_folder_path in xef_folder_paths:
	xef_files_paths+=glob(os.path.join(xef_folder_path, '*.xef'))

# Remove the repititions
if(not enable_repeat):
	xef_files_paths = file_filter(xef_files_paths, base_write_folder, in_format_flag, xef_rgb_factor)

xef_rex = re.compile('xef - Microsoft\\xae Kinect Studio', re.IGNORECASE)

print 'Processing: ', len(xef_files_paths), ' files.'
if(print_fnames):
	print xef_files_paths
	sys.exit(0)

class XEF(Thread):
	def __init__(self, xef_file_path):
		super(XEF, self).__init__(name = xef_file_path)
		self.xef_file_path = xef_file_path

	def run(self): 
		global parse_flag, xef_flag, gui_flag, file_active
		xef_flag = True
		try:
			os.system(self.xef_file_path)
			xef_flag = False
		except Exception as exp:
			print(exp)
			while(file_active): continue
			file_active = True
			with open(error_log_filename, 'a') as fp:
				fp.write(' [Error in os.system] ' + '\n')
			file_active = False

class GUI():
	def __init__(self, xef_file_name):
		auto.FAILSAFE = True # Drag the mouse to top left to stop autogui
		auto.PAUSE = 2 # Pause for 2 seconds after every autogui operation
		self.width, self.height = auto.size()
		self.xef_file_name = os.path.basename(xef_file_name) # convert absolute path to just the filename

		# Add extension if it is not added
		if(self.xef_file_name[-4:] != '.xef'): self.xef_file_name = self.xef_file_name + '.xef'

	def run_gui(self):
		global parse_flag, xef_flag, gui_flag, file_active
		rex = re.compile(self.xef_file_name + ' - Microsoft\\xae Kinect Studio', re.IGNORECASE)

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

		## Wait until Kinect studio is fully open
		while(True):
			res = auto.locateCenterOnScreen(os.path.join(images_folder, 'start_cond.PNG'))
			if(res != None): break
			else: time.sleep(0.2)

		gui_flag = True

		## Connect Kinect Studio
		res = auto.locateCenterOnScreen(os.path.join(images_folder, 'connect.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		# else:
		# 	print('Kinect Studio already connected')

		## Enable color stream
		res = auto.locateCenterOnScreen(os.path.join(images_folder, 'activate.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		# else:
		# 	print('Color stream already connected')
		time.sleep(2)

		## Play video
		res = auto.locateCenterOnScreen(os.path.join(images_folder, 'play.PNG'))
		if res is not None:
			cx, cy = res
			auto.click(cx, cy)
			auto.moveTo(self.width/2, self.height/2)
		else:
			print('Play button not found')
			while(file_active): continue
			file_active = True
			with open(error_log_filename, 'a') as fp:
				fp.write(' [No play button] ')
			file_active = False

		xef_window.close()
		while not parse_flag: continue
		gui_flag = False

def parse(parser):
	global parse_flag, xef_flag, gui_flag, file_active
	parse_flag = True
	num_images, video_time, fps = parser.parse()

	while(file_active): continue
	file_active = True
	with open(error_log_filename, 'a') as fp: 
		fp.write(' [num_images: {}, video_time: {}, FPS: {}]\n'.format(num_images, video_time, fps))
	file_active = False
	parse_flag = False

# Write the date and time to the file:
with open(error_log_filename, 'w') as fp:
	fp.write(str(datetime.now()) + '\n\n')

for file_path in xef_files_paths:
	# Logging it to a file
	while(file_active): continue
	file_active = True
	with open(error_log_filename, 'a') as fp: fp.write(os.path.basename(file_path) + ' : ')
	file_active = False

	# Close kinect studio if they are open
	matched_keys = [window_name for window_name in auto.getWindows().keys() if xef_rex.search(window_name) is not None]
	if(len(matched_keys) != 0): os.system('taskkill /f /im kstudio.exe') # Works only on windows
	time.sleep(kinect_studio_open_time)

	# Initialize the function that opens and holds the XEF File
	xef_thread = XEF(file_path)

	# Open the XEF File. This line is non blocking call. 
	xef_thread.start()
	time.sleep(kinect_studio_open_time)

	## Initialize XEF Parser
	parser = Parser(os.path.basename(file_path), base_write_folder, compress_flag = False, thresh_empty_cycles=thresh_empty_cycles,\
					 dynamic_thresh_fac = dynamic_thresh_fac, in_format_flag = in_format_flag)
	parse_thread = Thread(name = 'parse_thread', target = parse, args = (parser, ))

	# Initialize auto clicking thread
	gui = GUI(os.path.basename(file_path))
	gui_thread = Thread(name = 'clicks_on_gui', target = gui.run_gui)

	# Run the threads in parallel
	parse_thread.start(); 
	time.sleep(1)

	gui_thread.start()	

	while(parse_thread.isAlive()): continue
	os.system('taskkill /f /im kstudio.exe') # Works only on windows

	# Wait for all threads to join
	parse_thread.join()
	xef_thread.join()
	gui_thread.join()

	time.sleep(1)