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