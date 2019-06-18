from scipy.io import loadmat

A = loadmat('time_data.mat', chars_as_strings = True, matlab_compatible = False)
A = A['time_data']

print A
