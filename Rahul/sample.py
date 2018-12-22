from shutil import copy
import glob,os

read_path = r'F:\a'
write_path = r'F:\b'

files = glob.glob(os.path.join(read_path,'*'))

for file in files:
	copy(file,write_path)