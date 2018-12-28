"""
DON'T use this file if gestures(folders to be written) are not recorded in the sequence 
"""

import os,sys
import glob

#Enter the paths: from(read) and to(write) folder
base_path_read = r'E:\AHRQ\Study_IV\XEF_Files'
base_path_write = r'G:\AHRQ\Study_IV\XEF_Files'
read_folder = 'S11_L8'
write_folder = 'S12_L8'

#files in the read folder are sorted based on gestures id(1_1,2_1 etc)
#files in write_folder are sorted based on time of the files creation.

read_file_path = os.path.join(base_path_read,read_folder)
write_file_path = os.path.join(base_path_write,write_folder)

# if os.stat(read_file_path).st_ctime > os.stat(write_file_path).st_ctime:
# 	sys.exit('write folder was created before read_folder')

if read_folder.split('_')[1]!=write_folder.split('_')[1]:
	sys.exit('Read and Write lexicons are different. This code will not work if the lexicons are different')

if len(os.listdir(read_file_path))!=len(os.listdir(write_file_path)):
	sys.exit('number of files in To and From folders are different')

read_file_names=os.listdir(read_file_path)
read_file_ids=[]

for file in read_file_names:
	read_file_ids.append(int(file.split('_')[0]+file.split('_')[1]))

zipped= zip(read_file_ids,read_file_names)
zipped.sort(key = lambda t: t[0])
sorted_gestures = list(zip(*zipped)[1])
gestnames_towrite=[gesture.replace(read_folder.split('_')[0],write_folder.split('_')[0]) for gesture in sorted_gestures]

write_files=glob.glob(os.path.join(write_file_path,"*"))
file_ctime=[]
fname=[]
for file in write_files:
	file_ctime.append(os.stat(file).st_ctime)
	fname.append(file)

zipped_wfolders=zip(file_ctime,fname)
zipped_wfolders.sort(key = lambda t: t[0])
sorted_wfold = list(zip(*zipped_wfolders)[1])

for i in range(len(sorted_wfold)):
	os.rename(sorted_wfold[i],os.path.join(write_file_path,gestnames_towrite[i]))
	# print sorted_wfold[i],os.path.join(write_file_path,gestnames_towrite[i])

