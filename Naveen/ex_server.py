import numpy as np
import os, sys
import random, socket
from threading import Thread
import time
from fake_synapse import synapse
import synapseCommandAction as sca

####
# Sometimes it 'Connection closes' saying timed out. Look into it. 
# 
# Happens bacuse of the socket.setdefaulttimeout(2) in ex_client. If 2 is made 10 then it's working fine. Checked many times
####

## Global Static Variables
TCP_IP = '10.186.130.21'

TCP_PORT = 5000
BUFFER_SIZE = 1024
MAX_CLIENTS = 1
INITIAL_MESSAGE = 'Handshake'

MAX_QUEUE_SIZE = 1028
QUEUE_PUSH_RATE = 10

class Server():
    def __init__(self):

        ## Socket variables
        self.connect_status = False # Connection not yet established. 
        self.client, self.addr = None, None
        self.fl_sock_com = False
        self.sock = None
        socket.setdefaulttimeout(30)
        self.init_socket()

    def init_socket(self):
        ## Waiting for establishing the connection between server and client
        self.sock_connect()
        self.wait_for_handshake()

    def sock_connect(self):
        print 'Waiting for clients: '
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Opening the socket
        self.sock.bind((TCP_IP, TCP_PORT))
        self.sock.listen(MAX_CLIENTS)
        self.client, self.addr = (self.sock.accept())
        self.connect_status = True

    def sock_recv(self):
        if(not self.connect_status): self.sock_connect()

        data_received = False
        data = self.client.recv(BUFFER_SIZE)
        # Send true, if you receive any string of nonzero length
        if len(data) != 0:
            print 'Received command',data
            data_received = True
            # self.client.send(str(True)) # We want to send True, once the synapse execution is done and not now.
        return data

    def th_socket(self):
        # Call Aayush's Synapse command script

        if (not os.path.exists("Calibration.txt")):
            sca.gestureCommands("0_3")
            time.sleep(20)
        while True:
            # if(not self.connect_status): self.wait_for_connection() # This is not relevant beccause
            #    wait_for_connection expects to receive INITIAL_MESSAGE
            try:
                data = self.sock_recv()
                # print data
                ### Temporary
                # Find a way to monitor synapse. when we should we send False ?
                # synapse_Flag = synapse(data) #Aayush's code should be executed from here. Output shall be True or False
                # Pass in data to raw_input in Aayush's script
                synapse_flag=sca.gestureCommands(data[0], data[1]) #it should return TRUE if command is executed properly

                #synapse_Flag=True
                if synapse_Flag:
                    print data,'has been executed'
                    self.client.send(str(True)) # Send True once the execuction is done.
                
            except Exception as exp:
                print exp
                print 'Connection Closed'
                self.connect_status = False
                self.client.close()

    def wait_for_handshake(self):
        print 'Waiting for connection: .'
        data = self.client.recv(BUFFER_SIZE)
        if data == INITIAL_MESSAGE:
            print 'Received a handshake'
            self.connect_status = True
            self.client.send(str(True))

    def run(self):
        sock_thread = Thread(name='server_thread', target=self.th_socket)
        sock_thread.start()
        

if __name__ == '__main__':
    print '--------- Server ---------'
    server = Server()
    server.run()