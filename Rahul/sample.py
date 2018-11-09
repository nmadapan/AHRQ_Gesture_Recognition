# import numpy as np
# import pickle,sys
# from scipy.interpolate import interp1d 

# a= np.random.randint(1,10,(3,4))
# print a
# def interpn(yp, num_points=9, kind = 'nearest'):
#     # yp is a gesture instance
#     # No. of frames will be increased/reduced to num_points
#     xp = np.linspace(0, 1, num = yp.shape[0])
#     x = np.linspace(0, 1, num = num_points)
#     y = np.zeros((x.size, yp.shape[1]))
#     for dim in range(yp.shape[1]):
#         f = interp1d(xp, yp[:, dim], kind = kind)
#         y[:, dim] = f(x)
#     return y
# print interpn(a)

print 5/2