import time
from Tkinter import *
import tkFont
import keyboard #Using module keyboard

master = Tk()
helv36 = tkFont.Font(family='Helvetica', size=36, weight='bold')
w = 400 # width for the Tk root
h = 400
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


def separator():
    Label(master=master,background='#FFFFFF',text='separator',fg='#FFFFFF').pack(fill=X)

def main():
    global bn1
    bg_colors = ['#C0C0C0', '#002dd3']
    fg_colors = ['#000000', '#FFFFFF']
    separator()
    bn1 = Label(master=master, font=helv36, text='Option 1', background = '#C0C0C0',  highlightbackground ="#8EF0F7")
    bn1.pack(fill=X)
    separator()
    # bn3.grid(row=2, column=0, pady=(0, 10))
    bn2 = Label(master=master, font=helv36, text='Option 2', background = '#C0C0C0')
    bn2.pack(fill=X)
    separator()
    bn3 = Label(master=master, font=helv36, text='Option 3', background = '#C0C0C0')
    bn3.pack(fill=X)
    separator()
    # bn1.grid(row=0, column=0, pady=(0, 10))
    # bn2.grid(row=1, column=0, pady=(0, 10))
    # bn3.grid(row=2, column=0, pady=(0, 10))

    """Just print out some event infomation when keys are pressed."""
    option = 0
    pressed = False
    while True:#making a loop
        try: #usedtry so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('j') and not pressed: #if key 'a' is pressed
                pressed = True
                index = option % 2
                bn1['text'] = "Option" + str(option)
                bn1['fg'] = fg_colors[index]
                bn1['bg'] = bg_colors[index]
                option += 1
                print("MAAAAW")
            if not keyboard.is_pressed('j'):
                pressed = False
        except:
            break #if user pressed other than the given key the loop will break   while 1:
        master.update_idletasks()
        master.update()

if __name__ == "__main__":
    main()
