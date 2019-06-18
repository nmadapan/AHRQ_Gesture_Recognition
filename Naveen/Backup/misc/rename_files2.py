from os.path import join
from glob import glob
from os import rename
from os.path import basename, dirname
from copy import deepcopy
from shutil import copyfile

base_path = r'G:\AHRQ\Study_IV\NewData2\Temp'
before = ['L6', '5_3']
after = ['L11', '10_1']

all_files_paths = glob(join(base_path, '*.*'))

for fpath in all_files_paths:
	nfpath = deepcopy(fpath)
	for idx in range(len(before)):
		nfpath = nfpath.replace(before[idx], after[idx])
	print fpath, nfpath
	rename(fpath, nfpath)

# base_path = r'G:\AHRQ\Study_IV\NewData2\Temp'
# before = 'Flip_Horizontal'
# after = 'X_Horizontal'
# all_files_paths = glob(join(base_path, '*.*'))
# for fpath in all_files_paths:
# 	fname = basename(fpath)
# 	fdir = dirname(fpath)
# 	fname_split_list = fname.split('_')
# 	prev_sub_id = int(float(fname_split_list[2][1:]))
# 	fname_split_list[2] = 'S' + str(prev_sub_id)
# 	nfpath = join(fdir, '_'.join(fname_split_list))
# 	rename(fpath, nfpath)

# for fpath in all_files_paths:
# 	if before in fpath:
# 		n_fpath = fpath.replace(before, after)


# for fpath in all_files_paths:
# 	if()
# 	n_fpath = fpath.replace('S3', 'S8')
# 	rename(fpath, n_fpath)