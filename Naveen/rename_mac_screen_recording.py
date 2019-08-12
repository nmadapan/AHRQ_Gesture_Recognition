from __future__ import print_function
import os
from os.path import join
from os import rename
import time

fname = 'screen.mp4'
dirname = '/Users/gonza337/Desktop/study_v_screen_recordings'

while True:
	try:
		print('. ', end = '')
		files = os.listdir(dirname)
		if fname in files:
			ts = str(int(os.path.getctime(join(dirname,fname))))
			new_name = fname.split('.')[0] + '_' + ts + '.mp4'
			os.rename(join(dirname, fname), join(dirname,new_name))
			print('\nRenamed: ', fname, new_name)
		time.sleep(4)
	except KeyboardInterrupt:
		print('Exiting !!')
		break
	except Exception as exp:
		print(exp)
		time.sleep(4)
		pass
		