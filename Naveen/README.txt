File naming convention:
	PascalCase: classes
		Ex: KinectReader.py and XefParser.py
	snake_case: scripts
		Ex: autogui_xef_parser.py

KinectReader.py
	* Base CLASS for connecting to Kinect Studio or actual Kinect

XefParser.py
	* Base CLASS for parsing the XEF files into RGB, Depth and Skeletal data from Kinect stream
	* This expects you to manually open the Kinect Studio

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