# Gesture Recognition Sytem

## Table of Contents
   * [System Requirements](#system-requirements)
   * [Installation](#installation)
   * [Installation Hacks](#installation-hacks)
   * [How to Run](#how-to-run)

## Description
This project aims to develop realtime gesture recognition for browsing medical images in the operating room (OR). This system is developed to recognize dynamic hand gestures including the finger configurations.

Overall, it requires *two computers*.
1. **Main Computer**
	1. Windows 10.
	2. Install everything that is described in [*Installation*](#installation)
	3. This computer MUST have Nvidia GPU RAM >= 4.0 GB
2. **Synapse Computer**
	1. Medical image manipulation software known as *Synapse* runs in this computer.
	2. Install Python 2.7
	3. Install [pyautogui](https://pyautogui.readthedocs.io/en/latest/install.html).
	4. Install [OpenCV](https://docs.opencv.org/3.3.1/d5/de5/tutorial_py_setup_in_windows.html) and [Pillow](https://pypi.org/project/Pillow/2.2.1/).

## System Requirements
1. Microsoft Kinect V2 Sensor
2. Windows 10
3. Python 2.7
4. Python 3.6

## Installation
1. [Install Kinect for Windows SDK 2.0](https://www.microsoft.com/en-us/download/details.aspx?id=44561)
2. Install Kinect wrapper for python - [pykinect2](https://github.com/Kinect/PyKinect2.git). Enter the following on your terminal. It works only with python 2.7.
```
$ pip install pykinect2
```
3. Install [pyautogui](https://pyautogui.readthedocs.io/en/latest/install.html) - python wrapper to trigger clicks and keystrokes from code.
```
$ pip install pyautogui
```
4. Clone the following GIT repository - Convolutional Pose Machines [CPM](https://github.com/shihenw/convolutional-pose-machines-release.git)
```
$ git clone https://github.com/shihenw/convolutional-pose-machines-release.git
```
5. Install [tensorflow](https://www.tensorflow.org/install/) in a virtual environment. It requries python 3. You can use package manager such as [Anaconda](https://conda.io/docs/user-guide/install/windows.html) to create a virtual environment for python 3 and install tensor flow. For detailed instructions, follow this [link](https://medium.com/intel-student-ambassadors/installing-tensorflow-on-windows-with-anaconda-af6fa6280a4b)
```
$ pip3 install tensorflow
```
6. Clone this repository. Enter the following on your terminal.
```
$ git clone https://github.com/nmadapan/AHRQ_Gesture_Recognition.git
```

## Installation Hacks
1. Add the following address to the path: *C:\Program Files\Microsoft SDKs\Kinect\v2.0_1409\Tools\KinectStudio*
2. Install [pykinect2](https://github.com/Kinect/PyKinect2.git) from **source** to ensure that you install the latest version.
3. Make sure to plug in the Kinect in USB 3.0 port.
4. In order to batch process XEF files, you need to take the images from *Kinect Studio V2.0*. Open *Kinect Studio V2.0* by entering **kstudio** on your terminal. You can find the images in *AHRQ_Gesture_Recognition/Naveen/Images*

## Data Recording and Processing
### Step - 1: Record data using Kinect Studio v2.0

### Step - 2: Processing the .XEF files

### Step - 3: Creating annotations automatically

### Step - 4: Running a base SVM classifier

## How to Run
### Main Computer [Incomplete]
Open two terminals: one for python 2 and one for python 3.
1. On python 2 terminal, run the following:
```
$ python AHRQ_Gesture_Recognition/Naveen/realtime_main.py
```
2. Open the virtual environment where tensorflow is installed. Run the following:
```
$ py CPM/sample_recv_cpm.py
```

### Synapse Computer [Incomplete]
Run the following:
```
$ python AHRQ_Gesture_Recognition/Naveen/ex_server.py
```

## Miscellaneous information
Location of the surgeon data: G:\AHRQ\Study_IV\RealData

	File extensions:
		There are supposed to be a total of ten extensions.
		_color.txt
			* Color pixel coordintates of the body joints. Each row has 50 elements (x, y) for 25 joints.
		_depth.avi (Depth video from kinect)
		_rgb.avi (Color video from kinect)
		_depth.txt
			* Depth pixel coordintates of the body joints. Each row has 50 elements (x, y) for 25 joints.
		_rgbts.txt
			* time stamps of each frame in the RGB video.
		_skelts.txt
			* time stamps of each frame in the skeleton data.
		_skel.txt
			* Skeleton data. Each row has 75 elements. (x, y, z in meters) of 25 joints.
		_konelog.txt
			* You are not going to use this.
			* First kinect that is recognizing gestures. This file is recorded in GPU computer.
			* Each instance looks like the following:
				* ts,No. skel frames: _
				* ts,Size of skel inst: _ (size of the feature vector)
				* ts,Dom. hand: _ (If true, right hand is dominant. If False, left hand is dominant. )
				* ts,start_ts_gesture,end_ts_gesture,2_1,6_3,10_3,1_1,5_0,2_1,command name
		_ktwolog.txt
			* This file saves the log of the user actions when operating synapse
			* Each line corresponds to one gesture and it's corresponding action in synapse through the acnowledgement pad.
			* After One gesture is performed, 5 options are sent to the user. Then, those 5 options are 
			corrected to match the current task (in case one command is missing, it is added and if a command is not part of
			the task it is replaced by the commands that look the same that are part of the task). Finally, 
			the user selects one option out of the 5 and synapse automatically  performs that action using pyautogui. 
			* The fileformat is Sx_Ly_Tz, where Sx is the subject number x, Ly is the lexicon number y, and Tz is the
			Task number z. 
			* Each line (instance) has the following elements in this order:
				* Performend gesture initial timestamp (after any hand crossed the threshold). When the gesture begins
				* Performed gesture final timestamp (after both hands are under the threshold). When the gesture ends.
				* The five command options sent by the gesture recognition system.
				* The five command options after adjusting to the task.
				* The five command options after replacig adding or replacing the first option with similar 
				depending to context/modifier rules (the gestures that the command can be confused with).
				* Timestamp when the ackowledgement options appear.
				* Timestamp when the user selects an option in the acklowedgement pad.
				* Selected command (if empty, the user did not select any command).
				* Boolean indicating if the surgeon used the "More commands" option during the selection process.
				* Initial timestamp of the automatic synapse execution of the command.
				* Final timestamp of the atomatic synapse execution of the command.
			* Location of commands.json: *\AHRQ_Gesture_Recognition\Naveen\commands.json
		_screen.mov
			* Screen recording video file.
		status.json:
			* This is present in G:\AHRQ\Study_IV\RealData\status.json
