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
        # self.wait_for_connection()

    def recv_image(self, buf_sz = 200000):
        data = self.client.recv(buf_sz)
        if(len(data) == 0): return None

        flag = False
        if(data[-1] != '!'): flag = True
        num_chunks = 1
        while(flag):
            num_chunks += 1
            data += self.client.recv(buf_sz)
            if(data[-1] == '!'): flag = False
        print('No. of chunks: ', num_chunks)
        return data[:-1]

    def run_image(self):
        print('--------- Server ---------')
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.recv_image()
                # print 'Len. of data: ', len(data)
                flag = self.process_data(data)
                self.client.send(str(flag is not None))
                time.sleep(0.5)
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                break ########## Remove it later on

    def run(self):
        print('--------- Server ---------')
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.client.recv(self.buffer_size)
                print(data[:20])
                finger_lengths = self.process_data(data)
                self.client.send(str(finger_lengths is not None))
                time.sleep(0.5)
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                break ########## Remove it later on

    def wait_for_connection(self):
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
        if(data is None or len(data) == 0): return None
        ## TODO: Handle empty strings

        data = data.split('_')
        print(len(data))
        img_shape = tuple(map(int, data[:3]))
        data = data[3:]
        B = np.reshape(map(np.uint8, data), img_shape)
        # cv2.imshow('Received Image', B)
        # cv2.waitKey(0)        

        return B

    def send_data(self, data):
        if self.connect_status:
            self.client.send(data)
            return True
        else:
            return None

    def recv_data(self):
        return self.client.recv(self.buffer_size)

class Client():
    def __init__(self, tcp_ip, port = 6000, buffer_size = 1024):
        socket.setdefaulttimeout(10.0) # this time has to set based on the time taken by synapse. If less time is set exception is raised
        self.connect_status = False
        self.data_received = False
        self.TCP_IP = tcp_ip
        self.TCP_PORT = port
        self.buffer_size = buffer_size

        # self.init_socket(timeout = 10)

    def sock_connect(self, timeout = 30):
        # Description:
        #   If connected, return as is
        #   Else, keep trying to connect forever. 
        print('Client: Connecting to server .', )
        if(self.connect_status): 
            print('Connected!')
            return

        start = time.time()
        while(not self.connect_status):
            try:
                self.sock = socket.socket()
                self.sock.connect((self.TCP_IP, self.TCP_PORT)) ## Blocking call. Gives time out exception on time out.
                self.connect_status = True
                self.sock.send(INITIAL_MESSAGE)
                print('. ',)
                time.sleep(0.5)                 
            except Exception as exp:
                print('. ',)
                time.sleep(0.5)
            if(time.time()-start > timeout):
                print('Connection Failed! Waited for more than ' + str(timeout) + ' seconds.')
                sys.exit(0)

    def sock_recv(self, timeout = 30):
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
                print('. ',)
            except Exception as exp:
                print('. ',)
                time.sleep(0.5)

            if(time.time()-start > timeout):
                print('No delivery message! Waited for more than ' + str(timeout) + ' seconds.')
                sys.exit(0)     

        return data

    def init_socket(self, timeout = 30):
        self.sock_connect()
        self.sock_recv()

    def send_data(self, data):  
        if self.connect_status:
            self.sock.send(data)
            return self.sock.recv(self.buffer_size)
        else:
            return None

    def close(self):
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
            A = np.random.randint(0, 255, (80, 80, 3))
            astr = '_'.join(map(str, list(A.shape) + A.flatten().tolist()))
            flag = client.send_data(astr)
            # print flag
        except Exception as exp:
            print('raising exception', exp)
            client.connect_status = False
            break
        # time.sleep(0.5)
        idx += 1

    print('Closing the client')
    client.close()