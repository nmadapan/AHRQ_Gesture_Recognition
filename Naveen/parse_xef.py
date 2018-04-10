import cv2, os, sys, time
import numpy as np
from KinectReader import KinectReader

## XEF Format: PersonID_LexiconID_Context_Modifier

## Output file formats
	# Folder : PersonID_LexiconID

## Initalization
xef_file_name = 'S2_L6_blu_blue' # Don't add the extension
base_data_folder = os.path.join('..', 'Data')
compress_flag = False

write_folder = os.path.join(base_data_folder, '_'.join(xef_file_name.split('_')[:2]))

if not os.path.isdir(base_data_folder): os.mkdir(base_data_folder)
if not os.path.isdir(write_folder): os.mkdir(write_folder)

class XEF_Parser(object):
	def __init__(self):
		# Flags
		self.image_counter = 0

		# File Pointers
		self.skel_pts_file_id = open(os.path.join(write_folder, xef_file_name+'_skel.txt'),'w')
		self.color_pts_file_id = open(os.path.join(write_folder, xef_file_name+'_color.txt'),'w')
		self.depth_pts_file_id = open(os.path.join(write_folder, xef_file_name+'_depth.txt'),'w')
		self.rgb_vid_addr = os.path.join(os.path.join(write_folder, xef_file_name+'_rgb.avi'))
		self.depth_vid_addr = os.path.join(os.path.join(write_folder, xef_file_name+'_depth.avi'))

		# Initialize Kinect
		self.kr = KinectReader()

		# Video Recorder
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		self.rgb_vr = cv2.VideoWriter(self.rgb_vid_addr, fourcc, 30.0, (self.kr.color_width, self.kr.color_height), isColor = True)
		self.depth_vr = cv2.VideoWriter(self.depth_vid_addr, fourcc, 30.0, (self.kr.depth_width, self.kr.depth_height), isColor = False)

	def parse(self):
		# Flags
		spin = True
		first_rgb, first_depth, first_body = False, False, False
		quit_count = 0
		max_quit_count = 0

		# cv2.namedWindow('RGB_Video')
		while True:
			try:
				# Refreshing Frames
				if first_rgb: self.kr.update_rgb()
				else: first_rgb = self.kr.update_rgb()

				if first_depth: self.kr.update_depth()
				else: first_depth = self.kr.update_depth()

				if first_body: self.kr.update_body()
				else: first_body = self.kr.update_body()

				if not (first_rgb and first_depth and first_body): raise Exception('Some modalities are missing ...')
				else: break

				time.sleep(0.1)
				print '. ', 		
			except Exception as exp:
				time.sleep(0.1)
				print '. ', 
		
		print '\n All modules connected !!\n'
		print 'Reading and Saving ', 
		dynamic_thresh = 200
		dynamic_thresh_fac = 2
		try:
			start_time = time.time()
			while spin:
				# Refreshing Frames
				rgb_flag = self.kr.update_rgb()
				depth_flag = self.kr.update_depth()
				body_flag = self.kr.update_body()
				if rgb_flag:
					max_quit_count = max(max_quit_count, quit_count)
					dynamic_thresh = max(dynamic_thresh, dynamic_thresh_fac * max_quit_count) 
					quit_count = 0
					# cv2.imshow('RGB_Video', cv2.resize(self.kr.color_image, None, fx=0.5, fy=0.5))
					self.image_counter += 1
					if self.image_counter%25 == 0: print '. ', 
				else: quit_count += 1

				if quit_count > dynamic_thresh: spin = False

				## Saving RGB and Depth videos
				if rgb_flag: self.rgb_vr.write(self.kr.color_image)
				if depth_flag: self.depth_vr.write(self.kr.depth_image)
				if body_flag:
					self.skel_pts_file_id.write(' '.join(map(str,self.kr.skel_pts.tolist()))+'\n')
					self.color_pts_file_id.write(' '.join(map(str,self.kr.color_skel_pts.tolist()))+'\n')
					self.depth_pts_file_id.write(' '.join(map(str,self.kr.depth_skel_pts.tolist()))+'\n')

				# Breaking condition
				# if cv2.waitKey(1) == ord('q') : spin = False
				time.sleep(0.01)

		except Exception as exp:
			print exp
		
		print '\n', 'Total No. of frames: ', self.image_counter
		print 'Video time: ', time.time() - start_time
		print 'FPS: ', int(self.image_counter / (time.time() - start_time))

		## Closing Kinect, RGB, Depth, and annotation file streams
		self.kr.sensor.close()
		self.color_pts_file_id.flush()
		self.color_pts_file_id.close()
		self.depth_pts_file_id.flush()
		self.depth_pts_file_id.close()
		self.rgb_vr.release()
		self.depth_vr.release()	
		if compress_flag: self.compress_videos()

	def compress_videos(self):
		from moviepy.editor import VideoFileClip
		rgb_clip = VideoFileClip(self.rgb_vid_addr)
		rgb_clip.write_videofile(self.rgb_vid_addr[:-4]+'.webm', audio=False)
		os.remove(self.rgb_vid_addr)

		depth_clip = VideoFileClip(self.depth_vid_addr)
		depth_clip.write_videofile(self.depth_vid_addr[:-4]+'.webm', audio=False)
		os.remove(self.depth_vid_addr)

__main__ = "Annotate Files"
parser = XEF_Parser ()
parser.parse()

