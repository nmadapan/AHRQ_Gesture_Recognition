from __future__ import print_function
from os.path import join
from glob import glob
from os import rename
from os.path import basename, dirname, join, isfile, isdir
from copy import deepcopy
from shutil import copyfile
import cv2
import sys
import json
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import r2_score
from helpers import *

import warnings
warnings.filterwarnings("ignore", category = Warning)

import statsmodels.api as sm
import statsmodels.formula.api as smf

from scipy.stats import linregress
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import KFold, GridSearchCV

class ProcessKinectLog:
	def __init__(self, lex_paths, scores_npz_path, best_lex_names, \
				worst_lex_names, cmds_path = 'reduced_commands.json', normalize = True, debug = False):
		self.lex_paths = sorted(lex_paths, lex_path_cmp)
		self.vac_path = scores_npz_path
		self.best_lex_names = best_lex_names
		self.worst_lex_names = worst_lex_names
		self.cmds_dict = json_to_dict(cmds_path)
		self.cmd_names = sorted(self.cmds_dict.keys(), cmp = class_str_cmp)
		# If True, then the usability scores are normalized w.r.t each command. 
		self.normalize = normalize
		# If True, there will be a lot of printing. 
		self.debug = debug
		self.method = None # Updated by the call to process()
		self.model = None # Updated by the call to regress()

		## Verify if the paths are authentic.
		try:
			for lex_path in self.lex_paths:
				assert isdir(lex_path), lex_path + ' Directory not found'
			assert isfile(self.vac_path), self.vac_path + ' File not found'
		except Exception as exp:
			print(exp)
			sys.exit('\nError !! Exiting. ')

		## Derived variables
		self.lex_names = [basename(lex_path) for lex_path in self.lex_paths]
		self.lex_ids = [int(basename(lex_path)[1:]) for lex_path in self.lex_paths]
		if(self.debug): print('Lexicon IDs: ', self.lex_ids)

		## Create dictionary representation
		self.av_keys = ['gest_time', 'init_cmds', 'fin_cmds', 'ack_time', \
						'selected_cmd', 'is_more_cmds', 'syn_time']
		## HARD CODED !!!
		self.av_ids = [(0, 1), (2, 2+5), (12, 12+5), (17, 18), 19, 20, (21, 22)]
		self.gest_time_key = 'gest_time'
		self.init_cmds_key = 'init_cmds'
		self.fin_cmds_key = 'fin_cmds'
		self.ack_time_key = 'ack_time'
		self.selected_cmd_key = 'selected_cmd'
		self.is_more_cmds_key = 'is_more_cmds'
		self.syn_time_key = 'syn_time'
		assert len(self.av_keys) == len(self.av_ids), 'av_keys and av_ids should have same length'

		## Reading the npz file
		npz_dict = np.load(self.vac_path)
		self.all_vac_scores = npz_dict['scores_reduced']
		self.vac_scores_dict = {}
		for lex_id, lex_name in zip(self.lex_ids, self.lex_names):
			# lex_id starts from one. so substracting one. 
			self.vac_scores_dict[lex_name] = self.all_vac_scores[:, lex_id-1, :]
		self.vac_names = npz_dict['vacs']
		if(self.debug): 
			print('Information related to npz dict')
			print('Keys: ', npz_dict.keys())
			print('Reduced command IDs: ', npz_dict['reduced_cmd_ids'])

	def custom_normalize(self, usa_dict):
		'''
		Description:
			Normalize w.r.t the command. 
		Input arguments:
			usa_dict - dictionary
			{'L2': [1D np.array of 20 values], 'L3': [list of 20 values], ...}
		'''
		usa_dict = deepcopy(usa_dict)
		for cmd_idx, cmd_name in enumerate(self.cmd_names):
			cmd_arr = np.array([usa_dict[lex_name][cmd_idx] for lex_name in self.lex_names])
			cmd_arr = (cmd_arr - np.min(cmd_arr))/(np.max(cmd_arr) - np.min(cmd_arr))
			for _idx, lex_name in enumerate(self.lex_names): usa_dict[lex_name][cmd_idx] = cmd_arr[_idx]
		return usa_dict

	def regress(self, X1, X2, method = 'ols', train_per = 0.8):
		'''
			Description:
				regress(y, X)
		'''
		## Update class variables
		self.method = method

		## Randomization
		perm = np.random.permutation(X1.size)
		K = int(train_per * X1.size)
		tr_x, tr_y = X2[:K,:], X1[:K]
		ts_x, ts_y = X2[K:,:], X1[K:]

		self.train(tr_x, tr_y)
		pred_tr_y = self.predict(tr_x)
		tr_mse, tr_r2, _ = self.get_reg_scores(tr_y, pred_tr_y)
		pred_wh_y = self.predict(X2)
		wh_mse, wh_r2, _ = self.get_reg_scores(X1, pred_wh_y)
		pred_ts_y = self.predict(ts_x)
		ts_mse, r2, adj_r2 = self.get_reg_scores(ts_y, pred_ts_y)

		print('Whole R2 =', wh_r2, 'Whole MSE = ', wh_mse, 'Test MSE =', ts_mse)

	def train_ols_rlm_lstsq(self, X, y, num_folds = 5):
		kf = KFold(n_splits = num_folds, shuffle = True)
		mse_list = []
		model_list = []
		for train_idx, valid_idx in kf.split(X):
			tr_x, tr_y = X[train_idx], y[train_idx]
			va_x, va_y = X[valid_idx], y[valid_idx]
			if(self.method == 'ols'):
				res = sm.OLS(tr_y, tr_x).fit()
				pred_va_y = np.dot(va_x, res.params)
			elif(self.method == 'rlm'):
				res = sm.RLM(tr_y, tr_x, M = sm.robust.norms.HuberT()).fit()
				pred_va_y = np.dot(va_x, res.params)
			elif(self.method == 'lstsq'):
				res = np.linalg.lstsq(tr_x, tr_y, rcond = None)[0]
				pred_va_y = np.dot(va_x, res)
			va_mse, va_r2, _ = self.get_reg_scores(va_y, pred_va_y)
			mse_list.append(va_mse)
			model_list.append(res)
		print('MSE: ', mse_list)
		min_idx = np.argmin(mse_list)
		self.model = model_list[min_idx]

	def train_svr(self, X, y, num_folds = 5):
		## SVR hyperparameters
		parameters = {'C': (1, 10, 100, 1000), \
				'degree': (1, 2, 3, 4, 5)}
		svr = SVR(kernel = 'poly', gamma = 'scale')
		clf = GridSearchCV(svr, parameters, cv = num_folds, refit = True)
		clf.fit(X, y)
		print(clf.best_params_)
		self.model = clf

	def train_dt(self, X, y, num_folds = 5):
		parameters = {'max_depth': (2, 3, 4, 5)}
		dtr = DecisionTreeRegressor()
		clf = GridSearchCV(dtr, parameters, cv = num_folds, refit = True)
		clf.fit(X, y)
		print(clf.best_params_)
		self.model = clf

	def train(self, X, y):
		if(self.method in ['ols', 'rlm', 'lstsq']):
			self.train_ols_rlm_lstsq(X, y)
		elif(self.method == 'svr'):
			self.train_svr(X, y)
		elif(self.method == 'dt'):
			self.train_dt(X, y)
		else:
			sys.exit('Error! Wrong model name')

	def predict(self, X):
		if(self.method in ['ols', 'rlm']):
			return np.dot(X, self.model.params)
		elif(self.method == 'lstsq'):
			return np.dot(X, self.model)
		elif(self.method in ['svr', 'dt']):
			return self.model.predict(X)
		else:
			sys.exit('Error! Wrong model name')

	def find_best_lexicon(self):
		res = []
		for lex_id in range(self.all_vac_scores.shape[1]):
			X = self.all_vac_scores[:,lex_id,:]
			res.append(self.predict(X))
		res = np.array(res).T
		# print(res)
		print(1 + np.argmin(res, axis = 1))

	def get_reg_scores(self, y_true, y_pred, dof = 6):
		r2 = r2_score(y_true, y_pred)
		N = y_true.size
		adj_r2 = 1 - (1 - r2) * ((N-1)/(N-dof-1))
		mse = np.mean((y_true - y_pred)**2)
		return np.round(mse, 4), np.round(r2, 2), np.round(adj_r2, 2)

	def combine_lexs(self, data_dict):
		'''
		Description:
		Input arguments:
			data_dict - dictionary
			{'L2': [1D np.array of 20 values], 'L3': [list of 20 values], ...}
		Return: 
			Concatenating those 1D np.array s together. Returns a list of 80 values. 
		'''		
		data = []
		for lex_idx, lex_name in enumerate(self.lex_names):
			data += data_dict[lex_name].tolist()
		data = np.array(data)
		return data

	def create_fslog_dict(self, raw_data):
		'''
		Input arguments: raw_data
			list of sublists. Each sublist contains the values present in each row of _annotfs*.txt or _annote*.txt
		Return: dictionary
			{gesture_id: [True, False, ...], gesture_id: [True, False, ...]}
			True indicates the focus shift and False otherwise. 
		'''		
		raw_dict = {}
		for line in raw_data:
			if line[0] not in raw_dict: raw_dict[line[0]] = []
			raw_dict[line[0]] += [line[1] == 'Yes']
		return raw_dict

	def create_kstarlog_dict(self, raw_data):
		'''
		Input arguments: raw_data
			list of sublists. Each sublist contains the values present in each row of *_k*log.txt
		Return: dictionary
			{0: {av_key: value, av_key: value, ...}, 1: {av_key: value, av_key: value, ...}, ...}
		'''
		raw_dict = {}
		for idx, line in enumerate(raw_data):
			raw_dict[idx] = {}
			for av_key, av_ids in zip(self.av_keys, self.av_ids):
				if(av_key in [self.gest_time_key, self.ack_time_key, self.syn_time_key]):
					if(line[av_ids[0]] == 'None' or line[av_ids[1]] == 'None'):
						raw_dict[idx][av_key] = -1
					else:
						raw_dict[idx][av_key] = float(line[av_ids[1]]) - float(line[av_ids[0]])
				elif(av_key in [self.init_cmds_key, self.fin_cmds_key]):
					raw_dict[idx][av_key] = line[av_ids[0]:av_ids[1]]
				elif(av_key == self.selected_cmd_key):
					raw_dict[idx][av_key] = line[av_ids]
				elif(av_key == self.is_more_cmds_key):
					raw_dict[idx][av_key] = line[av_ids] == 'True'
				else:
					assert False, 'Error ! Invalid key ' + av_key
		return raw_dict

	def compute_fs(self, raw_dict):
		avg_fs_dict = {}
		std_fs_dict = {}
		freq_dict = {} # No. of times the gesture is used
		for key, value in raw_dict.items():
			avg_fs_dict[key] = np.mean(value)
			std_fs_dict[key] = np.std(value)
			freq_dict[key] = len(value)
		return avg_fs_dict, std_fs_dict, freq_dict

	def compute_avg_time(self, raw_dict):
		avg_time_dict = {}
		std_time_dict = {}
		freq_dict = {}
		for _, value in raw_dict.items():
			if(value[self.selected_cmd_key] not in avg_time_dict):
				avg_time_dict[value[self.selected_cmd_key]] = []
			avg_time_dict[value[self.selected_cmd_key]].append(value[self.gest_time_key])
		for key in avg_time_dict:
			freq_dict[key] = len(avg_time_dict[key])
			std_time_dict[key] = np.std(avg_time_dict[key])
			avg_time_dict[key] = np.mean(avg_time_dict[key])
		return avg_time_dict, std_time_dict, freq_dict

	def complete_missing_keys(self, ex_dict, remove_keys = ['10_1']):
		# print(ex_dict.keys())
		ex_dict2 = deepcopy(ex_dict)
		for key in self.cmd_names:
			if key not in ex_dict:
				if(self.debug): print('Missing ', key)
				key_prefix = key.split('_')[0]
				for _key in ex_dict.keys():
					if key_prefix == _key.split('_')[0]:
						if(self.debug): print('Replacing with ' + _key)
						ex_dict2[key] = ex_dict[_key]
						break

		ex_dict = deepcopy(ex_dict2)
		for key in ex_dict:
			if key in remove_keys:
				ex_dict2.pop(key, None)

		return ex_dict2

	def combine_con_mod(self, avg_time_dict):
		## Combine the context and mofidier usability indices.
		context_dict = {}
		modifier_dict = {}
		for key in avg_time_dict.keys():
			if(key.split('_')[-1] == '0'):
				context_dict[key] = avg_time_dict[key]
			else:
				modifier_dict[key] = avg_time_dict[key]

		for key in modifier_dict:
			con_key = key.split('_')
			con_key[-1] = '0'
			con_key = '_'.join(con_key)
			if(con_key in context_dict):
				modifier_dict[key] += context_dict[con_key]

		return modifier_dict

	def process(self, ext = '*_ktwolog.txt', flag = True, method = 'scipy'):
		usa_dict = {} # Dictionary containing the time taken for each command
		for lex_name, lex_path in zip(self.lex_names, self.lex_paths):
			txt_files = glob(join(lex_path, ext))

			## Read data from the *_ktwolog.txt files
			raw_data = []
			for txt_file in txt_files:
				with open(txt_file, 'r') as fp:
					raw_data += [line.strip().split(',') for line in fp.readlines()]

			## Transform raw data into dictionary with the keys present in self.av_keys
			if('log' in ext):
				raw_dict = self.create_kstarlog_dict(raw_data)
			elif('annot' in ext):
				raw_dict = self.create_fslog_dict(raw_data)
			## Compute average time for each gesture id in that lexicon
			# Gesture IDs are keys in the dict
			if('log' in ext):
				avg_dict, std_dict, freq_dict = self.compute_avg_time(raw_dict)
			elif('annot' in ext):
				avg_dict, std_dict, freq_dict = self.compute_fs(raw_dict)
			# print(lex_name, len(raw_dict))
			## Combine context and modifiers
			final_dict = self.combine_con_mod(avg_dict)
			# print('Before Len: ', len(final_dict))
			final_dict = self.complete_missing_keys(final_dict, remove_keys = ['10_1'])
			# print('After Len: ', len(final_dict))

			## Sort the keys based on commands ids
			keys = final_dict.keys()
			cmds = sorted(keys, cmp = class_str_cmp)
			cmds_arr = []
			# print(lex_name, cmds)
			for key in cmds:
				cmds_arr.append(final_dict[key])

			## This dictionary contains a key for lexicon id
			usa_dict[lex_name] = np.array(cmds_arr)

		if(self.normalize): 
			usa_dict = self.custom_normalize(usa_dict)
			## VAC Normalization is not making any difference.
			# self.vac_scores_dict = self.custom_normalize(self.vac_scores_dict)

		# for idx, lex_name in enumerate(self.lex_names):
		# 	print(lex_name)
		# 	print(usa_dict[lex_name].shape)
		# 	print(self.vac_scores_dict[lex_name].shape)

		vac_data = self.combine_lexs(self.vac_scores_dict)
		usa_data = self.combine_lexs(usa_dict)

		if(flag and self.normalize): usa_data -= 1

		# regress(y, X) # y is 1D np.ndarray. X is 2D np.ndarray
		# vac_data = np.random.uniform(0, 1, (80, 6))
		# usa_data = np.random.uniform(0, 1, (80, ))
		self.regress(usa_data, vac_data, method = method)
		self.find_best_lexicon()

		# vac_idx = 0
		# cmd_idx = -1
		# markers = ['<', '>', 's', 'p']
		# colors = ['red', 'red', 'green', 'green']
		# plt.figure()
		# for idx, lex_name in enumerate(self.lex_names):
		# 	print(usa_dict[lex_name].shape, self.vac_scores_dict[lex_name][:, vac_idx].shape)
		# 	if(cmd_idx != -1):
		# 		plt.scatter(usa_dict[lex_name][cmd_idx], self.vac_scores_dict[lex_name][cmd_idx, vac_idx], marker = markers[idx], c = colors[idx])
		# 	else:
		# 		plt.scatter(usa_dict[lex_name][:], self.vac_scores_dict[lex_name][:, vac_idx], marker = markers[idx], c = colors[idx])
		# plt.legend(self.lex_names)
		# plt.xlabel('Time taken in seconds')
		# plt.ylabel('VAC ' + self.vac_names[vac_idx] + ' values')
		# plt.show()

		return usa_data, vac_data

	# def save_plots(self, usa_data, vac_data, title = '', usa_name = ''):
	# 	sz = vac_data.shape[0]
	# 	for vac_idx, vac_name in enumerate(self.vac_names):
	# 		vac_arr = vac_data[:, vac_idx][:, np.newaxis]
	# 		self.regress(usa_data, vac_arr, method = method)
	# 		# plt.figure()
	# 		plt.scatter(usa_data[:sz/2], vac_arr[:sz/2], marker = '<', color = 'red')
	# 		plt.scatter(usa_data[sz/2:], vac_arr[sz/2:], marker = 's', color = 'green')
	# 		print(self.model.coef_)
	# 		plt.legend(['L2/3', 'L6/8'])
	# 		plt.xlabel(usa_name)
	# 		plt.ylabel('VAC ' + vac_name + ' values')
	# 		fname = join('results', '_'.join([usa_name, vac_name, method])+'.png')
	# 		plt.savefig(fname)

	def annotation_statistics(self):
		fs_exts = ['*annotfsa.txt', '*annotfsd.txt', '*annotfsn.txt']
		e_exts = ['*annotea.txt', '*annoted.txt', '*annoten.txt']
		names = ['Anirudh', 'Daniela', 'Naveen']
		for lex_name, lex_path in zip(self.lex_names, self.lex_paths):
			print(lex_name, ': ')
			for pname, fs_ext, e_ext in zip(names, fs_exts, e_exts):
				print('\t', pname)
				print('\t\tScreen:', len(glob(join(lex_path, '*screen.mov'))))
				print('\t\tFS:', len(glob(join(lex_path, fs_ext))))
				print('\t\tER:', len(glob(join(lex_path, e_ext))))

if(__name__ == '__main__'):
	best_lex_names = ['L6', 'L8']
	worst_lex_names = ['L2', 'L3']
	base_path = r'H:\AHRQ\Study_IV\RealData'
	lex_names = ['L2', 'L6', 'L8', 'L3']
	lex_paths = [join(base_path, lex_name) for lex_name in lex_names]
	method = 'svr'

	## scores.npz file has 'scores_reduced' key consisting of VAC data
	# for only 20 commands present in the reduced_commands.json file. 
	npz_path = r'scores.npz'
	pobj = ProcessKinectLog(lex_paths, npz_path, \
		best_lex_names = best_lex_names, worst_lex_names = worst_lex_names,\
		cmds_path = 'reduced_commands.json', normalize = True)

	print('Random test')
	tr_x = np.random.rand(80, 6)
	tr_y = np.random.rand(80)
	pobj.regress(tr_y, tr_x, method = method)

	## Combining THREE usability metrics
	print('Acutal Usability Metrics')
	print('Gesture Time')
	time_data, vac_data = pobj.process(ext = '*_kthreelog.txt', method = method)
	# pobj.save_plots(time_data, vac_data, usa_name = 'gesture_time', title = '')
	print('Focus Shifts')
	fs_data, _ = pobj.process(ext = '*_annotfs*.txt', method = method)
	# pobj.save_plots(fs_data, vac_data, usa_name = 'focus_shifts', title = '')
	print('Errors')	
	e_data, _ = pobj.process(ext = '*_annote*.txt', method = method)
	# pobj.save_plots(e_data, vac_data, usa_name = 'error_rate', title = '')

	# print(time_data.shape, vac_data.shape)
	# print(fs_data.shape)
	# print(e_data.shape)

	# ## Total usability data
	# # This would give 80 x 3 np.ndarray
	# usa_data = np.array([time_data, fs_data, e_data]).T
	# pobj.regress(usa_data, vac_data)

	# pobj.annotation_statistics()

	## Things that are worrying: 
	# 1. For these two settings (2,3,6,8) and (1,2,5,7), the R^2 is pretty good. 