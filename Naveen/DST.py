#!/usr/bin/env python

'''
Install Instructions:
	* Open the command line
	* git clone https://github.com/reineking/pyds.git
	* cd pyds && python setup.py build && python setup.py install
'''

from __future__ import print_function
from pyds import MassFunction
import numpy as np
from sklearn.neighbors import NearestNeighbors
from copy import deepcopy
import time

class DST:
	"""
	the class of Dempster-Shafer Theory (DST)
	and Dempster's Rule of Combination (DRC)
	"""

	def __init__(self, num_models, num_classes, class_names = None, internal_cnames = None):
		'''
		Description:
			Note that the internal class names can only be a string of one charecter.
			So a workaround was made to isolate internal classes from actual class names.
			* internal class names are present in internal_cnames
			* actual class names are present in class_names
		Input arguments:
			* num_models: no. of models
			* num_classes: no. of classes
			* class_names: actual class names
			* internal_cnames: internal class names (cnames)
		Return:
			* self
		'''
		## a list of 52 single charecter strings. If no. of classes is more than 52,
			# internal_cnames can not be none.
		self.alphabets = np.array([chr(idx) for idx in range(97, 97+26)] + \
						[chr(idx) for idx in range(65, 65+26)])
		self.num_classes = num_classes
		self.num_models = num_models

		## Update ACTUAL class names
		if(class_names is None): class_names = map(str, range(num_classes))
		assert len(class_names) == num_classes, 'ERROR! No. of classes in class_names \
												should be equal to num_classes.'
		self.actual_cnames = deepcopy(class_names)

		## Update INTERNAL class names
		self.cnames = None
		if(self.num_classes > 52):
			if(internal_cnames is None):
				raise Exception('ERROR! If no. of classes are more than 52, internal_cnames can NOT be None. ')
			else:
				assert len(internal_cnames) == self.num_classes, \
							'The size of internal_cnames should be equal to num_classes'
				self.cnames = deepcopy(self.internal_cnames)
		else:
			self.cnames = self.alphabets[:self.num_classes]

		## Create dictionaries that map internal class names to external class names.
		self.dst_to_actual_cnames = dict(zip(self.cnames, self.actual_cnames))
		self.actual_to_dst_cnames = dict(zip(self.actual_cnames, self.cnames))

		## Update model names
		self.mnames = ['m'+str(ix) for ix in range(self.num_models)]

		self.m_dict = {}

	def predict(self, M):
		'''
		Description:
			Given the probability matrix M (num_models x num_classes),
			Predict the class label that have highest probability according to the DST.
		Input arguments:
			* M - 2D np.ndarray of size num_models x num_classes
		Return:
			* Index of the predicted label
			* Actual class name
		'''
		assert M.ndim == 2, 'Error! M should be a 2D np.ndarray.'
		assert self.num_models == M.shape[0], 'No. of rows in M should be equal to num_models'
		assert self.num_classes == M.shape[1], 'No. of columns in M should be equal to num_classes'

		## Clone and normalization
		M = np.copy(M)
		M = (M.transpose() / np.sum(M, axis = 1)).transpose()

		## Format w.r.t DST
		for mname, mprobs in zip(self.mnames, M):
			self.add_mass({mname: dict(zip(self.cnames, mprobs))})
		m_comb = self.drc_comb(self.mnames)

		## vote is to select the label with the largest mass
		y_pred = list(self.vote(m_comb))
		if(len(y_pred) > 1):
			print('More than one class predicted. Picking the first class')
			print('Predicted classes: ', y_pred)

		## Pick the first class label
		y_pred = y_pred[0]
		y_pred, = np.where(self.cnames == y_pred)

		if(self.actual_cnames is not None):
			return y_pred[0], self.actual_cnames[y_pred[0]]
		else:
			return y_pred[0], None

	def add_mass(self, m, show=0):
		"""
		m is a dict of {name: mass_function}
		mass_function = {'class1':weight1, 'class2': weight2, ...}
		"""

		## create mass function
		m_pyd = MassFunction(m.values()[0])
		self.m_dict[m.keys()[0]] = m_pyd
		if show:
			print("mass %s added ===>" % m.keys()[0], m_pyd)

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
				print("Invalid mass names!")
				return
		n = len(dict_names)
		if n < 2:
			print("Invalid mass numbers!")
			return
		m_comb = self.m_dict[dict_names[0]] & self.m_dict[dict_names[1]]
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

if __name__ == '__main__':
	## Parameters
	num_classes = 4
	num_models = 5
	class_names = ['class_1', 'class_2', 'class_3', 'class_4']

	## Example probability matrix
	# Each row in m represents a voter, in total 5 voters (m0~m4)
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

	## Method - 1 ==> Conventional
	print('<---- Method 1 ------>')
	dst = DST(num_models = num_models, num_classes = num_classes, class_names = class_names)
	## Normalization
	for i in range(len(m)): m[i,:] = m[i,:] / np.sum(m[i,:])
	## add the mass from the 5 voters
	for i in range(5):
		dst.add_mass({'m'+str(i): {'a':m[i,0], 'b':m[i,1], 'c': m[i,2], 'd':m[i,3]}})
	## use DRC to combine votes from the 5 voters
	m_comb = dst.drc_comb(['m0', 'm1', 'm2', 'm3', 'm4'])
	# print("Combined mass using DRC ===> ", m_comb)
	## vote is to select the label with the largest mass
	y_pred = dst.vote(m_comb)
	print("Method 1 - y_pred: %s" % y_pred)

	## Method - 2 ==> Conventional
	print('\n<---- Method 2 ------>')
	dst2 = DST(num_models = num_models, num_classes = num_classes, class_names = class_names)
	y_pred, actual_cname = dst2.predict(m)
	print("y_pred: %s <==> %s" % (y_pred, actual_cname))

	## Random Experiment
	print('\n<---- Random experiment -----> ', end = '')
	num_models = 4
	num_classes = 40
	print('No. of models = {0}, No. of classes = {1}'.format(num_models, num_classes))
	start = time.time()
	dst3 = DST(num_models = num_models, num_classes = num_classes)
	y_pred, actual_cname = dst3.predict(np.random.uniform(0, 1, (num_models, num_classes)))
	print('Time taken: {:.04f} seconds.'.format(time.time()-start))
	print("Prediction: class index = %s, class label = %s" % (y_pred, actual_cname))
