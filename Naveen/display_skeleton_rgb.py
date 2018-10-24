from KinectReader import kinect_reader
from helpers import *
import cv2

kr = kinect_reader()
wait_for_kinect(kr) ## Blocking call until timeout = 30 seconds.

enable_depth = False

rgb_image = None
depth_image = None

while(True):
	rgb_flag = kr.update_rgb()
	if enable_depth: depth_flag = kr.update_depth()
	body_flag = kr.update_body(display_skel = True)

	if rgb_flag:
		rgb_image = np.copy(kr.color_image)
		resz_rgb_image = cv2.resize(rgb_image, None, fx = 0.5, fy = 0.5)
		# cv2.imshow('Color Image', resz_rgb_image)

	if(enable_depth):
		if(depth_flag):
			depth_image = np.copy(kr.depth_image)
			resz_depth_image = cv2.resize(depth_image, None, fx = 1, fy = 1)
			# cv2.imshow('Depth Image', resz_depth_image)

	if(body_flag):
		color_skel_pts = kr.color_skel_pts.tolist()
		if enable_depth: depth_skel_pts = kr.depth_skel_pts.tolist()
		if(rgb_image is not None):
			img = kr.draw_body(rgb_image, color_skel_pts, line_color = (0, 255, 100), thickness = 10)
			if(img is not None): 
				resz_img = cv2.resize(img, None, fx = 0.5, fy = 0.5)
				cv2.imshow('Color Image with Body', resz_img)
		if enable_depth:
			if(depth_image is not None):
				img = kr.draw_body(depth_image, depth_skel_pts, line_color = (0, 255, 100), thickness = 10)
				if(img is not None): 
					resz_img = cv2.resize(img, None, fx = 1, fy = 1)
					cv2.imshow('Depth Image with Body', resz_img)

	if cv2.waitKey(2) == ord('q'):
		cv2.destroyAllWindows()
		break

kr.close()