import numpy as np
import os, sys
import random, socket
from threading import Thread
import time

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

    def run(self):
        print '--------- Server ---------'
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.client.recv(32)
                flag = self.process_data(data)
                self.client.send(str(flag))
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
        data = self.client.recv(self.buffer_size)
        if data == INITIAL_MESSAGE:
            print 'Received a handshake'
            self.connect_status = True
            self.client.send(str(True))

    def process_data(self, data):
        return True

class Client():
    def __init__(self, tcp_ip, port = 6000):
        socket.setdefaulttimeout(10.0) # this time has to set based on the time taken by synapse. If less time is set exception is raised
        self.connect_status = False
        self.data_received = False
        self.TCP_IP = tcp_ip
        self.TCP_PORT = port

        # self.init_socket(timeout = 10)

    def sock_connect(self, timeout = 30):
        # Description:
        #   If connected, return as is
        #   Else, keep trying to connect forever. 
        print 'Connecting to server .', 
        if(self.connect_status): 
            print 'Connected!'
            return

        start = time.time()
        while(not self.connect_status):
            try:
                self.sock = socket.socket()
                self.sock.connect((self.TCP_IP, self.TCP_PORT)) ## Blocking call. Gives time out exception on time out.
                self.connect_status = True
                self.sock.send(INITIAL_MESSAGE)
                print '. ',
                time.sleep(0.5)                 
            except Exception as exp:
                print '. ',
                time.sleep(0.5)
            if(time.time()-start > timeout):
                print 'Connection Failed! Waited for more than ' + str(timeout) + ' seconds.'
                sys.exit(0)

    def sock_recv(self, timeout = 30):
        print '\nWaiting for delivery message: .', 
        data = None
        start = time.time()
        while(not self.data_received):
            try:
                data = self.sock.recv(32) # Blocking call # Gives time out exception
                if data:
                    print('Handshake successfull ! ! !')
                    self.data_received = True
                    break
                print '. ',
            except Exception as exp:
                print '. ',
                time.sleep(0.5)

            if(time.time()-start > timeout):
                print 'No delivery message! Waited for more than ' + str(timeout) + ' seconds.'
                sys.exit(0)     

        return data

    def init_socket(self, timeout = 30):
        self.sock_connect()
        self.sock_recv()

    def send_data(self, data):  
        if self.connect_status:
            self.sock.send(data)
            return bool(self.sock.recv(32))
        else:
            return None

if __name__ == '__main__':
    tcp_ip = 'localhost'
    tcp_port = 5000 

    server = Server(tcp_ip, tcp_port)
    server_thread = Thread(name='server_thread', target=server.run)    

    client = Client(tcp_ip, tcp_port)
    # client_thread = Thread(name='client_thread', target=client.run)

    server_thread.start()

    idx = 0
    while(idx < 3):
        if(not client.connect_status): client.init_socket()
        try:
            value = str(random.randint(0, 100))
            flag = client.send_data(value)
            print value
        except Exception as exp:
            print 'raising exception',exp
            client.connect_status = False
        time.sleep(0.5)
        idx += 1

    print 'Closing the client'
    client.sock.close()