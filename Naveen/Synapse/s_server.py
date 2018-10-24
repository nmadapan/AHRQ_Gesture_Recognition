import os, sys, time, inspect
from threading import Thread
######### Add parent directory at the beggining of the path #######
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
###################################################################
import synapseCommandAction as sca

from CustomSocket import Server 

class SynapseServer(Server):
    def run(self, only_once = True):
        if (not os.path.exists("calibration.txt")):
            ## Find the calibration parameters again
            synapse_Flag = sca.gestureCommands("0_4")    
        ########################
        # Receives a data string from a client, prints it, sends True/False to the client
        # If only_once is True, it will receive only one data string. Otherwise, it will receive infinitely. 
        ########################        
        print('--------- Server ---------')
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.client.recv(self.buffer_size)
                synapse_Flag = sca.gestureCommands(data) #it should return TRUE if command is executed properly
                # synapse_Flag = True #it should return TRUE if command is executed properly
                if synapse_Flag:
                    print("Command: ",data, "was executed")
                self.client.send(str(synapse_Flag))
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                if(only_once): break 


if __name__ == '__main__':
    #### Variables #######
    tcp_ip = 'localhost'
    tcp_port = 10000 

    # Initialize the server Thread
    server = SynapseServer(tcp_ip, tcp_port, buffer_size = 1000000)
    server_thread = Thread(name='server_thread', target=server.run)    
    server_thread.start()