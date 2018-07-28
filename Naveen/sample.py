import numpy as np
import json
from helpers import *

fpaths = glob(os.path.join('..', 'Data', 'L2', '*_skel.txt'))
fpaths = [os.path.basename(fpath) for fpath in fpaths]
fpaths = sorted(fpaths, cmp = skelfile_cmp)
print fpaths

# a = [([1, 2], [2, 3]), ([1, 2], [2, 3])]
# x, y = zip(*a)
# print list(x), y
# print len(' ')
# # with open('param.json', 'r') as fp:

# # 	data = json.load(fp)

# # print json_to_dict('param.json')

# class New:
# 	def __init__(self):
# 		self.update()

# 	def update(self):
# 		data = json_to_dict('param.json')
# 		for key, value in data.items():
# 			setattr(self, key, value)

# 	def print_stuff(self):
# 		print self.dim_per_joint
# 		print self.all_flag
# 		print self.feature_types

# inst = New()
# inst.print_stuff()

# # a = np.random.randint(0 ,10, (10, ))
# # print a.shape
# # print a.reshape(2, -1)

# # strs = ['7_1', '1_0', '4_2']

# # print sorted(strs, cmp=class_str_cmp)

# # print json_to_dict('param.json')
# # x = np.random.rand(4)
# # print x
# # print x.ndim
# # x = x[np.newaxis]
# # print x.ndim

