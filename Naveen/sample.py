import numpy as np
from scipy.io import savemat
from scipy.interpolate import interp1d	
from random import shuffle

a = set(['a', 'b', 'c'])
b = set(['a', 'c', 'd'])
print b.difference(b.intersection(a))

# print np.random.randint(0, 10, (2, 5))
# print np.random.randint(0, 10, (2, 5))

# def func(**kwargs):
# 	print kwargs.values()

# func(a=1, b= 2)

# def interpn(xp, yp, x):
# 	y = np.zeros((x.size, yp.shape[1]))
# 	for dim in range(yp.shape[1]):
# 		f = interp1d(xp, yp[:, dim], kind='linear')
# 		y[:, dim] = f(x)
# 	return y

# xp = np.linspace(0, 1, 10)
# yp = np.random.rand(10, 2)

# x = np.linspace(0, 1, 20)

# y = interpn(xp, yp, x)

# print yp
# print y