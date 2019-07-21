from PIL import ImageGrab
import numpy as np
import cv2
from os.path import join, basename, dirname
import time

base_folder = 'Backup'
fname = 'output_screen'

fps = 30.0
res = (1920, 1080)
display = False

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter(join(base_folder, fname+'.mov'), fourcc, fps, res)
ts_file = open(join(base_folder, fname+'ts.txt'), 'w')

while(True):
	try:
		img = ImageGrab.grab(bbox=(0,0,res[0],res[1])) # bbox specifies specific region (bbox= x,y,width,height)
		img_np = np.array(img)
		out.write(img_np)
		ts_file.write(str(time.time()) + '\n')
		if display:
			cv2.imshow('frame',cv2.resize(img_np, None, fx = 0.5, fy = 0.5))
			if cv2.waitKey(1) == ord('q'):
				break
	except KeyboardInterrupt:
		print('Ctrl+C encountered! Exiting!!')
		break

ts_file.flush()
ts_file.close()
out.release()
if display: cv2.destroyAllWindows()