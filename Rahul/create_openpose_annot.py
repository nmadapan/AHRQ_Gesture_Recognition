import os, shutil

## Works only on Rahul's computer

exe_addr = '.\\bin\OpenPoseDemo.exe'
base_out_path = 'F:\Rahul\DropBox\Dropbox\AHRQ_Temp'

root_write_folder = os.path.join(base_out_path, 'Results')
if os.path.isdir(root_write_folder): shutil.rmtree(root_write_folder)
if not os.path.isdir(root_write_folder): os.mkdir(root_write_folder)

video_folders_path = os.path.join(base_out_path, 'Videos_SortBy_Commands_28')
video_folders = os.listdir(video_folders_path)

for vid_folder in video_folders:
	vid_folder_addr = os.path.join(video_folders_path, vid_folder)
	vid_names = os.listdir(vid_folder_addr)
	write_folder = os.path.join(root_write_folder, vid_folder)
	if not os.path.isdir(write_folder): os.mkdir(write_folder)

	print 'Processing :', vid_folder

	for vid_file in vid_names:
		print vid_file
		input_path = os.path.join(vid_folder_addr, vid_file)
		temp_write_folder = os.path.join(write_folder, vid_file[:-4])
		if not os.path.isdir(temp_write_folder): os.mkdir(temp_write_folder)

		system_str = exe_addr + ' --video '+ input_path + ' --write_keypoint_format ' + 'xml ' + \
					 ' --write_keypoint ' + temp_write_folder + ' --hand '
		# print system_str
		os.system(system_str)
