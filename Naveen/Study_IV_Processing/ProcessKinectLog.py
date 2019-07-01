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

import statsmodels.api as sm
import statsmodels.formula.api as smf

class ProcessKinectLog:
	def __init__(self, lex_paths, scores_npz_path, best_lex_names, worst_lex_names, cmds_path = 'redcued_commands.json', normalize = True):
		self.lex_paths = sorted(lex_paths, lex_path_cmp)
		self.vac_path = scores_npz_path
		self.best_lex_names = best_lex_names
		self.worst_lex_names = worst_lex_names
		self.cmds_dict = json_to_dict(cmds_path)
		self.cmd_names = sorted(self.cmds_dict.keys(), cmp = class_str_cmp)
		self.normalize = normalize

		## TODO: Initialize all command times to 0. Use all commands. If it doesnt exist use the one that is from the same group.

		## Verify if the paths are authentic.
		try:
			for lex_path in self.lex_paths:
				assert isdir(lex_path), lex_path + ' Directory not found'
			assert isfile(self.vac_path), self.vac_path + ' File not found'
		except Exception as exp:
			print(exp)
			sys.exit('Error !! Exiting. ')

		## Derived variables
		self.lex_names = [basename(lex_path) for lex_path in self.lex_paths]
		self.lex_ids = [int(basename(lex_path)[1:]) for lex_path in self.lex_paths]
		# print('Lexicon IDs: ', self.lex_ids)

		## Create dictionary representation
		self.av_keys = ['gest_time', 'init_cmds', 'fin_cmds', 'ack_time', 'selected_cmd', 'is_more_cmds', 'syn_time']
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
		self.vac_scores_dict = {}
		for lex_id, lex_name in zip(self.lex_ids, self.lex_names):
			self.vac_scores_dict[lex_name] = npz_dict['scores_reduced'][:, lex_id, :]
		self.vac_names = npz_dict['vacs']
		# print(npz_dict.keys())
		# print(npz_dict['reduced_cmd_ids'])

		## Updated by the call to process
		self.raw_data = None
		self.raw_dict = None

		# avg_time_dict, std_time_dict, freq_dict = self.compute_avg_time()
		# final_dict = self.combine_con_mod(avg_time_dict)

		self.process()

	def process(self):
		usa_time_dict = {} # Dictionary containing the time taken for each command
		for lex_name, lex_path in zip(self.lex_names, self.lex_paths):
			txt_files = glob(join(lex_path, '*_ktwolog.txt'))

			## Read data from the *_ktwolog.txt files
			raw_data = []
			for txt_file in txt_files:
				with open(txt_file, 'r') as fp:
					raw_data += [line.strip().split(',') for line in fp.readlines()]

			## Transform raw data into dictionary with the keys present in self.av_keys
			raw_dict = self.create_dict(raw_data)
			## Compute average time for each gesture in that lexicon
			avg_time_dict, std_time_dict, freq_dict = self.compute_avg_time(raw_dict)
			# print(lex_name, len(raw_dict))
			## Combine context and modifiers
			final_dict = self.combine_con_mod(avg_time_dict)
			# print('Before Len: ', len(final_dict))
			final_dict = self.complete_missing_keys(final_dict)
			# print('After Len: ', len(final_dict))

			# print(lex_name, len(final_dict))

			## Sort the keys based on commands ids
			keys = final_dict.keys()
			cmds = sorted(keys, cmp = class_str_cmp)
			cmds_time = []
			# print(lex_name, cmds)
			for key in cmds:
				cmds_time.append(final_dict[key])

			## This dictionary contains a key for lexicon id
			usa_time_dict[lex_name] = np.array(cmds_time)

		if(self.normalize):
			for cmd_idx, cmd_name in enumerate(self.cmd_names):
				cmd_times = np.array([usa_time_dict[lex_name][cmd_idx] for lex_name in self.lex_names])
				cmd_times = (cmd_times - np.min(cmd_times))/(np.max(cmd_times) - np.min(cmd_times))
				for _idx, lex_name in enumerate(self.lex_names): usa_time_dict[lex_name][cmd_idx] = cmd_times[_idx]

		for idx, lex_name in enumerate(self.lex_names):
			print(lex_name)
			print(usa_time_dict[lex_name].shape)
			print(self.vac_scores_dict[lex_name].shape)

		vac_data, usa_data = self.combine_lexs(self.vac_scores_dict, usa_time_dict)

		results_ols = sm.OLS(usa_data, vac_data).fit()
		print(results_ols.summary())

		rlm_model = sm.RLM(usa_data, vac_data, M=sm.robust.norms.HuberT())
		rlm_results = rlm_model.fit()
		print(rlm_results.summary())

		# vac_idx = 5
		# cmd_idx = -1
		# markers = ['<', '>', 's', 'p']
		# colors = ['red', 'red', 'green', 'green']
		# plt.figure()
		# for idx, lex_name in enumerate(self.lex_names):
		# 	print(usa_time_dict[lex_name].shape, self.vac_scores_dict[lex_name][:, vac_idx].shape)
		# 	if(cmd_idx != -1):
		# 		plt.scatter(usa_time_dict[lex_name][cmd_idx], self.vac_scores_dict[lex_name][cmd_idx, vac_idx], marker = markers[idx], c = colors[idx])
		# 	else:
		# 		plt.scatter(usa_time_dict[lex_name][:], self.vac_scores_dict[lex_name][:, vac_idx], marker = markers[idx], c = colors[idx])
		# plt.legend(self.lex_names)
		# plt.xlabel('Time taken in seconds')
		# plt.ylabel('VAC ' + self.vac_names[vac_idx] + ' values')
		# plt.show()

	def combine_lexs(self, vac_dict, usa_dict):
		vac_data, usa_data = [], []
		for lex_idx, lex_name in enumerate(self.lex_names):
			vac_data += vac_dict[lex_name].tolist()
			usa_data += usa_dict[lex_name].tolist()
		vac_data = np.array(vac_data)
		usa_data = np.array(usa_data)
		return np.array(vac_data), np.array(usa_data)

	def create_dict(self, raw_data):
		raw_dict = {}
		for idx, line in enumerate(raw_data):
			raw_dict[idx] = {}
			for av_key, av_ids in zip(self.av_keys, self.av_ids):
				if(av_key in [self.gest_time_key, self.ack_time_key, self.syn_time_key]):
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
		print(ex_dict.keys())
		ex_dict2 = deepcopy(ex_dict)
		for key in self.cmd_names:
			if key not in ex_dict:
				print('Missing ', key)
				key_prefix = key.split('_')[0]
				for _key in ex_dict.keys():
					if key_prefix in _key:
						print('Replacing with ' + _key)
						ex_dict2[key] = ex_dict[_key]
						break

		ex_dict = deepcopy(ex_dict2)
		for key in ex_dict:
			if key in remove_keys:
				ex_dict2.pop(key, None)

		return ex_dict2

	def combine_con_mod(self, avg_time_dict):
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

if(__name__ == '__main__'):
	best_lex_names = ['L6', 'L8']
	worst_lex_names = ['L2', 'L3']
	base_path = r'G:\AHRQ\Study_IV\RealData'
	lex_names = ['L2', 'L6', 'L8', 'L3']
	lex_paths = [join(base_path, lex_name) for lex_name in lex_names]
	npz_path = r'scores.npz'
	pobj = ProcessKinectLog(lex_paths, npz_path, \
		best_lex_names = best_lex_names, worst_lex_names = worst_lex_names,\
		cmds_path = 'reduced_commands.json')

	temp = np.load('scores.npz')
	print(temp.keys())
