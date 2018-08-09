## Assumptions:
#	* There is only roll angle about person's veritcal axis
#	* Kinect is not tilted
##
import os
import numpy as np
import sys

basepath = 'D:\\AHRQ\\Study_IV\\Data\\Data\\L3'
skelname = '1_0_S1_L3_Scroll_X_skel.txt'
newname = skelname[:-4] + '_flip.txt'

with open(os.path.join(basepath, skelname), 'r') as fp:
	lines = fp.readlines()
	lines = [map(float, line.strip().split(' ')) for line in lines]

fp = open(os.path.join(basepath, newname), 'w') 

left_sh_idx = 4
right_sh_idx = 8
spine_idx = 0

for line in lines:
	torso = np.array(line[3*spine_idx:3*spine_idx+3] )
	left_sh = np.array(line[3*left_sh_idx:3*left_sh_idx+3])
	right_sh = np.array(line[3*right_sh_idx:3*right_sh_idx+3])
	
	mat = np.reshape(line, (25, 3))

	# Normalize w.r.t torso
	mat = mat - torso

	# Find the theta
	zr = right_sh[-1]
	zl = left_sh[-1]
	shoulder_length = np.linalg.norm(left_sh-right_sh)
	theta = np.arcsin((zr-zl)/shoulder_length)

	R = np.eye(3)
	R[0, 0] = np.cos(theta)
	R[0, 2] = np.sin(theta)
	R[2, 0] = -np.sin(theta)
	R[2, 2] = np.cos(theta)

	# Transform the matrix
	mat = np.dot(R, mat.transpose())
	mat[0, :] = -mat[0, :]
	mat = mat.transpose() + torso

	line = mat.flatten()
	fp.write(' '.join(map(str, line)) + '\n')

fp.flush()
fp.close()