import numpy as np
import json
from helpers import *

# with open('commands.json', 'r') as fp:
# 	data = json.load(fp)

# print json_to_dict('param.json')

class New:
	def __init__(self):
		self.update()

	def update(self):
		data = json_to_dict('param.json')
		for key, value in data.items():
			setattr(self, key, value)

	def print_stuff(self):
		print self.dim_per_joint
		print self.all_flag
		print self.feature_types

inst = New()
inst.print_stuff()
