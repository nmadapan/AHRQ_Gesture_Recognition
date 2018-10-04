import numpy as np
import os, sys
import random, socket
from threading import Thread
import time

####
# Sometimes it 'Connection closes' saying timed out. Look into it. 
# 
#
####

## Global Static Variables
TCP_IP = '128.46.125.218'
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
        socket.setdefaulttimeout(10)
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
            print 'Received a message'
            data_received = True
            # self.client.send(str(True)) # We want to send True, once the synapse execution is done and not now.
        return data

    def th_socket(self):
        while True:
            # if(not self.connect_status): self.wait_for_connection() # This is not relevant beccause
            #    wait_for_connection expects to receive INITIAL_MESSAGE
            try:
                data = self.sock_recv()
                print data
                ### Temporary
                time.sleep(1) # Lets say synapse took three seconds to finish the task.
                ### Temporary
                # Find a way to monitor synapse. when we should we send False ?
                self.client.send(str(True)) # Send True once the execuction is done. 
                time.sleep(0.5)
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