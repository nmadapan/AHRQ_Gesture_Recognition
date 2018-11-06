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
        self.status = {"prev_action": "", "panel_dim": [1, 1],
                "window_open": False, "active_panel": [1, 1],
                "rulers": {"len": 0}, "toUse": "Keyboard",
                "hold_action": None, "defaultCommand": None, "group1_command": None,
                "firstW": None, "firstH": None, "jumpW": None,"jumpH": None}

        # Command action list. The first row is an internal action list for self management

        self.actionList = [["Admin", "Quit", "Get Status", "Switch ToUse", "Reset"],
                ["Scroll", "Up", "Down"],
                ["Flip", "Horizontal", "Vertical"],
                ["Rotate", "Clockwise", "Counter-Clockwise"],
                ["Zoom", "In", "Out"],
                ["Switch Panel", "Left", "Right", "Up", "Down"],
                ["Pan", "Left", "Right", "Up", "Down"],
                ["Ruler", "Measure", "Delete"],
                ["Window", "Open", "Close"],
                ["Manual Contrast", "Increase", "Decrease"],
                ["Layout", "One-Panel", "Two-Panels", "Three-Panels", "Four-Panels"],
                ["Contrast Presets", "I", "II"]]


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
            (self.status["hold_action"], self.status["defaultCommand"], self.status["group1_command"]) = (None, None, None)
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

    def get_bbox(self, before, after, thresholds = None, draw = False):
            if (type(before) != type(after)):
                    return ValueError('before and after should have same type')
            if (isinstance(before, str)):
                    if (not os.path.isfile(before)):
                            sys.exit(before + ' does NOT exist')
                    if (not os.path.isfile(after)):
                            sys.exit(after + ' does NOT exist')
                    before = cv2.imread(before)
                    after = cv2.imread(after)
            elif (isinstance(before, np.ndarray)):
                    assert before.ndim == 3 and after.ndim == 3, 'before and after needs to be rgb arrays'
                    assert (before.shape[0] == after.shape[0]) and (before.shape[1] == after.shape[1]),\
                             'before and after arrays should be of same dimension'

            dif = cv2.cvtColor(np.uint8(np.abs(after - before)), cv2.COLOR_BGR2GRAY)
            _, dif = cv2.threshold(dif,127,255,0)

            x_sum = np.mean(dif, axis = 0)
            y_sum = np.mean(dif, axis = 1)

            if (thresholds == None):
                    x_thresh = np.mean(x_sum)
                    #y_thresh = x_thresh
                    y_thresh = np.mean(y_sum)
            else:
                    x_thresh = thresholds[0]
                    y_thresh = thresholds[1]

            x_sum, y_sum = x_sum > x_thresh, y_sum > y_thresh

            x1, x2 = np.argmax(x_sum), x_sum.size - np.argmax(np.flip(x_sum, 0)) - 1
            y1, y2 = np.argmax(y_sum), y_sum.size - np.argmax(np.flip(y_sum, 0)) - 1

            if (draw):
                    after = cv2.rectangle(after,(x1,y1),(x2,y2),(0,255,0),4)
                    cv2.imshow('Frame', cv2.resize(after, None, fx=0.5, fy=0.5))
                    cv2.waitKey(0)

            return (x1, y1, x2, y2)


    def resetPanelMoves(self):
            self.status["firstW"] = (float(self.width) / (float(self.status["panel_dim"][1]) * 2.0))
            self.status["firstH"] = (float(self.height) / (float(self.status["panel_dim"][0]) * 2.0))
            self.status["jumpW"] = (self.status["firstW"] * 2.0 if self.status["panel_dim"][1] != 1 else 0)
            self.status["jumpH"] = (self.status["firstH"] * 2.0 if self.status["panel_dim"][0] != 1 else 0)

    def moveToActivePanel(self):
            moveToX = self.status["firstW"] + (self.status["active_panel"][1] - 1) * (self.status["jumpW"])
            moveToY = self.status["firstH"] + (self.status["active_panel"][0] - 1) * (self.status["jumpH"])
            auto.moveTo(moveToX, moveToY)

    # Reset height of top bar and save it
    def resetTopBarHeight(self):
            self.moveToActivePanel()
            auto.click()
            ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.nativeH)).save(os.path.join("SCA_Images", "fullscreen.png"))
            auto.moveTo(auto.position()[0], 0)
            time.sleep(1)
            ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.nativeH)).save(os.path.join("SCA_Images", "afterTopBar.png"))
            topBarBox = self.get_bbox(os.path.join("SCA_Images", "fullscreen.png"), os.path.join("SCA_Images", "afterTopBar.png"))
            self.topBarHeight = topBarBox[3] - topBarBox[1] + 1
            ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.topBarHeight + self.macH)).save(os.path.join("SCA_Images", "topBar.png"))

    # Reset the right click
    def resetRightClick(self):
            self.moveToActivePanel()
            auto.click()
            beforeRightPath = os.path.join("SCA_Images", "RightClick", "beforeRight.png")
            ImageGrab.grab(bbox=self.boundBoxNoDash).save(beforeRightPath)
            auto.click(button='right')
            time.sleep(1)
            afterRightPath = os.path.join("SCA_Images", "RightClick", "afterRight.png")
            ImageGrab.grab(bbox=self.boundBoxNoDash).save(afterRightPath)
            rightBox = self.get_bbox(beforeRightPath, afterRightPath)
            print "rightBox: %s" % (rightBox,)
            (self.rightBoxW, self.rightBoxH) = (rightBox[2] - rightBox[0] + 1, rightBox[3] - rightBox[1] + 1)
            print "rightBox WxH: %s" % ((self.rightBoxW, self.rightBoxH),)
            self.optionH = (self.rightBoxH * 36.0 / 1000.0) / self.scale
            self.rightHR = (self.rightBoxH * 10.0 / 1000.0) / self.scale
            self.rightPlus = (self.rightBoxH * 8.0 / 1000.0) / self.scale
            self.rightIcons = (self.rightBoxH * 50.0 / 1000.0)
            self.rightOffset = (self.rightBoxH * 58.0 / 1000.0)

            (rightx1, righty1) = (rightBox[0] + self.boundBoxNoDash[0], rightBox[1] + self.boundBoxNoDash[1])
            (x1, y1) = (rightx1 + self.rightIcons, righty1 + self.rightOffset)
            (x2, y2) = (rightx1 + self.rightBoxW, righty1 + self.rightBoxH)
            ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(os.path.join("SCA_Images", "RightClick", "rightClick.png"))

            self.moveToActivePanel()
            auto.click()

    # Reset rightClick's presets or its scaleRotateFlip
    def resetRightOptions(self, option, offset):
            self.moveToActivePanel()
            auto.click()
            auto.click(button='right')
            located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "rightClick.png"))
            if (located is not None): (rightx1, righty1, w, h) = located
            else:
                    print "Cannot find " + option + " on calibration reset. Attempting reset on rightClick."
                    self.resetRightClick()
                    located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "rightClick.png"))
                    if (located is not None): (rightx1, righty1, w, h) = located
                    else:
                            print "Failed to reset " + option + "."
                            return
            moveToX = (rightx1 + w / 2.0) / self.scale
            moveToY = (righty1 / self.scale) + (self.optionH * offset) + self.rightHR
            auto.moveTo(moveToX, moveToY)
            time.sleep(1)
            self.moveToActivePanel()
            auto.press("0")
            afterRightPath = os.path.join("SCA_Images", "RightClick", "afterRight.png")
            afterOptionPath = os.path.join("SCA_Images", "RightClick", "after" + option + ".png")
            ImageGrab.grab(bbox=self.boundBoxNoDash).save(afterOptionPath)
            box = self.get_bbox(afterRightPath, afterOptionPath)
            print option + " box: %s" % (box,)
            (boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
            print option + " box WxH: %s" % ((boxW, boxH),)
            (x1, y1) = (box[0], box[1])
            optionPath = os.path.join("SCA_Images", "RightClick", option + ".png")
            ImageGrab.grab(bbox=(x1 + self.rightIcons, y1, x1 + boxW, y1 + boxH)).save(optionPath)
            auto.click()

    def resetAll(self):
            print "\nWarming up synapse system...\n"
            self.resetTopBarHeight()
            self.resetRightClick()
            self.resetRightOptions("presets", 8.5)
            self.resetRightOptions("scaleRotateFlip", 9.5)
            print "\nCompleted warm-up, make your gestures!\n"


    # Report situation to command prompt, useful for debugging and for users understanding an issue.
    def promptNotify(self,message, sleepAmt):
            openWindow(prompt)
            print message
            time.sleep(sleepAmt)

    # Find Synapse's rightClick image
    def findRightClick(self,offset):
            located = auto.locateOnScreen(os.path.join("SCA_Images", "RightClick", "rightClick.png"))
            if (located is not None):
                    (x1, y1, w, h) = located
                    auto.moveTo((x1 / self.scale) + (w / 2.0) * self.scale, (y1 + (offset / 1000.0) * self.status["rightBoxH"]) / self.scale)
                    return True
            else:
                    print "Error when performing right click function."
                    return False

    # Handles the killing signals of the class
    def signalHandler(self, sig, frame):
        self.removeImagesPrompt()
        sys.exit(0)

    def calibrate(self):

        # if there is a calibration file, use it, if not
        # generate a calibration
        self.resetPanelMoves()
        self.openWindow(self.viewer)

        if (os.path.exists(self.calibrationPath)):
            f = open(self.calibrationPath, "r")
            self.status = json.loads(" ".join([line.rstrip('\n') for line in f]))
            f.close()
        else:
            self.resetAll()
            f = open(self.calibrationPath, "w")
            f.write(json.dumps(self.status, indent=4, separators=(',', ': ')))
            f.close()

if __name__ == "__main__":
    syn_action = SynapseAction()
    # set up the signal handler
    signal.signal(signal.SIGINT, syn_action.signalHandler)
    # Run the program
    syn_action.calibrate()
    while True: continue



