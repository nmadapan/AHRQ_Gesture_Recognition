import numpy as np
import json
from helpers import *

# with open('param.json', 'r') as fp:
# 	data = json.load(fp)

# print data.keys(), data.values()

# a = np.random.randint(0 ,10, (10, ))
# print a.shape
# print a.reshape(2, -1)

strs = ['7_1', '1_0', '4_2']

print sorted(strs, cmp=class_str_cmp)

