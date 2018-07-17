import numpy as np
import json

# with open('param.json', 'r') as fp:
# 	data = json.load(fp)

# print data.keys(), data.values()

a = np.random.randint(0 ,10, (10, ))
print a.shape
print a.reshape(2, -1)