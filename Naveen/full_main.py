
# pose 1: head to extended arms very slowly 2 times.
# pose 2: very fast zoom out. 10 times.
# pose 3: very fast hand down. 10 times.
# have the two videos manually recorded
# ask for recorded folder, target folder and subject number
# batch process:
	# XeF files to get the skeleton data
	# calib routine on first vid to get max_r
	# calib rountin on second vid to get max_dr
	# calibrate fingers routine

# change real time routine so it reads the params from the args
# add the calib params to the real time routine
# call real time with the json params for calib

import Tkinter
import tkMessageBox

top = Tkinter.Tk()
def hello():
   tkMessageBox.showinfo("Say Hello", "Hello World")

B1 = Tkinter.Button(top, text = "Say Hello", command = hello)
B1.pack()

top.mainloop()