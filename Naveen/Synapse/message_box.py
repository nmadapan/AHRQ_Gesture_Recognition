import time
from Tkinter import *
import keyboard #Using module keyboard

master = Tk()
w = 400 # width for the Tk root
h = 115
# get screen width and height
ws = master.winfo_screenwidth() # width of the screen
hs = master.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# set the dimensions of the screen
# and where it is placed
master.geometry('%dx%d+%d+%d' % (w, h, x, y))

option = 0
bn1 = None

def callback():
    global option
    global bn1
    if option % 2 ==0 :
        bn1['highlightbackground']= '#FFFF00'
    else:
        bn1['highlightbackground']= '#8EF0F7'
    option += 1


"""Simple example showing how to get keyboard events."""

def main():
    global bn1
    bn1 = Button(master, text='Option 1', highlightbackground ="#8EF0F7", command=callback)
    bn1.pack(fill=X)
    bn2 = Button(master, text='Option 2', command=callback).pack(fill=X)
    bn3 = Button(master, text='Option 3', command=callback).pack(fill=X)

    """Just print out some event infomation when keys are pressed."""
    while True:#making a loop
        try: #used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('a'): #if key 'a' is pressed
                print('You Pressed A Key!')
                # break #finishing the loop
            else:
                pass
        except:
            break #if user pressed other than the given key the loop will break   while 1:
        master.update_idletasks()
        master.update()

if __name__ == "__main__":
    main()
