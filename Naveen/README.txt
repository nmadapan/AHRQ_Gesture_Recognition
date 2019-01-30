How to run the realtime code: 

* Make sure that following are connected:
	1. Kinect V2
	2. AHRQ Drive V (G:)

1. Without fingers:
	* Training a classifier
		- For new subjects, run python run_svm.py
		- For old subjects, run python run_svm_new.py (make sure to change the subject id that you wanna eliminate.)
		- This will generate the pickle files containing the trained SVM classifier and instance variables. 
		- In each file set the following flags:
			* ENABLE_FINGERS - False
			* LEXICON_ID - appropriate lexicon id. For instance, 'L8'
			* TASK_ID - appropriate task id. For instance, 1 or 2
			* ELIMINATE_SUBJECT_ID - appropriate subject ID. For instance, 'S2'
	* Run real time code
		- python realtime_main.py
			* In each file set the following flags:
				- IP_SYNAPSE: IP of MAC Synapse computer
				- PORT_SYNAPSE: Port of MAC Synapse computer
				- ENABLE_SYNAPSE_SOCKET: If True, enable the synapse socket. 
				- ENABLE_CPM_SOCKET: If False, disable the fingers in feature computation. 
				- LEXICON_ID: Appropriate lexicon ID: For instance "L8"

2. With fingers:
	* Anaconda setup
		- Open 'Anaconda Navigator' in Windows computer. 
		- Click 'Environments'
		- Select the following virtual environment 'tensorflow'
		- Click the 'Play' button next to 'tensorflow' and open the terminal.
	* Training a classifier
		- For new subjects, run python run_svm.py
		- For old subjects, run python run_svm_new.py (make sure to change the subject id that you wanna eliminate.)
		- This will generate the pickle files containing the trained SVM classifier and instance variables. 
		- In each file set the following flags:
			* ENABLE_FINGERS - True
			* LEXICON_ID - appropriate lexicon id. For instance, 'L8'
			* TASK_ID - appropriate task id. For instance, 1 or 2
			* ELIMINATE_SUBJECT_ID - appropriate subject ID. For instance, 'S2'
	* Run real time code
		- python realtime_main.py
			* In each file set the following flags:
				- IP_SYNAPSE: IP of MAC Synapse computer
				- PORT_SYNAPSE: Port of MAC Synapse computer
				- ENABLE_SYNAPSE_SOCKET: If True, enable the synapse socket. 
				- ENABLE_CPM_SOCKET: If True, enable the fingers in feature computation. 
				- LEXICON_ID: Appropriate lexicon ID: For instance "L8"

Requirements:
	1. Add kinectstudio to the Path:
		Go to to the installation path of kinect studio,
		it will look something like: C:\Program Files\Microsoft SDKs\Kinect\v2.0_1409\Tools\KinectStudio.
		And add that directory to the system enviroment variable called PATH


File naming convention:
	PascalCase: classes
		Ex: KinectReader.py and XefParser.py
	snake_case: scripts
		Ex: autogui_xef_parser.py

Formats:
	1. skeleton text file
		* It is a space separated file
		* No. of rows equal to no. of frames in the xef file
		* No. of numbers in each row is 75 --> (25 {Joints of Kinect} x 3 {x, y, z}) --> [x1, y1, z1, x2, y2, z2, ...]
	2. RGB Video file
		* It is a .avi file
	3. Depth Video file
		* It is a .avi file
	4. Annotation text file
		* Each row contains the frame number of either start or end of the gesture
		* It has only one number in each row. 
		* Start frame ID followed by end frame ID and so on
		* No. of rows are equal to twice the number of gesture instances present in the skeleton file
	5. Skeleton points on RGB text file
		* It is a space separated file consisting of pixel positions of Kinect joints on the RGB video
		* No. of rows equal to no. of frames in the xef file
		* No. of numbers in each row is 50 --> (25 {Joints of Kinect} x 2 {x, y}) --> [x1, y1, x2, y2, ...]		
	6. Skeleton points on Depth text file
		* It is a space separated file consisting of pixel positions of Kinect joints on the Depth video
		* No. of rows equal to no. of frames in the xef file	
		* No. of numbers in each row is 50 --> (25 {Joints of Kinect} x 2 {x, y}) --> [x1, y1, x2, y2, ...]		

KinectReader.py
	* Base CLASS for connecting to Kinect Studio or actual Kinect

XefParser.py
	* Base CLASS for parsing the XEF files into RGB, Depth and Skeletal data from Kinect stream
	* This expects you to manually open the Kinect Studio

FeatureExtractor.py
	* Base CLASS for creating feature vectors from skeleton files and annotation files

autogui_xef_parser.py
	* SCRIPT for automatically opening the kinect studio and parse the data, given the path to the XEF file

batch_autogui_xef_parser.py
	* SCRIPT for automatically BATCH processing multiple XEF files and parsing the data

create_automatic_annotations.py
	* Given the path to the skeleton data text file, this SCRIPT automatically creates the annotations (start and end frame ID of each gesture instance)

batch_create_automatic_annotations.py
	* BATCH processes multiple skeleton data text files and this SCRIPT creates automatic annotations for them. 

verify_annotations.py
	* Given the RGB video and annotations text file, this SCRIPT splits the video based on the annotations. 

annotate_video.py
	* This SCRIPT allows you to create the annotations MANUALLY by clicking the RGB video

generate_features.py
	* This SCRIPT explains how to use FeatureExtractor class

Logfiles
	* This folder contains the log files containing num_images, fps, video_time of each xef file. This will help debug later on.

Params.json
	- max_r: max lenth of the entire arm (meters)
	- max_dr: speed of the hand (m/frame)
	- max_th: max differece between the theta_t and theta_t+1 where theta_t is the angle made by dx,dy of the hand trayectory
	- max_dth: max change in angle that can happen
	- all_flag: use all posible feature types. When false, the user must specify in "feature types" the features that will be used.
	- feature_types: features to use (if all flag is False)
	- num_joints: number of joints to consider (1: just the hand, 2: hand and elbow)
	- dominant_first: when True, the hand with more motion will be placed first in the features.
	- dominant_first_thresh: the threshold for considering a hand dominant over the other.
	- dim_per_joint: 3 by default (x,y,z). Can be specified in the range of 1-3.
	- randomize: randomize the order of the instances (gesture samples)
	- equate_dim: make the dimention of the feature space the same for all samples
	- fixed_num_frames: fixed number of features to use in the equate dimention option when set to True.
	- lengths_per_frame: number of finger lenths to consider (comming from open pose)
	- openpose_downsample_rate: downsampling rate for open-pose processing.