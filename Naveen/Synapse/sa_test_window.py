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
import json

(width, height) = tuple(float(e) for e in auto.size())
(nativeW, nativeH) = tuple(float(e) for e in ImageGrab.grab().size)
scale = nativeW / width
# Get the Synapse window
(macH, viewer, prompt) = (44.0 * nativeW / 2880.0, "Citrix Viewer", "Terminal")

status = {"prev_action": "", "panel_dim": [1, 1],
    "window_open": False, "active_panel": [1, 1],
    "rulers": {"len": 0}, "toUse": "Keyboard",
    # "hold_action": None,
    "topBarHeight": None, "defaultCommand": None, "group1_command": None,
    "firstW": None, "firstH": None, "jumpW": None,"jumpH": None}


os.system("open -a " + viewer.replace(" ", "\\ "))

auto.moveTo(width / 2, height / 2)
time.sleep(1)
auto.click()
# original Page with a dash
time.sleep(1)
regularPath = os.path.join("SCA_Images", "Window", "regular.png")
regular = ImageGrab.grab(bbox=(0, macH, nativeW, nativeH))
regular.save(regularPath)
# new page without the dash, "ICA Seamless Host Agent"
auto.hotkey("alt", "tab")
time.sleep(1)
icaSHAPath = os.path.join("SCA_Images", "Window", "icaSHA.png")
icaSHA = ImageGrab.grab(bbox=(0, macH, nativeW, nativeH))
icaSHA.save(icaSHAPath)
# everything including and inside the dash
status["window_bbnd"] = ImageChops.difference(regular, icaSHA).size
auto.hotkey("alt", "tab")
# patient info window pop-up
auto.hotkey("command", "altleft", "e")
time.sleep(5)
auto.moveTo(0, height / 2.0)
# patient info window without a dash
patInfoPath = os.path.join("SCA_Images", "Window", "patInfo.png")
patInfo = ImageGrab.grab(bbox=(0, macH, nativeW, nativeH))
patInfo.save(patInfoPath)
# Get the patient information window box
patInfoBox = ImageChops.difference(icaSHA, patInfo).getbbox()
print str(patInfoBox)
window = patInfo.crop(box=patInfoBox)
window.save(os.path.join("SCA_Images", "Window", "window.png"))
# Save Close
seriesClosePath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose.png")
(x1, y1, x2, y2) = patInfoBox
(tempX, tempY) = (x2, y1)
(x1, y1) = (tempX + ((-14.0 - 90.0) * scale / 2.0), tempY + (3.0) * scale / 2.0)
(x2, y2) = (tempX + (-14.0) * scale / 2.0, tempY + (43.0) * scale / 2.0)
print str(tuple((x1, y1, x2, y2)))
print str(tuple((x2 - x1, y2 - y1)))
seriesClose = ImageGrab.grab(bbox=(x1, y1 + macH, x2, y2 + macH))
seriesClose.save(seriesClosePath)
# patient info window gray without a dash
auto.keyDown("alt")
auto.press("tab")
auto.press("tab")
auto.keyUp("alt")
time.sleep(1)
patInfoGrayPath = os.path.join("SCA_Images", "Window", "patInfoGray.png")
patInfoGray = ImageGrab.grab(bbox=(0, macH, nativeW, nativeH))
patInfoGray.save(patInfoGrayPath)
window_gray = patInfoGray.crop(box=patInfoBox)
window_gray.save(os.path.join("SCA_Images", "Window", "window_gray.png"))
# Save Close_Gray
seriesClose_GrayPath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose_Gray.png")
seriesClose_Gray = ImageGrab.grab(bbox=(x1, y1 + macH, x2, y2 + macH))
seriesClose_Gray.save(seriesClose_GrayPath)
auto.hotkey("alt", "tab")
# Hover over close box, save Close_Red
auto.moveTo((x1 + x2) / (2.0 * scale), (y1 + y2) / (2.0 * scale) + macH / scale)
time.sleep(1)
patInfoRedPath = os.path.join("SCA_Images", "Window", "patInfoRed.png")
patInfoRed = ImageGrab.grab(bbox=(0, macH, nativeW, nativeH))
patInfoRed.save(patInfoRedPath)
window_red = patInfoRed.crop(box=patInfoBox)
window_red.save(os.path.join("SCA_Images", "Window", "window_red.png"))
seriesClose_RedPath = os.path.join("SCA_Images", "Window", "Closes", "seriesClose_Red.png")
seriesClose_Red = ImageGrab.grab(bbox=(x1, y1 + macH, x2, y2 + macH))
seriesClose_Red.save(seriesClose_RedPath)
status["window_open"] = True
time.sleep(5)
os.system("open -a " + prompt.replace(" ", "\\ "))
print "Window Open Finished"
time.sleep(5)
os.system("open -a " + prompt.replace(" ", "\\ "))

auto.moveTo(width / 2, height / 2)
for file in os.listdir(os.path.join("SCA_Images", "Window", "Closes")):
    if (not file.endswith(".png")): continue
    close = auto.locateCenterOnScreen(os.path.join("SCA_Images", "Window", "Closes", file))
    if (close is not None):
    	print file
        #(x1, y1, w, h) = close
        #auto.moveTo((2 * x1 + w) / (scale * 2.0), (2 * y1 + h) / (scale * 2.0))
        (x, y) = close
        print close
        auto.moveTo(x / scale, y / scale)
        auto.click()
        status["window_open"] = (not status["window_open"])
        break
#auto.hotkey("command", "fn", "f4")


os.system("open -a " + prompt.replace(" ", "\\ "))
print "Window Close Finished"

