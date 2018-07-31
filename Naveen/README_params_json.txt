max_r: max lenth of the entire arm (meters)
max_dr: speed of the hand (m/frame)
max_th: max differece between the theta_t and theta_t+1 where theta_t is the angle made by dx,dy of the hand trayectory
max_dth: max change in angle that can happen
all_flag: use all posible feature types. When false, the user must specify in "feature types" the features that will be used.
feature_types: features to use (if all flag is False)
num_joints: number of joints to consider (1: just the hand, 2: hand and elbow)
dominant_first: when True, the hand with more motion will be placed first in the features.
dominant_first_thresh: the threshold for considering a hand dominant over the other.
dim_per_joint: 3 by default (x,y,z). Can be specified in the range of 1-3.
randomize: randomize the order of the instances (gesture samples)
equate_dim: make the dimention of the feature space the same for all samples
fixed_num_frames: fixed number of features to use in the equate dimention option when set to True.
lengths_per_frame: number of finger lenths to consider (comming from open pose)
openpose_downsample_rate: downsampling rate for open-pose processing.