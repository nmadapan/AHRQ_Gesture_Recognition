from __future__ import print_function
import numpy as np
import os, sys
import random, socket
from threading import Thread
import time
# import cv2

## Global Static Variables
INITIAL_MESSAGE = 'Handshake'

class Server():
    def __init__(self, tcp_ip = 'localhost', tcp_port = 5000, max_clients = 1, buffer_size = 1024):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.max_clients = max_clients
        self.buffer_size = buffer_size

        ## Socket Initialization
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Opening the socket
        self.sock.bind((self.tcp_ip, self.tcp_port))
        self.sock.listen(self.max_clients)
        self.connect_status = False # Connection not yet established.

        self.client, self.addr = None, None
        ## Waiting for establishing the connection between server and client
        # self.wait_for_connection() # In realtime, call wait_for_connection from outside. 

    def recv_image(self, buf_sz = 200000):
        #####################
        # When a large image is sent in the form of a string, it will be sent in multiple parts. 
        # IMPORTANT: The image string is expected to end with '!' 
        # This function puts the parts together and returns the full image string. 
        # Format of image string:
        #   256_256_3_126_68_56...34!
        #   First three numbers (256, 256, 3) is the shape of RGB image. 
        # Return:
        #   A string of the form: 256_256_3_126_68_56...34
        #####################
        data = self.client.recv(buf_sz) # Obtain each part
        if(len(data) == 0): return None

        flag = False
        if(data[-1] != '!'): flag = True
        num_chunks = 1
        while(flag): # Loop until the a part ends with '!'
            num_chunks += 1
            data += self.client.recv(buf_sz) # Append parts together
            if(data[-1] == '!'): flag = False
        print('No. of chunks: ', num_chunks)
        return data[:-1]

    def example_run_image(self, only_once = True):
        ########################
        # Receives an image string from a client, converts it into an ndarray, sends True/False to the client
        # If only_once is True, it will receive only one image. Otherwise, it will receive infinitely. 
        ########################
        print('--------- Server ---------')
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.recv_image() # Obtain the image
                flag = self.process_data(data) # Reformat the image string into a np.ndarray
                self.client.send(str(flag is not None)) # Return a delivery message. 
                time.sleep(0.5)
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                if(only_once): break 

    def run(self, only_once = True):
        ########################
        # Receives a data string from a client, prints it, sends True/False to the client
        # If only_once is True, it will receive only one data string. Otherwise, it will receive infinitely. 
        ########################        
        print('--------- Server ---------')
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.client.recv(self.buffer_size)
                print(data)
                if(len(data) != 0): self.client.send(b'True')
                else: self.client.send(b'False')
                time.sleep(0.5)
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                if(only_once): break 

    def wait_for_connection(self):
        ######################
        # This function established connection with the client.
        ######################
        print('Server: Waiting for connection:')
        self.client, self.addr = (self.sock.accept())
        data = self.client.recv(self.buffer_size)

        if data == INITIAL_MESSAGE.encode('utf-8'):
            print('Success: Received: ', data)
            self.connect_status = True
            self.client.send(b'True')
        else:
            print('Failure: Received: ', data)
            self.connect_status = False
            self.client.send(b'False')

    def process_data(self, data):
        ###########################
        # Input:
        #   data is of form: 256_256_3_126_68_56...34
        #   Convert the image string into an RGB image
        #   Image string is joined with '_'. 
        #   (256, 256, 3) is the shape of the image. The 
        # Return:
        #   An ndarray which is an RGB image. 
        ###########################
        if(data is None or len(data) == 0): return None

        data = data.split('_')
        print(len(data))
        img_shape = tuple(map(int, data[:3])) # Shape of the image
        data = data[3:] 
        B = np.reshape(map(np.uint8, data), img_shape)
        return B

    def send_data(self, data):
        ###################
        # Purpose: sends data to the client. 
        # If connect_status is True, return True. Else, return None
        ###################
        if self.connect_status:
            self.client.send(data)
            return True
        else:
            return None

    def recv_data(self):
        ###################
        # Purpose: receive data from the client. 
        # It will return timeout exception on timeout. 
        ###################        
        return self.client.recv(self.buffer_size)

class Client():
    def __init__(self, tcp_ip, port = 6000, buffer_size = 1024):
        socket.setdefaulttimeout(10.0) # this time has to set based on the time taken by synapse. If less time is set exception is raised
        self.connect_status = False
        self.data_received = False
        self.TCP_IP = tcp_ip
        self.TCP_PORT = port
        self.buffer_size = buffer_size
        # self.init_socket(timeout = 10) # In realtime, call wait_for_connection from outside. 

    def sock_connect(self, timeout = 30):
        ######################
        # Description:
        #   If already connected, return True
        #   Else, keep trying to connect forever until timeout.
        #   This functions sends 'Handshake' to the server.
        ######################
        print('Client: Connecting to server .', end= '')
        if(self.connect_status): 
            print('Connected!')
            return True

        start = time.time()
        while(not self.connect_status):
            try:
                self.sock = socket.socket()
                self.sock.connect((self.TCP_IP, self.TCP_PORT)) ## Blocking call. Gives time out exception on time out.
                self.connect_status = True
                self.sock.send(INITIAL_MESSAGE)
                print('. ', end= '')
                time.sleep(0.5)                 
            except Exception as exp:
                print('. ', end= '')
                time.sleep(0.5)
            if(time.time()-start > timeout):
                print('Connection Failed! Waited for more than ' + str(timeout) + ' seconds.')
                sys.exit(0)

    def sock_recv(self, timeout = 30):
        ######################
        # Description: 
        #   Infinitely wait for a delivery message after sending 'Handshake' to the server
        #   It releases when server sends 'True' back
        ######################
        print('\nWaiting for delivery message: .', )
        data = None
        start = time.time()
        while(not self.data_received):
            try:
                data = self.sock.recv(self.buffer_size) # Blocking call # Gives time out exception
                print('Received: ', data)
                if data:
                    print('Handshake successfull ! ! !')
                    self.data_received = True
                    break
                print('. ', end= '')
            except Exception as exp:
                print('. ', end= '')
                time.sleep(0.5)
            if(time.time()-start > timeout):
                print('No delivery message! Waited for more than ' + str(timeout) + ' seconds.')
                sys.exit(0)     

        return data

    def init_socket(self, timeout = 30):
        ## After creating instance of Server class. Call init_socket() for establishing the connection.
        self.sock_connect()
        self.sock_recv()

    def send_data(self, data):  
        ###################
        # Purpose: sends data to the server. 
        # If connect_status is True, return the delivery message of the server. Else, return None
        ###################        
        if self.connect_status:
            self.sock.send(data)
            return self.sock.recv(self.buffer_size)
        else:
            return None

    def close(self):
        ## Close the connection with the server. 
        self.sock.close()

if __name__ == '__main__':
    tcp_ip = 'localhost'
    tcp_port = 5000 

    server = Server(tcp_ip, tcp_port, buffer_size = 1000000)
    server_thread = Thread(name='server_thread', target=server.run)    

    client = Client(tcp_ip, tcp_port, buffer_size = 1000000)
    # client_thread = Thread(name='client_thread', target=client.run)

    server_thread.start()

    idx = 0
    while(idx < 3):
        print('idx: ', idx)
        if(not client.connect_status): client.init_socket()
        try:
            ## When you call server.example_run_image
            # A = np.random.randint(0, 255, (80, 80, 3))
            # astr = '_'.join(map(str, list(A.shape) + A.flatten().tolist()))
            # flag = client.send_data(astr)

            ## When you call server.run
            flag = client.send_data('Hello World')
        except Exception as exp:
            print('raising exception', exp)
            client.connect_status = False
            break
        idx += 1

    print('Closing the client')
    client.close()