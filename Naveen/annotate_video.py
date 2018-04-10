import cv2, numpy as np, os, sys, time
import glob

vid_file_name = 'Naveen_L6_OpenPalm_Close_rgb.avi' # Add the extension
base_data_folder = os.path.join('..', 'Data')
desired_fps = 30

video_path = glob.glob(os.path.join(base_data_folder,'*', vid_file_name))

write_file = vid_file_name[:-8] + '_annot.txt'
write_path = glob.glob(os.path.join(base_data_folder, '_'.join(vid_file_name.split('_')[:2])))[0]
write_path = os.path.join(write_path, write_file)

if len(video_path) != 1: 
	print 'More than one or no vidoes with the filename'; 
	sys.exit()
else:
	video_path = video_path[0]

class Annotate(object):
	def __init__(self):
		# Flags
		self.image_counter = 0
		# Video stream
		self.stream = cv2.VideoCapture(video_path)
		# File Pointers
		self.annot_file_id = open(write_path, 'w')

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