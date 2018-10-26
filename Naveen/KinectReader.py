from pykinect2 import PyKinectV2 as pk
from pykinect2 import PyKinectRuntime
import cv2, numpy as np, os, time, math, ctypes

'''
Description: A kinect v2 wrapper to read RGB, Depth and Skeleton data in real-time or from an XEF file.

How to use it:
	from KinectReader import kinect_reader
	kr = kinect_reader()
	kr.update_rgb()
		Returns True if there is color image
	kr.color_image
		np.ndarray (H x W x 3) containing the latest color image
	kr.update_depth()
		Returns True if there is depth image
	kr.depth_image
		np.ndarray (H x W) containing the latest depth image
	kr.update_body()
		Returns True if there is a skeleton
	kr.skel_pts
		A 1D np.ndarray containing 75 elements. x, y, z positions of the 25 kinect joints. Refer to kinect_joint_names.json for full list of kinect joint names and their ids.
	kr.color_skel_pts
		A 1D np.ndarray containing 50 elements. x, y positions of the 25 pixel coordinates in RGB image of the 25 joints
	kr.depth_skel_pts
		A 1D np.ndarray containing 50 elements. x, y positions of the 25 pixel coordinates in Depth image of the 25 joints
'''

class kinect_reader(object):
	def __init__(self, types = pk.FrameSourceTypes_Color | pk.FrameSourceTypes_Body | pk.FrameSourceTypes_Depth):
		self.sensor = PyKinectRuntime.PyKinectRuntime(types)

		self.color_type = pk.FrameSourceTypes_Color
		self.depth_type = pk.FrameSourceTypes_Body
		self.body_type = pk.FrameSourceTypes_Depth

		self.body_frame = None

		# color_image Initialization
		self.color_width = self.sensor.color_frame_desc.Width # 1920
		self.color_height = self.sensor.color_frame_desc.Height # 1080
		self.depth_width = self.sensor.depth_frame_desc.Width #
		self.depth_height = self.sensor.depth_frame_desc.Height #

		self.color_image = np.zeros((self.color_height, self.color_width, 3), dtype=np.uint8)

		self.skel_joint_obj = None
		self.color_skel_obj = None
		self.depth_skel_obj = None
		self.skel_pts = None
		self.color_skel_pts = None
		self.depth_skel_pts	= None

		self.color_image = None
		self.last_color_frame_access = -1

		self.depth_image = None
		self.last_depth_frame_access = -1

		self.body_frame = None
		self.last_body_frame_access = -1

	def close(self):
		self.sensor.close()

	def draw_body(self, img = None, img_skel_pts = None, only_upper_body = True, line_color = (255,255,255), thickness = 15, draw_gest_thresh = True, thresh_level = 0.2):
		'''
		Description:
			Draw the skeleton on the image (RGB/Depth), given the pixel coordinates of the skeleton.
		Input arguments:
			* img: np.ndarray. Either RGB (H x W x 3) or Depth (H x W)
			* img_skel_pts: A list of 50 elements. [x0, y0, x1, y1, x2, y2, ...]. (xi,yi) is the pixel coordinate of the ith kinect joint.
			* only_upper_body: If True, only upper body is drawn
			* line_color: The color of the line. It is a tuple of three elements. (B, G, R). B, G and R are the intensity values of blue, green and red channels.
			* thickness: thickness of the line in terms of no. of pixels.
			* thresh_level: What is the threshold level at which gesture will start. 0.2 indicates 20% of the (distance between torso and the neck) above the torso level.
			* draw_gest_thresh: If True, gesture threshold is drawn on the image.
		Return:
			* img: np.ndarray of same size as input image. The image with the skeleton drawn on a copy of the input image.
		'''

		# Return None, if the img or the skeleton points are None
		if(img is None or img_skel_pts is None): return None

		def display_joint(j_start, j_end):
			'''
			Description:
				Draw a line between the given two kinect joints.
			Input arguments:
				j_start: starting kinect joint index
				j_end: ending kinect joint index
			Return:
				True, on sucess. False, on failure.
			'''
			try:
				start = (int(img_skel_pts[2*j_start]), int(img_skel_pts[2*j_start+1]))
				end = (int(img_skel_pts[2*j_end]), int(img_skel_pts[2*j_end+1]))
				cv2.line(img, start, end, line_color, thickness)
				return True
			except Exception as exp:
				return False

		# Head/Neck/Torso
		display_joint(pk.JointType_Head, pk.JointType_Neck)
		display_joint(pk.JointType_Neck, pk.JointType_SpineShoulder)
		display_joint(pk.JointType_SpineShoulder, pk.JointType_SpineMid)
		display_joint(pk.JointType_SpineMid, pk.JointType_SpineBase)
		display_joint(pk.JointType_SpineShoulder, pk.JointType_ShoulderRight)
		display_joint(pk.JointType_SpineShoulder, pk.JointType_ShoulderLeft)
		display_joint(pk.JointType_SpineBase, pk.JointType_HipRight)
		display_joint(pk.JointType_SpineBase, pk.JointType_HipLeft)

		# Upper left limb
		display_joint(pk.JointType_ShoulderLeft, pk.JointType_ElbowLeft)
		display_joint(pk.JointType_ElbowLeft, pk.JointType_WristLeft)
		display_joint(pk.JointType_WristLeft, pk.JointType_HandLeft)
		# display_joint(pk.JointType_HandLeft, pk.JointType_HandTipLeft)
		# display_joint(pk.JointType_WristLeft, pk.JointType_ThumbLeft)

		# Upper Right limb
		display_joint(pk.JointType_ShoulderRight, pk.JointType_ElbowRight)
		display_joint(pk.JointType_ElbowRight, pk.JointType_WristRight)
		display_joint(pk.JointType_WristRight, pk.JointType_HandRight)
		# display_joint(pk.JointType_HandRight, pk.JointType_HandTipRight)
		# display_joint(pk.JointType_WristRight, pk.JointType_ThumbRight)

		# If draw_gest_thresh is True, Draw the gesture threshold.
		if(draw_gest_thresh):
			neck = color_skel_pts[2*pk.JointType_Neck:2*pk.JointType_Neck+2]
			base = color_skel_pts[2*pk.JointType_SpineBase:2*pk.JointType_SpineBase+2]

			# If neck or base are not detected, don't draw anything
			if(np.isinf(np.sum(neck)) or np.isnan(np.sum(neck))): return None
			if(np.isinf(np.sum(base)) or np.isnan(np.sum(base))): return None

			thresh_x = int(base[0])
			thresh_y = int(thresh_level * (neck[1] - base[1]) + base[1])

			thresh_disp_len = int(thresh_level * (neck[1] - base[1]))

			## Boundary conditions for starting point
			start_x = thresh_x - thresh_disp_len
			if(start_x < 0): start_x = 0
			elif(start_x >= img.shape[1]): start_x = img.shape[1] - 1
			## Boundary conditions for ending point
			end_x = thresh_x + thresh_disp_len
			if(end_x < 0): end_x = 0
			elif(end_x >= img.shape[1]): end_x = img.shape[1] - 1

			start = (start_x, thresh_y)
			end = (end_x, thresh_y)

			cv2.circle(img,(int(thresh_x),int(thresh_y)), 10, (0,0,255), -1)
			cv2.line(img, start, end, (50, 0, 255), thickness)

		## If only_upper_body is True, draw only the upper body. Else, draw the entire body.
		if(not only_upper_body):
			# Lower left limb
			display_joint(pk.JointType_HipLeft, pk.JointType_KneeLeft)
			display_joint(pk.JointType_KneeLeft, pk.JointType_AnkleLeft)
			display_joint(pk.JointType_AnkleLeft, pk.JointType_FootLeft)

			# Lower right limb
			display_joint(pk.JointType_HipRight, pk.JointType_KneeRight)
			display_joint(pk.JointType_KneeRight, pk.JointType_AnkleRight)
			display_joint(pk.JointType_AnkleRight, pk.JointType_FootRight)

		return img

	def update_rgb(self):
		rgb_flag = self.sensor.has_new_color_frame()
		if rgb_flag:
			self.color_image = self.sensor.get_last_color_frame()
			self.color_image  = np.reshape(self.color_image, (self.color_height, self.color_width, -1))
			self.color_image = cv2.cvtColor(self.color_image,cv2.COLOR_BGRA2BGR)
			self.last_color_frame_access = self.sensor._last_color_frame_access
		else:
			self.color_image = None
			self.last_color_frame_access = -1
		return rgb_flag

	def update_depth(self):
		depth_flag = self.sensor.has_new_depth_frame()
		if depth_flag:
			depth_arr = self.sensor.get_last_depth_frame()
			self.depth_image = np.reshape(depth_arr ,(self.depth_height, self.depth_width)) # (424 - depth_height, 512 - depth_width)
			self.depth_image = np.uint8(self.depth_image*255)
			self.last_depth_frame_access = self.sensor._last_depth_frame_access
		else:
			self.depth_image = None
			self.last_depth_frame_access = -1
		return depth_flag

	def update_body(self):
		body_flag = self.sensor.has_new_body_frame()
		if body_flag:
			self.body_frame = self.sensor.get_last_body_frame()
			self.last_body_frame_access = self.sensor._last_body_frame_access
		else:
			self.body_frame = None
			self.last_body_frame_access = -1

		## Finding a large body index
		if self.body_frame is not None:
			body_depth_list = []
			for i in range(0, self.sensor.max_body_count):
				body_iterate = self.body_frame.bodies[i]
				if not body_iterate.is_tracked:
					body_depth_list.append(float('inf'))
				else:
					self.skel_joint_obj = body_iterate.joints
					## Find the depth of head, left & right shoulder and neck
					depths = [self.skel_joint_obj[pk.JointType_Head].Position.z, self.skel_joint_obj[pk.JointType_ShoulderLeft].Position.z, \
							self.skel_joint_obj[pk.JointType_ShoulderRight].Position.z, self.skel_joint_obj[pk.JointType_Neck].Position.z]

					# The average distance between the kinect to the joint is considered as the overall depth
					body_depth_list.append(np.mean(depths))

			## The consider the body that is closer to the kinect.
			if min(body_depth_list) != float('inf'):
				closer_body_id = np.argmin(body_depth_list)
				body_iterate = self.body_frame.bodies[closer_body_id]
				if body_iterate.is_tracked:
					self.skel_joint_obj = body_iterate.joints
					self.color_skel_obj = self.sensor.body_joints_to_color_space(self.skel_joint_obj)
					self.depth_skel_obj = self.sensor.body_joints_to_depth_space(self.skel_joint_obj)
					## Obtain the corresponding skeletons on the RGB image and the depth image.
					self.update_skeleton()
				else:
					self.skel_joint_obj, self.color_skel_obj, self.depth_skel_obj = None, None, None
					print('No Bodies are Tracked !')
					body_flag = False
			else:
				body_flag = False
		return body_flag

	def update_skeleton(self):
		## Body skeleton in world coordinates (x, y, z) in meters
		## 1D np.ndarraly of 75 elements [x1, y1, z1, x2, y2, z2, ...]
		self.skel_pts = np.array([[self.skel_joint_obj[idx].Position.x, self.skel_joint_obj[idx].Position.y, self.skel_joint_obj[idx].Position.z] for idx in range(25)]).flatten()
		## Skeleton on the RGB image in terms of pixel coordinates of the joints in the RGB image.
		## 1D np.ndarray of 50 elements [x1, y1, x2, y2, ...]
		self.color_skel_pts = np.array([[self.color_skel_obj[idx].x, self.color_skel_obj[idx].y] for idx in range(25)]).flatten()
		## Skeleton on the Depth image in terms of pixel coordinates of the joints in the depth image.
		## 1D np.ndarray of 50 elements [x1, y1, x2, y2, ...]
		self.depth_skel_pts = np.array([[self.depth_skel_obj[idx].x, self.depth_skel_obj[idx].y] for idx in range(25)]).flatten()

__main__ = "Kinect v2 Reader"
