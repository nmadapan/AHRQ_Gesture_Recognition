import numpy as np
from scipy.interpolate import interp1d

## Velocity
d_reps = np.ones(left.shape[0]-2).tolist(); d_reps.append(2)
d_left = np.diff(left, axis = 0);
d_left = np.repeat(d_left, d_reps, axis = 0)
d_right = np.diff(right, axis = 0);
d_right = np.repeat(d_right, d_reps, axis = 0)
features['d_left'] = d_left
features['d_right'] = d_right

## Acceleration
dd_reps = np.ones(left.shape[0]-3).tolist(); dd_reps.append(3)
dd_left = np.diff(np.diff(left, axis = 0), axis = 0);
dd_left = np.repeat(dd_left, dd_reps, axis = 0)
dd_right = np.diff(np.diff(right, axis = 0), axis = 0);
dd_right = np.repeat(dd_right, dd_reps, axis = 0)
features['dd_left'] = dd_left
features['dd_right'] = dd_right

## Angle
theta_left = np.arctan2(d_left, np.roll(d_left, 1, axis = 1))
theta_right = np.arctan2(d_right, np.roll(d_right, 1, axis = 1))
features['theta_left'] = theta_left
features['theta_right'] = theta_right

## Angular velocity
d_theta_left = np.diff(theta_left, axis = 0);
d_theta_left = np.repeat(d_theta_left, d_reps, axis = 0)
d_theta_right = np.diff(theta_right, axis = 0);
d_theta_right = np.repeat(d_theta_right, d_reps, axis = 0)
features['d_theta_left'] = d_theta_left
features['d_theta_right'] = d_theta_right

## Angular acceleration
dd_theta_left = np.diff(np.diff(theta_left, axis = 0), axis = 0);
dd_theta_left = np.repeat(dd_theta_left, dd_reps, axis = 0)
dd_theta_right = np.diff(np.diff(theta_right, axis = 0), axis = 0);
dd_theta_right = np.repeat(dd_theta_right, dd_reps, axis = 0)
features['dd_theta_left'] = dd_theta_left
features['dd_theta_right'] = dd_theta_right

with open('raw_features.pickle', 'wb') as fp:
	pickle.dump(features, fp)

with open('raw_features.pickle', 'rb') as fp:
	dic = pickle.load(fp)

x = np.array(range(num_points))
x_new = np.linspace(0, num_points - 1)

for keys, values in features.items():
	data = features[keys]
	x = np.array(range())