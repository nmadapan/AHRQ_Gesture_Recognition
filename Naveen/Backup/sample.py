import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

a = np.array([1, 2, 3, 4])
print(a.count(2))

mu, sigma = 100, 15
x = mu + sigma*np.random.randn(10000)

print(x.shape)

# the histogram of the data
n, bins, patches = plt.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
# print(bins.shape)

# # add a 'best fit' line
# y = mlab.normpdf( bins, mu, sigma)
# l = plt.plot(bins, y, 'r--', linewidth=1)

plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)

plt.show()


# import numpy as np
# from scipy.io import savemat
# from scipy.interpolate import interp1d	
# from random import shuffle

# a = np.random.randint(0, 10, (1, 4))
# b = np.random.randint(0, 10, (4,1))
# print a
# print b
# print np.sum(b == a)



# x = 'a'
# y = 'b'
# a = '%s, %s'%(x, y)
# b = '{}, {}'.format(x, y)
# print a, b

# a = set(['a', 'b', 'c'])
# b = set(['a', 'c', 'd'])
# print b.difference(b.intersection(a))

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