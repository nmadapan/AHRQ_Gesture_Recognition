from __future__ import print_function
import os
import os.path
from os import rename
import time

fname = 'delete.mp4'
dirname = os.getcwd()

while True:
	try:
		print('. ', end = '')
		files = os.listdir(dirname)
		if fname in files:
			new_name = fname.split('.')[0] + '_' + str(int(os.path.getctime(fname))) + '.mp4'
			os.rename(fname, new_name)
		print('\nRenamed: ', fname, new_name)
		time.sleep(10)
	except KeyboardInterrupt:
		print('Exiting !!')
		break
	except Exception as exp:
		time.sleep(10)
		pass
		