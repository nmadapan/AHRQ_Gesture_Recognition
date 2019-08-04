import time
import pyautogui as auto

def change_tab(previous_pause):
    auto.PAUSE = 0.1
    auto.keyDown('command')
    auto.press('tab')
    auto.keyUp('command')
    auto.PAUSE = previous_pause

for i in range(10):
    change_tab()
    
