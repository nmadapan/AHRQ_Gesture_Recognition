import numpy as np
import os, sys
import random, socket
from threading import Thread
import time

## Global Static Variables
TCP_IP = '128.46.125.209'
TCP_PORT = 5000
BUFFER_SIZE = 1024
MAX_CLIENTS = 1
INITIAL_MESSAGE = 'Handshake'

MAX_QUEUE_SIZE = 1028
QUEUE_PUSH_RATE = 10

class Server():
    def __init__(self):
        ## Socket Initialization
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Opening the socket
        self.sock.bind((TCP_IP, TCP_PORT))
        self.sock.listen(MAX_CLIENTS)
        self.connect_status = False # Connection not yet established.

        self.client, self.addr = None, None
        ## Waiting for establishing the connection between server and client
        self.wait_for_connection()

    def th_socket(self):
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.client.recv(BUFFER_SIZE)
                ### Temporary
                time.sleep(3) # Lets say synapse took three seconds to finish the task.
                ### Temporary
                self.client.send(str(True))
                print data
                time.sleep(0.5)
            except Exception as exp:
                print exp
                print 'Connection Closed'
                self.connect_status = False
                self.client.close()

    def wait_for_connection(self):
        print 'Waiting for connection: .'
        self.client, self.addr = (self.sock.accept())
        data = self.client.recv(BUFFER_SIZE)
        if data == INITIAL_MESSAGE:
            print 'Received a handshake'
            self.connect_status = True
            self.client.send(str(True))

    def run(self):
        sock_thread = Thread(name='server_thread', target=server.th_socket)
        synapse_thread = Thread(name='synapse_thread', target=server.th_synapse)

        sock_thread.start()
        synapse_thread.start()
        

if __name__ == '__main__':
    print '--------- Server ---------'
    server = Server()
    server.run()