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


class OsirixAction:
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
        (self.macH, self.viewer, self.prompt) = (44.0 * self.nativeW / 2880.0, "OsiriX Lite", "Terminal")
        # Get the path for the calibration file
        if calibrationPath is None:
            self.calibrationPath = "calibration" + "_".join(list(str(e) for \
                e in [self.width, self.height, self.scale])).replace(".", "-") + ".txt"

        # Variables of the osirix window
        # TODO all of this variables should probably go. Check that the code that uses them
        # goes away
        # self.optionH = None
        # self.rightHR = None
        # self.rightPlus = None
        # self.rightIcons = None
        # self.rightOffset = None
        # self.rightBoxW = None
        # self.rightBoxH = None

        # Status of the system:
        self.status = {"prev_action": "", "panel_dim": [1, 1],
            "window_open": False, "active_panel": [1, 1],
            "rulers": {"len": 0}, "defaultCommand": None, "group1_command": None,
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
        os.system("open -a " + toOpen.replace(" ", "\\ "))

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

    # Report situation to command prompt, useful for debugging and for users understanding an issue.
    def promptNotify(self,message, sleepAmt):
        openWindow(prompt)
        print message
        time.sleep(sleepAmt)

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
            scrollAmount = (10 if status["params"] == "" else int(status["params"]))
            auto.scroll((-1 * scrollAmount if action == "Up" else scrollAmount))

        ####################################################
        ####################### FLIP #######################
        ####################################################

        elif (command == "Flip" and action != "Flip"):
            self.moveToActivePanel()
            auto.click()
            auto.press("h" if action == "Horizontal" else "v")

        ####################################################
        ##################### ROTATE #######################
        ####################################################

        elif (command == "Rotate" and action != "Rotate"):
            self.moveToActivePanel()
            auto.click(button='right')
            auto.click()
            auto.moveTo(794.0 / self.scale, macH / (2.0 * self.scale))
            auto.click()
            (moveToX, moveToY) = (1089.0, (macH / 2.0) + (7.0 + (38.0 * 5.0) + 24.0 + (38.0) + 24.0 + (38.0 * 4.5)))
            auto.moveTo(moveToX / self.scale, moveToY / self.scale)
            moveToX = (1468.0 + (482.0 / 2.0))
            auto.moveTo(moveToX / self.scale, moveToY / self.scale)
            moveToY += (-1.0 * (38.0 * 0.5) + (64.0 * 2.0) + 22.0 + 92.0)
            moveToY += ((106.0 * 0.5) if action == "Clockwise" else 106.0 + (96.0 * 0.5))
            auto.moveTo(moveToX / self.scale, moveToY / self.scale)
            auto.click()

        ####################################################
        ##################### ZOOM #########################
        ####################################################

        elif (command == "Zoom"):
            splitParams = self.status["params"].split("_")
            # If performing just the context
            # or an a modifier alone
            if actionID == 0 or\
            (self.status["defaultCommand"] is None and commandID != 0):
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
            self.status["active_panel"][ind] = min(self.status["active_panel"][ind], self.status["panel_dim"][ind])
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
            if (action == "Open" and not self.status["window_open"]):
                self.status["window_open"] = True
            elif (action == "Close" and self.status["window_open"]):
                self.status["window_open"] = False

        ####################################################
        ################ MANUAL CONTRAST ###################
        ####################################################

        elif (command == "Manual Contrast"):
            splitParams = self.status["params"].split("_")
            if (self.status["defaultCommand"] is None):
                if (self.status["group1_command"] is None):
                    self.moveToActivePanel()
                    auto.press("w")
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
            auto.moveTo(194.0 / scale, 105.0 / scale)
            auto.click()
            auto.PAUSE = 0
            for i in range(12): auto.press("up")
            (status["panel_dim"][0], status["panel_dim"][1]) = (1, actionID)
            for i in range((actionID - 1) * (actionID - 1)): auto.press("down")
            auto.PAUSE = 0.75
            auto.press("space")
            self.resetPanelMoves()
            (status["active_panel"][0], status["active_panel"][1]) = (1, 1)
            self.moveToActivePanel()
            auto.click()

        ####################################################
        ################ CONTRAST PRESETS ##################
        ####################################################

        elif (command == "Contrast Presets" and action != "Contrast Presets"):
            auto.press(action)

        return True


if __name__ == "__main__":
    osirix_action = OsirixAction()
    # set up the signal handler
    # signal.signal(signal.SIGINT, osirix_action.signalHandler)
    # Run the program
    # osirix_action.calibrate()
    command_list = ["1_0", "1_1", "1_2", "1_1", "2_0", "2_1", "2_2", "2_1", "2_1", "2_2", "2_0","3_0", "3_1", "3_2", "3_1", "3_1", "3_2", "3_0", "4_0", "4_1", "4_1", "4_2", "4_2", "4_0", "4_0", "4_1", "4_2", "3_1", "4_1", "4_1", "4_0", "6_0", "6_1", "6_1", "6_2", "6_2", "6_0", "6_0", "6_1", "6_2"]
    command_list = ["4_0", "4_1", "4_1", "4_2", "4_2", "4_0", "4_0", "4_1", "4_2", "3_1", "4_1", "4_1", "4_0"]
    command_list = ["4_0", "4_1", "4_1", "4_2", "4_2", "4_0", "4_0", "4_1", "4_2", "3_1", "4_1", "4_1", "4_0", "6_0", "6_1", "6_1", "6_2", "6_2", "6_0", "6_0", "6_1", "6_2"]
    command_list = ["4_1", "6_0", "6_4", "6_4", "6_4"]
    # command_list = ["6_0", "6_1", "6_1", "6_1", "6_1", "6_1", "6_1", "6_1", "6_1"]
    command_list = ["8_1", "8_2", "10_1", "10_2", "10_3", "10_4"]

    for cmd in command_list:
        success = osirix_action.gestureCommands(cmd)
        print "execution of command", cmd, "flag:", success
        time.sleep(2)

    # osirix_action.resetTopBarHeight()
    # OPEN PATIENT INFO WINDOW
    # TODO: ONLY WORKS if the windows in in focus from before. FIGURE OUT HOW TO FOCUS THE WINDOW AUTOMATICALLY ON THE CALIBRATON
    # osirix_action.moveToActivePanel()
    # auto.click()
    # auto.hotkey("command", "optionLeft", "e")
    # time.sleep(5)
    # # CLOSE WINDOW: warning, closes any window on focus, so it's dangerous
    # auto.hotkey("command", "optionLeft", "f4")
    # time.sleep(1)

    #auto.hotkey("command", "enter")
    osirix_action.openWindow(osirix_action.prompt)
    while True: continue



