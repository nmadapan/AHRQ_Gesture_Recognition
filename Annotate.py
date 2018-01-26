import cv2, numpy as np, os, sys, time
from KinectReader import KinectReader

## XEF Format: PersonID_LexiconID_Context_Modifier ## Replace Context/Modifier by None if NA

## Output file formats
	# Folder : PersonID_LexiconID

xef_file_name = 'Naveen_L6_OpenPalm_Close' # Don't add the extension
compress_flag = True

write_folder = os.path.join('.', 'Data', '_'.join(xef_file_name.split('_')[:2]))

if not os.path.isdir('Data'): os.mkdir('Data')
if not os.path.isdir(write_folder): os.mkdir(write_folder)

class Annotate(object):
	def __init__(self):
		# Flags
		self.image_counter = 0

		# File Pointers
		self.annot_file_id = open(os.path.join(write_folder, xef_file_name+'_annot.txt'), 'w')
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

	def mouse_callback(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONUP:
			print self.image_counter, 
			self.annot_file_id.write(str(self.image_counter)+'\n')

	def annotate_and_save(self):
		spin = True
		cv2.namedWindow('RGB_Video')
		cv2.setMouseCallback('RGB_Video', self.mouse_callback)
		while True:
			try:
				# Refreshing Frames
				self.kr.update_rgb()
				self.kr.update_depth()
				self.kr.update_body(display_skel=False)
				self.kr.update_skeleton()
				print '\n All modules connected !!'
				break
			except Exception as exp:
				time.sleep(0.1)
				print '. ', 
		try:
			while spin:
				self.image_counter += 1

				# Refreshing Frames
				self.kr.update_rgb()
				self.kr.update_depth()
				self.kr.update_body(display_skel=False)
				self.kr.update_skeleton()
				cv2.imshow('RGB_Video', cv2.resize(self.kr.color_image, None, fx=0.5, fy=0.5))

				## Saving RGB and Depth videos
				self.rgb_vr.write(self.kr.color_image)
				self.depth_vr.write(self.kr.depth_image)
				self.skel_pts_file_id.write(' '.join(map(str,self.kr.skel_pts.tolist()))+'\n')
				self.color_pts_file_id.write(' '.join(map(str,self.kr.color_skel_pts.tolist()))+'\n')
				self.depth_pts_file_id.write(' '.join(map(str,self.kr.depth_skel_pts.tolist()))+'\n')

				# Breaking condition
				if cv2.waitKey(1) == ord('q') :
					spin = False

		except Exception as exp:
			print exp
		print '\n', 'Total No. of frames: ', self.image_counter

		## Closing Kinect, RGB, Depth, and annotation file streams
		self.kr.sensor.close()
		self.annot_file_id.flush()
		self.annot_file_id.close()
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

