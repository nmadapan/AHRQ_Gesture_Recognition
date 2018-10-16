import numpy as np
import os, sys
import random, socket
from threading import Thread
import time

####
# Sometimes it 'Connection closes' saying timed out. Look into it. 
# 
# Happens bacuse of the socket.setdefaulttimeout(2) in ex_client. If 2 is made 10 then it's working fine. Checked many times
####

## Global Static Variables
# Call Aayush's Synapse command script
import synapseCommandAction as sca
if (not os.path.exists("Calibration.txt")):
    sca.gestureCommands("0_3")
while True:
    # if(not self.connect_status): self.wait_for_connection() # This is not relevant beccause
    #    wait_for_connection expects to receive INITIAL_MESSAGE
        #data = self.sock_recv()
    data = "6_1"
    synapse_Flag = True
    sca.gestureCommands(data)
    # print data
    ### Temporary
    # Find a way to monitor synapse. when we should we send False ?
    # synapse_Flag = synapse(data) #Aayush's code should be executed from here. Output shall be True or False
    # Pass in data to raw_input in Aayush's script
    time.sleep(3)
    #synapse_Flag=True
    if synapse_Flag:
        print data,'has been executed'
        print "exiting"