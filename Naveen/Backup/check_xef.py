import cv2, numpy as np, os, sys, time
from KinectReader import KinectReader

## XEF Format: PersonID_LexiconID_Context_Modifier ## Replace Context/Modifier by None if NA

## Output file formats
	# Folder : PersonID_LexiconID

#Sample_L6_OpenPalm_Close
#Naveen_L6_OpenPalm_Close

xef_file_name = 'Naveen_L6_OpenPalm_Close' # Don't add the extension
compress_flag = False

write_folder = os.path.join('..', 'Data', '_'.join(xef_file_name.split('_')[:2]))

if not os.path.isdir('..\Data'): os.mkdir('..\Data')
if not os.path.isdir(write_folder): os.mkdir(write_folder)

class Annotate(object):
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

	def annotate_and_save(self):
		quit_count = 0
		recv_flag = False
		spin = True
		# cv2.namedWindow('RGB_Video')
		while True:
			try:
				# Refreshing Frames
				self.kr.update_rgb()
				self.kr.update_depth()
				self.kr.update_body(display_skel=False)
				# self.kr.update_skeleton()
				print '\n All modules connected !!'
				break
			except Exception as exp:
				print exp
				time.sleep(0.1)
				print '. ', 
		try:
			while spin:
				start = time.time()
				# Refreshing Frames
				rgb_flag = self.kr.update_body()
				# print 'Time in per cycle: ', time.time()-start

				if rgb_flag:
					quit_count = 0
					recv_flag = True
					# cv2.imshow('RGB_Video', cv2.resize(self.kr.color_image, None, fx=0.5, fy=0.5))
					self.image_counter += 1
					# print rgb_flag
				else: 
					quit_count += 1

				# print quit_count

				if recv_flag and quit_count > 1000000: spin = False
				## Saving RGB and Depth videos
				# if rgb_flag: self.rgb_vr.write(self.kr.color_image)

				# Breaking condition
				if cv2.waitKey(1) == ord('q') :
					spin = False

		except Exception as exp:
			print exp
		print '\n', 'Total No. of frames: ', self.image_counter

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
annot_obj = Annotate ()
annot_obj.annotate_and_save()

