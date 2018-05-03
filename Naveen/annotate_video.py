import cv2
import numpy as np
import os, sys, time

#####################
#
# Description:
# 	This file displays the RGB video. You are expected to annotate (by left clicking) both the start and 
#		the end point of each gesture instance. 
#	It automatically saves the start and end frame numbers into a text file.
#
# How to use:
#
#	video_file_path: It contains the absolute path of the .avi file. Change this path. 
#	desired_fps: At what fps do you want to wach the video at
#	Thats it. Run this file. 
#
#####################

# Initialization
video_file_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\S2_L6\\4_1_S2_L6_Zoom_In_rgb.avi'
desired_fps = 8

# Initialize the file pointers
write_file = os.path.basename(video_file_path)[:-8] + '_annot.txt'
write_foler_path = os.path.join(os.path.dirname(video_file_path), 'Annotations')
if not os.path.isdir(write_foler_path): os.mkdir(write_foler_path)
write_file_path = os.path.join(write_foler_path, write_file)

if not os.path.isfile(video_file_path): 
	print 'Video file does not exists'; 
	sys.exit()

class Annotate(object):
	def __init__(self):
		# Flags
		self.image_counter = 0
		# Video stream
		self.stream = cv2.VideoCapture(video_file_path)
		# File Pointers
		self.annot_file_id = open(write_file_path, 'w')

	def mouse_callback(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONUP:
			print self.image_counter, 
			self.annot_file_id.write(str(self.image_counter)+'\n')

	def annotate_and_save(self):
		spin = True
		cv2.namedWindow('RGB_Video')
		cv2.setMouseCallback('RGB_Video', self.mouse_callback)
		start_time = time.time()
		try:
			while self.stream.isOpened() and spin:
				ret, frame = self.stream.read()
				if not ret: break
				self.image_counter += 1
				cv2.imshow('RGB_Video', cv2.resize(frame, None, fx=0.5, fy=0.5))
				# Breaking condition
				delay_millis = int(1000/desired_fps)
				if cv2.waitKey(delay_millis) == ord('q'): spin = False
		except Exception as exp:
			print exp
		print 'Total No. of frames: ', self.image_counter
		print 'Time taken: ', time.time() - start_time

		## Closing annotation file streams
		self.annot_file_id.flush()
		self.annot_file_id.close()
		self.stream.release()
		cv2.destroyAllWindows()

__main__ = "Annotate Files"
annot_obj = Annotate ()
annot_obj.annotate_and_save()