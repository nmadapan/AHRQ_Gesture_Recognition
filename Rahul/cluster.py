import numpy as np 
import glob,os 

# removing files which are not in log file
#firstly, remove all the log files for which we don't have openpose files



base_path='/Rahul/AHRQ/'
pose_annot='Results'
annot_files='Annotations'

skel_folders=glob.glob(os.path.join(base_path,pose_annot,"*"))
annot_files=glob.glob(os.path.join(base_path,annot_files,"*"))	


#remving the pose files from all the folders
for fold in skel_folders:
	files=os.listdir(fold)
	for file in files:
		if file[-8:-4]=='pose':
			print(file)
			os.remove(os.path.join(fold,file))



#removing the files which are not in the log files 
for fold in skel_folders:
	fold_files=os.listdir(fold)
	for file in annot_files:
		if fold[20:23]==file[24:27]:
			# print(fold,file)
			f=open(file,'r')
			nums=f.read()
			# nums=nums.strip().replace('\n',' ')
			# nums = list(map(int, nums))
			# print(nums)	

for k in nums:
	print(k)


# f=open(annot_files[1],'r')
# print(f.read())

# for i in range(len(annot_files)):
# 	print(annot_files[i])