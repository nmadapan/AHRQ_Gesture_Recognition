from helpers import *
import numpy as np

a = [1, 2, 3]
b = [1, 2, 3]
c = [1, 2, 3]

print zip(a, b, c)

# class Hello:
# 	def __init__(self):
# 		pass

# 	def create_vars(self, filepath):
# 		try:
# 			with open(filepath, 'r') as fp:
# 				lines = fp.readlines()
# 				for line in lines:
# 					line = line.strip()
# 					if(len(line) == 0): continue
# 					if(line[0] == '#'): continue
# 					words = line.split('=')
# 					assert len(words)==2, 'Error! params.txt'
# 					words = [word.strip() for word in words]
# 					setattr(self, words[0], float(words[1]))
# 		except Exception as exp:
# 			print exp

# h = Hello()
# h.create_vars('param.txt')
# # print h.hello, h.abc