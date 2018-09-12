import numpy as np
import json
from helpers import *

a = np.array([1, 2, 3])
b = np.array([1, 2, 3])

print a.reshape(1, -1)


# yp = np.float32(np.random.randint(0, 10, (4, 3)))
# reps = np.array([0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3])

# print yp
# print reps

# print smart_interpn(yp, reps, kind = 'linear')