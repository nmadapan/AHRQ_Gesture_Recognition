from helpers import *
import cv2
from copy import deepcopy
from KinectReader import kinect_reader 

class FancyDisplay:
	def __init__(self, image = None, delay = 2, color_skel_pts = None, line_color = (0, 255, 100), thickness = 10, window_str = 'Window'):
		self.image = image
		self.color_skel_pts = color_skel_pts
		self.line_color = line_color
		self.thickness = thickness
		self.delay = delay
		self.window_str = window_str
		self.kr = kinect_reader()

		cv2.namedWindow(self.window_str)

	def update_image(self, new_img):
		if(new_img is not None): self.image = np.copy(new_img)

	def update_skel_pts(self, skel_pts):
		if(skel_pts is not None): self.color_skel_pts = deepcopy(skel_pts)

	def refresh(self):
		flag = True
		if((self.image is not None) and (self.color_skel_pts is not None)):
			image_with_skel = self.kr.draw_body(self.image, self.color_skel_pts, line_color = self.line_color, thickness = self.thickness)
			if(image_with_skel is not None):
				resz_img = cv2.resize(image_with_skel, None, fx = 0.5, fy = 0.5)
				cv2.imshow(self.window_str, resz_img)
				flag = True
		if cv2.waitKey(self.delay) == ord('q'):
			cv2.destroyAllWindows()
			flag = False
		return flag


if __name__ == '__main__':
	kr = kinect_reader()
	wait_for_kinect(kr) ## Blocking call until timeout = 30 seconds.	

	window_str = 'Color Image with Body'

	rgb_obj = FancyDisplay(window_str = window_str)
	flag = True

	while flag:
		rgb_flag = kr.update_rgb()
		body_flag = kr.update_body()

		rgb_obj.update_image(kr.color_image)
		rgb_obj.update_skel_pts(kr.color_skel_pts)

		flag = rgb_obj.refresh()

	kr.close()