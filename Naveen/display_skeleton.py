import cv2, numpy as np, os, sys, time, math
from helpers import json_to_dict, get_body_length

base_path = 'D:\\AHRQ\\Study_IV\\Data\\Data\\L3'
skel_filename = '3_0_S3_L3_Rotate_X_skel_flip.txt'
joint_names_file = '.\\kinect_joint_names.json'

class DisplaySkeleton:
	def __init__(self, skeleton_path, joint_names_path = 'kinect_joint_names.json', \
				color_image = None):
		self.skeleton_path = skeleton_path
		self.W, self.H = 1920, 1080 # Kinect by default records 1920 x 1080
		self.color_image = color_image if color_image is not None else\
			np.zeros((self.H, self.W, 3), dtype = np.uint8) # Black background if no image is passed.
		self.jnames = json_to_dict(joint_names_path)
		self.line = None
		self.run_flag = True

	def get_lines(self):
		# Returns list of lists. Inner list is a list of 75 elements (x1, y1, z1 ... )
		lines = []
		with open(self.skeleton_path, 'r') as fp:
			for line in fp.readlines():
				line = line.replace('-inf', '-1').replace('inf', '-1')
				line = map(float, line.strip().split(' '))
				lines.append(line)
		return lines

	def body_basics(self):
		# Head/Neck/Torso
		self.display_joint(self.jnames['JointType_Head'], self.jnames['JointType_Neck'])
		self.display_joint(self.jnames['JointType_Neck'], self.jnames['JointType_SpineShoulder'])
		self.display_joint(self.jnames['JointType_SpineShoulder'], self.jnames['JointType_SpineMid'])
		self.display_joint(self.jnames['JointType_SpineMid'], self.jnames['JointType_SpineBase'])
		self.display_joint(self.jnames['JointType_SpineShoulder'], self.jnames['JointType_ShoulderRight'])
		self.display_joint(self.jnames['JointType_SpineShoulder'], self.jnames['JointType_ShoulderLeft'])
		self.display_joint(self.jnames['JointType_SpineBase'], self.jnames['JointType_HipRight'])
		self.display_joint(self.jnames['JointType_SpineBase'], self.jnames['JointType_HipLeft'])

		# Upper left limb
		(L1, ok1) = self.display_joint(self.jnames['JointType_ShoulderLeft'], self.jnames['JointType_ElbowLeft'])
		(L2, ok2) = self.display_joint(self.jnames['JointType_ElbowLeft'], self.jnames['JointType_WristLeft'])
		self.display_joint(self.jnames['JointType_WristLeft'], self.jnames['JointType_HandLeft'])
		self.display_joint(self.jnames['JointType_HandLeft'], self.jnames['JointType_HandTipLeft'])
		self.display_joint(self.jnames['JointType_WristLeft'], self.jnames['JointType_ThumbLeft'])

		# Upper Right limb
		self.display_joint(self.jnames['JointType_ShoulderRight'], self.jnames['JointType_ElbowRight'])
		self.display_joint(self.jnames['JointType_ElbowRight'], self.jnames['JointType_WristRight'])
		self.display_joint(self.jnames['JointType_WristRight'], self.jnames['JointType_HandRight'])
		self.display_joint(self.jnames['JointType_HandRight'], self.jnames['JointType_HandTipRight'])
		self.display_joint(self.jnames['JointType_WristRight'], self.jnames['JointType_ThumbRight'])

		# Lower left limb
		self.display_joint(self.jnames['JointType_HipLeft'], self.jnames['JointType_KneeLeft'])
		self.display_joint(self.jnames['JointType_KneeLeft'], self.jnames['JointType_AnkleLeft'])
		self.display_joint(self.jnames['JointType_AnkleLeft'], self.jnames['JointType_FootLeft'])

		# Lower right limb
		self.display_joint(self.jnames['JointType_HipRight'], self.jnames['JointType_KneeRight'])
		self.display_joint(self.jnames['JointType_KneeRight'], self.jnames['JointType_AnkleRight'])
		self.display_joint(self.jnames['JointType_AnkleRight'], self.jnames['JointType_FootRight'])

		# # Upper left limb
		# if ok1 and ok2:
		# 	ElbowLeft = skel_joint_obj[self.jnames['JointType_ElbowLeft].TrackingState
		# 	Angle_between_line = math.acos(np.dot(L1, L2)/np.sqrt(np.sum(L1**2))/np.sqrt(np.sum(L2**2)))
		# 	str_out = str(int(Angle_between_line*180/math.pi)) + " degrees"
		# 	if (ElbowLeft != TrackingState_NotTracked):
		# 		elbowpts = (int(color_skel_obj[self.jnames['JointType_ElbowLeft].x), int(color_skel_obj[self.jnames['JointType_ElbowLeft].y))
		# 		cv2.putText(color_image, str_out, elbowpts, cv2.FONT_HERSHEY_SIMPLEX, 4, (0,255,0),2)

	def display_joint(self, j_start, j_end):
		x1, y1 = tuple(self.line[j_start*2 : j_start*2+2])
		x2, y2 = tuple(self.line[j_end*2 : j_end*2+2])

		if (x1 == -1 or x2 == -1):
			return 0, 0

		# try:
		start = (x1, y1)
		end = (x2, y2)

		# We are missing the line drawing function.
		cv2.line(self.temp_image,start,end,(255,255,255),15)

		L = np.asarray(start) - np.asarray(end)
		return L, 1

		# except Exception as e: # there are skel_joint_obj at infty, need to catch it
		# 	print e
		# 	return 0, 0

	def run(self):
		self.lines = self.get_lines()

		for line in self.lines:
			body_len = get_body_length(line)
			m_to_pix = self.H / (3 * body_len)

			line = np.array(line).reshape(25, 3)
			line -= line[self.jnames['JointType_SpineBase'],:] # Substract the torso
			line[:,1] *= -1 # WHYYYYY. NO IDEA.
			line = (m_to_pix * line[:,:-1]) + np.array([self.W/2.0, self.H/2.0])
			self.line = np.int16(line.flatten()).tolist()

			# TODO: in regular circumstances you would read the new
			# image frame in here
			self.temp_image = self.color_image.copy()
			self.body_basics()
	
			# Show the image
			cv2.imshow('Window', cv2.resize(self.temp_image, None, fx = 0.5, fy = 0.5))
			if cv2.waitKey(1) == ord('q'):
				cv2.destroyAllWindows()
				self.run_flag = False

			time.sleep(0.04)
			if(not self.run_flag): break

disp_obj = DisplaySkeleton(os.path.join(base_path, skel_filename), joint_names_file)
disp_obj.run()