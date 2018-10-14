# Gesture Recognition Sytem

## Description

## Table of Contents

   * [System Requirements](#system-requirements)
   * [Installation](#installation)
   * [Installation Hacks](#installation-hacks)

## System Requirements

1. Windows 10
2. Python 2.7
3. Microsoft Kinect V2 Sensor

## Installation

1. [Install Kinect for Windows SDK 2.0](https://www.microsoft.com/en-us/download/details.aspx?id=44561)
2. Install Kinect wrapper for python - [pykinect2](https://github.com/Kinect/PyKinect2.git). Enter the following on your terminal.

```
$ pip install pykinect2
```

3. Install [pyautogui](https://pyautogui.readthedocs.io/en/latest/install.html) - python wrapper to trigger clicks and keystrokes from code.

```
$ pip install pyautogui
```

4. Clone this repository. Enter the following on your terminal.

```
$ git clone https://github.com/nmadapan/AHRQ_Gesture_Recognition.git
```

## Installation Hacks

1. Add the following address to the path: *C:\Program Files\Microsoft SDKs\Kinect\v2.0_1409\Tools\KinectStudio*
2. Install [pykinect2](https://github.com/Kinect/PyKinect2.git) from **source** to ensure that you install the latest version.
3. Make sure to plug in the Kinect in USB 3.0 port.
4. In order to batch process XEF files, you need to take the images from *Kinect Studio V2.0*. Open *Kinect Studio V2.0* by entering **kstudio** on your terminal. You can find the images in *AHRQ_Gesture_Recognition/Naveen/Images*
