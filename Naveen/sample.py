import numpy as np
from scipy.io import savemat

a = 5
b = 6

x = np.random.rand(a)
y = np.random.rand(b)

# savemat('test.mat', dict(x=[x, y]))

# # Create a list of numpy arrays (_ x Fixed)
# # Create a list of numpy arrays (_ x num_classes) # One hot vector 
# # savemat('', dict(data_input = _, data_output = _))

# print x, y
# print np.concatenate((x, y), axis = 0)

a = set([1, 1, 2, 2, 3])
print list(a)