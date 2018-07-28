import cv2, numpy as np, os, sys
import glob
import matplotlib.pyplot as plt

skel_path = '12_0_S99_L99_x_x_skel.txt'
## Global parameters
torso_id = 0
neck_id = 2
left_hand_id = 7
right_hand_id = 11
thresh_level = 0.2

base_id = torso_id

## Read skeleton file
with open(skel_path, 'r') as fp:
	lines = fp.readlines()
	lines = [map(float, line.split(' ')) for line in lines]
if len(lines) == 0: 
	print os.path.basename(skel_path), ' has 0 lines'

left = []
right = []

for idx, line in enumerate(lines):
	left_y = np.array(line[3*left_hand_id:3*left_hand_id+3]) - np.array(line[3*base_id:3*base_id+3])
	right_y = np.array(line[3*right_hand_id:3*right_hand_id+3]) - np.array(line[3*base_id:3*base_id+3])
	left.append(left_y.tolist())
	right.append(right_y.tolist())

left = np.array(left)
right = np.array(right)

plt.plot(range(left.shape[0]), left[:,2])
plt.plot(range(right.shape[0]), right[:,2])
plt.xlabel('frame ids')
plt.legend(['left', 'right'])
plt.show()
