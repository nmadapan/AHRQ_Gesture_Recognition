import numpy as np

def func(a):
	global b
	b = 2

global b
b = 5
func(3)
print b