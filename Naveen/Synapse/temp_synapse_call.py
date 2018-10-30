import numpy as np
import os, sys
import random, socket
from threading import Thread
import time
import traceback


####
# Sometimes it 'Connection closes' saying timed out. Look into it.
#
# Happens bacuse of the socket.setdefaulttimeout(2) in ex_client. If 2 is made 10 then it's working fine. Checked many times
####
#dataList = ["1_1 40", "1_2 30", "2_1", "2_2", "3_1", "3_2", "4_1 250_600_450", "4_2 30", "6_1", "6_2 500_630", "6_3 80", "6_4 40", "7_1 500_600_700_800", "7_1 400_300_900_500", "7_2 2", "7_2 1", "8_1", "8_2", "9_1 60", "9_2 30", "10_4", "5_1", "5_2", "5_3", "5_4", "5_1", "0_2", "11_1", "11_2"]
dataList = ["10_2"]
# 0_3 to toggle between keyboard and images...the first 0_3 switches from keyboard to images

## Global Static Variables
# Call Aayush's Synapse command script
import synapseCommandAction as sca
#if (not os.path.exists("calibration1920_1080_1.txt")):
#    synapse_Flag = sca.gestureCommands("0_4 All")
i = 0
while True and i < len(dataList):
    # if(not self.connect_status): self.wait_for_connection() # This is not relevant beccause
    #    wait_for_connection expects to receive INITIAL_MESSAGE
    try:
        data = dataList[i]
        print "Running command: " + str(data)
        # print data
        ### Temporary
        # Find a way to monitor synapse. when we should we send False ?
        # synapse_Flag = synapse(data) #Aayush's code should be executed from here. Output shall be True or False
        # Pass in data to raw_input in Aayush's script
        synapse_Flag=sca.gestureCommands(data) #it should return TRUE if command is executed properly
        #time.sleep(10)

        if synapse_Flag:
            print data,'has been executed'
            time.sleep(2)
            #self.client.send(str(True)) # Send True once the execution is done.
        else:
            print data,'has failed execution'
        i += 1

    except Exception as exp:
        print exp
        print 'Connection Closed'
        traceback.print_exc(file=sys.stdout)
        break
        #self.connect_status = False
        #self.client.close()

# Open command prompt or Terminal when finished with synapse commands
import platform
sca.openWindow("Command Prompt" if platform.system() == "Windows" else "Terminal")
