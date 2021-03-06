import cv2, os, sys, time
import numpy as np
from KinectReader import kinect_reader

#####################
#
# Description:
# 	This file parses kinect stream (either in the form of real Kinect V2 or Kinect Studio - .XEF) 
#		file into RGB video, depth video, and skeletal data.
# 	This code expects to have a kinect stream in the background. 
#	You need to manually connect the Kinect or open .xef file and then, call this code
# 	Note: This file does not batch process more than one xef file at once. 
# 	Note: Run another script that loops over this class for batch processing. 
#
# How to use:
#
#	from XefParser import Parser
#	parser = Parser(filename, path_to_folder_to_write, True/False, thresh_empty_cycles, in_format_flag)
#		# filename can be with or without extension. It works both with filenames and absolute paths.
#		# filename format: GroupID_ModifierID_SubjectID_LexiconID_GroupName_ModifierName.xef
#	 	# True if you want to compress the videos, False otherwise.
#		# thresh_empty_cycles: No. of empty cycles to wait for the arrival of first RGB frame, quit otherwise 
#		# in_format_flag: True if the filename is in the right format, False otherwise. 
#	parser.parse()
#		# It creates path_to_folder_to_write\\SubjectID_LexiconID folder and creates five files if in_format_flag is True
#		# It creates path_to_folder_to_write folder and creates five files if in_format_flag is False
#			# 1. filename_rgb.avi #(RGB video)
#			# 2. filename_depth.avi #(Depth video)
#			# 3. filename_skel.txt #(x, y, z of 25 joints concatenated into one row. No. of rows = No. of frames)
#			# 4. filename_color.txt #(x, y pixel coordinates of RGB image of 25 joints concatenated into one row)
#			# 5. filename_depth.txt #(x, y pixel coordinates of Depth image of 25 joints concatenated into one row)
#
#	For example:
#	 	parser = Parser('2_1_S2_L6_X_Horizontal', base_write_folder = '..\\Data', compress_flag = False, \
#					thresh_empty_cycles = 200, in_format_flag = True)
#		parser.parse()
#
#####################

class Parser(object):
	def __init__(self, xef_file_name, base_write_folder = '..\\Data', compress_flag = False, \
				thresh_empty_cycles = 200, dynamic_thresh_fac = 2, in_format_flag = True, types_str = ['r', 'd', 'b']):

		self.xef_file_name = os.path.basename(xef_file_name)
		self.base_write_folder = base_write_folder
		self.compress_flag = compress_flag # Compresses the rgb and depth videos if True
		self.thresh_empty_cycles = thresh_empty_cycles # No. of empty cycles to wait for the arrival of first RGB frame, quit otherwise
		self.dynamic_thresh_fac = dynamic_thresh_fac
		self.types_str = types_str

		# Remove the file extension if existed
		if(self.xef_file_name[-4:] == '.xef'): self.xef_file_name = self.xef_file_name[:-4]

		# Make and write directories if absent
		if(in_format_flag):
			self.write_folder = os.path.join(self.base_write_folder, '_'.join(self.xef_file_name.split('_')[3:4]))
		else:
			self.write_folder = self.base_write_folder
		if not os.path.isdir(self.base_write_folder): os.mkdir(self.base_write_folder)
		if not os.path.isdir(self.write_folder): os.mkdir(self.write_folder)

		# Flags
		self.image_counter = 0

		# File Pointers
		self.skel_pts_file_id = open(os.path.join(self.write_folder, self.xef_file_name+'_skel.txt'), 'w')
		self.skel_timestamp_file_id = open(os.path.join(self.write_folder, self.xef_file_name+'_skelts.txt'), 'w')
		self.color_pts_file_id = open(os.path.join(self.write_folder, self.xef_file_name+'_color.txt'), 'w')
		self.depth_pts_file_id = open(os.path.join(self.write_folder, self.xef_file_name+'_depth.txt'), 'w')
		self.rgb_vid_addr = os.path.join(os.path.join(self.write_folder, self.xef_file_name+'_rgb.avi'))
		self.rgb_timestamp_file_id = open(os.path.join(self.write_folder, self.xef_file_name+'_rgbts.txt'), 'w')
		self.depth_vid_addr = os.path.join(os.path.join(self.write_folder, self.xef_file_name+'_depth.avi'))

		# Initialize Kinect
		self.kr = kinect_reader()
		types = 0
		self.rec_color, self.rec_depth, self.rec_body = False, False, False
		if('r' in self.types_str): 
			types = types | self.kr.color_type
			self.rec_color = True
		if('d' in self.types_str): 
			types = types | self.kr.depth_type
			self.rec_depth = True
		if('b' in self.types_str): 
			types = types | self.kr.body_type
			self.rec_body = True
		self.types = types

		# Video Recorder
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		self.rgb_vr = cv2.VideoWriter(self.rgb_vid_addr, fourcc, 30.0, (self.kr.color_width, self.kr.color_height), isColor = True)
		self.depth_vr = cv2.VideoWriter(self.depth_vid_addr, fourcc, 30.0, (self.kr.depth_width, self.kr.depth_height), isColor = False)

	def parse(self):
		# Flags
		spin = True
		first_rgb, first_depth, first_body = False, False, False

		init_start_time = time.time()
		print 'Connecting to Kinect . ', 

		cv2.namedWindow('RGB_Video')
		# Wait for all modules (rgb, depth, skeleton) to connect
		while True:
			try:
				# Refreshing Frames
				if self.rec_color:
					if first_rgb: self.kr.update_rgb()
					else: first_rgb = self.kr.update_rgb()

				if self.rec_depth:
					if first_depth: self.kr.update_depth()
					else: first_depth = self.kr.update_depth()

				if self.rec_body:
					if first_body: self.kr.update_body()
					else: first_body = self.kr.update_body()

				if ((self.rec_color == first_rgb) and (self.rec_depth==first_depth) and (self.rec_body==first_body)): break

				time.sleep(0.5)
				print '. ', 		
			except Exception as exp:
				time.sleep(0.5)
				print '. ', 
			if(time.time()-init_start_time > 30): 
				print('Waited for more than 30 seconds. Exiting')
				return (-1, -1, -1)
		
		print '\nAll modules connected !!'
		print 'Parsing XEF ', 

		# Initialize flags to stop accordingly
		quit_count = 0 # Count no. of empty cycles (iterations with no RGB frame) between two RGB frames
		max_quit_count = 0 # Stores maximum no. of empty cycles between subsequent RGB frames
		dynamic_thresh = self.thresh_empty_cycles # No. of empty cycles to wait before qutting
		# dynamic_thresh_fac = 4 # dynamic_thresh changes with time based on this number
		
		video_time = 0.0
		empty_iter = 0
		loop_delay = 0.001

		try:
			start_time = time.time()
			while spin:
				# Refreshing Frames
				if self.rec_color: rgb_flag = self.kr.update_rgb()
				if self.rec_depth: depth_flag = self.kr.update_depth()
				if self.rec_body: body_flag = self.kr.update_body()
				if (self.rec_color and rgb_flag):
					max_quit_count = max(max_quit_count, quit_count)
					# Update dynamic threshold if you witness larger delays in RGB frame arrivals
					dynamic_thresh = max(dynamic_thresh, self.dynamic_thresh_fac * max_quit_count) 
					quit_count = 0
					cv2.imshow('RGB_Video', cv2.resize(self.kr.color_image, None, fx=0.5, fy=0.5))
					self.image_counter += 1
					if self.image_counter%25 == 0: print '. ', 
				else: quit_count += 1

				if quit_count > dynamic_thresh: spin = False

				## Saving RGB and Depth videos
				if rgb_flag:
					video_time += (time.time() - start_time - (empty_iter+1)*loop_delay)
					start_time = time.time()
					empty_iter = 0
					self.rgb_vr.write(self.kr.color_image)
					self.rgb_timestamp_file_id.write('%0.8f'%(self.kr.last_color_frame_access)+'\n')
				else:
					empty_iter += 1
				if depth_flag: self.depth_vr.write(self.kr.depth_image)
				if body_flag:
					self.skel_pts_file_id.write(' '.join(map(str,self.kr.skel_pts.tolist()))+'\n')
					self.skel_timestamp_file_id.write('%0.8f'%(self.kr.last_body_frame_access)+'\n')
					self.color_pts_file_id.write(' '.join(map(str,self.kr.color_skel_pts.tolist()))+'\n')
					self.depth_pts_file_id.write(' '.join(map(str,self.kr.depth_skel_pts.tolist()))+'\n')

				# Breaking condition
				if cv2.waitKey(1) == ord('q') : spin = False
				time.sleep(loop_delay)

		except Exception as exp:
			print exp
		
		print '\n', 'Total No. of frames: ', self.image_counter
		print 'Video time: ', video_time, 'seconds'
		fps = int(self.image_counter / video_time)
		print 'FPS: ', fps

		## Closing Kinect, RGB, Depth, and annotation file streams
		self.kr.sensor.close()
		self.skel_pts_file_id.flush()
		self.skel_pts_file_id.close()
		self.color_pts_file_id.flush()
		self.color_pts_file_id.close()
		self.depth_pts_file_id.flush()
		self.depth_pts_file_id.close()
		self.rgb_vr.release()
		self.depth_vr.release()	
		self.rgb_timestamp_file_id.flush()
		self.rgb_timestamp_file_id.close()
		self.skel_timestamp_file_id.flush()
		self.skel_timestamp_file_id.close()

		if self.compress_flag: self.compress_videos()
		return (self.image_counter, video_time, fps)

	def compress_videos(self):
		from moviepy.editor import VideoFileClip
		rgb_clip = VideoFileClip(self.rgb_vid_addr)
		rgb_clip.write_videofile(self.rgb_vid_addr[:-4]+'.webm', audio=False)
		os.remove(self.rgb_vid_addr)

		depth_clip = VideoFileClip(self.depth_vid_addr)
		depth_clip.write_videofile(self.depth_vid_addr[:-4]+'.webm', audio=False)
		os.remove(self.depth_vid_addr)

__main__ = "Annotate Files"
parser = Parser('1_1_x_x_x_x')
parser.parse()

