import numpy as np
import os, sys

# def sz_in_kb(filepath):
# 	if(not os.path.isfile(filepath)):
# 		sys.exit('file: '+filepath+' does NOT exist')
# 	return float('%.1f'%(os.stat(filepath).st_size/1024.0))

# fname = 'E:\\AHRQ\\Study_IV\\XEF_Files\\S1_L3\\10_1_S1_L3_X_OnePanel.xef'
# print os.stat(fname)
# print sz_in_kb(fname) / 1024.0 / 1024.0

# # 67s - 10 GB
# # 90s - 13.6
# # 59s - 9.3

# A = np.random.rand(3,4)
# print A
# print np.std(A, axis = 0)

x = np.random.randint(0, 10, 3)
y = np.random.randint(0, 10, 3)
print x, y

z = np.append(x, y)
print z

print(2!=9)
print(not False)