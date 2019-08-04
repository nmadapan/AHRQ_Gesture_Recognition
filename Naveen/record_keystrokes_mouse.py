
# coding: utf-8

# In[ ]:

# an example of tracking activities
import pyHook
import pythoncom
import os
from os.path import join, basename, dirname, isdir
import time
import argparse
import sys
import ctypes

lexicon_id = 'L0'
subject_id = 'S22'
task_id = 'T1'
base_write_folder = r'D:\AHRQ\Study_V\Study_V_Data'

##########################
#####   PARSING       ####
##########################
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lexicon_id", default=lexicon_id,
					help=("Example: L1"))
parser.add_argument("-s", "--subject_id", default=subject_id,
					help=("Example: S1"))
parser.add_argument("-t", "--task_id", default=task_id,
					help=("Example: T1"))
args = vars(parser.parse_args())

subject_id = args['subject_id']
lexicon_id = args['lexicon_id']
task_id = args['task_id']

fname = '_'.join([subject_id, lexicon_id, task_id])
folder_path = join(base_write_folder, lexicon_id)

if(not isdir(folder_path)): os.makedirs(folder_path)
cur_time = str(int(time.time()))

k_path = join(folder_path, fname+'_km_'+cur_time+'.txt')

def left_down(event):
    #print("left click - "+ str(event.Position))
    a = str((time.time()))
    with open(k_path,"a+") as f:
        f.write(a+" Left click "+ str(event.Position)+'\n') 
    return True # if return false, the event will not be passed on to other programs. 
                # The cursor will appear freeze

def right_down(event):
    #print ("right click - "+str(event.Position))
    a = str((time.time()))
    with open(k_path,"a+") as f:
        f.write(a+" Right click "+ str(event.Position)+'\n')
    return True    

def middle_down(event):
    #print("middle click - "+str(event.Position))
    a = str((time.time()))
    with open(k_path,"a+") as f:
        f.write(a+" Middle click "+ str(event.Position)+'\n')
    return True

prev_key = None
curr_key = None

def OnKeyboardEvent(event):
    global curr_key, prev_key
    a = str((time.time()))
    with open(k_path,"a+") as f:
        f.write(a+" Key "+str(event.Key)+'\n')
    prev_key = curr_key
    curr_key = str(event.Key)
    if(prev_key in ['Lcontrol', 'Rcontrol'] and curr_key in ['c', 'C']):
        hm.UnhookMouse()
        hm.UnhookKeyboard()
        ctypes.windll.user32.PostQuitMessage(0)

    return True

hm = pyHook.HookManager()    

# hook mouse
hm.SubscribeMouseLeftDown(left_down)
hm.SubscribeMouseRightDown(right_down)
hm.SubscribeMouseMiddleDown(middle_down)

hm.HookMouse()

#hook keyboard
hm.KeyDown = OnKeyboardEvent # watch for all keyboard events
hm.HookKeyboard()

pythoncom.PumpMessages()
hm.UnhookMouse()
hm.UnhookKeyboard()