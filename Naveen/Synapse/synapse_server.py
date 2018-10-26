import numpy as np
import os, sys
import random, socket
from threading import Thread
import time
import cv2 as cv

## This is a script. Be careful where it is being imported.
# import synapseCommandAction as sca

####
# Sometimes it 'Connection closes' saying timed out. Look into it.
#
# Happens bacuse of the socket.setdefaulttimeout(2) in ex_client. If 2 is made 10 then it's working fine. Checked many times
####

## Global Static Variables
# TCP_IP = socket.gethostbyname(socket.gethostname())
TCP_IP = 'localhost'
print "IP: ", TCP_IP

TCP_PORT = 10000
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
        self.sock = None
        # socket.setdefaulttimeout(30)
        self.init_socket()

    def init_socket(self):
        ## Waiting for establishing the connection between server and client
        self.sock_connect()
        self.wait_for_handshake()

    def sock_connect(self):
        print 'Waiting for clients: '
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Opening the socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        else:
            data = None
        return data

    def th_socket(self):
        # Call Aayush's Synapse command script
        if (not os.path.exists("calibration.txt")):
            ## Find the calibration parameters again
            synapse_Flag = sca.gestureCommands("0_4")
        received_data = None
        while True:
            # try:
            #     received_data = self.sock_recv()
            # except Exception as exp:
            #     print exp
            #     print 'Connection Closed'
            #     self.connect_status = False
            #     self.client.close()
            #     received_data = None

            received_data = self.sock_recv()


            if received_data is not None:
                # synapse_Flag = sca.gestureCommands(data) #it should return TRUE if command is executed properly
                synapse_Flag = True #it should return TRUE if command is executed properly
                time.sleep(2)
                if synapse_Flag:
                    print 'Received: ', received_data
                    print received_data, 'has been executed'
                self.client.sendall(str(synapse_Flag)) # Send the flag to the client once the execuction is done.
                print received_data, 'Flag sent'

            else:
                print 'Connection Closed'
                self.connect_status = False
                self.client.close()
                received_data = None

    def wait_for_handshake(self):
        print 'Waiting for connection: .'
        data = self.client.recv(BUFFER_SIZE)
        if data == INITIAL_MESSAGE:
            print 'Received a handshake'
            self.connect_status = True
            self.client.send(str(True))
        print 

    def run(self):
        sock_thread = Thread(name='server_thread', target=self.th_socket)
        sock_thread.start()

if __name__ == '__main__':
    print '--------- Server ---------'
    server = Server() ## Initialize server object
    server.run()
