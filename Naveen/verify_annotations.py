import cv2 as cv, numpy as np, os, shutil,sys

#####################
#
# Description:
#	base_path: Absolute path of the folder in which the video is present.
#	file_name: Name of the video WITH EXTENSION
#	annotations_path: The text file that has annotations, i.e. the start and end frames of each gesture instance.
#	write_folder: Absolute path of the directory where you want to write the gesture instances. 
#
# How to use:
#	Change base_path, file_name, annotations_path, and write_folder
#	Thats it. Run the script.
#####################

## Initialization
# base_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data'
base_path = 'F:\\AHRQ\\Study_IV\\AHRQ_Gesture_Recognition\\Data\\L6'
file_name ='3_1_S2_L6_Rotate_CW_rgb.avi' # WITH EXTENSION
annotations_path = os.path.join(base_path, 'Annotations', (file_name.split('.')[0][:-4]+str('_annot2.txt')) )
write_folder = '..\\Test'


# Remove the write_folder if it existed
if os.path.isdir(write_folder): shutil.rmtree(write_folder)
# Create the write_folder
if not os.path.isdir(write_folder): os.mkdir(write_folder)

avi_path = os.path.join(base_path, file_name) # Full path to the video file

with open(annotations_path, 'r') as fid:
	annot = fid.readlines()
	annot = map(int, annot)
	annot = np.reshape(annot, (-1, 2))
	
print 'Splitting:', os.path.basename(avi_path)
cap = cv.VideoCapture(avi_path)
image_count = 0
gest_count = 0
gest_flag = False
rgb_fourcc = cv.VideoWriter_fourcc(*'XVID')

print 'Writing Gesture: ', 

while True and gest_count < annot.shape[0]:
	if cap.isOpened():
		ret, frame = cap.read()
		if(frame is None): break
		# cv.imshow('Frame', cv.resize(frame, None, fx = 0.5, fy = 0.5))
		if annot[gest_count, 0] == image_count:
			write_path = os.path.join(write_folder, os.path.basename(avi_path).split('.')[0]+'_'+str(gest_count)+'.avi')
			rgb_vr = cv.VideoWriter(write_path, rgb_fourcc, 30.0, (1920, 1080), isColor = True)
			print gest_count, 
			gest_flag = True
		elif annot[gest_count, 1] == image_count:
			rgb_vr.write(np.uint8(frame))
			rgb_vr.release()
			gest_flag = False
			gest_count += 1
		image_count += 1
		
		if gest_flag:
			rgb_vr.write(np.uint8(frame))

print '\nTotal Images: ', image_count
cap.release()