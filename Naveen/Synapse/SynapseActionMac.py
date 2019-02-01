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
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import json
sys.path.append("..")
from SynapseCommand import SynapseCommand
from Tkinter import *
import tkFont
import keyboard
from helpers import file_to_list, json_to_dict, turn_int
import ntplib
import time
import csv


class SynapseAction:
    def __init__(self, lexicon, commandFile, recordingPath, imageFolder=None, keyboard=True, calibrationPath = None):
        ####################
        ## autogui setup  ##
        auto.FAILSAFE = True
        auto.PAUSE = 0.25
        ####################

        self.imageFolder = "SCA_Images" if imageFolder is None else imageFolder
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
        print(self.calibrationPath)
        # Initialize the command desambiguation tool
        self.finalCmd = SynapseCommand(lexicon, recordingPath)
        self.cmd_dict = json_to_dict(commandFile)

        # open the file. If it exists, say that it exists and exit the program with an error.
        # Do not overrwite
        if os.path.isfile(recordingPath):
            print("RECORDING FILE ALREADY EXISTS, CHOOSE ANOTHER NAME")
            exit(1)
        else:
            f = open(recordingPath,'w')
            self.recording_file = csv.writer(f, delimiter=",")

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
            "window_open": False, "active_panel": [0, 0],
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

        # Acknowledgment variables
        self.root_window = Tk()
        self.big_font = tkFont.Font(family='Helvetica', size=36, weight='bold')
        # window size
        root_w = 400
        root_h = 455
        # get screen width and height
        ws = self.root_window.winfo_screenwidth() # width of the screen
        hs = self.root_window.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (root_w/2)
        y = (hs/2) - (root_h/2)
        # set the dimensions of the screen
        # and where it is placed
        self.root_window.geometry('%dx%d+%d+%d' % (root_w, root_h, x, y))
        self.btn_list = []
        self.bg_colors = ['#C0C0C0', '#002dd3']
        self.fg_colors = ['#000000', '#FFFFFF']

        # create the menu
        def separator():
            Label(master=self.root_window,background=self.fg_colors[1],
                text='separator',fg=self.fg_colors[1]).pack(fill=X)
        separator()
        for i in range(5):
            self.btn_list.append(Label(master=self.root_window, font=self.big_font,
                text='Option '+str(i), background = self.bg_colors[0]))
            self.btn_list[-1].pack(fill=X)
            separator()
        self.btn_list.append(Label(master=self.root_window, font=self.big_font,
            text='More Commands', background = self.bg_colors[0]))
        self.btn_list[-1].pack(fill=X)


    # Closes/Minimizes every window and leaves active the windows
    # with the name "toOpen"
    def openWindow(self, toOpen, windowOpen=False):
        # Look into "start" command for Windows
        if (platform.system() == "Windows"):
            window_names = auto.getWindows().keys()
            for window_name in window_names:
                auto.getWindow(window_name).minimize()
                if (toOpen in window_name and (windowOpen or "Patient Information" not in window_name)):
                    xef_window = auto.getWindow(window_name)
                    xef_window.maximize()
                    xef_window.minimize()
                    xef_window.maximize()
                    break
        else: os.system("open -a " + toOpen.replace(" ", "\\ "))

    # Remove images generated in the process of running the program
    def removeImages(self):
        paths = [os.path.join(self.imageFolder, "RightClick"), os.path.join(self.imageFolder, "Window", "Closes"),
            os.path.join(self.imageFolder, "Window"), os.path.join(self.imageFolder, "Layout"), os.path.join(self.imageFolder)]
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
            moveToX = self.status["firstW"] + (self.status["active_panel"][1]) * (self.status["jumpW"])
            moveToY = self.status["firstH"] + (self.status["active_panel"][0]) * (self.status["jumpH"])
            auto.moveTo(moveToX, moveToY)

    # Reset height of top bar and save it
    def resetTopBarHeight(self):
            self.moveToActivePanel()
            time.sleep(3)
            auto.click()
            ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.nativeH)).\
                save(os.path.join(self.imageFolder, "fullscreen.png"))
            auto.moveTo(auto.position()[0], 0)
            time.sleep(3)
            ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.nativeH)).\
                save(os.path.join(self.imageFolder, "afterTopBar.png"))
            topBarBox = self.get_bbox(os.path.join(self.imageFolder, "fullscreen.png"), \
                os.path.join(self.imageFolder, "afterTopBar.png"))
            self.status["topBarHeight"] = topBarBox[3] - topBarBox[1] + 1
            ImageGrab.grab(bbox=(0, self.macH, self.nativeW, self.status["topBarHeight"] + self.macH)).save(os.path.join(self.imageFolder, "topBar.png"))

    # Reset the right click
    def resetRightClick(self):
            self.moveToActivePanel()
            auto.click()
            beforeRightPath = os.path.join(self.imageFolder, "RightClick", "beforeRight.png")
            ImageGrab.grab(bbox=self.boundBoxNoDash).save(beforeRightPath)
            auto.click(button='right')
            time.sleep(1)
            afterRightPath = os.path.join(self.imageFolder, "RightClick", "afterRight.png")
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
            ImageGrab.grab(bbox=(x1, y1, x2, y2)).save(os.path.join(self.imageFolder, "RightClick", "rightClick.png"))

            self.moveToActivePanel()
            auto.click()

    # Reset rightClick's presets or its scaleRotateFlip
    def resetRightOptions(self, option, offset):
            self.moveToActivePanel()
            auto.click()
            auto.click(button='right')
            located = auto.locateOnScreen(os.path.join(self.imageFolder, "RightClick", "rightClick.png"))
            if (located is not None): (rightx1, righty1, w, h) = located
            else:
                print "Cannot find " + option + " on calibration reset. Attempting reset on rightClick."
                self.resetRightClick()
                located = auto.locateOnScreen(os.path.join(self.imageFolder, "RightClick", "rightClick.png"))
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
            afterRightPath = os.path.join(self.imageFolder, "RightClick", "afterRight.png")
            afterOptionPath = os.path.join(self.imageFolder, "RightClick", "after" + option + ".png")
            ImageGrab.grab(bbox=self.boundBoxNoDash).save(afterOptionPath)
            box = self.get_bbox(afterRightPath, afterOptionPath)
            print option + " box: %s" % (box,)
            (boxW, boxH) = (box[2] - box[0] + 1, box[3] - box[1] + 1)
            print option + " box WxH: %s" % ((boxW, boxH),)
            (x1, y1) = (box[0], box[1])
            optionPath = os.path.join(self.imageFolder, "RightClick", option + ".png")
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
            located = auto.locateOnScreen(os.path.join(self.imageFolder, "RightClick", "rightClick.png"))
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

    def acklowledment(self, sequence_list):
        ack_init_ts = time.time()
        # bring the python window to the  front
        os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
        auto.PAUSE = 0.5
        self.root_window.deiconify()
        pressed = False
        y_pressed = False
        # Init colors
        first_row = True
        for btn_index in range(len(self.btn_list)-1):
            print "dictionary check:", sequence_list[btn_index]
            if sequence_list[btn_index] in self.cmd_dict:
                btn_tex = self.cmd_dict[sequence_list[btn_index]]
            else:
                print "WRONG TASK"
                return None
            if first_row:
                self.btn_list[btn_index]['fg'] = self.fg_colors[1]
                self.btn_list[btn_index]['bg'] = self.bg_colors[1]
                first_row = False
            else:
                self.btn_list[btn_index]['fg'] = self.fg_colors[0]
                self.btn_list[btn_index]['bg'] = self.bg_colors[0]
            self.btn_list[btn_index]['text'] = btn_tex
        self.btn_list[-1]['fg'] = self.fg_colors[0]
        self.btn_list[-1]['bg'] = self.bg_colors[0]
        self.root_window.update_idletasks()
        self.root_window.update()

        option = 0
        option_number = len(sequence_list)+1
        print "I GOT HERE"
        while True:
            print "INSIDE LOOP"
            if keyboard.is_pressed('3') and not pressed:
                pressed= True
                highlight_index = option % option_number
                self.btn_list[highlight_index]['fg'] = self.fg_colors[0]
                self.btn_list[highlight_index]['bg'] = self.bg_colors[0]
                option += 1
                highlight_index = option % option_number
                self.btn_list[highlight_index]['fg'] = self.fg_colors[1]
                self.btn_list[highlight_index]['bg'] = self.bg_colors[1]

            elif keyboard.is_pressed('y') and not y_pressed:
                y_pressed = True
                text_index = option % option_number
                self.openWindow(self.viewer)
                auto.PAUSE = 1
                if text_index == option_number -1:
                    sub_win_w = 1395
                    sub_win_h = 730
                    window = Toplevel(self.root_window,width=sub_win_w,height=sub_win_h)
                    window.geometry('%dx%d+%d+%d' % (sub_win_w, sub_win_h, 20, 50))
                    cmd_keys = self.cmd_dict.keys()
                    column_number = 3
                    num_of_cmds = len(cmd_keys)
                    column_elem_num = num_of_cmds/column_number
                    cmd_keys.sort(key=turn_int)
                    # create the windows with all the commands
                    option_matrix = []
                    for i in range(3):
                        max_j = column_elem_num if i < 2 else num_of_cmds - column_elem_num*(column_number-1)
                        column = []
                        for j in range(max_j):
                            label = Label(window,font=self.big_font,
                                text=self.cmd_dict[cmd_keys[i*column_elem_num+j]],
                                background = self.bg_colors[0],
                                borderwidth=2, relief="groove", width=22
                                )
                            label.grid(row=j, column=i, padx=10, pady=10)
                            column.append(label)
                        option_matrix.append(column)
                    window.lift()
                    window.attributes("-topmost", True)
                    sub_pressed = [False, False, False, False]
                    keys = ['3','2','1','4']
                    option_modifier = [1,-1,-1,1]
                    column_option = 0
                    row_option = 0
                    highlight_row = 1
                    highlight_col = 0

                    # Make the first element highlighted
                    option_matrix[0][0]['fg'] = self.fg_colors[1]
                    option_matrix[0][0]['bg'] = self.bg_colors[1]
                    while True:
                        for pressed_index in range(len(keys)):
                            if keyboard.is_pressed(keys[pressed_index]) \
                                    and not sub_pressed[pressed_index]:
                                sub_pressed[pressed_index]= True
                                highlight_row = row_option % len(option_matrix)
                                highlight_col = column_option % len(option_matrix[highlight_row])
                                print("UNHIGHLIGHTING =", highlight_col, highlight_row)
                                option_matrix[highlight_row][highlight_col]['fg'] = self.fg_colors[0]
                                option_matrix[highlight_row][highlight_col]['bg'] = self.bg_colors[0]
                                # if up or down
                                if pressed_index < 2:
                                    column_option += option_modifier[pressed_index]
                                    highlight_col = column_option % len(option_matrix[highlight_row])
                                else:
                                    row_option += option_modifier[pressed_index]
                                    highlight_row = row_option % len(option_matrix)
                                    highlight_col = column_option % len(option_matrix[highlight_row])
                                    column_option = highlight_col
                                option_matrix[highlight_row][highlight_col]['fg'] = self.fg_colors[1]
                                option_matrix[highlight_row][highlight_col]['bg'] = self.bg_colors[1]

                        for pressed_index in range(len(keys)):
                            if not keyboard.is_pressed(keys[pressed_index]):
                                sub_pressed[pressed_index] = False
                            if not keyboard.is_pressed('y'):
                                y_pressed = False

                        if keyboard.is_pressed('y') and not y_pressed:
                            y_pressed = True
                            #Get the selected option
                            row_num = row_option % len(option_matrix)
                            col_num = column_option % len(option_matrix[highlight_row])
                            key_index = row_num*len(option_matrix[0]) + col_num
                            window.destroy()
                            self.root_window.withdraw()
                            self.openWindow(self.viewer)
                            auto.PAUSE = 1
                            ack_end_ts = time.time()
                            return ack_init_ts, ack_end_ts, cmd_keys[key_index], True

                        self.root_window.update_idletasks()
                        self.root_window.update()
                else:
                    self.root_window.withdraw()
                    self.openWindow(self.viewer)
                    auto.PAUSE = 1
                ack_end_ts = time.time()
                return ack_init_ts, ack_end_ts, sequence_list[text_index], False

            elif keyboard.is_pressed('x') and not pressed:
                self.root_window.withdraw()
                self.openWindow(self.viewer)
                auto.PAUSE = 1
                ack_end_ts = time.time()
                return ack_init_ts, ack_end_ts, None, False

            if not keyboard.is_pressed('3'):
                pressed = False
            if not keyboard.is_pressed('y'):
                y_pressed = False
            # except:
                # break #if user pressed other than the given key the loop will break   while 1:
            self.root_window.update_idletasks()
            self.root_window.update()
        # time.sleep(1.5)

    def gestureCommands(self, sequence_list):
        # add the gesture timestamps and the 5 command options to the file recording
        recording_line = sequence_list
        print "RECEIVED: ", sequence_list
        ack_init_t, ack_end_ts, sequence, more_cmd_bool = self.acklowledment(sequence_list[2:])
        print ("EXECUTING", sequence)
        (commandID, actionID) = (-1, -1)
        commandAction = self.finalCmd.get_command(sequence)
        # commandAction = sequence
        # add the acknowlegment timestamps, the final comand and
        # the information about more commands usage to the file recording
        recording_line += [ack_init_t, ack_end_ts, sequence, more_cmd_bool]

        synapse_init_ts = time.time()
        ############# CHECK THAT THE COMMAND IS VALID ####################
        ##################################################################
        if commandAction is None:
            synapse_end_ts = time.time()
            recording_line += [synapse_init_ts, synapse_init_ts]
            self.recording_file.writerow(recording_line)
            print "RETURNING IN HERE"
            return False
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
            scrollAmount = (5 if self.status["params"] == "" else int(self.status["params"]))
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
                auto.PAUSE = 0.25
                auto.mouseDown()
                # add the context if we are just performing a context
                self.status["defaultCommand"] = command
            # if we are performing a zoom in or a zoom out
            if actionID != 0:
                # Get the level, acording to the params or default
                if (len(splitParams) % 2 == 1 and self.status["params"] != ""):
                    level = (-1 * int(splitParams[0]) if action == "In" else int([0]))
                else:
                    level = (-75 if action == "In" else 75)
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
            # TODO change if we are going to use more than 1 by X pannel configs
            self.status["active_panel"][1] += (-1 if action == "Left" or action == "Up" else 1)
            self.status["active_panel"][1] = max(0, self.status["active_panel"][1])
            self.status["active_panel"][1] = min(self.status["active_panel"][1], self.status["panel_dim"][1]-1)
            print("active pannels:",self.status["active_panel"])
            print("layout:",self.status["panel_dim"])
            self.moveToActivePanel()
            auto.click()

        ####################################################
        ###################### PAN #########################
        ####################################################

        elif (command == "Pan" and action != "Pan"):
            splitParams = self.status["params"].split("_")
            self.moveToActivePanel()
            auto.click()
            auto.click(button='right')
            auto.PAUSE = 0.1
            auto.press("0")
            auto.press("p")
            auto.PAUSE = 0
            auto.press("enter")
            auto.PAUSE = 0.25
            # (auto.press(e) for e in ["p", "enter"])
            # Get the jump of the pan acording to the parameters
            if (len(splitParams) % 2 == 1 and self.status["params"] != ""):
                level = (int(splitParams[0]) if action == "Left" or action == "Up" else -1 * int(splitParams[0]))
            else:
                level = (20 if action == "Left" or action == "Up" else -20)
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
            auto.mouseDown()
            print "moving from:", moveToX, moveToY
            print "moving to:",  toMoveX, toMoveY
            auto.moveTo(toMoveX, toMoveY)
            auto.mouseUp()

        ####################################################
        ###################### WINDOW  ######################
        ####################################################

        # General way it should work, but it would have issues.
        # For now, don't test Window Open/Close (no 8_1 or 8_2)
        elif (command == "Ruler" and action != "Ruler"):
            # Ucomment the return to not ignore window
            return True

        ####################################################
        ###################### WINDOW ######################
        ####################################################

        # General way it should work, but it would have issues.
        # For now, don't test Window Open/Close (no 8_1 or 8_2)
        elif (command == "Window" and action != "Window"):
            # Ucomment the return to not ignore window
            return True
            if (action == "Open" and not self.status["window_open"]):
                if (platform.system() == "Windows"): auto.hotkey("win", "alt", "e")
                else: auto.hotkey("command", "altright", "e")
                time.sleep(5)
            elif (action == "Close" and self.status["window_open"]):
                if (platform.system() == "Windows"):
                    self.openWindow(self.viewer, True)
                    auto.hotkey("fn", "alt", "f4")
                else: auto.hotkey("command", "altright", "f4")

        ####################################################
        ################ MANUAL CONTRAST ###################
        ####################################################
        elif (command == "Manual Contrast"):
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
                auto.PAUSE = 0.1
                auto.press("w")
                auto.PAUSE = 0.25
                auto.mouseDown()
                # add the context if we are just performing a context
                self.status["defaultCommand"] = command
            # if we are performing a zoom in or a zoom out
            if actionID != 0:
                (oldLocationX, oldLocationY) = auto.position()
                if (len(splitParams) == 1):
                    if (splitParams[0] != ""):
                        level = (-1 * int(splitParams[0]) if action == "Decrease" else int(splitParams[0]))
                    else:
                        level = (-10 if action == "Decrease" else 10)
                else:
                    print "For " + command + ", you must pass a maximum of one argument."
                    synapse_end_ts = time.time()
                    recording_line += [synapse_init_ts, synapse_init_ts]
                    self.recording_file.writerow(recording_line)
                    return False
                auto.moveTo(oldLocationX, oldLocationY + level)
                self.status["group1_command"] = command

        ####################################################
        ##################### LAYOUT #######################
        ####################################################
        elif (command == "Layout" and action != "Layout"):
            # Set using_pictures to True to get panels with pyautogui instead of a
            # hardcoded position
            hardcoded_x = 410
            hardcoded_y = 230
            using_pictures = False
            # NOTE: DIVIDE BY TWO ONLY IN THE MAC. IT HAS THAT PROBLEM
            # Move to the top of the screen so the menu appears
            self.moveToActivePanel()
            time.sleep(2)
            auto.click()
            auto.moveTo(auto.position()[0], 0)
            time.sleep(2)
            # Look for the image of the layout
            layoutPath = os.path.join(self.imageFolder, "Layout", "layout.png")
            # get the center of the image
            (center_x, center_y) = auto.locateCenterOnScreen(layoutPath)
            auto.click(center_x/2,center_y/2)
            # wait for the image to appear
            time.sleep(4)
            # Get the image name depending on the action:
            if (using_pictures):
                optionImgName = str(actionID) + ".png"
                layoutOptionPath = os.path.join(self.imageFolder, "Layout", optionImgName)
                print layoutOptionPath
                (center_x, center_y) = auto.locateCenterOnScreen(layoutOptionPath)
                auto.click(center_x/2,center_y/2)
            else:
                # clicl in the position of the panel
                auto.click(hardcoded_x + 70*actionID,hardcoded_y)
            self.status["panel_dim"] = [1, actionID]
            self.status["active_panel"] = [0, 1] if actionID ==3 else [0,0]
            time.sleep(2)
            self.resetPanelMoves()
            self.moveToActivePanel()
            auto.click()


        ####################################################
        ################ CONTRAST PRESETS ##################
        ####################################################

        elif (command == "Contrast Presets" and action != "Contrast Presets"):
            self.moveToActivePanel()
            auto.click()
            auto.click(button='right')
            auto.PAUSE = 0.1
            for key in ["0", "i", "right"]:
                auto.press(key)
                auto.PAUSE = 0.1
            time.sleep(0.5)
            auto.press("0")
            for i in range(actionID + 1):
                auto.press("down")
                auto.PAUSE = 0.1
            auto.press("enter")
            auto.PAUSE = 0.25
            time.sleep(1)

        synapse_end_ts = time.time()
        recording_line += [synapse_init_ts, synapse_init_ts]
        self.recording_file.writerow(recording_line)
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
    command_list = ["4_1", "6_0", "6_3", "6_3", "6_3"]
    command_list = ["4_1", "6_0", "6_3", "6_4", "6_3"]
    command_list = ["4_1","6_1", "6_2", "6_3", "6_4", "6_4", "6_3", "6_2", "6_1"]
    command_list = ["9_0", "9_2", "4_0", "9_2", "3_1", "9_1"]
    command_list = ["11_1", "11_2", "4_1", "11_1"]
    command_list = ["10_1", "10_2", "10_3", "10_4"]

    # For now, don't test Window Open/Close (no 8_1 or 8_2)

    for cmd in command_list:
        success = syn_action.gestureCommands(cmd)
        print "execution of command", cmd, "flag:", success
        time.sleep(3)

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
