import time
from Tkinter import *
import tkFont
import keyboard #Using module keyboard

master = Tk()
helv36 = tkFont.Font(family='Helvetica', size=36, weight='bold')
w = 400 # width for the Tk root
h = 300
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
bn_list = []



def separator():
    Label(master=master,background='#FFFFFF',text='separator',fg='#FFFFFF').pack(fill=X)

def main():
    global bn1
    bg_colors = ['#C0C0C0', '#002dd3']
    fg_colors = ['#000000', '#FFFFFF']
    separator()
    bn_list.append(Label(master=master, font=helv36, text='Option 1', background = '#C0C0C0',  highlightbackground ="#8EF0F7"))
    bn_list[-1].pack(fill=X)
    separator()
    # bn3.grid(row=2, column=0, pady=(0, 10))
    bn_list.append(Label(master=master, font=helv36, text='Option 2', background = '#C0C0C0'))
    # bn2.pack(fill=X)
    bn_list[-1].pack(fill=X)
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
                bn_list[0]['text'] = "Option" + str(option)
                bn_list[0]['fg'] = fg_colors[index]
                bn_list[0]['bg'] = bg_colors[index]
                option += 1
            if not keyboard.is_pressed('j'):
                pressed = False
        except:
            break #if user pressed other than the given key the loop will break   while 1:
        master.update_idletasks()
        master.update()

if __name__ == "__main__":
    main()
