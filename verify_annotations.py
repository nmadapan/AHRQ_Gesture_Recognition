import cv2 as cv, numpy as np, os

xef_file_name = 'Naveen_L6_OpenPalm_Close' # Don't add the extension
read_folder = os.path.join('.', 'Data', '_'.join(xef_file_name.split('_')[:2]))
write_folder = '.\\Test'

annot_filename = xef_file_name+'_annot.txt'
video_filename = xef_file_name+'_rgb.webm'

with open( os.path.join(read_folder, annot_filename) ) as fid:
	annot = fid.readlines()
	annot = map(int, annot)
	annot = np.reshape(annot, (-1, 2))
	# print annot

cap = cv.VideoCapture( os.path.join(read_folder, video_filename))
image_count = 0
gest_count = 0
gest_flag = False
rgb_fourcc = cv.VideoWriter_fourcc(*'XVID')

print 'Writing Gesture: ', 

while True and gest_count < annot.shape[0]:
	if cap.isOpened():
		ret, frame = cap.read()
		# cv.imshow('Frame', cv.resize(frame, None, fx = 0.5, fy = 0.5))
		image_count += 1
		if annot[gest_count, 0] == image_count:
			write_path = os.path.join(write_folder, video_filename.split('.')[0]+'_'+str(gest_count)+'.avi')
			rgb_vr = cv.VideoWriter(write_path, rgb_fourcc, 30.0, (1920, 1080), isColor = True)
			gest_count += 1
			print gest_count, 
			gest_flag = True
		elif annot[gest_count, 1] == image_count:
			rgb_vr.write(np.uint8(frame))
			rgb_vr.release()
			gest_flag = False
		if gest_flag:
			rgb_vr.write(np.uint8(frame))

		# if cv.waitKey(1) == ord('q'): break

print '\nTotal Images: ', image_count
cap.release()