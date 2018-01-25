from pykinect2 import PyKinectV2 as pk
from pykinect2 import PyKinectRuntime
import cv2, numpy as np, os, time, math, ctypes

class KinectReader(object):
	def __init__(self):
		# Kinect runtime object, we want only color and body frames 
		self.sensor = PyKinectRuntime.PyKinectRuntime(pk.FrameSourceTypes_Color | pk.FrameSourceTypes_Body | pk.FrameSourceTypes_Depth)

		self.body_frame = None

		# color_image Initialization
		self.color_width = self.sensor.color_frame_desc.Width # 1920
		self.color_height = self.sensor.color_frame_desc.Height # 1080
		self.depth_width = self.sensor.depth_frame_desc.Width # 
		self.depth_height = self.sensor.depth_frame_desc.Height # 

		self.color_image = np.zeros((self.color_height, self.color_width, 3), dtype=np.uint8)

	def Body_basics(self):
		# Head/Neck/Torso
		self.display_joint(pk.JointType_Head, pk.JointType_Neck)
		self.display_joint(pk.JointType_Neck, pk.JointType_SpineShoulder)
		self.display_joint(pk.JointType_SpineShoulder, pk.JointType_SpineMid)
		self.display_joint(pk.JointType_SpineMid, pk.JointType_SpineBase)
		self.display_joint(pk.JointType_SpineShoulder, pk.JointType_ShoulderRight)
		self.display_joint(pk.JointType_SpineShoulder, pk.JointType_ShoulderLeft)
		self.display_joint(pk.JointType_SpineBase, pk.JointType_HipRight)
		self.display_joint(pk.JointType_SpineBase, pk.JointType_HipLeft)

		# Upper left limb
		(L1, ok1) = self.display_joint(pk.JointType_ShoulderLeft, pk.JointType_ElbowLeft)
		(L2, ok2) = self.display_joint(pk.JointType_ElbowLeft, pk.JointType_WristLeft)
		self.display_joint(pk.JointType_WristLeft, pk.JointType_HandLeft)
		self.display_joint(pk.JointType_HandLeft, pk.JointType_HandTipLeft)
		self.display_joint(pk.JointType_WristLeft, pk.JointType_ThumbLeft)

		# Upper Right limb
		self.display_joint(pk.JointType_ShoulderRight, pk.JointType_ElbowRight)
		self.display_joint(pk.JointType_ElbowRight, pk.JointType_WristRight)
		self.display_joint(pk.JointType_WristRight, pk.JointType_HandRight)
		self.display_joint(pk.JointType_HandRight, pk.JointType_HandTipRight)
		self.display_joint(pk.JointType_WristRight, pk.JointType_ThumbRight)

		# Lower left limb
		self.display_joint(pk.JointType_HipLeft, pk.JointType_KneeLeft)
		self.display_joint(pk.JointType_KneeLeft, pk.JointType_AnkleLeft)
		self.display_joint(pk.JointType_AnkleLeft, pk.JointType_FootLeft)

		# Lower right limb
		self.display_joint(pk.JointType_HipRight, pk.JointType_KneeRight)
		self.display_joint(pk.JointType_KneeRight, pk.JointType_AnkleRight)
		self.display_joint(pk.JointType_AnkleRight, pk.JointType_FootRight)

		# Upper left limb
		if ok1 and ok2:
			ElbowLeft = self.skel_joint_obj[pk.JointType_ElbowLeft].TrackingState
			Angle_between_line = math.acos(np.dot(L1, L2)/np.sqrt(np.sum(L1**2))/np.sqrt(np.sum(L2**2)))
			str_out = str(int(Angle_between_line*180/math.pi)) + " degrees"
			if (ElbowLeft != pk.TrackingState_NotTracked):
				elbowpts = (int(self.color_skel_obj[pk.JointType_ElbowLeft].x), int(self.color_skel_obj[pk.JointType_ElbowLeft].y))
				cv2.putText(self.color_image, str_out, elbowpts, cv2.FONT_HERSHEY_SIMPLEX, 4, (0,255,0),2)

	def display_joint(self, j_start, j_end):
		statJ0 = self.skel_joint_obj[j_start].TrackingState;
		statJ1 = self.skel_joint_obj[j_end].TrackingState;

		if (statJ0 == pk.TrackingState_NotTracked):
			return 0, 0

		if (statJ1 == pk.TrackingState_NotTracked):
			return 0, 0

		if (statJ0 == pk.TrackingState_Inferred) and (statJ1 == pk.TrackingState_Inferred):
			return 0, 0

		try:
			start = (int(self.color_skel_obj[j_start].x), int(self.color_skel_obj[j_start].y))
			end = (int(self.color_skel_obj[j_end].x), int(self.color_skel_obj[j_end].y))

			# We are missing the line drawing function.
			cv2.line(self.color_image,start,end,(255,255,255),15)

			L = np.asarray(start) - np.asarray(end)
			return L, 1

		except Exception as e: # there are skel_joint_obj at infty, need to catch it
			# print e
			return 0, 0

	def update_rgb(self):
		if self.sensor.has_new_color_frame():
			self.color_image = self.sensor.get_last_color_frame()
			self.color_image  = np.reshape(self.color_image, (self.color_height, self.color_width, -1))
			self.color_image = cv2.cvtColor(self.color_image,cv2.COLOR_BGRA2BGR)

	def update_depth(self):
		if self.sensor.has_new_depth_frame():
			depth_arr = self.sensor.get_last_depth_frame()
			self.depth_image = np.reshape(depth_arr ,(self.depth_height, self.depth_width)) # (424 - depth_height, 512 - depth_width)
			self.depth_image = np.uint8(self.depth_image*255)
			# cv2.imshow("depth", self.depth_image)

	# Yet to be verified with two people
	def update_body(self, display_skel=False):
		if self.sensor.has_new_body_frame():
			self.body_frame = self.sensor.get_last_body_frame()
		
		# Finding a large body index
		body_length_list = []
		if self.body_frame is not None:
			for i in range(0, self.sensor.max_body_count):
				body_iterate = self.body_frame.bodies[i]
				if not body_iterate.is_tracked:
					continue
				self.skel_joint_obj = body_iterate.joints
				head_coord = [self.skel_joint_obj[pk.JointType_Head].Position.x, self.skel_joint_obj[pk.JointType_Head].Position.y,\
							   self.skel_joint_obj[pk.JointType_Head].Position.z]
				right_foot_coord = [self.skel_joint_obj[pk.JointType_FootRight].Position.x, self.skel_joint_obj[pk.JointType_FootRight].Position.y,\
									self.skel_joint_obj[pk.JointType_FootRight].Position.z]
				# Distance from head to right foot is the body length
				body_length_list.append(np.linalg.norm(np.array(head_coord) - np.array(right_foot_coord)))
				if display_skel: self.Body_basics()
		
			large_body_id = np.argmax(body_length_list)
			body_iterate = self.body_frame.bodies[large_body_id]
			if body_iterate.is_tracked:
				self.skel_joint_obj = body_iterate.joints
				self.color_skel_obj = self.sensor.body_joints_to_color_space(self.skel_joint_obj)
				self.depth_skel_pts = self.sensor.body_joints_to_depth_space(self.skel_joint_obj)
			else:
				print('No Bodies are Tracked !')

	def update_skeleton(self):
		self.skel_pts = np.array([[self.skel_joint_obj[idx].Position.x, self.skel_joint_obj[idx].Position.y, self.skel_joint_obj[idx].Position.z] for idx in range(25)]).flatten()
		self.color_skel_pts = np.array([[int(self.color_skel_obj[idx].x), int(self.color_skel_obj[idx].y)] for idx in range(25)]).flatten()
		self.depth_skel_pts = np.array([[int(self.depth_skel_pts[idx].x), int(self.depth_skel_pts[idx].y)] for idx in range(25)]).flatten()

__main__ = "Kinect v2 Reader"
