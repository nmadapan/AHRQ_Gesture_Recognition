import cv2 as cv, numpy as np, os, shutil,sys

file_name='2_1_S2_L6_X_Horizontal_rgb' #without extension

base_path='F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Data\S2_L6'

avi_path=os.path.join(base_path,(file_name+str('.avi')))
annotations_path=os.path.join(base_path,'Annotations',(file_name[:-4]+str('_annot2.txt')))

write_folder = '..\\Test'

if os.path.isdir(write_folder): shutil.rmtree(write_folder)
if not os.path.isdir(write_folder): os.mkdir(write_folder)

with open(annotations_path, 'r') as fid:
	annot = fid.readlines()
	annot = map(int, annot)
	annot = np.reshape(annot, (-1, 2))
	
print avi_path
cap = cv.VideoCapture(avi_path)
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
			write_path = os.path.join(write_folder, os.path.basename(avi_path).split('.')[0]+'_'+str(gest_count)+'.avi')
			rgb_vr = cv.VideoWriter(write_path, rgb_fourcc, 30.0, (1920, 1080), isColor = True)
			print gest_count, 
			gest_flag = True
		elif annot[gest_count, 1] == image_count:
			rgb_vr.write(np.uint8(frame))
			rgb_vr.release()
			gest_flag = False
			gest_count += 1
		
		if gest_flag:
			rgb_vr.write(np.uint8(frame))

print '\nTotal Images: ', image_count
cap.release()