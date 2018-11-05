import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import ImageGrab
from PIL import ImageChops
import signal
import sys
import math
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import json


class SynapseAction:
    def __init__(self, keyboard=True, calibrationPath = None):
        ####################
        ## autogui setup  ##
        auto.FAILSAFE = True
        auto.PAUSE = 0.25
        ####################

        # Get window sizes
        (self.width, self.height) = tuple(float(e) for e in auto.size())
        (self.nativeW, self.nativeH) = tuple(float(e) for e in ImageGrab.grab().size)
        self.scale = self.nativeW / self.width
        # Get the Synapse window
        (self.macH, self.viewer, self.prompt) = ((0, "\\\\Remote", "Command Prompt") if platform.system() == "Windows"
                else (44.0 * self.nativeW / 2880.0, "Citrix Viewer", "Terminal"))
        # Border around the window
        self.border = (20.0 * self.nativeW / 2880.0) + (4.0 * self.scale)
        self.boundBoxNoDash = (self.border, self.macH + self.border, self.nativeW - self.border, self.nativeH - self.border)
        # Get the path for the calibration file
        if calibrationPath is None:
            self.calibrationPath = "calibration" + "_".join(list(str(e) for \
                    e in [self.width, self.height, self.scale])).replace(".", "-") + ".txt"

        # Variables of the synapse window
        self.topBarHeight = None
        self.optionH = None
        self.rightHR = None
        self.rightPlus = None
        self.rightIcons = None
        self.rightOffset = None
        self.rightBoxW = None
        self.rightBoxH = None

        # Status of the system:
        self.status = {}

    # Closes/Minimizes every window and leaves active the windows
    # with the name "toOpen"
    def openWindow(self, toOpen):
            # Look into "start" command for Windows
            if (platform.system() == "Windows"):
                    window_names = auto.getWindows().keys()
                    for window_name in window_names:
                            auto.getWindow(window_name).minimize()
                            if (toOpen in window_name):
                                    xef_window_name = window_name
                    xef_window = auto.getWindow(xef_window_name)
                    xef_window.maximize()
            else: os.system("open -a " + toOpen.replace(" ", "\\ "))

    # Remove images generated in the process of running the program
    def removeImages(self):
            paths = [os.path.join("SCA_Images", "RightClick"), os.path.join("SCA_Images", "Window", "Closes"),
                    os.path.join("SCA_Images", "Window"), os.path.join("SCA_Images", "Layout"), os.path.join("SCA_Images")]
            for path in paths:
                    if (not os.path.exists(path)): continue
                    for file in os.listdir(path):
                            if file.endswith(".png"): os.remove(os.path.join(path, file))
            os.remove(self.calibrationPath)


    # Prompt notification if choosing to remove the images
    def removeImagesPrompt(self):
            self.openWindow(self.prompt)
            # TODO uncomment this line
            # (self.status["hold_action"], self.status["defaultCommand"], self.status["group1_command"]) = (None, None, None)
            f = open(self.calibrationPath, "w")
            f.write(json.dumps(self.status, indent=4, separators=(',', ': ')))
            f.close()
            while True:
                    ans = raw_input("Do you want to remove the images saved in the folder? (y/n)")
                    if (len(ans) == 1 and (ans.lower() == "y" or ans.lower() == "n")):
                            if ans.lower() == "y": self.removeImages()
                            break
                    else: print "Unrecognized request, please enter either 'y' or 'n'"
            print ""

    # Handles the killing signals of the class
    def signalHandler(self, sig, frame):
	self.removeImagesPrompt()
	sys.exit(0)

    def start(self):
        # set up the signal handler
        signal.signal(signal.SIGINT, self.signalHandler)

        while True:
            continue

if __name__ == "__main__":
    syn_action = SynapseAction()
    # Run the program
    syn_action.start()


