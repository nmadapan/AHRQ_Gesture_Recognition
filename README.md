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
