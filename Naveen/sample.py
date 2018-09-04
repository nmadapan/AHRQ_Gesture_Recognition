import numpy as np
import json
from helpers import *

a = ((1,2), (2,3))
print a
print list(a)

# from threading import Thread
# import time
# class ThreadTest:
# 	def __init__(self):
# 		self.flag = True
# 		pass

# 	def generate(self):
# 		while True:
# 			self.flag = np.random.randint(0 ,100)
# 			print 'Producer: ', self.flag
# 			time.sleep(5)

# 	def print_status(self):
# 		while True: 
# 			print '\tConsumer: ', self.flag
# 			time.sleep(5)

# inst = ThreadTest()

# thread1 = Thread(name = 'thread1', target = inst.generate)
# thread2 = Thread(name = 'thread2', target = inst.print_status)

# thread1.start()
# thread2.start()

# # from datetime import datetime
# # import time

# # for _ in range(100):
# # 	print int(time.time()*100)
# # 	_ = np.random.rand(1920, 1080, 3)

# # # var = [None]
# # # a =2

# # # def func(l, b):
# # # 	l[-1] = 2
# # # 	b = 3
# # # func(var,a)

# # # print(var)
# # # print(a)





# # # # fpaths = glob(os.path.join('..', 'Data', 'L2', '*_skel.txt'))
# # # # fpaths = [os.path.basename(fpath) for fpath in fpaths]
# # # # fpaths = sorted(fpaths, cmp = skelfile_cmp)
# # # # print fpaths

# # # # a = [([1, 2], [2, 3]), ([1, 2], [2, 3])]
# # # # x, y = zip(*a)
# # # # print list(x), y
# # # # print len(' ')
# # # # # with open('param.json', 'r') as fp:

# # # # # 	data = json.load(fp)

# # # # # print json_to_dict('param.json')

# # # # class New:
# # # # 	def __init__(self):
# # # # 		self.update()

# # # # 	def update(self):
# # # # 		data = json_to_dict('param.json')
# # # # 		for key, value in data.items():
# # # # 			setattr(self, key, value)

# # # # 	def print_stuff(self):
# # # # 		print self.dim_per_joint
# # # # 		print self.all_flag
# # # # 		print self.feature_types

# # # # inst = New()
# # # # inst.print_stuff()

# # # # # a = np.random.randint(0 ,10, (10, ))
# # # # # print a.shape
# # # # # print a.reshape(2, -1)

# # # # # strs = ['7_1', '1_0', '4_2']

# # # # # print sorted(strs, cmp=class_str_cmp)

# # # # # print json_to_dict('param.json')
# # # # # x = np.random.rand(4)
# # # # # print x
# # # # # print x.ndim
# # # # # x = x[np.newaxis]
# # # # # print x.ndim

