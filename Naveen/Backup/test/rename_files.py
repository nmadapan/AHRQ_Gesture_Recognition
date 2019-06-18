from glob import glob
from os.path import join, basename, dirname, splitext
from os import rename
from shutil import copyfile

# txt_files = glob('.\\*.txt')
# for txt_file in txt_files:
# 	dname, full_fname = dirname(txt_file), basename(txt_file)
# 	fname, ext = splitext(full_fname)
# 	new_fname = fname + '_konelog' + ext
# 	rename(txt_file, join(dname, new_fname))


## Copy files
from_path = r'E:\AHRQ\AHRQ_Gesture_Recognition\Naveen\Backup\test'
to_path = r'G:\AHRQ\Study_IV\RealData'
check_str = '_konelog'

txt_files = glob(join(from_path, '*.txt'))
txt_files = [tfile for tfile in txt_files if check_str in tfile]
for txt_file in txt_files:
	dname, full_fname = dirname(txt_file), basename(txt_file)
	lex_name = full_fname.split('_')[1]
	dst_fpath = join(join(to_path, lex_name), full_fname)
	copyfile(txt_file, dst_fpath)
