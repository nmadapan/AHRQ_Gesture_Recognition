#!/usr/bin/env python
'''
Install Instructions:
	* Open the command line
	* git clone https://github.com/reineking/pyds.git
	* cd pyds && python setup.py build && python setup.py install
'''

from pyds import MassFunction
import numpy as np
from sklearn.neighbors import NearestNeighbors

class DST:
	"""
	the class of Dempster-Shafer Theory (DST)
	and Dempster's Rule of Combination (DRC)
	"""

	def __init__(self):
		self.m_dict = {}
		self.num_classes = None
		self.num_models = None
		self.cnames = None
		self.mnames = None

	def predict(self, M, mnames = None, cnames = None):
		'''
		Description:
		Input arguments:
			* M - 2D np.ndarray of size num_models x num_classes
		'''
		assert M.ndim == 2, 'Error! M should be a 2D np.ndarray.'
		if(mnames is None):
			mnames = ['m'+str(ix) for ix in range(M.shape[0])]
		else: assert len(mnames) == M.shape[0], 'Size of mnames should be equal to no. of rows in M'
		if(cnames is None):
			cnames = [str(ix) for ix in range(M.shape[1])]
		else: assert len(mnames) == M.shape[1], 'Size of cnames should be equal to no. of columns in M'

		M = np.copy(M)
		self.mnames = mnames
		self.cnames = cnames
		self.num_classes = M.shape[1]
		self.num_models = M.shape[0]

		M = (M.transpose() / np.sum(M, axis = 1)).transpose()

		for mname, mprobs in zip(self.mnames, M):
			# print {mname: dict(zip(cnames, mprobs))}
			self.add_mass({mname: dict(zip(cnames, mprobs))})

		m_comb = self.drc_comb(self.mnames)
		print "Combined mass using DRC ===> ", m_comb

		# vote is to select the label with the largest mass
		y_pred = self.vote(m_comb)
		print "y_pred: %s" % y_pred
		return y_pred


	def add_mass(self, m, show=0):
		"""
		m is a dict of {name: mass_function}
		mass_function = {'class1':weight1, 'class2': weight2, ...}
		"""

		# print 'Printing Keyssss'
		# print m.values()[0]

		# create mass function
		m_pyd = MassFunction(m.values()[0])
		self.m_dict[m.keys()[0]] = m_pyd
		if show:
			print "mass %s added ===>" % m.keys()[0], m_pyd

	def drc_comb(self, dict_names):
		"""
		use DRC to combine the mass function from several resources,
		as indicated by each name in dict_names
		we use the element e in dict_names to query self.m_dict[e]
		to find the corresponding mass function
		at the end, DRC will be used to create 1 mass funcation which
		combines confidences from all the dict_names mass functions
		"""
		for name in dict_names:
			if name not in self.m_dict:
				print "Invalid mass names!"
				return

		n = len(dict_names)
		if n < 2:
			print "Invalid mass numbers!"
			return
		m_comb = self.m_dict[dict_names[0]] & self.m_dict[dict_names[1]]
		# print '#################'
		# print self.m_dict
		# print '----------------'
		# print m_comb
		for i in range(2,n):
			m_comb = m_comb & self.m_dict[dict_names[i]]
		return m_comb

	def vote(self, m):
		"""
		make a decision to select the label of the class which has the largest
		mass function.
		"""
		maxv = -1
		maxlabel = 0
		for key in m:
			if m[key] >= maxv:
				maxv = m[key]
				maxlabel = key
		return maxlabel

	def vote_knn(self,m):
		"""
		make a decision based on knn
		"""
		maxv = -1
		maxlabel = 0
		neigh = NearestNeighbors(2, metric='')

if __name__ == '__main__':
	dst = DST()
	# each row in m represents a voter, in total 5 voters (m0~m4)
	# the four columns represent the four labels (a,b,c,d)
	# each row does not have to sum to 1
	# we will normalize them later
	n = \
	[
	[0.1, 0.42,0.3,0.1],
	[0.2, 0.36, 0.2, 0.05],
	[0.15, 0.41, 0.4, 0.09],
	[0.1, 0.33, 0.2, 0.12],
	[0.2, 0.25, 0.2, 0.25],
	]

	m = np.copy(np.array(n))

	for i in range(len(m)):
		m[i,:] = m[i,:] / np.sum(m[i,:])

	# add the mass from the 5 voters
	for i in range(5):
		dst.add_mass({'m'+str(i): {'a':m[i,0], 'b':m[i,1], 'c': m[i,2], 'd':m[i,3]}})

	# print dst.m_dict

	# use DRC to combine votes from the 5 voters
	m_comb = dst.drc_comb(['m0', 'm1', 'm2', 'm3', 'm4'])
	print "Combined mass using DRC ===> ", m_comb

	# vote is to select the label with the largest mass
	y_pred = dst.vote(m_comb)
	print "y_pred: %s" % y_pred

	# print '#######################'
	dst2 = DST()
	dst2.predict(m)
	# print dst2.m_dict
