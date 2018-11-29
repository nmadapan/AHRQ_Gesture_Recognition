import numpy as np
import cv2
import os
import platform
import time
import pyautogui as auto
from PIL import Image
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
        # IMPORTANT
        # For Mac, just found out that doing "alt+tab" goes through the windows
        # Which shows and doesn't show the dash
        # Use that with a proper image difference to get the boundBoxNoDash
        #
        self.border = (20.0 * self.nativeW / 2880.0) + (4.0 * self.scale)
        self.boundBoxNoDash = (self.border, self.macH + self.border, self.nativeW - self.border, self.nativeH - self.border)
        # Get the path for the calibration file
        if calibrationPath is None:
            self.calibrationPath = "calibration" + "_".join(list(str(e) for \
                e in [self.width, self.height, self.scale])).replace(".", "-") + ".txt"

        # Variables of the synapse window
        # TODO all of this variables should probably go. Check that the code that uses them
        # goes away
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
            # "hold_action": None,
            "topBarHeight": None, "defaultCommand": None, "group1_command": None,
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

        # Synapse behavior parameters
        self.menuSleep = 0.75


    # Closes/Minimizes every window and leaves active the windows
    # with the name "toOpen"
    def openWindow(self, toOpen):
        # Look into "start" command for Windows
        if (platform.system() == "Windows"):
            window_names = auto.getWindows().keys()
            for window_name in window_names: auto.getWindow(window_name).minimize()
            for window_name in window_names:
                if toOpen in window_name and "Patient Information" not in window_name:
                    auto.getWindow(window_name).maximize()
                    break
        else: os.system("open -a " + toOpen.replace(" ", "\\ "))

    # Remove images generated in the process of running the program
    def removeImages(self):
        paths = [os.path.join("SCA_Images", "RightClick"), os.path.join("SCA_Images", "Window", "Closes"),
            os.path.join("SCA_Images", "Window"), os.path.join("SCA_Images", "Layout"), os.path.join("SCA_Images")]
        for path in paths:
            if (not os.path.exists(path)): continue
            for file in os.listdir(path):
                    if file.endswith(".png"): os.remove(os.path.join(path, file))
        # os.remove(self.calibrationPath)


    # Prompt notification if choosing to remove the images
    def removeImagesPrompt(self):
        #(self.status["hold_action"], self.status["defaultCommand"], self.status["group1_command"]) = (None, None, None)
        (self.status["defaultCommand"], self.status["group1_command"]) = (None, None)
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
        time.sleep(3)
        auto.click()
        ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.nativeH)).\
            save(os.path.join("SCA_Images", "fullscreen.png"))
        auto.moveTo(auto.position()[0], 0)
        time.sleep(3)
        ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.nativeH)).\
            save(os.path.join("SCA_Images", "afterTopBar.png"))
        topBarBox = self.get_bbox(os.path.join("SCA_Images", "fullscreen.png"), \
            os.path.join("SCA_Images", "afterTopBar.png"))
        self.status["topBarHeight"] = topBarBox[3] - topBarBox[1] + 1
        ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.status["topBarHeight"] + self.macH)).save(os.path.join("SCA_Images", "topBar.png"))

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
    # def signalHandler(self, sig, frame):
        # self.removeImagesPrompt()
        # sys.exit(0)

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

    def gestureCommands(self, sequence):
        print "getting command:", sequence
        (commandID, actionID) = (-1, -1)
        commandAction = sequence

        ##################################################################
        ############# CHECK THAT THE COMMAND IS VALID ####################
        ##################################################################
        if (sequence.find(" ") != -1):
            commandAction = sequence[:sequence.find(" ")]
            self.status["params"] = sequence[sequence.find(" ") + 1:]
        #elif (self.status["hold_action"] is None): self.status["params"] = ""
        else: self.status["params"] = ""
        if (commandAction.find("_") != -1):
            try:
                commandID = int(commandAction[:commandAction.find("_")])
                actionID = int(commandAction[commandAction.find("_") + 1:])
                command = self.actionList[commandID][0]
                action = self.actionList[commandID][actionID]
            except ValueError:
                print "Unrecognized sequence of commands!\n"
                return False
            except IndexError:
                print "Incorrect commands!\n"
                return False
        else:
            print "Invalid command entered!\n"
            return False
        ############# FINISH CHECKING  #####################
        # default command is the modifier and groupt1_command the context
        # RESET CONTEXT AND MODIFIER
        if (self.status["defaultCommand"] != command and self.status["defaultCommand"] is not None):
            # if is changing from one command to another and not from a reset`
            print "resetting context", self.status["defaultCommand"],  command
            self.status["defaultCommand"] = None
            auto.mouseUp()
        if (self.status["group1_command"] != command and self.status["group1_command"] is not None):
            # if is changing from one command to another and not from a reset`
            print "resetting modifier", self.status["group1_command"], command
            self.status["defaultCommand"] = None
            self.status["group1_command"] = None
            auto.mouseUp()


        ####################################################
        ################## ADMIN COMANDS ###################
        ####################################################

        if (command == "Admin" and action != "Admin"):
            if (action == "Quit"):
                removeImagesPrompt()
                sys.exit(0)
            elif (action == "Get Status"):
                print "------\nself.status\n------"
                print "Previous action: " + self.status["prev_action"]
                print "Panel Dimension: " + str(self.status["panel_dim"][0]) + 'x' + str(self.status["panel_dim"][1])
                print "Active panel: " + str(self.status["active_panel"][0]) + 'x' + str(self.status["active_panel"][1])
                print "Patient information window: " + ("opened" if self.status["window_open"] else "closed")
                print ""
            elif (action == "Reset"):
                if (self.status["params"] == "All"):
                    calibration.resetAll()
                if (self.status["params"] == "TopBar"):
                    calibration.resetTopBarHeight()
                elif (self.status["params"] == "RightClick"):
                    calibration.resetRightClick()
                elif (self.status["params"] == "Presets"):
                    calibration.resetRightOptions("presets", 8.5)
                elif (self.status["params"] == "ScaleRotateFlip"):
                    calibration.resetRightOptions("scaleRotateFlip", 9.5)
                (self.status["topBarHeight"], self.status["optionH"], self.status["rightHR"], self.status["rightPlus"], self.status["rightIcons"],
                    self.status["rightOffset"], self.status["rightBoxW"], self.status["rightBoxH"]) = calibration.getAll()
                f = open(calibrationPath, "w")
                f.write(json.dumps(self.status, indent=4, separators=(',', ': ')))
                f.close()
                # if (self.status["hold_action"] is not None):
                #     sequence = self.status["hold_action"]
                #     self.status["hold_action"] = "held"
                #     return gestureCommands(sequence)

        ####################################################
        ###################### SCROLL ######################
        ####################################################

        elif (command == "Scroll" and action != "Scroll"):
            self.moveToActivePanel()
            auto.click()
            scrollAmount = (50 if self.status["params"] == "" else int(self.status["params"]))
            auto.PAUSE = 0
            for i in range(scrollAmount): auto.press("right" if action == "Up" else "left")
            auto.PAUSE = 0.25
            auto.click()

        ####################################################
        ####################### FLIP #######################
        ####################################################

        elif (command == "Flip" and action != "Flip"):
            self.moveToActivePanel()
            auto.click(button='right')
            auto.PAUSE = 0.1
            auto.press("0")
            auto.press("s")
            time.sleep(self.menuSleep)
            auto.press("0")
            auto.press("h" if action == "Horizontal" else "v")
            auto.PAUSE = 0.25

        ####################################################
        ##################### ROTATE #######################
        ####################################################

        elif (command == "Rotate" and action != "Rotate"):
            self.moveToActivePanel()
            auto.click(button='right')
            auto.PAUSE = 0.1
            auto.press("0")
            auto.press("s")
            time.sleep(self.menuSleep)
            auto.press("0")
            auto.press("r")
            if (action != "Clockwise"): auto.press("down")
            auto.press("enter")
            auto.PAUSE = 0.25

        ####################################################
        ##################### ZOOM #########################
        ####################################################

        elif (command == "Zoom"):
            splitParams = self.status["params"].split("_")
            # If performing just the context
            # or an a modifier alone
            if actionID == 0 or\
            (self.status["defaultCommand"] is None and commandID !=0):
                self.moveToActivePanel()
                auto.click()
                auto.click(button='right')
                auto.PAUSE = 0.1
                auto.press("z")
                auto.mouseDown()
                # add the context if we are just performing a context
                self.status["defaultCommand"] = command
            # if we are performing a zoom in or a zoom out
            if actionID != 0:
                # Get the level, acording to the params or default
                if (len(splitParams) % 2 == 1 and self.status["params"] != ""):
                    level = (-1 * int(splitParams[0]) if action == "In" else int([0]))
                else:
                    level = (-100 if action == "In" else 100)
                    if (len(splitParams) <= 1):
                        (moveToX, moveToY) = auto.position()
                    else:
                        (moveToX, moveToY) = (int(splitParams[len(splitParams) - 2]), int(splitParams[len(splitParams) - 1]))
                    auto.moveTo(moveToX, moveToY)
                    auto.mouseDown()
                    auto.moveTo(moveToX, moveToY + level)
                    #auto.mouseUp()
                    self.status["group1_command"] = command

        ####################################################
        ################## SWITCH PANEL ####################
        ####################################################

        elif (command == "Switch Panel" and action != "Switch Panel"):
            ind = int(actionID / 3)
            self.status["active_panel"][ind] += (-1 if action == "Left" or action == "Up" else 1)
            self.status["active_panel"][ind] = max(1, self.status["active_panel"][ind])
            self.status["active_panel"][ind] = min(self.status["active_panel"][ind], self.status["panel_dim"])
            self.moveToActivePanel()
            auto.click()

        ####################################################
        ###################### PAN #########################
        ####################################################

        elif (command == "Pan"):
            splitParams = self.status["params"].split("_")
            # If performing just the context
            # or an a modifier alone
            if actionID == 0 or\
            (self.status["defaultCommand"] is None and commandID !=0):
                self.moveToActivePanel()
                auto.click()
                auto.click(button='right')
                auto.PAUSE = 0.1
                auto.press("0")
                auto.press("p")
                auto.PAUSE = 0
                auto.press("enter")
                # (auto.press(e) for e in ["p", "enter"])
                auto.mouseDown()
                # add the context if we are just performing a context
                self.status["defaultCommand"] = command

            # if we are performing a pan modifier
            if actionID != 0:
                # Get the jump of the pan acording to the parameters
                if (len(splitParams) % 2 == 1 and self.status["params"] != ""):
                    level = (int(splitParams[0]) if action == "Left" or action == "Up" else -1 * int(splitParams[0]))
                else:
                    level = (40 if action == "Left" or action == "Up" else -40)
                # Get the initial position of the pan according to the parameters
                if (len(splitParams) <= 1):
                    (moveToX, moveToY) = auto.position()
                else:
                    (moveToX, moveToY) = (int(splitParams[len(splitParams) - 2]), int(splitParams[len(splitParams) - 1]))
                # Get the final position of the pan according to the command
                if (action == "Left" or action == "Right"):
                    (toMoveX, toMoveY) = (moveToX + level, moveToY)
                else:
                    (toMoveX, toMoveY) = (moveToX, moveToY + level)
                # Move the pan
                auto.moveTo(moveToX, moveToY)
                if self.status["defaultCommand"] is not None:
                    auto.mouseDown()
                print "moving to:",  toMoveX, toMoveY
                auto.moveTo(toMoveX, toMoveY)
                #auto.mouseUp()
                self.status["group1_command"] = command

        ####################################################
        ###################### WINDOW ######################
        ####################################################

        # General way it should work, but it would have issues.
        # For now, don't test Window Open/Close (no 8_1 or 8_2)
        elif (command == "Window" and action != "Window"):
            # Coordinates on AHRQ Dell with scale 1.0:
            # (iconW, barW) = (57.0, 15.0)
            # (moveToX, moveToY) = (iconW * 5.5 + barW, (self.status["topBarHeight"] - 9.0) / 2.0)
            #
            # Coordinates on Mac with scale 2.0:
            # (iconW, barW) = (74.0, 19.0)
            # (moveToX, moveToY) = (iconW * 5.5 + barW, (macH + (self.status["topBarHeight"] - 9.0) / 2.0) / scale)
            #
            # Therefore, try using:
            # (iconW, barW) = (57.0 * self.status["topBarHeight"] / 169.0, 15.0 * self.status["topBarHeight"] / 169.0)
            # (moveToX, moveToY) = (iconW * 5.5 + barW, (macH + (self.status["topBarHeight"] - 9.0) / 2.0) / scale)
            # Uncomment the return to not ignore window
            #return True
            if (action == "Open" and not self.status["window_open"]):
                self.moveToActivePanel()
                auto.click()
                if (platform.system() == "Windows"):
                    auto.hotkey("win", "alt", "e")
                    time.sleep(5)
                else:
                    # original Page with a dash
                    regularPath = os.path.join("SCA_Images", "Window", "regular.png")
                    regular = ImageGrab.grab(0, self.macH, self.nativeW, self.nativeH)
                    regular.save(regularPath)
                    # new page without the dash, "ICA Seamless Host Agent"
                    auto.hotkey("alt", "tab")
                    icaSHAPath = os.path.join("SCA_Images", "Window", "icaSHA.png")
                    icaSHA = ImageGrab.grab(0, self.macH, self.nativeW, self.nativeH)
                    icaSHA.save(icaSHAPath)
                    # everything including and inside the dash
                    diff = ImageChops.difference(regular, icaSHA)
                    self.status["window_bbnd"] = diff.size
                    auto.hotkey("alt", "tab")
                    auto.hotkey("command", "altleft", "e")
                    time.sleep(5)
                    # patient info window without a dash
                    patInfoPath = os.path.join("SCA_Images", "Window", "patInfo.png")
                    patInfo = ImageGrab.grab(0, self.macH, self.nativeW, self.nativeH)
                    patInfo.save(patInfoPath)
                    # patient info window gray without a dash
                    auto.keyDown("alt")
                    auto.press("tab")
                    auto.press("tab")
                    auto.keyUp("alt")
                    patInfoGrayPath = os.path.join("SCA_Images", "Window", "patInfoGray.png")
                    patInfoGray = ImageGrab.grab(0, self.macH, self.nativeW, self.nativeH)
                    patInfoGray.save(patInfoGrayPath)
                    # GET THE WINDOW, SAVE ITS CLOSE IMAGES
                    diff2 = ImageChops.difference(patInfo, patInfoGray)
                    auto.hotkey("alt", "tab")
                    # seriesClose.png == difference between icaSHA and patInfo
                    # seriesClose_Gray.png == difference between icaSHA and patInfoGray
                    # seriesClose_Red.png == difference between icaSHA and (new image for hovering over close)
                    #
                    """
                    (x1, y1, x2, y2) = (diffBox[i] + box[(i % 2)] for i in range(4))
                    ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffSeriesPath)
                    (tempX, tempY) = (x2, y1)
                    auto.moveTo(tempX, tempY)
                    (x1, y1) = (tempX + ((-14.0 - 90.0) * scale / 2.0), tempY + (3.0) * scale / 2.0)
                    (x2, y2) = (tempX + (-14.0) * scale / 2.0, tempY + (43.0) * scale / 2.0)
                    seriesClosePath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose.png")
                    seriesClose_RedPath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose_Red.png")
                    seriesClose_GrayPath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose_Gray.png")
                    ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClosePath)
                    auto.moveTo((x1 + x2) / (scale * 2.0), (y1 + y2) / (scale * 2.0))
                    ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClose_RedPath)
                    auto.moveTo(0, (y1 + y2) / (scale * 2.0))
                    auto.click()
                    ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(seriesClose_GrayPath)
                    """
                self.status["window_open"] = True
            elif (action == "Close" and self.status["window_open"]):
                # Windows hasn't been tested but it should work
                # Mac sometimes closes Citrix instead of Patient Info
                if (platform.system() == "Windows"):
                    # Have not tested the code below, but hopefully will work
                    # Should do the following:
                    # Minimize all windows except for ones inside Synapse
                    window_names = auto.getWindows().keys()
                    for window_name in window_names:
                        if not (window_name.endswith(" - \\\\Remote")):
                            auto.getWindow(window_name).minimize()
                    window_names = auto.getWindows().keys()
                    # Maximize only the "Patient Information" window that's in Synapse
                    for window_name in window_names:
                        try:
                            if window_name.endswith(" - \\\\Remote") and window_name.startswith("Patient Information for "):
                                xef_window = auto.getWindow(window_name)
                                # Resize the window to be half screen-width x half screen-height
                                # Click on the close button
                                xef_window.maximize()
                                xef_window.resize(width / 2.0, height / 2.0)
                                (closeX, closeY) = (10 + (width * 90.0 / 1920.0), 2 + (width * 40.0 / 1920.0))
                                xef_window.clickRel(x=(width / 2.0 - closeX), y=closeY, clicks=1, button='left')
                                break
                        except Exception as e:
                            continue
                    #auto.hotkey("fn", "alt", "f4")
                else: auto.hotkey("command", "fn", "f4")
                self.status["window_open"] = False

        ####################################################
        ################ MANUAL CONTRAST ###################
        ####################################################

        elif (command == "Manual Contrast"):
            splitParams = self.status["params"].split("_")
            if (self.status["defaultCommand"] is None):
                if (self.status["group1_command"] is None):
                    self.moveToActivePanel()
                    auto.click(button='right')
                    (auto.press(e) for e in ["0", "w"])
                if (command == action):
                    self.status["defaultCommand"] = command
                    auto.mouseDown()
                else:
                    if (splitParams[0] != ""):
                        level = (-1 * int(splitParams[0]) if action == "Decrease" else int(splitParams[0]))
                    else:
                        level = (-50 if action == "Decrease" else 50)
                    (oldLocationX, oldLocationY) = auto.position()
                    auto.mouseDown()
                    auto.moveTo(oldLocationX, oldLocationY + level)
                    self.status["group1_command"] = command
            else:
                (oldLocationX, oldLocationY) = auto.position()
                if (len(splitParams) == 1):
                    if (self.status["params"] != ""):
                        level = (-1 * int(splitParams[0]) if action == "Decrease" else int(splitParams[0]))
                    else:
                        level = (-50 if action == "Decrease" else 50)
                else:
                    print "For " + command + ", you must pass a maximum of one argument."
                    return False
                auto.moveTo(oldLocationX, oldLocationY + level)

        ####################################################
        ##################### LAYOUT #######################
        ####################################################

        elif (command == "Layout" and action != "Layout"):
            # Coordinates on AHRQ Dell with scale 1.0:
            # (iconW, barW) = (57.0, 15.0)
            # (moveToX, moveToY) = (iconW * 10.5 + barW * 3.0, (self.status["topBarHeight"] - 9.0) / 2.0)
            #
            # Coordinates on Mac with scale 2.0:
            # (iconW, barW) = (74.0, 19.0)
            # (moveToX, moveToY) = (iconW * 10.5 + barW * 3.0, (macH + (self.status["topBarHeight"] - 9.0) / 2.0) / scale)
            #
            # Therefore, try using:
            # (iconW, barW) = (57.0 * self.status["topBarHeight"] / 169.0, 15.0 * self.status["topBarHeight"] / 169.0)
            # (moveToX, moveToY) = (iconW * 10.5 + barW * 3.0, (macH + (self.status["topBarHeight"] - 9.0) / 2.0) / scale)
            (oldLocationX, oldLocationY) = auto.position()
            auto.moveTo(oldLocationX, 0)
            time.sleep(1)
            (iconW, barW) = (57.0 * self.status["topBarHeight"] / 169.0, 15.0 * self.status["topBarHeight"] / 169.0)
            (moveToX, moveToY) = (iconW * 10.5 + barW * 3.0, (self.macH + (self.status["topBarHeight"] - 9.0) / 2.0) / self.scale)
            auto.moveTo(moveToX, moveToY)
            auto.click()
            time.sleep(5)
            if (platform.system() == "Windows"):
                window_names = auto.getWindows().keys()
                for window_name in window_names:
                    try:
                        if window_name.endswith(" - \\\\Remote") and window_name.startswith("Page Layout - "):
                            (winX, winY) = auto.getWindow(window_name).position()
                            (x1, y1) = (winX + 67.0 * width / 1920.0, winY + 95.0 * width / 1920.0)
                            (jumpX, jumpY) = (93.0 * width / 1920.0, 97.0 * width / 1920.0)
                            (self.status["panel_dim"][0], self.status["panel_dim"][1]) = (1, actionID)
                            x1 += (self.status["panel_dim"][1] - 1) * jumpX
                            auto.moveTo(x1, y1)
                            auto.click()
                            resetPanelMoves()
                            moveToActivePanel()
                            auto.click()
                            break
                    except Exception as e:
                        continue
            # box = (1.0 * scale, status["topBarHeight"], -1.0 * scale, -1.0 * scale)
            # box = tuple(boundBoxNoDash[i] + box[i] for i in range(4))
            # afterHoverPath = os.path.join("SCA_Images", "Layout", "afterHover.png")
            # ImageGrab.grab(bbox=box).save(afterHoverPath)
            # 429,54 on mac from topBar, without scale
            # if (platform.system() == "Windows"): auto.moveTo(642.0 * width / 1920.0, 80.0 * height / 1080.0)
            # else: auto.moveTo(857.0 / 2.0, (109.0 + 44.0) / 2.0)
            # (iconW, barW) = (57.0 * self.status["topBarHeight"] / 169.0, 15.0 * self.status["topBarHeight"] / 169.0)
            # (moveToX, moveToY) = (iconW * 10.5 + barW * 3.0, (macH + (self.status["topBarHeight"] - 9.0) / 2.0) / scale)
            # auto.moveTo(moveToX, moveToY)
            # auto.click()
            # time.sleep(5)
            # windowPath = os.path.join("SCA_Images", "Layout", "window.png")
            # ImageGrab.grab(bbox=box).save(windowPath)
            # diffLayoutPath = os.path.join("SCA_Images", "Layout", "diffLayout.png")
            # diffBox = get_bbox(afterHoverPath, windowPath)
            # (x1, y1, x2, y2) = (diffBox[i] + box[(i % 2)] for i in range(4))
            # ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(diffLayoutPath)
            # auto.moveTo(x1, y1)
            # time.sleep(2)
            # auto.moveTo(x1 / scale, y1 / scale)
            # time.sleep(2)
            # (x1, y1) = ((x1 + 91.0) / 2.0, (y1 + 127.0) / 2.0)
            # jumpX = (122.0 / 2.0)
            # (status["panel_dim"][0], status["panel_dim"][1]) = (1, actionID)
            # (x1, y1) = (472.0 + (actionID - 1) * 62.0, 217.0)
            # x1 += (status["panel_dim"][1] - 1) * jumpX
            # auto.moveTo(x1, y1)
            # auto.click()
            # resetPanelMoves()
            # moveToActivePanel()
            # auto.click()

        ####################################################
        ################ CONTRAST PRESETS ##################
        ####################################################

        elif (command == "Contrast Presets" and action != "Contrast Presets"):
            self.moveToActivePanel()
            auto.click()
            auto.click(button='right')
            auto.PAUSE = 0.1
            (auto.press(e) for e in ["0", "i", "right"])
            time.sleep(0.5)
            auto.press("0")
            for i in range(actionID + 1): auto.press("down")
            auto.press("enter")
            auto.PAUSE = 0.25
            time.sleep(1)

        return True


if __name__ == "__main__":
    syn_action = SynapseAction()
    # set up the signal handler
    # signal.signal(signal.SIGINT, syn_action.signalHandler)
    # Run the program
    syn_action.calibrate()
    command_list = ["1_0", "1_1", "1_2", "1_1", "2_0", "2_1", "2_2", "2_1", "2_1", "2_2", "2_0","3_0", "3_1", "3_2", "3_1", "3_1", "3_2", "3_0", "4_0", "4_1", "4_1", "4_2", "4_2", "4_0", "4_0", "4_1", "4_2", "3_1", "4_1", "4_1", "4_0", "6_0", "6_1", "6_1", "6_2", "6_2", "6_0", "6_0", "6_1", "6_2"]
    command_list = ["4_0", "4_1", "4_1", "4_2", "4_2", "4_0", "4_0", "4_1", "4_2", "3_1", "4_1", "4_1", "4_0"]
    command_list = ["4_0", "4_1", "4_1", "4_2", "4_2", "4_0", "4_0", "4_1", "4_2", "3_1", "4_1", "4_1", "4_0", "6_0", "6_1", "6_1", "6_2", "6_2", "6_0", "6_0", "6_1", "6_2"]
    command_list = ["4_1", "6_0", "6_4", "6_4", "6_4"]
    # command_list = ["6_0", "6_1", "6_1", "6_1", "6_1", "6_1", "6_1", "6_1", "6_1"]
    command_list = ["8_1", "8_2", "10_1", "10_2", "10_3", "10_4"]

    # For now, don't test Window Open/Close (no 8_1 or 8_2)

    for cmd in command_list:
        success = syn_action.gestureCommands(cmd)
        print "execution of command", cmd, "flag:", success
        time.sleep(2)

    # syn_action.resetTopBarHeight()
    # OPEN PATIENT INFO  WINDOW
    # TODO: ONLY WORKS if the windows in in focus from before. FIGURE OUT HOW TO FOCUS THE WINDOW AUTOMATICALLY ON THE CALIBRATON
    # syn_action.moveToActivePanel()
    # auto.click()
    # auto.hotkey("command", "optionLeft", "e")
    # time.sleep(5)
    # # CLOSE WINDOW: warning, closes any window on focus, so it's dangerous
    # auto.hotkey("command", "optionLeft", "f4")
    # time.sleep(1)

    #auto.hotkey("command", "enter")
    syn_action.openWindow(syn_action.prompt)
    while True: continue



